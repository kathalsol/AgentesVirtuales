import time
from openai import OpenAI
from argparse import ArgumentParser

OLLAMA_MODELS = [
    "qwen3:8b",
]

# Reutilizas EXACTAMENTE las mismas instrucciones
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

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


def medir_latencia(modelo):

    print(f"Conectando con el modelo Ollama {modelo}...")

    try:

        mensaje = "Hola Juan! Me siento solo"

        print(f"Mensaje: {mensaje}\n")

        inicio = time.perf_counter()
        ttft = None
        respuesta_completa = ""
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        
        response = client.chat.completions.create(
            model=modelo,
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
            stream=True,
            stream_options={"include_usage": True}  # Para obtener tokens al final
        )

        for chunk in response:
            # Capturar TTFT en el primer chunk con contenido
            if ttft is None and chunk.choices and chunk.choices[0].delta.content:
                ttft = time.perf_counter() - inicio
            
            # Acumular texto de respuesta
            if chunk.choices and chunk.choices[0].delta.content:
                respuesta_completa += chunk.choices[0].delta.content
            
            # El último chunk trae el usage (gracias a stream_options)
            if hasattr(chunk, "usage") and chunk.usage is not None:
                prompt_tokens = chunk.usage.prompt_tokens
                completion_tokens = chunk.usage.completion_tokens
                total_tokens = chunk.usage.total_tokens
        
        fin = time.perf_counter()
        latencia_total = fin - inicio

        print(
            f"Respuesta de Juan:\n"
            f"{respuesta_completa}\n"
        )

        print("-" * 60)
        print(f"TTFT (tiempo al primer token): {ttft:.2f} segundos" if ttft else "TTFT: No disponible")
        print(f"Latencia total:                {latencia_total:.2f} segundos")
        if ttft:
            print(f"Latencia de generación:        {(latencia_total - ttft):.2f} segundos")
        print(f"\nUso de tokens:")
        print(f"  - Input tokens:  {prompt_tokens}")
        print(f"  - Output tokens: {completion_tokens}")
        print(f"  - Total tokens:  {total_tokens}")
        print("\nCosto:")
        print("  - Costo total: $0.000000 (modelo local)")

        print("-" * 60)

    except Exception as e:
        print(f"Error: {e}")


def main():

    parser = ArgumentParser(
        description="Medir latencia de modelos Ollama"
    )

    parser.add_argument(
        "--modelo",
        type=str,
        default=",".join(OLLAMA_MODELS)
    )

    args = parser.parse_args()

    modelos = [m.strip() for m in args.modelo.split(",")]

    # Realizar 5 iteraciones por modelo para obtener un promedio
    for iteracion in range(5):
        print(f"\n=== Iteración {iteracion + 1} ===")
        for modelo in modelos:
            medir_latencia(modelo)


if __name__ == "__main__":
    main()