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

```text
03_Consolidado_Streamlit
```

Si esa hoja no existe, la app usará la primera hoja disponible.

## Campos principales esperados

La estructura base es la del consolidado Streamlit generado por el pipeline:

- `anio`
- `id_registro_anual`
- `id_estudio_anual`
- `codigo_estudio_limpio`
- `titulo_estudio`
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

La aplicación tolera columnas faltantes para mantener disponible la consulta principal.

## Base geográfica

La vista de mapa usa la capa departamental:

```text
data/GEO/DEP_PERU.geojson
```

Las coordenadas UTM de los registros se transforman a latitud y longitud para superponer los puntos sobre los departamentos del Perú.

## Agregar nuevos años

Para agregar otro año, coloca otro Excel con la misma hoja y estructura dentro de `data/`:

```text
data/
  especies_informes_mineros_2024_streamlit.xlsx
  especies_informes_mineros_2025_streamlit.xlsx
  especies_informes_mineros_2026_streamlit.xlsx
```

Evita dejar archivos temporales de Excel, por ejemplo:

```text
~$especies_informes_mineros_2025_streamlit.xlsx
```

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
3. En Streamlit Community Cloud, entra a **Advanced settings** y selecciona:

```text
Python version: 3.11
```

No uses Python 3.14 para esta app. Con Python 3.14 algunas dependencias de Streamlit/Pillow pueden intentar compilarse desde cero y fallar por librerías del sistema.

4. Sube los cambios:

```powershell
git add .
git commit -m "Actualizar app biodiversidad"
git push origin main
```

5. En Streamlit Community Cloud, la app se actualizará al detectar el nuevo `push`. Si modificaste dependencias o Python, usa **Manage app -> Reboot**.

## Vistas disponibles

- Dashboard
- Estudios
- Especies
- Mapa
- Descarga

## Notas de despliegue

- El repositorio no debe incluir `.git/`, `__pycache__/`, `.venv/` ni archivos `~$*.xlsx`.
- `runtime.txt` queda como referencia con `python-3.11`, pero la versión efectiva debe configurarse en Streamlit Cloud desde **Advanced settings**.
- El archivo de entrada actual pesa poco y puede mantenerse dentro del repositorio.
- Si en el futuro los Excel crecen mucho o contienen información sensible, conviene migrar la data a una base externa o usar secretos/configuración privada.
