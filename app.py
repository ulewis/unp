import streamlit as st
import openai
from openai import OpenAI  # Importamos la clase para instanciar el cliente
import pandas as pd
import numpy as np
from io import StringIO

# Define el prompt para clasificar comentarios
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

def zero_shot_classify(comment: str, client: OpenAI) -> str:
    """
    Clasifica un comentario utilizando GPT-4o (o GPT-4 si prefieres) y el prompt definido.
    
    Parámetros:
        comment: Comentario a clasificar.
        client: Instancia del cliente OpenAI.
        
    Retorna:
        La clasificación asignada (un número como string).
    """
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": comment}
    ]
    try:
        # Usamos el método del cliente para crear la solicitud de chat completions
        response = client.chat.completions.create(
            model="gpt-4o",  # Usa "gpt-3.5-turbo" o "gpt-4" según tu preferencia y disponibilidad
            messages=messages,
            temperature=0,
            max_tokens=10,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error al clasificar el comentario: {e}")
        return "Error"

# ----------------- Interfaz de Streamlit -----------------
st.set_page_config(page_title="Tesis UNP - Ingeniería mecatrónica", layout="wide")
st.header("Tesis UNP - Ingeniería mecatrónica")

# Campo para la API key de OpenAI
api_key = st.text_input("Ingresa tu API key de OpenAI", type="password")
client = None
if api_key:
    # Instanciamos el cliente con la API key proporcionada
    client = OpenAI(api_key=api_key)

# Explicación de las categorías
st.markdown("""
**Categorías de clasificación:**

- **0:** Comentario con postura contraria a la vacuna contra el VPH (antivacuna).
- **1:** Comentario con postura a favor de la vacuna contra el VPH (provacuna).
- **2:** Comentario que refleja una duda o dudas sobre la vacuna contra el VPH.
- **3:** Comentario que habla de cualquier otra cosa o en el que no se pueda clasificar.
""")

# Selección del modo de entrada
modo = st.radio("Selecciona la forma de entrada", ("Comentario directo", "Subir archivo (Excel/CSV)"))

if modo == "Comentario directo":
    comment = st.text_area("Ingresa el comentario a clasificar:")
    if st.button("Clasificar comentario"):
        if not api_key:
            st.error("Debes ingresar la API key de OpenAI.")
        elif comment.strip() == "":
            st.error("Por favor ingresa un comentario.")
        else:
            with st.spinner("Clasificando..."):
                result = zero_shot_classify(comment, client)
            st.success(f"El comentario fue clasificado como: **{result}**")
            st.info("Recuerda que:\n- 0: antivacuna\n- 1: provacuna\n- 2: duda\n- 3: otra cosa")
            
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
                            df['predicted_topic'] = df['Comment'].apply(lambda x: zero_shot_classify(x, client))
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
