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
            ]
        )

        fin = time.perf_counter()

        latencia = fin - inicio

        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens

        print(
            f"Respuesta de Juan:\n"
            f"{response.choices[0].message.content}\n"
        )

        print("-" * 60)

        print(f"Latencia total: {latencia:.2f} segundos")

        print("\nUso de tokens:")
        print(f"  - Input tokens: {prompt_tokens}")
        print(f"  - Output tokens: {completion_tokens}")
        print(f"  - Total tokens: {total_tokens}")

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

    for modelo in modelos:
        medir_latencia(modelo)


if __name__ == "__main__":
    main()