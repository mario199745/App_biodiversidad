<<<<<<< HEAD
# Explorador de fauna por informes mineros

Aplicación Streamlit para consultar registros consolidados de fauna extraídos de informes mineros. Está preparada para actualización web en Streamlit Community Cloud mediante GitHub.

## Estructura del proyecto

```text
App_biodiversidad_web_ready/
├─ app.py
├─ requirements.txt
├─ runtime.txt
├─ .streamlit/
│  └─ config.toml
└─ data/
   └─ especies_informes_mineros_2025_streamlit.xlsx
```

## Fuente de datos

La app lee automáticamente todos los archivos `.xlsx` ubicados en `data/`. Cada archivo anual debe contener la hoja:
=======
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
>>>>>>> origin/main

```text
03_Consolidado_Streamlit
```

<<<<<<< HEAD
Si esa hoja no existe, la app usará la primera hoja disponible y dejará una observación en el panel de carga.

## Campos principales esperados

La estructura base es la del consolidado Streamlit generado por el pipeline:
=======
Columnas mínimas esperadas:
>>>>>>> origin/main

- `anio`
- `id_registro_anual`
- `id_estudio_anual`
- `codigo_estudio_limpio`
- `titulo_estudio`
<<<<<<< HEAD
- `departamento_estudio`
- `provincia_estudio`
- `grupo_biologico`
- `nombre_cientifico`
- `nombre_comun`
- `clase`
- `orden`
- `familia`
- `estacion_fuente_original`
- `este_fuente_original`
- `norte_fuente_original`
- `zona_utm_fuente_original`
- `fuente_base_especies`
- `tipo_asignacion`
- `estado_revision`

La aplicación tolera columnas faltantes, pero las marcará en el panel **Calidad**.

## Agregar nuevos años

Para agregar otro año, coloca otro Excel con la misma hoja y estructura dentro de `data/`:

```text
data/
  especies_informes_mineros_2024_streamlit.xlsx
  especies_informes_mineros_2025_streamlit.xlsx
  especies_informes_mineros_2026_streamlit.xlsx
```

Evita dejar archivos temporales de Excel, por ejemplo:
=======
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
>>>>>>> origin/main

```text
~$especies_informes_mineros_2025_streamlit.xlsx
```

<<<<<<< HEAD
## Ejecutar localmente

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Con Conda:

```powershell
conda create -n especies_pdf python=3.11 -y
conda activate especies_pdf
pip install -r requirements.txt
streamlit run app.py
```

## Actualizar la app web

1. Copia o reemplaza los archivos del proyecto en tu repositorio de GitHub.
2. Verifica que `app.py`, `requirements.txt`, `runtime.txt`, `.streamlit/config.toml` y la carpeta `data/` estén en la raíz del repositorio.
3. Sube los cambios:

```powershell
git add .
git commit -m "Actualizar app biodiversidad"
git push origin main
```

4. En Streamlit Community Cloud, la app se actualizará al detectar el nuevo `push`. Si modificaste dependencias, puede hacer un redeploy completo.

## Vistas disponibles

- Dashboard
- Estudios
- Especies
- Coordenadas
- Calidad
- Descarga

## Notas de despliegue

- El repositorio no debe incluir `.git/`, `__pycache__/`, `.venv/` ni archivos `~$*.xlsx`.
- El archivo de entrada actual pesa poco y puede mantenerse dentro del repositorio.
- Si en el futuro los Excel crecen mucho o contienen información sensible, conviene migrar la data a una base externa o usar secretos/configuración privada.
=======
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
>>>>>>> origin/main
