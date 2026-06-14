import os
import time
from openai import AzureOpenAI
from dotenv import load_dotenv
from argparse import ArgumentParser

load_dotenv()

# Configuración Azure
endpoint = "https://proyectolaboratorioagentevirtual.openai.azure.com/"
api_version = "2025-04-01-preview"

subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

AZURE_MODELS = ["gpt-4.1", "gpt-4.1-mini"]
# Precios por 1K tokens (en USD)
AZURE_PRICES = {
    "gpt-4.1": {"input": 0.002, "output": 0.008},
    "gpt-4.1-mini": {"input": 0.00015, "output": 0.0006},
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
    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=subscription_key,
        azure_deployment=modelo
    )
    
    print(f"Conectando con el modelo Azure {modelo}...")

    try:
        mensaje = "Hola Juan! Me siento solo"
        print(f"Mensaje: {mensaje}\n")
        
        inicio = time.time()
        ttft = None
        respuesta_completa = ""
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        # stream=True para poder capturar el primer token
        stream = client.chat.completions.create(
            messages=[
                {"role": "system", "content": instrucciones_amigo},
                {"role": "user", "content": mensaje}
            ],
            model=modelo,
            stream=True,
            stream_options={"include_usage": True}  # Para obtener tokens al final
        )
        
        for chunk in stream:
            # Capturar TTFT en el primer chunk con contenido
            if ttft is None and chunk.choices and chunk.choices[0].delta.content:
                ttft = time.time() - inicio
            
            # Acumular texto de respuesta
            if chunk.choices and chunk.choices[0].delta.content:
                respuesta_completa += chunk.choices[0].delta.content
            
            # El último chunk trae el usage (gracias a stream_options)
            if hasattr(chunk, "usage") and chunk.usage is not None:
                prompt_tokens = chunk.usage.prompt_tokens
                completion_tokens = chunk.usage.completion_tokens
                total_tokens = chunk.usage.total_tokens

        fin = time.time()
        latencia_total = fin - inicio

        # Calcular costo
        prices = AZURE_PRICES.get(modelo, {"input": 0.002, "output": 0.008})
        cost_input = (prompt_tokens / 1_000) * prices["input"]
        cost_output = (completion_tokens / 1_000) * prices["output"]
        cost_total = cost_input + cost_output

        print(f"Respuesta de Juan:\n{respuesta_completa}\n")
        print("-" * 60)
        print(f"TTFT (tiempo al primer token): {ttft:.2f} segundos")
        print(f"Latencia total:                {latencia_total:.2f} segundos")
        print(f"Latencia de generación:        {(latencia_total - ttft):.2f} segundos")
        print(f"\nUso de tokens:")
        print(f"  - Input tokens:  {prompt_tokens}")
        print(f"  - Output tokens: {completion_tokens}")
        print(f"  - Total tokens:  {total_tokens}")
        print(f"\nCosto:")
        print(f"  - Costo input:  ${cost_input:.6f}")
        print(f"  - Costo output: ${cost_output:.6f}")
        print(f"  - Costo total:  ${cost_total:.6f}")
        print("-" * 60 + "\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = ArgumentParser(description="Medir latencia y costo de modelos Azure")
    parser.add_argument("--modelo", type=str, default=",".join(AZURE_MODELS), help="ID del modelo a probar (separados por coma)")
    args = parser.parse_args()
    
    modelos = [m.strip() for m in args.modelo.split(",")]

    # Realizar 5 iteraciones por modelo para obtener un promedio
    for iteracion in range(5):
        print(f"\n=== Iteración {iteracion + 1} ===")
        for modelo in modelos:
            medir_latencia(modelo)

if __name__ == "__main__":
    main()