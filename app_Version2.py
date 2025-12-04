import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Ruta Control TD SYNNEX", layout="wide")

# --- BASE DE DATOS SIMULADA (SESSION STATE) ---
# Nota: En una app real compartida en la nube, esto se reemplazaría 
# por una conexión a Google Sheets o una base de datos SQL.
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=[
        'ID', 'PEDIDO', 'CLIENTE', 'DIRECCION', 'CHOFER', 'PLACA', 
        'ESTADO', 'HORA_LLEGADA', 'HORA_FIN', 'DURACION'
    ])

if 'historial' not in st.session_state:
    st.session_state.historial = pd.DataFrame(columns=[
        'PEDIDO', 'CLIENTE', 'DIRECCION', 'CHOFER', 'PLACA', 
        'HORA_LLEGADA', 'HORA_FIN', 'DURACION'
    ])

# --- LÓGICA DE PLACAS ---
def obtener_placa(chofer):
    if chofer == "DAVES":
        return "BKN-763"
    elif chofer == "PIERO":
        return "CRA-391"
    return "POR ASIGNAR"

# --- LOGIN ---
def login():
    st.markdown("<h1 style='text-align: center;'>RUTA CONTRO</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>TD SYNNEX</h3>", unsafe_allow_html=True)
    st.divider()
    
    password = st.text_input("Ingrese su código de acceso (Login):", type="password")
    
    if password == "SYNNEX":
        st.session_state['role'] = "ADMIN"
        st.session_state['user'] = "ADMIN"
        st.rerun()
    elif password == "GRUPOSERGIO":
        st.session_state['role'] = "CHOFER"
        st.session_state['user'] = "DAVES"
        st.rerun()
    elif password == "ROVAI":
        st.session_state['role'] = "CHOFER"
        st.session_state['user'] = "PIERO"
        st.rerun()
    elif password:
        st.error("Código incorrecto")

# --- INTERFAZ PRINCIPAL ---
def main_app():
    # Título Requerido (Punto 10)
    st.title("RUTA CONTRO")
    st.subheader("TD SYNNEX")
    
    # Botón de salir
    col_user, col_logout = st.columns([8, 2])
    with col_user:
        st.info(f"Usuario conectado: {st.session_state['user']} ({st.session_state['role']})")
    with col_logout:
        if st.button("Cerrar Sesión"):
            del st.session_state['role']
            st.rerun()

    # Pestañas (Punto 5)
    tab1, tab2 = st.tabs(["📋 Lista de Pedidos", "clock Historial de Entregas"])

    # --- PESTAÑA 1: LISTA DE PEDIDOS ---
    with tab1:
        # SECCION ADMIN: CARGAR EXCEL (Punto 2 y 4)
        if st.session_state['role'] == "ADMIN":
            st.markdown("### 📤 Cargar Pedidos (Excel)")
            uploaded_file = st.file_uploader("Sube tu Excel (Columnas: PEDIDO, CLIENTE, DIRECCION, CHOFER)", type=['xlsx'])
            
            if uploaded_file:
                if st.button("Procesar Excel"):
                    try:
                        df_new = pd.read_excel(uploaded_file)
                        # Validar columnas
                        required_cols = ['PEDIDO', 'CLIENTE', 'DIRECCION', 'CHOFER']
                        if all(col in df_new.columns for col in required_cols):
                            # Asignar placas automáticamente (Punto 3)
                            df_new['PLACA'] = df_new['CHOFER'].apply(obtener_placa)
                            df_new['ESTADO'] = 'PENDIENTE'
                            df_new['HORA_LLEGADA'] = None
                            df_new['HORA_FIN'] = None
                            df_new['DURACION'] = None
                            # Generar ID único
                            df_new['ID'] = [f"{x}_{datetime.now().microsecond}" for x in df_new['PEDIDO']]
                            
                            st.session_state.pedidos = pd.concat([st.session_state.pedidos, df_new], ignore_index=True)
                            st.success("Pedidos cargados correctamente")
                        else:
                            st.error(f"El Excel debe tener las columnas: {required_cols}")
                    except Exception as e:
                        st.error(f"Error al leer el archivo: {e}")

        st.divider()

        # VISUALIZACIÓN Y GESTIÓN (Puntos 1, 6, 9)
        st.markdown("### 🚚 Gestión de Ruta")

        # Filtrado según Usuario (Punto 6)
        df_view = st.session_state.pedidos.copy()
        
        if st.session_state['user'] == "DAVES":
            df_view = df_view[df_view['CHOFER'] == "DAVES"]
        elif st.session_state['user'] == "PIERO":
            df_view = df_view[df_view['CHOFER'] == "PIERO"]
        
        # Mostrar cada pedido como una tarjeta
        if df_view.empty:
            st.info("No hay pedidos asignados pendientes.")
        
        for index, row in df_view.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
                
                with c1:
                    st.markdown(f"**Pedido:** {row['PEDIDO']}")
                    st.markdown(f"**Cliente:** {row['CLIENTE']}")
                    st.markdown(f"**Dirección:** {row['DIRECCION']}")
                
                with c2:
                    # Lógica de Admin para cambiar chofer (Punto 9)
                    if st.session_state['role'] == "ADMIN":
                        # Asegurar que exista valor por defecto en caso de datos nulos
                        current_driver = row['CHOFER'] if pd.notna(row['CHOFER']) else "DAVES"
                        nuevo_chofer = st.selectbox(
                            f"Chofer ({row['PEDIDO']})", 
                            ["DAVES", "PIERO"], 
                            index=["DAVES", "PIERO"].index(current_driver),
                            key=f"ch_{row['ID']}"
                        )
                        # Si cambia el chofer, actualizar placa automáticamente
                        if nuevo_chofer != row['CHOFER']:
                            st.session_state.pedidos.at[index, 'CHOFER'] = nuevo_chofer
                            st.session_state.pedidos.at[index, 'PLACA'] = obtener_placa(nuevo_chofer)
                            st.rerun()
                    else:
                        st.markdown(f"**Chofer:** {row['CHOFER']}")
                    
                    st.markdown(f"**Placa:** {row['PLACA']}")

                with c3:
                    # Control de Tiempos (Llegada y Fin) - Intro
                    status = row['ESTADO']
                    st.markdown(f"**Estado:** {status}")

                    if status == "PENDIENTE":
                        if st.button("📍 LLEGUÉ AL PUNTO", key=f"llegada_{row['ID']}"):
                            st.session_state.pedidos.at[index, 'HORA_LLEGADA'] = datetime.now()
                            st.session_state.pedidos.at[index, 'ESTADO'] = "EN ENTREGA"
                            st.rerun()
                    
                    elif status == "EN ENTREGA":
                        # Mostrar hora de llegada de forma segura
                        hora_llegada = row['HORA_LLEGADA']
                        try:
                            if pd.notna(hora_llegada):
                                if isinstance(hora_llegada, str):
                                    st.write(f"Llegada: {hora_llegada}")
                                else:
                                    st.write(f"Llegada: {hora_llegada.strftime('%H:%M:%S')}")
                        except Exception:
                            st.write(f"Llegada: {hora_llegada}")
                        if st.button("✅ ENTREGA TERMINADA", key=f"fin_{row['ID']}"):
                            fin = datetime.now()
                            inicio = row['HORA_LLEGADA']
                            # Asegurarse de que inicio sea datetime
                            if isinstance(inicio, str):
                                try:
                                    inicio_dt = datetime.strptime(inicio, '%Y-%m-%d %H:%M:%S')
                                except Exception:
                                    inicio_dt = fin
                            else:
                                inicio_dt = inicio
                            duracion = fin - inicio_dt
                            
                            # Mover a historial
                            nuevo_registro = {
                                'PEDIDO': row['PEDIDO'],
                                'CLIENTE': row['CLIENTE'],
                                'DIRECCION': row['DIRECCION'],
                                'CHOFER': row['CHOFER'],
                                'PLACA': row['PLACA'],
                                'HORA_LLEGADA': inicio_dt.strftime('%Y-%m-%d %H:%M:%S'),
                                'HORA_FIN': fin.strftime('%Y-%m-%d %H:%M:%S'),
                                'DURACION': str(duracion).split('.')[0] # Formato HH:MM:SS
                            }
                            st.session_state.historial = pd.concat([st.session_state.historial, pd.DataFrame([nuevo_registro])], ignore_index=True)
                            
                            # Borrar de lista activa
                            st.session_state.pedidos.drop(index, inplace=True)
                            st.rerun()

                with c4:
                    # Opción de Borrar (Punto 4)
                    if st.button("🗑️ Borrar", key=f"del_{row['ID']}"):
                        st.session_state.pedidos.drop(index, inplace=True)
                        st.rerun()

    # --- PESTAÑA 2: HISTORIAL (Punto 5 y 7) ---
    with tab2:
        st.markdown("### 📊 Historial de Entregas Completadas")
        
        # Filtro de seguridad: Choferes solo ven su propio historial si lo deseas, 
        # o todo el historial si no se especifica. Aquí aplicaré la misma lógica de filtro.
        df_hist_view = st.session_state.historial.copy()
        if st.session_state['user'] == "DAVES":
            df_hist_view = df_hist_view[df_hist_view['CHOFER'] == "DAVES"]
        elif st.session_state['user'] == "PIERO":
            df_hist_view = df_hist_view[df_hist_view['CHOFER'] == "PIERO"]

        st.dataframe(df_hist_view, use_container_width=True)

        # Botón Exportar a Excel (Punto 5)
        if not df_hist_view.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_hist_view.to_excel(writer, index=False, sheet_name='Historial')
            
            st.download_button(
                label="📥 Descargar Historial en Excel",
                data=buffer,
                file_name=f"historial_entregas_{datetime.now().date()}.xlsx",
                mime="application/vnd.ms-excel"
            )

# --- EJECUCIÓN ---
if 'role' not in st.session_state:
    login()
else:
    main_app()