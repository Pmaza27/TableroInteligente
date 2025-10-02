import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# ======================
# Funciones auxiliares
# ======================
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return None

def save_canvas_image(canvas_result, filename="img.png"):
    input_numpy_array = np.array(canvas_result.image_data)
    input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
    input_image.save(filename)
    return filename

# ======================
# Configuración
# ======================
st.set_page_config(page_title='Tablero Inteligente')
st.title('🖌️ Tablero Inteligente')

with st.sidebar:
    st.subheader("🔧 Funcionalidades disponibles:")
    option = st.selectbox(
        "Elige lo que quieres hacer:",
        ["Analizar boceto", "Resolver fórmulas matemáticas", "Mejorar dibujo", "Crear historia infantil"]
    )
    st.divider()
    st.subheader("🔑 Configuración")
    ke = st.text_input('Ingresa tu OpenAI API Key', type="password")

# Guardar API Key
if ke:
    os.environ['OPENAI_API_KEY'] = ke
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# ======================
# Área de Dibujo / Upload
# ======================
st.subheader("✏️ Dibuja o sube tu imagen")

col1, col2 = st.columns(2)
with col1:
    stroke_width = st.slider('Ancho de línea', 1, 30, 5)
    stroke_color = st.color_picker("Color de línea", "#000000")
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
with col2:
    uploaded_file = st.file_uploader("📂 O sube una imagen", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Imagen subida", use_column_width=True)

# ======================
# Lógica según opción
# ======================
if not api_key:
    st.warning("⚠️ Por favor ingresa tu API key en la barra lateral.")
else:
    if st.button("▶ Ejecutar"):

        # Guardar imagen desde canvas o subida
        image_path = None
        if canvas_result.image_data is not None:
            image_path = save_canvas_image(canvas_result)
        elif uploaded_file is not None:
            image_path = "uploaded.png"
            img.save(image_path)

        if not image_path:
            st.error("Por favor dibuja o sube una imagen antes de continuar.")
        else:
            base64_image = encode_image_to_base64(image_path)

            # ---- Analizar boceto ----
            if option == "Analizar boceto":
                with st.spinner("Analizando boceto..."):
                    prompt_text = "Describe en español brevemente el contenido de este boceto."
                    response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                            ]
                        }],
                        max_tokens=400,
                    )
                    st.success("✅ Análisis completado:")
                    st.write(response.choices[0].message.content)

            # ---- Resolver fórmulas matemáticas ----
            elif option == "Resolver fórmulas matemáticas":
                with st.spinner("Resolviendo..."):
                    prompt_text = "Reconoce la fórmula matemática en la imagen y resuélvela paso a paso."
                    response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                            ]
                        }],
                        max_tokens=500,
                    )
                    st.success("✅ Resultado de la fórmula:")
                    st.write(response.choices[0].message.content)

            # ---- Mejorar dibujo ----
            elif option == "Mejorar dibujo":
                style = st.radio("🎨 Elige estilo de mejora:", ["Realista", "Caricatura", "Anime", "Acuarela"])
                with st.spinner("Generando versión mejorada..."):
                    prompt_text = f"Mejora este boceto en una versión detallada, estilo {style}."
                    response = client.images.generate(
                        model="gpt-image-1",
                        prompt=prompt_text,
                        image=open(image_path, "rb"),
                        size="512x512"
                    )
                    improved_image_url = response.data[0].url
                    st.image(improved_image_url, caption=f"Imagen mejorada ({style})")

            # ---- Historia infantil ----
            elif option == "Crear historia infantil":
                with st.spinner("Creando historia..."):
                    prompt_text = f"Basándote en este dibujo, crea una historia infantil corta, creativa y entretenida."
                    response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                            ]
                        }],
                        max_tokens=500,
                    )
                    st.success("📖 Tu historia:")
                    st.write(response.choices[0].message.content)
