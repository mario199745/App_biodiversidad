# Checklist rápido para actualizar en la web

## Antes de subir

- [ ] Ejecutar localmente: `streamlit run app.py`
- [ ] Confirmar que el Excel está en `data/`
- [ ] Confirmar que la hoja principal se llama `03_Consolidado_Streamlit`
- [ ] Revisar la pestaña **Calidad** dentro de la app
- [ ] No subir `.venv/`, `__pycache__/`, `.git/`, `.env` ni archivos temporales `~$*.xlsx`

## Comandos Git

```powershell
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

Si la app no actualiza, usa **Manage app → Reboot** y revisa los logs.
