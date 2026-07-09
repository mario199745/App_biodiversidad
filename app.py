from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Fuentes y autorizaciones - SERFOR",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "dashboard_fuentes" / "base_fuentes_autorizaciones.xlsx"

COLOR_SEQUENCE = [
    "#176B55",
    "#D89B32",
    "#8E5A3C",
    "#4C8FA3",
    "#843E52",
    "#7B8E57",
]
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = COLOR_SEQUENCE

st.markdown(
    """
    <style>
      :root { --forest:#176B55; --sand:#F3EFE6; --ink:#17352D; }
      .stApp { background:linear-gradient(180deg,#F8FAF7 0,#FFFFFF 22rem); color:#17352D; }
      [data-testid="stSidebar"] { background:#123E34; }
      [data-testid="stSidebar"] * { color:#F7F2E8; }
      [data-testid="stMetric"] {
        background:white; border:1px solid #DDE7E1; border-radius:14px;
        padding:1rem 1.1rem; box-shadow:0 4px 18px rgba(23,53,45,.06);
      }
      .hero { padding:1.5rem 1.7rem; border-radius:20px; color:white;
        background:linear-gradient(120deg,#123E34,#24765F); margin-bottom:1.2rem; }
      .hero h1 { margin:0; font-size:2rem; letter-spacing:0; }
      .hero p { margin:.45rem 0 0; color:#E4F0EA; }
      .eyebrow { color:#DDB46A; font-size:.78rem; letter-spacing:.12em;
        text-transform:uppercase; font-weight:700; }
      .note { border-left:4px solid #D89B32; background:#FFF9ED;
        padding:.75rem 1rem; border-radius:0 10px 10px 0; }
      div[data-testid="stPlotlyChart"] { background:white; border-radius:14px; }
      div[data-testid="stDataFrame"] { border:1px solid #DDE7E1; border-radius:14px; }
      #MainMenu, footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def file_signature(path: Path) -> tuple[str, int, int]:
    if not path.exists():
        return ("", 0, 0)
    stat = path.stat()
    return (path.name, stat.st_size, stat.st_mtime_ns)


@st.cache_data(show_spinner=False)
def load_dashboard_base(path: str, signature: tuple[str, int, int]) -> dict[str, pd.DataFrame]:
    excel_path = Path(path)
    if not excel_path.exists():
        return {
            "fuentes": pd.DataFrame(),
            "departamentos": pd.DataFrame(),
            "provincias": pd.DataFrame(),
            "indice": pd.DataFrame(),
            "calidad": pd.DataFrame(),
            "diccionario": pd.DataFrame(),
        }

    sheets = {
        "fuentes": "fuentes",
        "departamentos": "departamentos_fuente",
        "provincias": "provincias_fuente",
        "indice": "indice_origen",
        "calidad": "control_calidad",
        "diccionario": "diccionario",
    }
    data: dict[str, pd.DataFrame] = {}
    for key, sheet_name in sheets.items():
        try:
            data[key] = pd.read_excel(excel_path, sheet_name=sheet_name, engine="openpyxl")
        except Exception:
            data[key] = pd.DataFrame()

    fuentes = data["fuentes"].copy()
    if not fuentes.empty:
        fuentes["anio"] = pd.to_numeric(fuentes.get("anio"), errors="coerce").astype("Int64")
        text_cols = fuentes.columns.difference(["anio", "fila_origen", "orden_archivo", "orden_hoja_origen"])
        for col in text_cols:
            fuentes[col] = fuentes[col].astype("string").fillna("").str.replace(r"\s+", " ", regex=True).str.strip()
    data["fuentes"] = fuentes
    return data


def option_values(df: pd.DataFrame, column: str) -> list[str]:
    if df.empty or column not in df.columns:
        return []
    values = df[column].dropna().astype(str).str.strip()
    values = values[values.ne("")]
    return sorted(values.unique().tolist())


def split_semicolon_values(series: pd.Series) -> pd.Series:
    if series.empty:
        return pd.Series(dtype="string")
    values = series.fillna("").astype(str).str.split(";").explode().str.strip()
    return values[values.ne("")]


def text_filter(df: pd.DataFrame, query: str, columns: list[str]) -> pd.DataFrame:
    if df.empty or not query.strip():
        return df
    available = [col for col in columns if col in df.columns]
    if not available:
        return df
    needle = query.strip().casefold()
    text = df[available].fillna("").astype(str).agg(" ".join, axis=1).str.casefold()
    return df[text.str.contains(needle, na=False, regex=False)]


def safe_unique_count(df: pd.DataFrame, column: str) -> int:
    if df.empty or column not in df.columns:
        return 0
    values = df[column].dropna().astype(str).str.strip()
    values = values[values.ne("")]
    return int(values.nunique())


def exploded_count(df: pd.DataFrame, column: str) -> int:
    if df.empty or column not in df.columns:
        return 0
    return int(split_semicolon_values(df[column]).nunique())


def contains_selected_values(series: pd.Series, selected: list[str]) -> pd.Series:
    if not selected:
        return pd.Series(True, index=series.index)
    selected_set = set(selected)
    return series.fillna("").astype(str).apply(
        lambda value: bool(selected_set.intersection(part.strip() for part in value.split(";") if part.strip()))
    )


def build_filters(fuentes: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.markdown("## 🌿 SERFOR")
        st.caption("Fuentes · Expedientes · Autorizaciones")
        st.divider()
        st.markdown("#### Filtros globales")

        years = sorted([int(value) for value in fuentes.get("anio", pd.Series(dtype="Int64")).dropna().unique()])
        selected_years = st.multiselect("Anio", years, placeholder="Todos los anios")

        auth_types = option_values(fuentes, "tipo_autorizacion")
        selected_auth_types = st.multiselect("Tipo de autorizacion", auth_types, placeholder="Todos")

        document_types = option_values(fuentes, "tipo_documento")
        selected_document_types = st.multiselect("Tipo de documento", document_types, placeholder="Todos")

        departments = sorted(split_semicolon_values(fuentes.get("departamento_normalizado", pd.Series(dtype=str))).unique().tolist())
        selected_departments = st.multiselect("Departamento", departments, placeholder="Todos")

        provinces = sorted(split_semicolon_values(fuentes.get("provincia_normalizada", pd.Series(dtype=str))).unique().tolist())
        selected_provinces = st.multiselect("Provincia", provinces, placeholder="Todas")

        remitentes = option_values(fuentes, "remitente")
        selected_remitentes = st.multiselect("Remitente", remitentes, placeholder="Todos")

        query = st.text_input("Buscar", placeholder="Expediente, titulo, remitente o resumen")

    filtered = fuentes.copy()
    if selected_years:
        filtered = filtered[filtered["anio"].isin(selected_years)]
    if selected_auth_types:
        filtered = filtered[filtered["tipo_autorizacion"].isin(selected_auth_types)]
    if selected_document_types:
        filtered = filtered[filtered["tipo_documento"].isin(selected_document_types)]
    if selected_departments:
        filtered = filtered[contains_selected_values(filtered["departamento_normalizado"], selected_departments)]
    if selected_provinces:
        filtered = filtered[contains_selected_values(filtered["provincia_normalizada"], selected_provinces)]
    if selected_remitentes:
        filtered = filtered[filtered["remitente"].isin(selected_remitentes)]

    return text_filter(
        filtered,
        query,
        ["nro_expediente", "titulo", "remitente", "departamento_original", "provincia_original", "resumen", "archivo_origen"],
    )


def dimension_table(fuentes: pd.DataFrame, source_column: str, value_column: str) -> pd.DataFrame:
    if fuentes.empty or source_column not in fuentes.columns:
        return pd.DataFrame(columns=[value_column, "fuentes"])

    rows: list[dict[str, object]] = []
    for row in fuentes[["id_fuente", source_column]].itertuples(index=False):
        for value in str(getattr(row, source_column) or "").split(";"):
            clean = value.strip()
            if clean:
                rows.append({"id_fuente": row.id_fuente, value_column: clean})

    if not rows:
        return pd.DataFrame(columns=[value_column, "fuentes"])
    tmp = pd.DataFrame(rows).drop_duplicates()
    return tmp.groupby(value_column, dropna=False)["id_fuente"].nunique().reset_index(name="fuentes")


def to_excel_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for sheet_name, df in sheets.items():
            safe_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=safe_name, index=False)
            workbook = writer.book
            worksheet = writer.sheets[safe_name]
            header_fmt = workbook.add_format({"bold": True, "bg_color": "#0F766E", "font_color": "#FFFFFF"})
            for col_num, value in enumerate(df.columns):
                worksheet.write(0, col_num, value, header_fmt)
                width = min(max(len(str(value)) + 4, 12), 46)
                worksheet.set_column(col_num, col_num, width)
            worksheet.autofilter(0, 0, max(len(df), 1), max(len(df.columns) - 1, 0))
            worksheet.freeze_panes(1, 0)
    return output.getvalue()


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><div class="eyebrow">SERFOR · Consulta integrada</div>'
        f"<h1>{title}</h1><p>{subtitle}</p></div>",
        unsafe_allow_html=True,
    )


def style_figure(fig, height: int = 420):
    fig.update_layout(
        height=height,
        margin={"l": 20, "r": 20, "t": 55, "b": 20},
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"family": "Arial", "color": "#17352D"},
        legend_title_text="",
    )
    fig.update_xaxes(gridcolor="#E8EEE9")
    fig.update_yaxes(gridcolor="#E8EEE9")
    return fig


def render_bar(df: pd.DataFrame, x: str, y: str, title: str, orientation: str = "v") -> None:
    if df.empty:
        st.info("No hay datos para los filtros actuales.")
        return
    fig = px.bar(df, x=x, y=y, text=y, title=title, orientation=orientation)
    fig.update_layout(title_x=0.02, xaxis_title=None, yaxis_title=None)
    st.plotly_chart(style_figure(fig), width="stretch")


base = load_dashboard_base(str(DATA_PATH), file_signature(DATA_PATH))
fuentes = base["fuentes"]
indice = base["indice"]
calidad = base["calidad"]

hero(
    "Fuentes, expedientes y autorizaciones",
    "Dashboard construido desde la base consolidada de estudios, informes y autorizaciones. "
    "La informacion anterior de especies fue reemplazada por una organizacion propia para esta nueva base.",
)

if fuentes.empty:
    st.error(f"No se encontro una base legible en `{DATA_PATH}`.")
    st.stop()

filtered = build_filters(fuentes)

st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Fuentes", f"{len(filtered):,}")
k2.metric("Expedientes", f"{safe_unique_count(filtered, 'nro_expediente'):,}")
k3.metric("Remitentes", f"{safe_unique_count(filtered, 'remitente'):,}")
k4.metric("Anios", f"{safe_unique_count(filtered, 'anio'):,}")

k5, k6, k7, k8 = st.columns(4)
k5.metric("Departamentos", f"{exploded_count(filtered, 'departamento_normalizado'):,}")
k6.metric("Provincias", f"{exploded_count(filtered, 'provincia_normalizada'):,}")
k7.metric("Tipos de documento", f"{safe_unique_count(filtered, 'tipo_documento'):,}")
k8.metric("Archivos origen", f"{safe_unique_count(filtered, 'archivo_origen'):,}")

if filtered.empty:
    st.warning("No hay registros para los filtros seleccionados.")
    st.stop()

tabs = st.tabs(["Resumen", "Fuentes", "Territorio", "Trazabilidad", "Descarga"])

with tabs[0]:
    a, b = st.columns(2)
    with a:
        by_year = filtered.groupby("anio", dropna=False).size().reset_index(name="fuentes")
        by_year["anio"] = by_year["anio"].astype("Int64").astype(str)
        render_bar(by_year, "anio", "fuentes", "Fuentes por anio")
    with b:
        by_auth = filtered.groupby("tipo_autorizacion", dropna=False).size().reset_index(name="fuentes")
        fig = px.pie(by_auth, names="tipo_autorizacion", values="fuentes", title="Tipo de autorizacion")
        fig.update_layout(title_x=0.02)
        st.plotly_chart(style_figure(fig), width="stretch")

    a, b = st.columns(2)
    with a:
        by_doc = (
            filtered.groupby("tipo_documento", dropna=False)
            .size()
            .reset_index(name="fuentes")
            .sort_values("fuentes", ascending=False)
        )
        render_bar(by_doc, "tipo_documento", "fuentes", "Tipo de documento")
    with b:
        by_source_file = (
            filtered.groupby("archivo_origen", dropna=False)
            .size()
            .reset_index(name="fuentes")
            .sort_values("fuentes")
        )
        render_bar(by_source_file, "fuentes", "archivo_origen", "Archivos origen", orientation="h")

    by_author = (
        filtered.assign(remitente_display=filtered["remitente"].replace("", "Sin dato"))
        .groupby("remitente_display", dropna=False)
        .size()
        .reset_index(name="fuentes")
        .sort_values("fuentes")
        .tail(25)
    )
    render_bar(by_author, "fuentes", "remitente_display", "Autor / institucion", orientation="h")

with tabs[1]:
    st.subheader("Explorador de fuentes")
    display_cols = [
        "id_fuente",
        "anio",
        "numeracion",
        "nro_expediente",
        "titulo",
        "tipo_documento",
        "tipo_autorizacion",
        "remitente",
        "departamento_normalizado",
        "provincia_normalizada",
        "resumen",
        "archivo_origen",
        "fila_origen",
    ]
    st.dataframe(filtered[[col for col in display_cols if col in filtered.columns]], width="stretch", hide_index=True)

with tabs[2]:
    a, b = st.columns(2)
    with a:
        by_department = dimension_table(filtered, "departamento_normalizado", "departamento").sort_values("fuentes")
        render_bar(by_department.tail(25), "fuentes", "departamento", "Departamentos", orientation="h")
    with b:
        by_province = dimension_table(filtered, "provincia_normalizada", "provincia").sort_values("fuentes")
        render_bar(by_province.tail(25), "fuentes", "provincia", "Provincias principales", orientation="h")

    territory_cols = ["id_fuente", "anio", "departamento_normalizado", "provincia_normalizada", "titulo", "nro_expediente"]
    st.dataframe(filtered[[col for col in territory_cols if col in filtered.columns]], width="stretch", hide_index=True)

with tabs[3]:
    st.subheader("Indice de origen")
    if indice.empty:
        st.info("La base final no contiene hoja de indice de origen.")
    else:
        st.dataframe(indice, width="stretch", hide_index=True)

    st.subheader("Control de calidad")
    if calidad.empty:
        st.info("La base final no contiene control de calidad.")
    else:
        st.dataframe(calidad, width="stretch", hide_index=True)

with tabs[4]:
    st.subheader("Descarga")
    filtered_departments = dimension_table(filtered, "departamento_normalizado", "departamento")
    filtered_provinces = dimension_table(filtered, "provincia_normalizada", "provincia")
    workbook = to_excel_bytes(
        {
            "fuentes_filtradas": filtered,
            "departamentos": filtered_departments,
            "provincias": filtered_provinces,
        }
    )
    st.download_button(
        "Descargar Excel filtrado",
        data=workbook,
        file_name="fuentes_autorizaciones_filtradas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )
    st.download_button(
        "Descargar CSV filtrado",
        data=filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="fuentes_autorizaciones_filtradas.csv",
        mime="text/csv",
        width="stretch",
    )
