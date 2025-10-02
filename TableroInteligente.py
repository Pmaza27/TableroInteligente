import os
import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""

# Función para convertir imagen a base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_image

# Configuración general
st.set_page_config(page_title='Tablero Inteligente')
st.title('🧠 Tablero Inteligente')

with st.sidebar:
    st.subheader("Acerca de:")
    st.write("Esta aplicación permite analizar dibujos, reconocer fórmulas matemáticas y más.")

# API key input
ke = st.text_input('🔑 Ingresa tu Clave OpenAI', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ.get('OPENAI_API_KEY')

# Cliente OpenAI
client = OpenAI(api_key=api_key) if api_key else None

# Menú de funcionalidades
funcionalidad = st.selectbox(
    "Elige la funcionalidad que deseas:",
    ["🖌️ Analizar Dibujo", "🔢 Resolver Fórmulas Matemáticas", "📚 Crear Historia Infantil"]
)

# =============== FUNCIÓN 1: ANALIZAR DIBUJO ====================
if funcionalidad == "🖌️ Analizar Dibujo":
    st.subheader("Dibuja un boceto en el panel y analízalo")
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)
    stroke_color = "#000000"
    bg_color = '#FFFFFF'

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=300,
        width=400,
        drawing_mode="freedraw",
        key="canvas",
    )

    analyze_button = st.button("🔍 Analizar Dibujo")

    if canvas_result.image_data is not None and api_key and analyze_button:
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
        input_image.save('img.png')

        base64_image = encode_image_to_base64("img.png")

        with st.spinner("Analizando dibujo..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user",
                     "content": [
                         {"type": "text", "text": "Describe brevemente en español la imagen."},
                         {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                     ]}
                ],
                max_tokens=500,
            )

        st.session_state.full_response = response.choices[0].message.content
        st.write("### 📝 Descripción generada:")
        st.write(st.session_state.full_response)
        st.session_state.analysis_done = True


# =============== FUNCIÓN 2: RECONOCER Y RESOLVER FÓRMULAS ====================
elif funcionalidad == "🔢 Resolver Fórmulas Matemáticas":
    st.subheader("Sube una imagen con una fórmula matemática escrita")
    uploaded_file = st.file_uploader("📂 Sube una imagen (JPG o PNG)", type=["jpg", "jpeg", "png"])
    solve_button = st.button("🧮 Reconocer y Resolver")

    if uploaded_file and api_key and solve_button:
        image = Image.open(uploaded_file)
        image.save("formula.png")

        base64_image = encode_image_to_base64("formula.png")

        with st.spinner("Reconociendo fórmula y resolviendo..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user",
                     "content": [
                         {"type": "text", "text": "Reconoce la fórmula matemática en esta imagen, exprésala en notación matemática y resuélvela paso a paso."},
                         {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                     ]}
                ],
                max_tokens=800,
            )

        st.markdown("### ✏️ Solución encontrada:")
        st.write(response.choices[0].message.content)


# =============== FUNCIÓN 3: CREAR HISTORIA INFANTIL ====================
elif funcionalidad == "📚 Crear Historia Infantil":
    st.subheader("Genera una historia infantil a partir de una idea")
    idea = st.text_area("Escribe una idea o tema para la historia")

    if st.button("✨ Crear Historia") and api_key and idea:
        with st.spinner("Generando historia..."):
            story_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Crea una historia infantil breve, creativa y entretenida sobre: {idea}"}],
                max_tokens=500,
            )
        st.markdown("**📖 Tu historia:**")
        st.write(story_response.choices[0].message.content)


# Warning si no hay API Key
if not api_key:
    st.warning("⚠️ Por favor ingresa tu API key para usar la aplicación.")

