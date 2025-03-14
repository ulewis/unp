import streamlit as st
import openai
import speech_recognition as sr
import pandas as pd
from io import StringIO

# -----------------------------------------------------
# PROMPT DE CLASIFICACIÓN 
prompt = """
Tendrás un rol de clasificador de comentarios de una publicación relacionada con la vacuna contra el VPH.
Sólo debes responder con un valor numérico.
No tienes permitido responder otra cosa que no sean números. Las clasificaciones son:

0: El comentario tiene una postura contraria a la vacuna contra el VPH (antivacuna).
1: El comentario tiene una postura a favor de la vacuna contra el VPH (provacuna).
2: El comentario refleja una duda o dudas relacionadas con la vacuna contra el VPH.
3: El comentario habla de cualquier otra cosa.

Trata de interpretar las intenciones de las personas, ya que se trata de comentarios de Facebook.
Si no puedes clasificar, tu respuesta debe ser "3".

Ahora, clasifica el siguiente comentario, teniendo en cuenta que tu respuesta es solo un número:
"""

# -----------------------------------------------------
# VARIABLE GLOBAL PARA EL CLIENTE
client = None

# -----------------------------------------------------
# FUNCIÓN PARA CLASIFICAR USANDO LA API DE OPENAI
def zero_shot_classify(comment: str) -> str:
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": comment}
    ]
    try:
        global client
        # Si no se ha creado aún, se instancia el cliente con la API key proporcionada
        if client is None:
            client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",  # Puedes cambiar a "gpt-4" si lo prefieres/disponible
            temperature=0,
            max_tokens=10,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error al clasificar el comentario: {e}")
        return "Error"

# -----------------------------------------------------
# FUNCIÓN DE SPEECH-TO-TEXT 
def record_audio() -> str:
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        st.info("Ajustando el ruido ambiente... Espera unos segundos.")
        recognizer.adjust_for_ambient_noise(source)
        st.info("Ajuste completado. ¡Puedes empezar a hablar!")
        st.info("Escuchando...")
        audio = recognizer.listen(source)
    try:
        # Reconoce el audio usando el servicio de Google
        text = recognizer.recognize_google(audio, language="es-ES")
        return text
    except sr.UnknownValueError:
        st.error("No se pudo entender el audio. Intenta de nuevo.")
        return None
    except sr.RequestError as e:
        st.error("Error al conectarse al servicio de reconocimiento; {0}".format(e))
        return None

# -----------------------------------------------------
# CONFIGURACIÓN E INTERFAZ DE STREAMLIT
st.set_page_config(page_title="Tesis UNP - Ingeniería Mecatrónica", layout="wide")
st.header("Tesis UNP - Ingeniería Mecatrónica")

# Campo para la API key de OpenAI
api_key = st.text_input("Ingresa tu API key de OpenAI", type="password")
if api_key:
    openai.api_key = api_key
    client = openai.OpenAI(api_key=api_key)

# Explicación de las categorías
st.markdown("""
**Categorías de clasificación:**

- **0:** Comentario con postura contraria a la vacuna contra el VPH (antivacuna).
- **1:** Comentario con postura a favor de la vacuna contra el VPH (provacuna).
- **2:** Comentario que refleja una duda o dudas sobre la vacuna contra el VPH.
- **3:** Comentario que habla de cualquier otra cosa o en el que no se pueda clasificar.
""")

# Selección del modo de entrada
modo = st.radio("Selecciona la forma de entrada", ("Comentario directo", "Reconocimiento de voz", "Subir archivo (Excel/CSV)"))

# -----------------------------------------------------
# MODO: COMENTARIO DIRECTO
if modo == "Comentario directo":
    comment = st.text_area("Ingresa el comentario a clasificar:")
    if st.button("Clasificar comentario"):
        if not api_key:
            st.error("Debes ingresar la API key de OpenAI.")
        elif comment.strip() == "":
            st.error("Por favor ingresa un comentario.")
        else:
            with st.spinner("Clasificando..."):
                result = zero_shot_classify(comment)
            st.success(f"El comentario fue clasificado como: **{result}**")
            st.info("Recuerda:\n- 0: antivacuna\n- 1: provacuna\n- 2: duda\n- 3: otra cosa")

# -----------------------------------------------------
# MODO: RECONOCIMIENTO DE VOZ
elif modo == "Reconocimiento de voz":
    if st.button("Grabar comentario"):
        if not api_key:
            st.error("Debes ingresar la API key de OpenAI.")
        else:
            recognized_text = record_audio()
            if recognized_text:
                st.write("Texto reconocido:")
                st.code(recognized_text)
                with st.spinner("Clasificando..."):
                    result = zero_shot_classify(recognized_text)
                st.success(f"El comentario fue clasificado como: **{result}**")
                st.info("Recuerda:\n- 0: antivacuna\n- 1: provacuna\n- 2: duda\n- 3: otra cosa")

# -----------------------------------------------------
# MODO: SUBIR ARCHIVO (Excel/CSV)
elif modo == "Subir archivo (Excel/CSV)":
    uploaded_file = st.file_uploader("Sube tu archivo de Excel o CSV", type=["xlsx", "xls", "csv"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            df = None

        if df is not None:
            st.write("Vista previa de los datos:")
            st.dataframe(df.head())

            # Verificar que exista la columna 'Comment'
            if "Comment" not in df.columns:
                st.error("El archivo debe contener una columna llamada 'Comment'.")
            else:
                if st.button("Clasificar comentarios del archivo"):
                    if not api_key:
                        st.error("Debes ingresar la API key de OpenAI.")
                    else:
                        with st.spinner("Clasificando comentarios..."):
                            df['predicted_topic'] = df['Comment'].apply(lambda x: zero_shot_classify(x))
                        st.success("¡Clasificación completada!")
                        st.write("Vista de resultados:")
                        st.dataframe(df.head())

                        # Preparar archivo CSV para descarga
                        csv_buffer = StringIO()
                        df.to_csv(csv_buffer, index=False)
                        st.download_button(
                            label="Descargar resultados en CSV",
                            data=csv_buffer.getvalue(),
                            file_name="resultados_clasificacion.csv",
                            mime="text/csv"
                        )
