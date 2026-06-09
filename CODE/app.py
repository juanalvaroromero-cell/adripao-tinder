import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import requests
import base64

# CONFIGURACIÓN: Pega aquí tu API Key de ImgBB
IMGBB_API_KEY = "36c7e334027277c292849e54122f068e"

st.set_page_config(page_title="ADRIPAO TINDER", page_icon="🔥", layout="centered")

st.title("🔥 ADRIPAO TINDER")
st.markdown("¡Bienvenido! Completa tu perfil para que nuestra IA encuentre a tu pareja ideal para el evento.")

with st.form(key="user_profile_form"):
    st.subheader("1. Datos Personales")
    user_name = st.text_input("Nombre completo o Apodo")
    user_gender = st.selectbox("Sexo", ["Hombre", "Mujer"])
    
    col1, col2 = st.columns(2)
    with col1:
        user_age = st.number_input("Edad", min_value=18, max_value=99, step=1)
    with col2:
        user_height = st.number_input("Altura (cm)", min_value=120, max_value=230, step=1)
        
    user_body_type = st.selectbox("Complexión", ["Delgada", "Atlética", "Normal", "Fuerte", "Curvy"])
    
    st.divider()
    st.subheader("2. Tus Intereses (¡Para la IA!)")
    user_hobbies = st.text_area("¿Cuáles son tus Hobbies?")
    user_movies = st.text_area("Menciona tus películas favoritas o géneros de cine")
    user_series = st.text_area("¿Cuáles son tus series favoritas?")
    
    st.divider()
    st.subheader("3. ¡Hora del Selfie!")
    user_photo = st.camera_input("Tómate una foto ahora mismo")
    
    submit_button = st.form_submit_button(label="Enviar mis datos y buscar pareja")

if submit_button:
    if not user_name or not user_photo or not user_hobbies:
        st.error("Por favor, asegúrate de poner tu nombre, escribir tus hobbies y tomarte la foto.")
    else:
        with st.spinner("Subiendo tu foto y guardando perfil..."):
            try:
                # 1. Convertir la foto de Streamlit a Base64 para enviarla por API
                image_bytes = user_photo.getvalue()
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                
                # 2. Subir la imagen a ImgBB
                upload_url = "https://api.imgbb.com/1/upload"
                payload = {
                    "key": IMGBB_API_KEY,
                    "image": image_b64
                }
                response = requests.post(upload_url, data=payload)
                result = response.json()
                
                if response.status_code == 200:
                    # Extraer la URL pública y directa de la imagen
                    photo_url = result['data']['url']
                    
                    # 3. Conectar a Google Sheets y preparar la fila
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    new_row = pd.DataFrame([{
                        "name": user_name,
                        "gender": user_gender,
                        "age": user_age,
                        "height": user_height,
                        "body_type": user_body_type,
                        "hobbies": user_hobbies,
                        "movies": user_movies,
                        "series": user_series,
                        "photo_url": photo_url  # URL directa a la foto
                    }])
                    
                    # 4. Actualizar la hoja de cálculo
                    try:
                        existing_data = conn.read(worksheet="Datos", ttl=0)
                        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
                    except Exception:
                        updated_data = new_row
                        
                    conn.update(worksheet="Datos", data=updated_data)
                    
                    st.balloons()
                    st.success("¡Tu perfil y tu foto han sido guardados con éxito!")
                else:
                    st.error(f"Error al subir la imagen: {result.get('error', {}).get('message', 'Desconocido')}")
                    
            except Exception as error_message:
                st.error(f"Hubo un error interno: {error_message}")