# Información de Patrimonio forestal - SERFOR

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

### Base institucional trazable

La version actual prioriza una base institucional preparada para crecer:

```text
data/patrimonio_biodiversidad_base.xlsx
```

Esta base se genera desde los Excel disponibles en `ESTUDIOS/ESTUDIOS_2024` y
`ESTUDIOS/ESTUDIOS_2025`, sin extraer todavia nueva informacion documental
desde PDF o Word.

Hojas principales:

- `01_fuentes`: estudios/fuentes con anio, expediente, titulo, tipo de documento,
  instrumento fuente, remitente, departamento y provincia.
- `02_inventario_excel`: archivos Excel/CSV detectados por estudio.
- `03_hojas_excel`: hojas detectadas, encabezado probable y marca de hoja candidata.
- `04_registros_especies`: filas de especies extraidas heuristicamente desde Excel
  y hojas candidatas pendientes de extraccion.
- `05_control_calidad`: controles basicos.
- `06_diccionario`: definicion inicial de campos.

Las hojas `02_inventario_excel`, `03_hojas_excel`, `05_control_calidad` y
`06_diccionario` son internas. El dashboard no las muestra al usuario final.

Para regenerarla:

```powershell
& 'C:\Users\USUARIO\miniconda3\Scripts\conda.exe' run -n especies_pdf python tools\build_patrimonio_excel_base.py
```

Si `data/patrimonio_biodiversidad_base.xlsx` existe, la app usa esta estructura.
Si no existe, conserva la lectura heredada de archivos anuales Streamlit.

La trazabilidad se conserva mediante:

- `archivo_maestro` y `fila_maestro` para fuentes.
- `ruta_archivo`, `archivo_excel` y `hoja_excel` para inventario.
- `archivo_origen`, `hoja_origen` y `fila_origen` para registros.
- `estado_revision` y `observaciones` para diferenciar registros extraidos,
  hojas candidatas y pendientes de validacion.

Para los departamentos se conserva el texto original del Excel en `departamento`
y se agrega `departamento_normalizado` para filtros, mapas y conteos. Esto evita
contar como departamentos distintos a combinaciones, errores de escritura o
valores no departamentales.

### Base anual heredada

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

Las coordenadas UTM de los registros se transforman a latitud y longitud para superponer los puntos sobre los departamentos del Perú. La visualización del mapa muestra solo los puntos que caen dentro del territorio peruano.

## Agregar nuevos años

Para agregar otro año, coloca otro Excel `.xlsx` o `.xlsm` con la misma hoja y estructura dentro de `data/`:

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

La aplicación detecta cambios por nombre, tamaño y fecha de modificación del archivo. Si se agrega, reemplaza o actualiza un Excel anual, la lectura se vuelve a calcular automáticamente.

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
