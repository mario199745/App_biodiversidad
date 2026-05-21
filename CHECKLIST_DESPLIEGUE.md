# Checklist rapido para actualizar en la web

## Antes de subir

- [ ] Ejecutar localmente: `streamlit run app.py`
- [ ] Confirmar que el Excel esta en `data/`
- [ ] Confirmar que la hoja principal se llama `03_Consolidado_Streamlit`
- [ ] Confirmar en Streamlit Community Cloud que **Python version** sea `3.11` en **Advanced settings**
- [ ] Revisar la pestana **Calidad** dentro de la app
- [ ] No subir `.venv/`, `__pycache__/`, `.git/`, `.env` ni archivos temporales `~$*.xlsx`

## Comandos Git

```bash
git status
git add app.py requirements.txt runtime.txt README.md CHECKLIST_DESPLIEGUE.md .streamlit/config.toml data/
git commit -m "Actualizar app biodiversidad"
git push origin main
```

## En Streamlit Community Cloud

- Repositorio: el de tu app
- Rama: `main`
- Archivo principal: `app.py`
- Carpeta de datos: `data/`
- Python version: `3.11`

Si la app no actualiza, usa **Manage app -> Reboot** y revisa los logs.
