from __future__ import annotations

import io
import re
<<<<<<< HEAD
import unicodedata
=======
>>>>>>> origin/main
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st

<<<<<<< HEAD

st.set_page_config(
    page_title="Explorador de fauna por informes mineros",
    page_icon="🦎",
=======
# =============================================================
# CONFIGURACIÓN GENERAL
# =============================================================
st.set_page_config(
    page_title="Especies por informes mineros",
    page_icon="🌿",
>>>>>>> origin/main
    layout="wide",
    initial_sidebar_state="expanded",
)

<<<<<<< HEAD
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
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

=======
DATA_DIR = Path("data")
SHEET_NAME = "03_Consolidado_Streamlit"
TEMP_PREFIX = "~$"

>>>>>>> origin/main
REQUIRED_COLUMNS = [
    "anio",
    "id_registro_anual",
    "id_estudio_anual",
    "codigo_estudio_limpio",
    "titulo_estudio",
<<<<<<< HEAD
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


def normalize_colname(name: object) -> str:
    text = unicodedata.normalize("NFKD", str(name).strip().lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\s+", "_", text)
=======
    "sector_asociado",
    "grupo_biologico",
    "familia",
    "nombre_cientifico",
    "estado_revision",
]

OPTIONAL_COLUMNS = [
    "remitente",
    "departamento_estudio",
    "provincia_estudio",
    "tipo_documento",
    "tipo",
    "orden",
    "clase",
    "subclase",
    "nivel_taxonomico_registro",
    "observacion_saneamiento",
    "tipo_asignacion",
    "fuente_archivo_anual",
]

# Paleta discreta estable para categorías biológicas.
COLOR_SEQUENCE = px.colors.qualitative.Set2 + px.colors.qualitative.Pastel


# =============================================================
# UTILIDADES
# =============================================================
def normalize_colname(name: object) -> str:
    """Convierte nombres de columnas a formato seguro para análisis."""
    text = str(name).strip().lower()
    text = re.sub(r"\s+", "_", text)
    text = text.replace("á", "a").replace("é", "e").replace("í", "i")
    text = text.replace("ó", "o").replace("ú", "u").replace("ñ", "n")
>>>>>>> origin/main
    text = re.sub(r"[^a-z0-9_]+", "", text)
    return text


def extract_year_from_filename(filename: str) -> int | None:
    match = re.search(r"(20\d{2})", filename)
<<<<<<< HEAD
    return int(match.group(1)) if match else None
=======
    if match:
        return int(match.group(1))
    return None
>>>>>>> origin/main


def clean_text_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
<<<<<<< HEAD
            df[col] = df[col].astype("string").fillna("").str.replace(r"\s+", " ", regex=True).str.strip()
    return df


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in CORE_COLUMNS:
=======
            df[col] = (
                df[col]
                .astype("string")
                .fillna("")
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
            )
    return df


def ensure_expected_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in REQUIRED_COLUMNS + OPTIONAL_COLUMNS:
>>>>>>> origin/main
        if col not in df.columns:
            df[col] = pd.NA
    return df


<<<<<<< HEAD
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


@st.cache_data(show_spinner="Leyendo Excel anuales desde data/")
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


=======
>>>>>>> origin/main
def to_excel_bytes(df: pd.DataFrame, sheet_name: str = "datos_filtrados") -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
        workbook = writer.book
        worksheet = writer.sheets[sheet_name[:31]]
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#0F766E", "font_color": "#FFFFFF"})
        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, header_fmt)
<<<<<<< HEAD
            width = min(max(len(str(value)) + 4, 12), 42)
=======
            width = min(max(len(str(value)) + 4, 12), 38)
>>>>>>> origin/main
            worksheet.set_column(col_num, col_num, width)
        worksheet.autofilter(0, 0, max(len(df), 1), max(len(df.columns) - 1, 0))
        worksheet.freeze_panes(1, 0)
    return output.getvalue()


<<<<<<< HEAD
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
        selected_years = st.multiselect("Año", years, default=years)

        groups = option_values(data, "grupo_biologico")
        selected_groups = st.multiselect("Grupo biológico", groups, default=groups)

        departments = option_values(data, "departamento_estudio")
        selected_departments = st.multiselect("Departamento", departments, default=departments)

        provinces = option_values(data, "provincia_estudio")
        selected_provinces = st.multiselect("Provincia", provinces, default=provinces)

        families = option_values(data, "familia")
        selected_families = st.multiselect("Familia", families, default=families)

        studies = option_values(data, "codigo_estudio_limpio")
        selected_studies = st.multiselect("Código de estudio", studies, default=studies)

        coord_mode = st.radio("Coordenadas", ["Todos", "Solo con coordenadas", "Sin coordenadas"], horizontal=False)
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
=======
def safe_unique_count(df: pd.DataFrame, column: str) -> int:
    if column not in df.columns or df.empty:
        return 0
    return int(df[column].dropna().astype(str).replace("", pd.NA).dropna().nunique())


def safe_count(df: pd.DataFrame) -> int:
    return int(len(df)) if df is not None else 0


def plot_empty(message: str) -> None:
    st.info(message)


# =============================================================
# CARGA DE DATOS
# =============================================================
@st.cache_data(show_spinner="Leyendo archivos Excel desde la carpeta data/…")
def load_data(data_dir: str, sheet_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    folder = Path(data_dir)
    files = sorted(
        [
            file
            for file in folder.glob("*.xlsx")
            if file.is_file() and not file.name.startswith(TEMP_PREFIX)
        ]
    )

    logs: list[dict[str, object]] = []
    frames: list[pd.DataFrame] = []

    if not folder.exists():
        return pd.DataFrame(), pd.DataFrame(
            [{"archivo": str(folder), "estado": "ERROR", "detalle": "No existe la carpeta data/."}]
        )

    if not files:
        return pd.DataFrame(), pd.DataFrame(
            [{"archivo": "data/", "estado": "ERROR", "detalle": "No se encontraron archivos .xlsx."}]
        )

    for file in files:
        try:
            raw = pd.read_excel(file, sheet_name=sheet_name, engine="openpyxl")
            raw.columns = [normalize_colname(col) for col in raw.columns]
            raw = ensure_expected_columns(raw)

            if raw["anio"].isna().all() or (raw["anio"].astype(str).str.strip() == "").all():
                year = extract_year_from_filename(file.name)
                raw["anio"] = year

            raw["archivo_leido"] = file.name
            raw = clean_text_columns(
                raw,
                [
                    "id_registro_anual",
                    "id_estudio_anual",
                    "codigo_estudio_limpio",
                    "titulo_estudio",
                    "sector_asociado",
                    "grupo_biologico",
                    "familia",
                    "nombre_cientifico",
                    "remitente",
                    "departamento_estudio",
                    "provincia_estudio",
                    "tipo_documento",
                    "tipo",
                    "orden",
                    "estado_revision",
                ],
            )
            raw["anio"] = pd.to_numeric(raw["anio"], errors="coerce").astype("Int64")
            frames.append(raw)
            logs.append(
                {
                    "archivo": file.name,
                    "estado": "OK",
                    "detalle": f"{len(raw):,} registros leídos desde {sheet_name}.",
                }
            )
        except Exception as exc:  # noqa: BLE001
            logs.append({"archivo": file.name, "estado": "ERROR", "detalle": str(exc)})

    data = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    log_df = pd.DataFrame(logs)
    return data, log_df


# =============================================================
# INTERFAZ
# =============================================================
st.markdown(
    """
    <style>
        .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
        [data-testid="stMetricValue"] {font-size: 1.6rem;}
        .small-note {font-size: 0.88rem; color: #4B5563;}
>>>>>>> origin/main
    </style>
    """,
    unsafe_allow_html=True,
)

<<<<<<< HEAD
st.title("🦎 Explorador de fauna por informes mineros")
st.caption(
    "Consulta registros anuales consolidados. Para agregar nuevos años, coloca Excel con la misma hoja "
    "03_Consolidado_Streamlit dentro de data/."
)

with st.sidebar:
    st.header("Datos")
    st.write("La aplicación lee todos los archivos `.xlsx` de `data/`.")
    if st.button("Recargar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

data, load_log = load_data(str(DATA_DIR), SHEET_NAME)

with st.sidebar:
    st.subheader("Estado de carga")
    st.dataframe(load_log, use_container_width=True, hide_index=True)

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

tabs = st.tabs(["Dashboard", "Estudios", "Especies", "Coordenadas", "Calidad", "Descarga"])

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
=======
st.title("🌿 Explorador de especies por informes mineros")
st.caption(
    "Aplicativo para consultar, comparar y validar registros de especies extraídos de informes o estudios vinculados al sector minero."
)

with st.sidebar:
    st.header("Configuración")
    st.write("Fuente de datos: Excel anual en carpeta `data/`.")
    if st.button("🔄 Recargar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    data, log_df = load_data(str(DATA_DIR), SHEET_NAME)

    st.divider()
    st.subheader("Estado de carga")
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True, hide_index=True)

if data.empty:
    st.error(
        "No se pudo cargar información. Verifica que exista la carpeta data/ y que los Excel tengan la hoja "
        f"`{SHEET_NAME}`."
    )
    st.stop()

# Filtros globales
with st.sidebar:
    st.divider()
    st.header("Filtros")

    years = sorted([int(x) for x in data["anio"].dropna().unique()])
    selected_years = st.multiselect("Año", years, default=years)

    groups = sorted(data["grupo_biologico"].dropna().astype(str).unique())
    selected_groups = st.multiselect("Grupo biológico", groups, default=groups)

    families = sorted(data["familia"].dropna().astype(str).unique())
    selected_families = st.multiselect("Familia", families, default=families)

    departments = sorted(data["departamento_estudio"].dropna().astype(str).unique())
    selected_departments = st.multiselect("Departamento del estudio", departments, default=departments)

    study_options = sorted(data["titulo_estudio"].dropna().astype(str).unique())
    selected_studies = st.multiselect("Estudio / informe", study_options, default=study_options)

    species_query = st.text_input("Buscar especie", placeholder="Ej.: Vanessa, Agromyzidae, sp.")

filtered = data.copy()
if selected_years:
    filtered = filtered[filtered["anio"].isin(selected_years)]
if selected_groups:
    filtered = filtered[filtered["grupo_biologico"].isin(selected_groups)]
if selected_families:
    filtered = filtered[filtered["familia"].isin(selected_families)]
if selected_departments:
    filtered = filtered[filtered["departamento_estudio"].isin(selected_departments)]
if selected_studies:
    filtered = filtered[filtered["titulo_estudio"].isin(selected_studies)]
if species_query.strip():
    q = species_query.strip().lower()
    filtered = filtered[filtered["nombre_cientifico"].str.lower().str.contains(q, na=False)]

# Aviso de estructura
missing_required = [col for col in REQUIRED_COLUMNS if col not in data.columns]
if missing_required:
    st.warning("Faltan columnas obligatorias: " + ", ".join(missing_required))

# KPIs
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
kpi1.metric("Años", safe_unique_count(filtered, "anio"))
kpi2.metric("Estudios", safe_unique_count(filtered, "id_estudio_anual"))
kpi3.metric("Registros", f"{safe_count(filtered):,}")
kpi4.metric("Especies únicas", safe_unique_count(filtered, "nombre_cientifico"))
kpi5.metric("Familias", safe_unique_count(filtered, "familia"))
kpi6.metric("Grupos", safe_unique_count(filtered, "grupo_biologico"))

st.divider()

# =============================================================
# TABS PRINCIPALES
# =============================================================
tab_dashboard, tab_estudios, tab_especies, tab_calidad, tab_descarga = st.tabs(
    [
        "📊 Dashboard",
        "📁 Explorador de estudios",
        "🔎 Explorador de especies",
        "✅ Control de calidad",
        "⬇️ Descarga",
    ]
)

with tab_dashboard:
    st.subheader("Dashboard general")
    st.write("Vista ejecutiva de registros, estudios y composición taxonómica.")

    col_a, col_b = st.columns(2)

    with col_a:
        records_by_year = (
            filtered.groupby("anio", dropna=False)
            .size()
            .reset_index(name="registros")
            .sort_values("anio")
        )
        if not records_by_year.empty:
            fig = px.bar(
                records_by_year,
                x="anio",
                y="registros",
                text="registros",
                title="Registros de especies por año",
            )
            fig.update_layout(xaxis_title="Año", yaxis_title="Registros", title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)
        else:
            plot_empty("No hay registros para graficar por año.")

    with col_b:
        species_by_year = (
            filtered.dropna(subset=["nombre_cientifico"])
            .groupby("anio")["nombre_cientifico"]
            .nunique()
            .reset_index(name="especies_unicas")
            .sort_values("anio")
        )
        if not species_by_year.empty:
            fig = px.line(
                species_by_year,
                x="anio",
                y="especies_unicas",
                markers=True,
                title="Especies únicas por año",
            )
            fig.update_layout(xaxis_title="Año", yaxis_title="Especies únicas", title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)
        else:
            plot_empty("No hay especies únicas para graficar por año.")

    col_c, col_d = st.columns(2)

    with col_c:
        composition = (
            filtered.groupby(["anio", "grupo_biologico"], dropna=False)
            .size()
            .reset_index(name="registros")
            .sort_values(["anio", "grupo_biologico"])
        )
        if not composition.empty:
            fig = px.bar(
                composition,
                x="anio",
                y="registros",
                color="grupo_biologico",
                color_discrete_sequence=COLOR_SEQUENCE,
                title="Composición por grupo biológico y año",
            )
            fig.update_layout(
                xaxis_title="Año",
                yaxis_title="Registros",
                legend_title="Grupo biológico",
                title_x=0.02,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            plot_empty("No hay composición por grupo biológico para graficar.")

    with col_d:
        study_ranking = (
            filtered.groupby(["id_estudio_anual", "codigo_estudio_limpio", "titulo_estudio"], dropna=False)[
                "nombre_cientifico"
            ]
            .nunique()
            .reset_index(name="especies_unicas")
            .sort_values("especies_unicas", ascending=True)
            .tail(15)
        )
        if not study_ranking.empty:
            study_ranking["estudio_corto"] = study_ranking["codigo_estudio_limpio"].astype(str) + " | " + study_ranking[
                "titulo_estudio"
            ].astype(str).str.slice(0, 60)
            fig = px.bar(
                study_ranking,
                y="estudio_corto",
                x="especies_unicas",
                orientation="h",
                text="especies_unicas",
                title="Estudios con mayor número de especies únicas",
            )
            fig.update_layout(xaxis_title="Especies únicas", yaxis_title="Estudio", title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)
        else:
            plot_empty("No hay estudios para ranking.")

    st.subheader("Tabla consolidada filtrada")
>>>>>>> origin/main
    display_cols = [
        "anio",
        "codigo_estudio_limpio",
        "titulo_estudio",
        "departamento_estudio",
<<<<<<< HEAD
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
=======
        "grupo_biologico",
        "familia",
        "nombre_cientifico",
        "estado_revision",
        "archivo_leido",
    ]
    display_cols = [col for col in display_cols if col in filtered.columns]
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

with tab_estudios:
>>>>>>> origin/main
    st.subheader("Explorador de estudios")
    study_table = (
        filtered.groupby(
            [
                "anio",
                "id_estudio_anual",
                "codigo_estudio_limpio",
                "titulo_estudio",
<<<<<<< HEAD
=======
                "remitente",
>>>>>>> origin/main
                "departamento_estudio",
                "provincia_estudio",
                "tipo_documento",
                "sector_asociado",
<<<<<<< HEAD
                "fuente_archivo_anual",
=======
>>>>>>> origin/main
            ],
            dropna=False,
        )
        .agg(
            registros=("id_registro_anual", "count"),
<<<<<<< HEAD
            taxones=("nombre_cientifico", "nunique"),
            familias=("familia", "nunique"),
            estaciones=("estacion_fuente_original", "nunique"),
=======
            especies_unicas=("nombre_cientifico", "nunique"),
            familias=("familia", "nunique"),
            grupos=("grupo_biologico", "nunique"),
>>>>>>> origin/main
        )
        .reset_index()
        .sort_values(["anio", "codigo_estudio_limpio"])
    )
<<<<<<< HEAD
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
=======

    if study_table.empty:
        st.info("No hay estudios con los filtros actuales.")
    else:
        selected_study_id = st.selectbox(
            "Selecciona un estudio",
            study_table["id_estudio_anual"].tolist(),
            format_func=lambda x: study_table.loc[study_table["id_estudio_anual"] == x, "codigo_estudio_limpio"].iloc[0]
            + " | "
            + study_table.loc[study_table["id_estudio_anual"] == x, "titulo_estudio"].iloc[0][:100],
        )
        study_row = study_table[study_table["id_estudio_anual"] == selected_study_id].iloc[0]
        study_df = filtered[filtered["id_estudio_anual"] == selected_study_id]

        info1, info2, info3, info4 = st.columns(4)
        info1.metric("Registros", int(study_row["registros"]))
        info2.metric("Especies únicas", int(study_row["especies_unicas"]))
        info3.metric("Familias", int(study_row["familias"]))
        info4.metric("Grupos", int(study_row["grupos"]))

        st.markdown("**Ficha del estudio**")
        ficha = pd.DataFrame(
            [
                ["Año", study_row["anio"]],
                ["Código", study_row["codigo_estudio_limpio"]],
                ["Título", study_row["titulo_estudio"]],
                ["Remitente", study_row["remitente"]],
                ["Departamento", study_row["departamento_estudio"]],
                ["Provincia", study_row["provincia_estudio"]],
                ["Tipo de documento", study_row["tipo_documento"]],
                ["Sector", study_row["sector_asociado"]],
            ],
            columns=["Campo", "Valor"],
        )
        st.dataframe(ficha, use_container_width=True, hide_index=True)

        col_e, col_f = st.columns(2)
        with col_e:
            group_counts = study_df.groupby("grupo_biologico").size().reset_index(name="registros")
            fig = px.bar(
                group_counts,
                x="grupo_biologico",
                y="registros",
                text="registros",
                color="grupo_biologico",
                color_discrete_sequence=COLOR_SEQUENCE,
                title="Registros por grupo biológico",
            )
            fig.update_layout(showlegend=False, xaxis_title="Grupo", yaxis_title="Registros", title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)

        with col_f:
            family_counts = (
                study_df.groupby("familia")["nombre_cientifico"]
                .nunique()
                .reset_index(name="especies_unicas")
                .sort_values("especies_unicas", ascending=True)
                .tail(12)
            )
            fig = px.bar(
                family_counts,
                y="familia",
                x="especies_unicas",
                orientation="h",
                text="especies_unicas",
                title="Familias más representadas",
            )
            fig.update_layout(xaxis_title="Especies únicas", yaxis_title="Familia", title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Lista de especies del estudio seleccionado**")
        species_cols = [
>>>>>>> origin/main
            "grupo_biologico",
            "familia",
            "orden",
            "nombre_cientifico",
<<<<<<< HEAD
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
=======
            "nivel_taxonomico_registro",
            "estado_revision",
        ]
        species_cols = [col for col in species_cols if col in study_df.columns]
        st.dataframe(
            study_df[species_cols].drop_duplicates().sort_values(["grupo_biologico", "familia", "nombre_cientifico"]),
            use_container_width=True,
            hide_index=True,
        )

with tab_especies:
    st.subheader("Explorador de especies")
    species_table = (
        filtered.groupby(["nombre_cientifico", "grupo_biologico", "familia"], dropna=False)
        .agg(
            registros=("id_registro_anual", "count"),
            estudios=("id_estudio_anual", "nunique"),
            anios=("anio", "nunique"),
>>>>>>> origin/main
        )
        .reset_index()
        .sort_values(["estudios", "registros"], ascending=False)
    )

<<<<<<< HEAD
    c1, c2 = st.columns(2)
    with c1:
        top_species = species_table.head(20).sort_values("registros", ascending=True)
=======
    col_g, col_h = st.columns([1, 1])
    with col_g:
        top_species = species_table.head(20).sort_values("estudios", ascending=True)
>>>>>>> origin/main
        if not top_species.empty:
            fig = px.bar(
                top_species,
                y="nombre_cientifico",
<<<<<<< HEAD
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
    st.subheader("Coordenadas UTM")
    coord_df = filtered[filtered["este_fuente_original"].notna() & filtered["norte_fuente_original"].notna()].copy()
    if coord_df.empty:
        st.info("No hay registros con coordenadas para los filtros actuales.")
    else:
        fig = px.scatter(
            coord_df,
            x="este_fuente_original",
            y="norte_fuente_original",
            color="grupo_biologico",
            facet_col="zona_utm_fuente_original" if coord_df["zona_utm_fuente_original"].nunique() <= 4 else None,
            hover_data=[
                "nombre_cientifico",
                "nombre_comun",
                "codigo_estudio_limpio",
                "estacion_fuente_original",
                "departamento_estudio",
                "provincia_estudio",
            ],
            color_discrete_sequence=COLOR_SEQUENCE,
            title="Distribución de registros con coordenadas UTM",
        )
        fig.update_layout(xaxis_title="Este", yaxis_title="Norte", title_x=0.02)
        st.plotly_chart(fig, use_container_width=True)

        coord_cols = [
            "anio",
            "codigo_estudio_limpio",
            "grupo_biologico",
            "nombre_cientifico",
            "nombre_comun",
            "estacion_fuente_original",
            "este_fuente_original",
            "norte_fuente_original",
            "zona_utm_fuente_original",
            "departamento_estudio",
            "provincia_estudio",
            "fuente_base_especies",
            "pagina_fuente_original",
        ]
        st.dataframe(coord_df[[c for c in coord_cols if c in coord_df.columns]], use_container_width=True, hide_index=True)

with tabs[4]:
    st.subheader("Control de calidad")
    st.dataframe(quality_checks(data), use_container_width=True, hide_index=True)

    q1, q2 = st.columns(2)
    with q1:
        st.markdown("**Registros sin coordenadas**")
        no_coords = data[data["este_fuente_original"].isna() | data["norte_fuente_original"].isna()]
        st.dataframe(
            no_coords[
                [
                    c
                    for c in [
                        "anio",
                        "codigo_estudio_limpio",
                        "nombre_cientifico",
                        "grupo_biologico",
                        "estado_revision",
                        "archivo_leido",
                    ]
                    if c in no_coords.columns
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
    with q2:
        st.markdown("**Grupos fuera de fauna esperada**")
        non_fauna = data[~data["grupo_biologico"].isin(FAUNA_GROUPS)]
        st.dataframe(
            non_fauna[
                [
                    c
                    for c in [
                        "anio",
                        "codigo_estudio_limpio",
                        "nombre_cientifico",
                        "grupo_biologico",
                        "familia",
                        "archivo_leido",
                    ]
                    if c in non_fauna.columns
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

with tabs[5]:
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
    st.markdown("**Archivos leidos**")
    st.dataframe(load_log, use_container_width=True, hide_index=True)

st.caption(
    "Actualización multiaño: agrega nuevos Excel en data/ con la hoja 03_Consolidado_Streamlit y la misma estructura."
=======
                x="estudios",
                orientation="h",
                text="estudios",
                color="grupo_biologico",
                color_discrete_sequence=COLOR_SEQUENCE,
                title="Especies más frecuentes según número de estudios",
            )
            fig.update_layout(xaxis_title="Estudios", yaxis_title="Especie", title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)
    with col_h:
        family_ranking = (
            filtered.groupby("familia")["nombre_cientifico"]
            .nunique()
            .reset_index(name="especies_unicas")
            .sort_values("especies_unicas", ascending=True)
            .tail(15)
        )
        if not family_ranking.empty:
            fig = px.bar(
                family_ranking,
                y="familia",
                x="especies_unicas",
                orientation="h",
                text="especies_unicas",
                title="Ranking de familias por especies únicas",
            )
            fig.update_layout(xaxis_title="Especies únicas", yaxis_title="Familia", title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Tabla de especies**")
    st.dataframe(species_table, use_container_width=True, hide_index=True)

    species_options = species_table["nombre_cientifico"].dropna().astype(str).tolist()
    if species_options:
        selected_species = st.selectbox("Selecciona una especie para ver detalle", species_options)
        selected_species_df = filtered[filtered["nombre_cientifico"] == selected_species]
        st.markdown(f"**Detalle para:** `{selected_species}`")
        detail_cols = [
            "anio",
            "codigo_estudio_limpio",
            "titulo_estudio",
            "departamento_estudio",
            "provincia_estudio",
            "grupo_biologico",
            "familia",
            "estado_revision",
        ]
        detail_cols = [col for col in detail_cols if col in selected_species_df.columns]
        st.dataframe(selected_species_df[detail_cols].drop_duplicates(), use_container_width=True, hide_index=True)

with tab_calidad:
    st.subheader("Control de calidad")
    st.write("Revisión automática de estructura mínima y posibles problemas antes de actualizar la base.")

    checks = []
    for col in REQUIRED_COLUMNS:
        if col not in data.columns:
            checks.append({"control": f"Existe columna {col}", "resultado": "ERROR", "observacion": "Columna ausente"})
        else:
            empty_count = data[col].isna().sum() + (data[col].astype(str).str.strip() == "").sum()
            checks.append(
                {
                    "control": f"Campos vacíos en {col}",
                    "resultado": "OK" if empty_count == 0 else "REVISAR",
                    "observacion": f"{int(empty_count)} registros vacíos",
                }
            )

    duplicate_ids = data[data["id_registro_anual"].duplicated(keep=False)] if "id_registro_anual" in data else pd.DataFrame()
    duplicate_species_study = data[
        data.duplicated(subset=["id_estudio_anual", "nombre_cientifico"], keep=False)
    ] if {"id_estudio_anual", "nombre_cientifico"}.issubset(data.columns) else pd.DataFrame()

    checks.append(
        {
            "control": "Duplicados de id_registro_anual",
            "resultado": "OK" if duplicate_ids.empty else "REVISAR",
            "observacion": f"{len(duplicate_ids)} registros duplicados",
        }
    )
    checks.append(
        {
            "control": "Especie repetida dentro del mismo estudio",
            "resultado": "OK" if duplicate_species_study.empty else "REVISAR",
            "observacion": f"{len(duplicate_species_study)} registros potencialmente repetidos",
        }
    )

    checks_df = pd.DataFrame(checks)
    st.dataframe(checks_df, use_container_width=True, hide_index=True)

    col_i, col_j = st.columns(2)
    with col_i:
        st.markdown("**Registros con ID duplicado**")
        if duplicate_ids.empty:
            st.success("No se detectaron duplicados en id_registro_anual.")
        else:
            st.dataframe(duplicate_ids, use_container_width=True, hide_index=True)
    with col_j:
        st.markdown("**Especie repetida dentro de un mismo estudio**")
        if duplicate_species_study.empty:
            st.success("No se detectaron repeticiones por especie-estudio.")
        else:
            cols = ["anio", "id_estudio_anual", "codigo_estudio_limpio", "nombre_cientifico", "familia", "grupo_biologico"]
            cols = [col for col in cols if col in duplicate_species_study.columns]
            st.dataframe(duplicate_species_study[cols], use_container_width=True, hide_index=True)

with tab_descarga:
    st.subheader("Descarga de resultados")
    st.write("Puedes descargar la tabla filtrada o los resúmenes principales para reportes rápidos.")

    download_cols = [col for col in filtered.columns if not col.startswith("unnamed")]
    filtered_download = filtered[download_cols].copy()

    csv_bytes = filtered_download.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Descargar tabla filtrada en CSV",
        data=csv_bytes,
        file_name="consolidado_filtrado_especies.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.download_button(
        "Descargar tabla filtrada en Excel",
        data=to_excel_bytes(filtered_download),
        file_name="consolidado_filtrado_especies.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    st.markdown("**Archivos leídos por la aplicación**")
    st.dataframe(log_df, use_container_width=True, hide_index=True)

st.caption(
    "Modo de actualización simple: agrega o reemplaza archivos Excel anuales en la carpeta data/ y mantén la hoja "
    f"{SHEET_NAME} con las mismas columnas."
>>>>>>> origin/main
)
