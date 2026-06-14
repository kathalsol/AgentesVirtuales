import os
import time
from google import genai
from dotenv import load_dotenv
from argparse import ArgumentParser

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MODELS = "models/gemini-2.5-flash,models/gemini-3.5-flash"

# Precios por millón de tokens (en USD)
GEMINI_PRICES = {
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-3.5-flash": {"input": 0.075, "output": 0.30},
}

# Instrucciones de personalidad
instrucciones_amigo = """
Usted es Juan, un compañero y asistente virtual costarricense especializado en acompañar personas adultas mayores en Costa Rica.

Su misión principal es:
- Mitigar la soledad no deseada.
- Estimular el bienestar cognitivo.
- Promover el bienestar emocional.
- Fomentar de manera sutil las conexiones sociales con familiares, amistades y vecinos.

Es una inteligencia artificial paciente, cálida, respetuosa y cercana.

ESTILO DE COMUNICACIÓN
- Utilice SIEMPRE el trato formal de 'usted'.
- Nunca utilice 'tú' ni 'vos'.
- Mantenga un tono afectuoso, empático y respetuoso.
- Evite completamente cualquier lenguaje infantilizante o paternalista.
- Trate siempre a la persona como un adulto sabio, capaz e independiente.
- Puede incorporar de forma natural expresiones costarricenses respetuosas cuando sea apropiado.

LONGITUD DE RESPUESTA
- Mantenga las respuestas cortas y fáciles de leer.
- Máximo 2 o 3 párrafos breves por respuesta.
- Evite explicaciones largas o complejas.
- Siempre que sea natural, finalice con una pregunta abierta para mantener la conversación.
"""

# Medir latencia y costo
def medir_latencia(modelo):
    print(f"Conectando con el modelo {modelo}...")
    mensaje = "Hola Juan! Me siento solo"
    print(f"Mensaje: {mensaje}\n")

    inicio = time.time()

    try:
        # Enviar mensaje
        chat = client.chats.create(
            model=modelo,
            config={'system_instruction': instrucciones_amigo}
        )
        
        response = chat.send_message(mensaje)
        
        fin = time.time()
        latencia = fin - inicio
        
        # Extraer modelo sin "models/" para buscar precios
        model_key = modelo.replace("models/", "")
        
        # Obtener uso de tokens
        input_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0
        output_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
        total_tokens = input_tokens + output_tokens
        
        # Calcular costo
        prices = GEMINI_PRICES.get(model_key, {"input": 0.075, "output": 0.30})
        cost_input = (input_tokens / 1_000_000) * prices["input"]
        cost_output = (output_tokens / 1_000_000) * prices["output"]
        cost_total = cost_input + cost_output
        
        print(f"Respuesta de Juan:\n{response.text}\n")
        print("-" * 60 + "\n")
        print(f"Latencia total: {latencia:.2f} segundos")
        print(f"\nUso de tokens:")
        print(f"  - Input tokens: {input_tokens}")
        print(f"  - Output tokens: {output_tokens}")
        print(f"  - Total tokens: {total_tokens}")
        print(f"\nCosto:")
        print(f"  - Costo input: ${cost_input:.6f}")
        print(f"  - Costo output: ${cost_output:.6f}")
        print(f"  - Costo total: ${cost_total:.6f}")
        print("-" * 60 + "\n")
        
    except Exception as e:
        print(f"Error: {e}\n")

def main():
    parser = ArgumentParser(description="Medir latencia y costo de modelos Gemini")
    parser.add_argument("--modelo", type=str, default=GEMINI_MODELS, help="ID del modelo a probar")
    args = parser.parse_args()
    
    for modelo in args.modelo.split(","):
        medir_latencia(modelo.strip())

if __name__ == "__main__":
    main()