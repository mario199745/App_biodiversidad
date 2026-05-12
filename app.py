from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st

# =============================================================
# CONFIGURACIÓN GENERAL
# =============================================================
st.set_page_config(
    page_title="Especies por informes mineros",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path("data")
SHEET_NAME = "03_Consolidado_Streamlit"
TEMP_PREFIX = "~$"

REQUIRED_COLUMNS = [
    "anio",
    "id_registro_anual",
    "id_estudio_anual",
    "codigo_estudio_limpio",
    "titulo_estudio",
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
    text = re.sub(r"[^a-z0-9_]+", "", text)
    return text


def extract_year_from_filename(filename: str) -> int | None:
    match = re.search(r"(20\d{2})", filename)
    if match:
        return int(match.group(1))
    return None


def clean_text_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
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
        if col not in df.columns:
            df[col] = pd.NA
    return df


def to_excel_bytes(df: pd.DataFrame, sheet_name: str = "datos_filtrados") -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
        workbook = writer.book
        worksheet = writer.sheets[sheet_name[:31]]
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#0F766E", "font_color": "#FFFFFF"})
        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, header_fmt)
            width = min(max(len(str(value)) + 4, 12), 38)
            worksheet.set_column(col_num, col_num, width)
        worksheet.autofilter(0, 0, max(len(df), 1), max(len(df.columns) - 1, 0))
        worksheet.freeze_panes(1, 0)
    return output.getvalue()


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
    </style>
    """,
    unsafe_allow_html=True,
)

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
    display_cols = [
        "anio",
        "codigo_estudio_limpio",
        "titulo_estudio",
        "departamento_estudio",
        "grupo_biologico",
        "familia",
        "nombre_cientifico",
        "estado_revision",
        "archivo_leido",
    ]
    display_cols = [col for col in display_cols if col in filtered.columns]
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

with tab_estudios:
    st.subheader("Explorador de estudios")
    study_table = (
        filtered.groupby(
            [
                "anio",
                "id_estudio_anual",
                "codigo_estudio_limpio",
                "titulo_estudio",
                "remitente",
                "departamento_estudio",
                "provincia_estudio",
                "tipo_documento",
                "sector_asociado",
            ],
            dropna=False,
        )
        .agg(
            registros=("id_registro_anual", "count"),
            especies_unicas=("nombre_cientifico", "nunique"),
            familias=("familia", "nunique"),
            grupos=("grupo_biologico", "nunique"),
        )
        .reset_index()
        .sort_values(["anio", "codigo_estudio_limpio"])
    )

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
            "grupo_biologico",
            "familia",
            "orden",
            "nombre_cientifico",
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
        )
        .reset_index()
        .sort_values(["estudios", "registros"], ascending=False)
    )

    col_g, col_h = st.columns([1, 1])
    with col_g:
        top_species = species_table.head(20).sort_values("estudios", ascending=True)
        if not top_species.empty:
            fig = px.bar(
                top_species,
                y="nombre_cientifico",
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
)
