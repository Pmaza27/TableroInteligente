import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# ==========================
# CONFIGURACIÓN INICIAL
# ==========================
Expert=" "
profile_imgenh=" "

if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# ==========================
# INTERFAZ STREAMLIT
# ==========================
st.set_page_config(page_title='Tablero Inteligente')
st.title('🧠 Tablero Inteligente')

with st.sidebar:
    st.subheader("📌 Acerca de:")
    st.write("Esta aplicación interpreta tus bocetos, resuelve fórmulas matemáticas, "
             "y hasta mejora tus dibujos con IA.")
    st.write("Selecciona qué quieres hacer con el menú desplegable.")

# Elegir funcionalidad
option = st.selectbox(
    "Elige una funcionalidad:",
    ["Análisis de boceto", "Resolver fórmulas matemáticas", "Generar historia infantil", "Mejorar dibujo"]
)

# Configuración del canvas
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
stroke_color = "#000000"
bg_color = '#FFFFFF'

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# Input API key
ke = st.text_input('🔑 Ingresa tu OpenAI API Key', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)


# ==========================
# FUNCIONALIDADES
# ==========================

# 1. ANALIZAR BOCETO
if option == "Análisis de boceto":
    if canvas_result.image_data is not None and api_key and st.button("🔍 Analizar boceto"):
        with st.spinner("Analizando tu dibujo..."):
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
            input_image.save('img.png')
            
            base64_image = encode_image_to_base64("img.png")
            st.session_state.base64_image = base64_image
            
            prompt_text = "Describe en español el contenido de este boceto."
            
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt_text},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        ]}
                    ],
                    max_tokens=500,
                )
                description = response.choices[0].message.content
                st.success("✅ Análisis completado:")
                st.write(description)
                st.session_state.full_response = description
                st.session_state.analysis_done = True
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")


# 2. RESOLVER FÓRMULAS MATEMÁTICAS
elif option == "Resolver fórmulas matemáticas":
    st.write("✏️ Dibuja o sube una fórmula matemática para resolverla.")
    
    uploaded_file = st.file_uploader("O sube una imagen con la fórmula", type=["png", "jpg", "jpeg"])
    trigger = st.button("🧮 Resolver fórmula")
    
    if (canvas_result.image_data is not None or uploaded_file) and api_key and trigger:
        with st.spinner("Resolviendo fórmula..."):
            if uploaded_file:
                img = Image.open(uploaded_file).convert("RGBA")
                img.save("formula.png")
            else:
                input_numpy_array = np.array(canvas_result.image_data)
                img = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
                img.save("formula.png")
            
            base64_image = encode_image_to_base64("formula.png")
            
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": [
                            {"type": "text", "text": "Reconoce la fórmula matemática en esta imagen, transcríbela en notación estándar y resuélvela paso a paso en español."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        ]}
                    ],
                    max_tokens=500,
                )
                result = response.choices[0].message.content
                st.success("✅ Fórmula reconocida y resuelta:")
                st.write(result)
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")


# 3. CREAR HISTORIA INFANTIL
elif option == "Generar historia infantil":
    if st.session_state.analysis_done:
        if st.button("✨ Crear historia infantil"):
            with st.spinner("Generando historia..."):
                story_prompt = f"Basándote en esta descripción: '{st.session_state.full_response}', crea una historia infantil breve, creativa y apropiada para niños."
                try:
                    story_response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": story_prompt}],
                        max_tokens=500,
                    )
                    story = story_response.choices[0].message.content
                    st.markdown("**📖 Tu historia:**")
                    st.write(story)
                except Exception as e:
                    st.error(f"Ocurrió un error: {e}")
    else:
        st.info("Primero analiza un boceto antes de crear la historia.")


# 4. MEJORAR DIBUJO
elif option == "Mejorar dibujo":
    st.write("🎨 Mejora tu boceto en distintos estilos con IA.")
    style = st.selectbox("Elige un estilo para mejorar la imagen:", ["realista", "anime", "acuarela", "digital art"])
    trigger = st.button("🚀 Mejorar dibujo")
    
    if canvas_result.image_data is not None and api_key and trigger:
        with st.spinner("Generando imagen mejorada..."):
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
            input_image.save('sketch.png')
            
            try:
                response = client.images.generate(
                    model="gpt-image-1",
                    prompt=f"Convierte este boceto en una versión detallada estilo {style}, manteniendo la esencia del trazo original.",
                    size="512x512"
                )
                improved_image_url = response.data[0].url
                st.image(improved_image_url, caption=f"Imagen mejorada ({style})")
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")


# ==========================
# ADVERTENCIA API KEY
# ==========================
if not api_key:
    st.warning("⚠️ Por favor ingresa tu API key.")

