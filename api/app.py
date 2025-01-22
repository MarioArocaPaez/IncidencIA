from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Configurar Flask
app = Flask(__name__)
CORS(app)

# Configurar el modelo y el prompt
template = """
Eres un asistente especializado en gestionar incidencias de conectividad basándote en la información proporcionada. Responde exclusivamente en español de España. Responde de forma clara y natural, y utiliza únicamente los datos disponibles en la información proporcionada. No des respuestas en forma de enumeraciones ni inventes información. Si algún dato no está disponible, indícalo explícitamente.

Te proporcionaré los datos completos de una incidencia en formato descriptivo. Utiliza únicamente esa información para generar tu respuesta. No utilices información adicional o inventada. Responde de forma clara, contextualizando los datos para que sean fáciles de entender.

Ejemplo de respuesta: "La incidencia con ID CUST00004 pertenece al cliente Cristian Tello. Actualmente está abierta desde el 9 de enero. Se trata de un problema con fibra óptica que causó un fallo total y degradación de servicio en la Sucursal Este. El nivel de severidad es bajo y la prioridad asignada es alta." No utilices enumeraciones o listas.

Datos de la incidencia:
{csv_data}

Pregunta: {question}

Respuesta:
"""

model = OllamaLLM(model="llama3", system_message="Eres un asistente que responde EXCLUSIVAMENTE en español de España. Responde de forma clara, natural y en ESPAÑOL.")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Cargar el archivo CSV
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path, sep=";")
        return df
    except Exception as e:
        print(f"Error al cargar el archivo CSV: {e}")
        return None

# Buscar un caso específico por ID Cliente
def get_case_by_id(df, client_id):
    case = df[df["ID Cliente"] == client_id]
    if case.empty:
        return None
    return case.iloc[0]

# Formatear caso para el modelo
def format_case_for_model(case):
    return (
        f"ID Cliente: {case['ID Cliente']}, Nombre Cliente: {case['Nombre Cliente']}, Estado Incidencia: {case['Estado Incidencia']}, "
        f"Resultado Prueba: {case['Resultado Prueba']}, Tipo Sistema: {case['Tipo Sistema']}, Nivel Severidad: {case['Nivel Severidad']}, "
        f"Tipo Impacto: {case['Tipo Impacto']}, Prioridad: {case['Prioridad']}, Equipo Afectado: {case['Equipo Afectado']}, "
        f"Ubicación: {case['Ubicación']}, Fecha Reporte: {case['Fecha Reporte']}, Fecha Resolución: {case['Fecha Resolución']}, "
        f"Descripción: {case['Descripción']}"
    )

# Ruta para manejar las consultas
@app.route('/consultar_incidencia', methods=['POST'])
def consultar_incidencia():
    try:
        # Cargar datos del archivo CSV
        if not hasattr(app, 'df'):
            app.df = load_csv("datos.csv")
        
        if app.df is None:
            return jsonify({"error": "No se pudo cargar el archivo CSV"}), 500

        # Obtener el ID Cliente de la solicitud
        data = request.json
        client_id = data.get("ID Cliente")

        if not client_id:
            return jsonify({"error": "ID Cliente es obligatorio"}), 400

        # Buscar el caso
        case = get_case_by_id(app.df, client_id)
        if case is None:
            return jsonify({"error": f"No se encontró ninguna incidencia con el ID {client_id}"}), 404

        # Formatear el caso y generar la respuesta del modelo
        formatted_case = format_case_for_model(case)
        result = chain.invoke({"csv_data": formatted_case, "question": f"Háblame sobre la incidencia del cliente con ID {client_id}."})
        
        return jsonify({"respuesta": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Iniciar la aplicación
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
