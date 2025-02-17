# Clasificador de Comentarios sobre Vacuna VPH

## Descripción
Esta aplicación web desarrollada con Streamlit permite clasificar automáticamente comentarios relacionados con la vacuna contra el Virus del Papiloma Humano (VPH). Utiliza el modelo GPT-4o de OpenAI para analizar y categorizar comentarios según su postura respecto a la vacuna.

## Características
- Clasificación de comentarios individuales
- Procesamiento por lotes a través de archivos CSV o Excel
- Interfaz gráfica intuitiva desarrollada con Streamlit
- Categorización en 4 clases diferentes:
  - **0**: Postura contraria a la vacuna (antivacuna)
  - **1**: Postura a favor de la vacuna (provacuna)
  - **2**: Dudas sobre la vacuna
  - **3**: Comentarios no relacionados o no clasificables

## Requisitos
- Python 3.6 o superior
- Bibliotecas requeridas:
  - streamlit
  - openai
  - pandas
  - numpy
- Una clave API válida de OpenAI

## Instalación

1. Clone este repositorio o descargue los archivos
2. Instale las dependencias necesarias:

```bash
pip install streamlit openai pandas numpy
```

## Uso

1. Ejecute la aplicación con Streamlit:

```bash
streamlit run streamlit_app.py
```

2. En su navegador, se abrirá la interfaz de la aplicación
3. Introduzca su clave API de OpenAI
4. Seleccione uno de los dos modos de entrada:
   - **Comentario directo**: para clasificar un solo comentario
   - **Subir archivo (Excel/CSV)**: para clasificar múltiples comentarios

### Análisis de archivo
Para analizar un archivo, este debe contener una columna llamada 'Comment' con los comentarios a clasificar. Los resultados se almacenarán en una nueva columna llamada 'predicted_topic' y podrá descargarlos en formato CSV.

## Funcionamiento interno

La aplicación utiliza un enfoque de "zero-shot learning" con GPT-4o para clasificar los comentarios. El prompt del sistema instruye al modelo para que clasifique cada comentario en una de las cuatro categorías mencionadas anteriormente. La temperatura se establece en 0 para obtener resultados más deterministas.

## Notas

- El tiempo de procesamiento puede variar según la cantidad de comentarios y la carga de la API de OpenAI
- El uso de la API de OpenAI está sujeto a costos según su política de precios
- La precisión de la clasificación depende de la calidad y claridad de los comentarios

## Tesis UNP - Ingeniería Mecatrónica

Este proyecto forma parte de una tesis de Ingeniería Mecatrónica de la Universidad Nacional de Piura (UNP).