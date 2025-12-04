# Ruta Contro - TD SYNNEX (Streamlit)

Esta aplicación permite:
- Cargar pedidos desde un Excel (ADMIN).
- Asignar placas automáticas según chofer.
- Ver la lista de pedidos por chofer.
- Registrar llegada y fin de entrega (calcula duración).
- Mover entregas completadas a historial y exportarlo a Excel.
- Login simple con códigos (SYNNEX, GRUPOSERGIO, ROVAI).

## Archivos
- app.py: Código principal de Streamlit.
- requirements.txt: Dependencias para instalar.
  
## Ejecutar localmente

1. Crea un entorno virtual (opcional pero recomendado):
   - python -m venv .venv
   - Linux/macOS: source .venv/bin/activate
   - Windows: .venv\Scripts\activate

2. Instala dependencias:
   - pip install -r requirements.txt

3. Ejecuta la app:
   - streamlit run app.py

4. Códigos de acceso:
   - ADMIN: SYNNEX
   - CHOFER DAVES: GRUPOSERGIO
   - CHOFER PIERO: ROVAI

## Formato del Excel de carga
El archivo Excel que subas debe tener exactamente estas columnas: PEDIDO, CLIENTE, DIRECCION, CHOFER

## Notas
- La app utiliza `st.session_state` como almacenamiento temporal. Si cierras el navegador o la sesión, los datos se perderán. Para producción se recomienda usar una base de datos real o Google Sheets.
- Si quieres que cree la versión con almacenamiento persistente (por ejemplo Google Sheets) o que despliegue la app en Streamlit Cloud, dímelo y te preparo los pasos siguientes.