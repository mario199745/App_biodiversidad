# Explorador de especies por informes mineros

Aplicativo Streamlit para consultar, comparar y validar registros de especies extraídos de estudios e informes vinculados al sector minero.

## 1. Estructura del proyecto

```text
app_especies_streamlit/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
└── data/
    └── especies_informes_mineros_2025_streamlit.xlsx
```

## 2. Fuente de datos

La aplicación usa la opción A de actualización simple: lee automáticamente todos los archivos Excel `.xlsx` ubicados en la carpeta `data/`.

Cada Excel anual debe mantener la hoja principal:

```text
03_Consolidado_Streamlit
```

Columnas mínimas esperadas:

- `anio`
- `id_registro_anual`
- `id_estudio_anual`
- `codigo_estudio_limpio`
- `titulo_estudio`
- `sector_asociado`
- `grupo_biologico`
- `familia`
- `nombre_cientifico`
- `estado_revision`

## 3. Cómo actualizar la información

Para agregar otro año, coloca un nuevo Excel anual dentro de `data/`, por ejemplo:

```text
data/
├── especies_informes_mineros_2024_streamlit.xlsx
├── especies_informes_mineros_2025_streamlit.xlsx
└── especies_informes_mineros_2026_streamlit.xlsx
```

La app leerá todos los archivos automáticamente, siempre que tengan la misma hoja y estructura.

Evita subir archivos temporales de Excel como:

```text
~$especies_informes_mineros_2025_streamlit.xlsx
```

## 4. Ejecución local

Instala las dependencias:

```bash
pip install -r requirements.txt
```

Ejecuta la aplicación:

```bash
streamlit run app.py
```

## 5. Despliegue en Streamlit Community Cloud usando GitHub

1. Crea un repositorio en GitHub.
2. Sube todos los archivos de esta carpeta.
3. Ingresa a Streamlit Community Cloud.
4. Crea una nueva app desde tu repositorio.
5. Selecciona `app.py` como archivo principal.
6. Despliega la aplicación.

## 6. Módulos del aplicativo

- Dashboard general.
- Explorador de estudios.
- Explorador de especies.
- Control de calidad.
- Descarga de resultados filtrados.

## 7. Recomendación operativa

Usa el Excel como fuente maestra anual. No cambies nombres de columnas ni nombres de hojas. Para actualizar información, edita el Excel, guárdalo y súbelo nuevamente a la carpeta `data/` del repositorio.
