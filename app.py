from __future__ import annotations

import io
import json
import re
import unicodedata
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st
from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import unary_union


st.set_page_config(
    page_title="Información de Patrimonio forestal - SERFOR",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
GEOJSON_PATH = DATA_DIR / "GEO" / "DEP_PERU.geojson"
SHEET_NAME = "03_Consolidado_Streamlit"
TEMP_PREFIX = "~$"

CORE_COLUMNS = [
    "anio",
    "id_registro_anual",
    "id_estudio_anual",
    "id_registro",
    "id_estudio",
    "codigo_estudio",
    "codigo_estudio_limpio",
    "titulo_estudio",
    "remitente",
    "departamento_estudio",
    "provincia_estudio",
    "sector_asociado",
    "tipo_documento",
    "tipo",
    "id_especie_base",
    "grupo_biologico",
    "nombre_cientifico",
    "nombre_comun",
    "nivel_taxonomico_registro",
    "clase",
    "subclase",
    "orden",
    "familia",
    "estacion_fuente_original",
    "este_fuente_original",
    "norte_fuente_original",
    "zona_utm_fuente_original",
    "departamento_fuente_original",
    "provincia_fuente_original",
    "pagina_fuente_original",
    "fuente_base_especies",
    "observacion_saneamiento",
    "tipo_asignacion",
    "estado_revision",
    "fuente_archivo_anual",
]

REQUIRED_COLUMNS = [
    "anio",
    "id_registro_anual",
    "id_estudio_anual",
    "codigo_estudio_limpio",
    "titulo_estudio",
    "grupo_biologico",
    "nombre_cientifico",
    "este_fuente_original",
    "norte_fuente_original",
    "estado_revision",
]

TEXT_COLUMNS = [
    "id_registro_anual",
    "id_estudio_anual",
    "id_registro",
    "id_estudio",
    "codigo_estudio",
    "codigo_estudio_limpio",
    "titulo_estudio",
    "remitente",
    "departamento_estudio",
    "provincia_estudio",
    "sector_asociado",
    "tipo_documento",
    "tipo",
    "id_especie_base",
    "grupo_biologico",
    "nombre_cientifico",
    "nombre_comun",
    "nivel_taxonomico_registro",
    "clase",
    "subclase",
    "orden",
    "familia",
    "estacion_fuente_original",
    "zona_utm_fuente_original",
    "departamento_fuente_original",
    "provincia_fuente_original",
    "pagina_fuente_original",
    "fuente_base_especies",
    "observacion_saneamiento",
    "tipo_asignacion",
    "estado_revision",
    "fuente_archivo_anual",
    "archivo_leido",
]

NUMERIC_COLUMNS = ["anio", "este_fuente_original", "norte_fuente_original"]

COLOR_SEQUENCE = px.colors.qualitative.Set2 + px.colors.qualitative.Bold
FAUNA_GROUPS = {"anfibios", "artropodos", "aves", "herpetofauna", "mamiferos", "reptiles"}
PERU_UTM_EPSG_PREFIX = "327"


def normalize_colname(name: object) -> str:
    text = unicodedata.normalize("NFKD", str(name).strip().lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_]+", "", text)
    return text


def extract_year_from_filename(filename: str) -> int | None:
    match = re.search(r"(20\d{2})", filename)
    return int(match.group(1)) if match else None


def clean_text_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype("string").fillna("").str.replace(r"\s+", " ", regex=True).str.strip()
    return df


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in CORE_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    return df


def normalize_dataset(df: pd.DataFrame, file_name: str) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalize_colname(col) for col in df.columns]
    df = ensure_columns(df)
    df["archivo_leido"] = file_name

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if df["anio"].isna().all():
        df["anio"] = extract_year_from_filename(file_name)
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int64")

    df = clean_text_columns(df, TEXT_COLUMNS)
    df["grupo_biologico"] = df["grupo_biologico"].str.lower()
    df["estado_revision"] = df["estado_revision"].str.lower()
    return df


@st.cache_data(show_spinner=False)
def load_data(data_dir: str, sheet_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    folder = Path(data_dir)
    logs: list[dict[str, object]] = []
    frames: list[pd.DataFrame] = []

    if not folder.exists():
        return pd.DataFrame(), pd.DataFrame(
            [{"archivo": str(folder), "estado": "ERROR", "detalle": "No existe la carpeta data/."}]
        )

    files = sorted(file for file in folder.glob("*.xlsx") if file.is_file() and not file.name.startswith(TEMP_PREFIX))
    if not files:
        return pd.DataFrame(), pd.DataFrame(
            [{"archivo": "data/", "estado": "ERROR", "detalle": "No se encontraron archivos .xlsx."}]
        )

    for file in files:
        try:
            workbook = pd.ExcelFile(file, engine="openpyxl")
            sheet = sheet_name if sheet_name in workbook.sheet_names else workbook.sheet_names[0]
            raw = pd.read_excel(file, sheet_name=sheet, engine="openpyxl")
            frame = normalize_dataset(raw, file.name)
            frames.append(frame)
            detail = f"{len(frame):,} registros leidos desde {sheet}."
            if sheet != sheet_name:
                detail += f" Hoja esperada no encontrada; se uso {sheet}."
            logs.append({"archivo": file.name, "estado": "OK", "detalle": detail})
        except Exception as exc:  # noqa: BLE001
            logs.append({"archivo": file.name, "estado": "ERROR", "detalle": str(exc)})

    data = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return data, pd.DataFrame(logs)


@st.cache_data(show_spinner=False)
def load_departments_geojson(path: str) -> dict:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_resource(show_spinner=False)
def load_peru_geometry(path: str):
    geojson = load_departments_geojson(path)
    polygons = [shape(feature["geometry"]) for feature in geojson.get("features", []) if feature.get("geometry")]
    return unary_union(polygons)


def safe_unique_count(df: pd.DataFrame, column: str) -> int:
    if df.empty or column not in df.columns:
        return 0
    return int(df[column].dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique())


def option_values(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df.columns:
        return []
    values = df[column].dropna().astype(str).str.strip()
    values = values[values.ne("")]
    return sorted(values.unique().tolist())


def normalize_label(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value).strip().upper())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\s+", " ", text)
    return text


def parse_utm_zone(value: object) -> int | None:
    if pd.isna(value):
        return None
    match = re.search(r"(17|18|19)", str(value))
    return int(match.group(1)) if match else None


def add_geographic_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    coord_df = df[df["este_fuente_original"].notna() & df["norte_fuente_original"].notna()].copy()
    if coord_df.empty:
        return coord_df

    coord_df["zona_utm_num"] = coord_df["zona_utm_fuente_original"].map(parse_utm_zone)
    coord_df["longitud"] = pd.NA
    coord_df["latitud"] = pd.NA

    for zone in sorted(coord_df["zona_utm_num"].dropna().unique()):
        epsg = f"EPSG:{PERU_UTM_EPSG_PREFIX}{int(zone):02d}"
        transformer = Transformer.from_crs(epsg, "EPSG:4326", always_xy=True)
        mask = coord_df["zona_utm_num"].eq(zone)
        lon, lat = transformer.transform(
            coord_df.loc[mask, "este_fuente_original"].astype(float).to_numpy(),
            coord_df.loc[mask, "norte_fuente_original"].astype(float).to_numpy(),
        )
        coord_df.loc[mask, "longitud"] = lon
        coord_df.loc[mask, "latitud"] = lat

    coord_df["longitud"] = pd.to_numeric(coord_df["longitud"], errors="coerce")
    coord_df["latitud"] = pd.to_numeric(coord_df["latitud"], errors="coerce")
    return coord_df.dropna(subset=["longitud", "latitud"])


def keep_points_inside_peru(coord_df: pd.DataFrame, peru_geometry) -> pd.DataFrame:
    if coord_df.empty:
        return coord_df

    inside = coord_df.apply(
        lambda row: peru_geometry.covers(Point(float(row["longitud"]), float(row["latitud"]))),
        axis=1,
    )
    return coord_df[inside].copy()


def department_count_table(df: pd.DataFrame, geojson: dict) -> pd.DataFrame:
    departments = [
        feature["properties"]["DEPARTAMEN"]
        for feature in geojson.get("features", [])
        if feature.get("properties", {}).get("DEPARTAMEN")
    ]
    base = pd.DataFrame({"departamento_mapa": sorted(departments)})

    counts = df.copy()
    counts["departamento_mapa"] = counts["departamento_estudio"].map(normalize_label)
    counts = counts.groupby("departamento_mapa", dropna=False).size().reset_index(name="registros")

    return base.merge(counts, on="departamento_mapa", how="left").fillna({"registros": 0})


def build_department_map(filtered: pd.DataFrame, departments_geojson: dict):
    department_counts = department_count_table(filtered, departments_geojson)
    fig = px.choropleth(
        department_counts,
        geojson=departments_geojson,
        locations="departamento_mapa",
        featureidkey="properties.DEPARTAMEN",
        color="registros",
        hover_name="departamento_mapa",
        hover_data={"departamento_mapa": False, "registros": ":,.0f"},
        color_continuous_scale="Teal",
        projection="mercator",
        title="Registros georreferenciados por departamento",
    )

    coord_df = add_geographic_coordinates(filtered)
    peru_geometry = load_peru_geometry(str(GEOJSON_PATH))
    coord_df = keep_points_inside_peru(coord_df, peru_geometry)
    for idx, (group, group_df) in enumerate(coord_df.groupby("grupo_biologico", dropna=False)):
        hover_text = (
            group_df["nombre_cientifico"].fillna("")
            + "<br>"
            + group_df["codigo_estudio_limpio"].fillna("")
            + "<br>"
            + group_df["departamento_estudio"].fillna("")
            + " / "
            + group_df["provincia_estudio"].fillna("")
        )
        fig.add_scattergeo(
            lon=group_df["longitud"],
            lat=group_df["latitud"],
            mode="markers",
            name=str(group) if str(group).strip() else "Sin grupo",
            text=hover_text,
            hovertemplate="%{text}<extra></extra>",
            marker={
                "size": 7,
                "opacity": 0.78,
                "color": COLOR_SEQUENCE[idx % len(COLOR_SEQUENCE)],
                "line": {"width": 0.6, "color": "#FFFFFF"},
            },
        )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        height=640,
        margin={"l": 0, "r": 0, "t": 56, "b": 0},
        legend_title_text="Grupo biologico",
        coloraxis_colorbar={"title": "Registros"},
    )
    return fig, coord_df


def to_excel_bytes(df: pd.DataFrame, sheet_name: str = "datos_filtrados") -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
        workbook = writer.book
        worksheet = writer.sheets[sheet_name[:31]]
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#0F766E", "font_color": "#FFFFFF"})
        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, header_fmt)
            width = min(max(len(str(value)) + 4, 12), 42)
            worksheet.set_column(col_num, col_num, width)
        worksheet.autofilter(0, 0, max(len(df), 1), max(len(df.columns) - 1, 0))
        worksheet.freeze_panes(1, 0)
    return output.getvalue()


def quality_checks(data: pd.DataFrame) -> pd.DataFrame:
    checks = []
    for col in REQUIRED_COLUMNS:
        if col not in data.columns:
            checks.append({"control": f"Existe columna {col}", "estado": "ERROR", "observacion": "Columna ausente"})
            continue
        empty = data[col].isna() | data[col].astype(str).str.strip().eq("")
        checks.append(
            {
                "control": f"Campos vacios en {col}",
                "estado": "OK" if not empty.any() else "REVISAR",
                "observacion": f"{int(empty.sum())} registros vacios",
            }
        )

    duplicated_id = data.duplicated(subset=["archivo_leido", "id_registro_anual"], keep=False)
    no_coords = data["este_fuente_original"].isna() | data["norte_fuente_original"].isna()
    non_fauna = ~data["grupo_biologico"].isin(FAUNA_GROUPS)
    checks.extend(
        [
            {
                "control": "Duplicados por archivo e id_registro_anual",
                "estado": "OK" if not duplicated_id.any() else "REVISAR",
                "observacion": f"{int(duplicated_id.sum())} registros duplicados",
            },
            {
                "control": "Registros sin coordenadas UTM",
                "estado": "OK" if not no_coords.any() else "REVISAR",
                "observacion": f"{int(no_coords.sum())} registros sin coordenadas",
            },
            {
                "control": "Registros fuera de grupos de fauna esperados",
                "estado": "OK" if not non_fauna.any() else "REVISAR",
                "observacion": f"{int(non_fauna.sum())} registros fuera de fauna esperada",
            },
        ]
    )
    return pd.DataFrame(checks)


def build_filters(data: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.header("Filtros")
        years = sorted([int(x) for x in data["anio"].dropna().unique()])
        selected_years = st.multiselect("Año", years, placeholder="Todos los años")

        groups = option_values(data, "grupo_biologico")
        selected_groups = st.multiselect("Grupo biológico", groups, placeholder="Todos los grupos")

        departments = option_values(data, "departamento_estudio")
        selected_departments = st.multiselect("Departamento", departments, placeholder="Todos los departamentos")

        provinces = option_values(data, "provincia_estudio")
        selected_provinces = st.multiselect("Provincia", provinces, placeholder="Todas las provincias")

        families = option_values(data, "familia")
        selected_families = st.multiselect("Familia", families, placeholder="Todas las familias")

        studies = option_values(data, "codigo_estudio_limpio")
        selected_studies = st.multiselect("Código de estudio", studies, placeholder="Todos los estudios")

        coord_mode = st.selectbox("Coordenadas", ["Todos", "Solo con coordenadas", "Sin coordenadas"])
        query = st.text_input("Buscar especie o nombre común", placeholder="Ej.: Telmatobius, cóndor")

    filtered = data.copy()
    if selected_years:
        filtered = filtered[filtered["anio"].isin(selected_years)]
    if selected_groups:
        filtered = filtered[filtered["grupo_biologico"].isin(selected_groups)]
    if selected_departments:
        filtered = filtered[filtered["departamento_estudio"].isin(selected_departments)]
    if selected_provinces:
        filtered = filtered[filtered["provincia_estudio"].isin(selected_provinces)]
    if selected_families:
        filtered = filtered[filtered["familia"].isin(selected_families)]
    if selected_studies:
        filtered = filtered[filtered["codigo_estudio_limpio"].isin(selected_studies)]

    has_coords = filtered["este_fuente_original"].notna() & filtered["norte_fuente_original"].notna()
    if coord_mode == "Solo con coordenadas":
        filtered = filtered[has_coords]
    elif coord_mode == "Sin coordenadas":
        filtered = filtered[~has_coords]

    if query.strip():
        q = query.strip().lower()
        text = filtered["nombre_cientifico"].str.lower() + " " + filtered["nombre_comun"].str.lower()
        filtered = filtered[text.str.contains(q, na=False)]
    return filtered


st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
    [data-testid="stMetricValue"] {font-size: 1.55rem;}
    div[data-testid="stDataFrame"] {border-radius: 0.75rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Información de Patrimonio forestal - SERFOR")
st.caption("Consulta y analiza registros consolidados de fauna reportados en informes mineros.")

data, _ = load_data(str(DATA_DIR), SHEET_NAME)

if data.empty:
    st.error(f"No se pudo cargar informacion. Verifica que exista `data/` y la hoja `{SHEET_NAME}`.")
    st.stop()

filtered = build_filters(data)

st.divider()
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
kpi1.metric("Anios", safe_unique_count(filtered, "anio"))
kpi2.metric("Estudios", safe_unique_count(filtered, "id_estudio_anual"))
kpi3.metric("Registros", f"{len(filtered):,}")
kpi4.metric("Taxones", safe_unique_count(filtered, "nombre_cientifico"))
kpi5.metric("Familias", safe_unique_count(filtered, "familia"))
kpi6.metric("Con coordenadas", f"{int((filtered['este_fuente_original'].notna() & filtered['norte_fuente_original'].notna()).sum()):,}")

if filtered.empty:
    st.warning("No hay registros para los filtros seleccionados. Ajusta los filtros del panel lateral.")

tabs = st.tabs(["Dashboard", "Estudios", "Especies", "Mapa", "Descarga"])

with tabs[0]:
    st.subheader("Resumen general")
    c1, c2 = st.columns(2)
    with c1:
        by_year = filtered.groupby("anio", dropna=False).size().reset_index(name="registros").sort_values("anio")
        if by_year.empty:
            st.info("No hay registros para los filtros actuales.")
        else:
            fig = px.bar(by_year, x="anio", y="registros", text="registros", title="Registros por año")
            fig.update_layout(xaxis_title="Año", yaxis_title="Registros", title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        by_group = filtered.groupby("grupo_biologico", dropna=False).size().reset_index(name="registros")
        if by_group.empty:
            st.info("No hay grupos para los filtros actuales.")
        else:
            fig = px.pie(
                by_group,
                names="grupo_biologico",
                values="registros",
                title="Distribución por grupo biológico",
                color_discrete_sequence=COLOR_SEQUENCE,
            )
            fig.update_layout(title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        by_department = (
            filtered.groupby("departamento_estudio", dropna=False)
            .size()
            .reset_index(name="registros")
            .sort_values("registros", ascending=True)
        )
        if not by_department.empty:
            fig = px.bar(
                by_department,
                y="departamento_estudio",
                x="registros",
                orientation="h",
                text="registros",
                title="Registros por departamento",
            )
            fig.update_layout(xaxis_title="Registros", yaxis_title="Departamento", title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)
    with c4:
        top_studies = (
            filtered.groupby(["codigo_estudio_limpio", "titulo_estudio"], dropna=False)["nombre_cientifico"]
            .nunique()
            .reset_index(name="taxones")
            .sort_values("taxones", ascending=True)
            .tail(15)
        )
        if not top_studies.empty:
            top_studies["estudio"] = top_studies["codigo_estudio_limpio"] + " | " + top_studies["titulo_estudio"].str.slice(0, 60)
            fig = px.bar(top_studies, y="estudio", x="taxones", orientation="h", text="taxones", title="Taxones por estudio")
            fig.update_layout(xaxis_title="Taxones", yaxis_title="Estudio", title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Vista consolidada filtrada")
    display_cols = [
        "anio",
        "codigo_estudio_limpio",
        "titulo_estudio",
        "departamento_estudio",
        "provincia_estudio",
        "grupo_biologico",
        "familia",
        "nombre_cientifico",
        "nombre_comun",
        "estacion_fuente_original",
        "este_fuente_original",
        "norte_fuente_original",
        "zona_utm_fuente_original",
        "tipo_asignacion",
        "estado_revision",
    ]
    st.dataframe(filtered[[c for c in display_cols if c in filtered.columns]], use_container_width=True, hide_index=True)

with tabs[1]:
    st.subheader("Explorador de estudios")
    study_table = (
        filtered.groupby(
            [
                "anio",
                "id_estudio_anual",
                "codigo_estudio_limpio",
                "titulo_estudio",
                "departamento_estudio",
                "provincia_estudio",
                "tipo_documento",
                "sector_asociado",
                "fuente_archivo_anual",
            ],
            dropna=False,
        )
        .agg(
            registros=("id_registro_anual", "count"),
            taxones=("nombre_cientifico", "nunique"),
            familias=("familia", "nunique"),
            estaciones=("estacion_fuente_original", "nunique"),
        )
        .reset_index()
        .sort_values(["anio", "codigo_estudio_limpio"])
    )
    st.dataframe(study_table, use_container_width=True, hide_index=True)

    if not study_table.empty:
        study_id = st.selectbox(
            "Detalle de estudio",
            study_table["id_estudio_anual"].tolist(),
            format_func=lambda x: study_table.loc[study_table["id_estudio_anual"] == x, "codigo_estudio_limpio"].iloc[0]
            + " | "
            + study_table.loc[study_table["id_estudio_anual"] == x, "titulo_estudio"].iloc[0][:90],
        )
        study_df = filtered[filtered["id_estudio_anual"] == study_id]
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Registros", len(study_df))
        s2.metric("Taxones", safe_unique_count(study_df, "nombre_cientifico"))
        s3.metric("Familias", safe_unique_count(study_df, "familia"))
        s4.metric("Estaciones", safe_unique_count(study_df, "estacion_fuente_original"))

        cols = [
            "grupo_biologico",
            "familia",
            "orden",
            "nombre_cientifico",
            "nombre_comun",
            "estacion_fuente_original",
            "este_fuente_original",
            "norte_fuente_original",
            "zona_utm_fuente_original",
            "tipo_asignacion",
        ]
        st.dataframe(study_df[[c for c in cols if c in study_df.columns]], use_container_width=True, hide_index=True)

with tabs[2]:
    st.subheader("Explorador de especies")
    species_table = (
        filtered.groupby(["nombre_cientifico", "nombre_comun", "grupo_biologico", "familia", "orden"], dropna=False)
        .agg(
            registros=("id_registro_anual", "count"),
            estudios=("id_estudio_anual", "nunique"),
            departamentos=("departamento_estudio", "nunique"),
            estaciones=("estacion_fuente_original", "nunique"),
        )
        .reset_index()
        .sort_values(["estudios", "registros"], ascending=False)
    )

    c1, c2 = st.columns(2)
    with c1:
        top_species = species_table.head(20).sort_values("registros", ascending=True)
        if not top_species.empty:
            fig = px.bar(
                top_species,
                y="nombre_cientifico",
                x="registros",
                color="grupo_biologico",
                orientation="h",
                text="registros",
                title="Taxones con más registros",
                color_discrete_sequence=COLOR_SEQUENCE,
            )
            fig.update_layout(xaxis_title="Registros", yaxis_title="Taxon", title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        families = (
            filtered.groupby("familia")["nombre_cientifico"]
            .nunique()
            .reset_index(name="taxones")
            .sort_values("taxones", ascending=True)
            .tail(15)
        )
        if not families.empty:
            fig = px.bar(families, y="familia", x="taxones", orientation="h", text="taxones", title="Taxones por familia")
            fig.update_layout(xaxis_title="Taxones", yaxis_title="Familia", title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)

    st.dataframe(species_table, use_container_width=True, hide_index=True)

with tabs[3]:
    st.subheader("Mapa de registros")
    if not GEOJSON_PATH.exists():
        st.info("No se encontro la base departamental para construir el mapa.")
    else:
        departments_geojson = load_departments_geojson(str(GEOJSON_PATH))
        fig, coord_df = build_department_map(filtered, departments_geojson)
        st.plotly_chart(fig, use_container_width=True)

        if coord_df.empty:
            st.info("No hay registros georreferenciables para los filtros actuales.")
        else:
            coord_cols = [
                "anio",
                "codigo_estudio_limpio",
                "grupo_biologico",
                "nombre_cientifico",
                "nombre_comun",
                "estacion_fuente_original",
                "departamento_estudio",
                "provincia_estudio",
                "latitud",
                "longitud",
                "zona_utm_fuente_original",
                "fuente_base_especies",
                "pagina_fuente_original",
            ]
            st.dataframe(coord_df[[c for c in coord_cols if c in coord_df.columns]], use_container_width=True, hide_index=True)

with tabs[4]:
    st.subheader("Descarga")
    download_cols = [col for col in filtered.columns if not col.startswith("unnamed")]
    filtered_download = filtered[download_cols].copy()

    st.download_button(
        "Descargar filtrado en CSV",
        data=filtered_download.to_csv(index=False).encode("utf-8-sig"),
        file_name="fauna_filtrada_streamlit.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.download_button(
        "Descargar filtrado en Excel",
        data=to_excel_bytes(filtered_download),
        file_name="fauna_filtrada_streamlit.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
