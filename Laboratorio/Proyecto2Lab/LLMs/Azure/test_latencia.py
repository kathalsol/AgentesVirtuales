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
    # Configurar cliente con el deployment específico del modelo
    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=subscription_key,
        azure_deployment=modelo
    )
    
    print(f"Conectando con el modelo Azure {modelo}...")

    try:
        # Enviar mensaje
        mensaje = "Hola Juan! Me siento solo"
        print(f"Mensaje: {mensaje}\n")
        
        inicio = time.time()

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": instrucciones_amigo,
                },
                {
                    "role": "user",
                    "content": mensaje,
                }
            ],
            model=modelo
        )
        
        fin = time.time()
        latencia = fin - inicio
        
        # Obtener uso de tokens
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        
        # Calcular costo
        prices = AZURE_PRICES.get(modelo, {"input": 0.002, "output": 0.008})
        cost_input = (prompt_tokens / 1_000) * prices["input"]
        cost_output = (completion_tokens / 1_000) * prices["output"]
        cost_total = cost_input + cost_output

        print(f"Respuesta de Juan:\n{response.choices[0].message.content}\n")
        print("-" * 60)
        print(f"Latencia total: {latencia:.2f} segundos")
        print(f"\nUso de tokens:")
        print(f"  - Input tokens: {prompt_tokens}")
        print(f"  - Output tokens: {completion_tokens}")
        print(f"  - Total tokens: {total_tokens}")
        print(f"\nCosto:")
        print(f"  - Costo input: ${cost_input:.6f}")
        print(f"  - Costo output: ${cost_output:.6f}")
        print(f"  - Costo total: ${cost_total:.6f}")
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
    
    for modelo in modelos:
        medir_latencia(modelo)

if __name__ == "__main__":
    main()