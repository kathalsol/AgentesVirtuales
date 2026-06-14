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
    ttft = None
    respuesta_completa = ""
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    
    max_intentos = 5
    delay_inicial = 2

    try:
        for intento in range(max_intentos):
            try:
                # Enviar mensaje
                chat = client.chats.create(
                    model=modelo,
                    config={'system_instruction': instrucciones_amigo}
                )
                
                response = chat.send_message(mensaje)
                
                # Si llegamos aquí, fue exitoso
                break
                
            except Exception as e:
                error_str = str(e)
                # Si es un error 503 (modelo saturado), reintentar
                if "503" in error_str and intento < max_intentos - 1:
                    espera = delay_inicial * (2 ** intento)  # Backoff exponencial
                    print(f"Modelo saturado. Reintentando en {espera} segundos (intento {intento + 1}/{max_intentos})...\n")
                    time.sleep(espera)
                    continue
                else:
                    # Cualquier otro error o último intento fallido
                    raise
        
        # Capturar TTFT (en este caso es el tiempo total sin streaming)
        ttft = time.time() - inicio
        respuesta_completa = response.text if hasattr(response, 'text') else str(response)
        
        fin = time.time()
        latencia = fin - inicio
        
        # Extraer modelo sin "models/" para buscar precios
        model_key = modelo.replace("models/", "")
        
        # Obtener uso de tokens de la respuesta
        input_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0
        output_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
        total_tokens = input_tokens + output_tokens
        
        # Calcular costo
        prices = GEMINI_PRICES.get(model_key, {"input": 0.075, "output": 0.30})
        cost_input = (input_tokens / 1_000_000) * prices["input"]
        cost_output = (output_tokens / 1_000_000) * prices["output"]
        cost_total = cost_input + cost_output
        
        print(f"Respuesta de Juan:\n{respuesta_completa}\n")
        print("-" * 60)
        print(f"Latencia total:                {latencia:.2f} segundos")
        print(f"\nUso de tokens:")
        print(f"  - Input tokens:  {input_tokens}")
        print(f"  - Output tokens: {output_tokens}")
        print(f"  - Total tokens:  {total_tokens}")
        print(f"\nCosto:")
        print(f"  - Costo input:  ${cost_input:.6f}")
        print(f"  - Costo output: ${cost_output:.6f}")
        print(f"  - Costo total:  ${cost_total:.6f}")
        print("-" * 60 + "\n")
        
    except Exception as e:
        print(f"Error: {e}\n")

def main():
    parser = ArgumentParser(description="Medir latencia y costo de modelos Gemini")
    parser.add_argument("--modelo", type=str, default=GEMINI_MODELS, help="ID del modelo a probar")
    args = parser.parse_args()
    
    # Realizar 5 iteraciones por modelo para obtener un promedio
    for iteracion in range(5):
        print(f"\n=== Iteración {iteracion + 1} ===")
        for modelo in args.modelo.split(","):
            medir_latencia(modelo.strip())

if __name__ == "__main__":
    main()