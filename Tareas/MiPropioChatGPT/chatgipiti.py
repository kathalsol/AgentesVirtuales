import os
import gradio as gr
from google import genai
from dotenv import load_dotenv

# 1. Configuración de Gemini
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "models/gemini-2.5-flash"

# 2. Función que procesa el chat
def responder_amigo(mensaje, historial):
    # Creamos las instrucciones de personalidad
    instrucciones_amigo = """
        Eres costarricense y eres un amigo cercano, relajado y buena onda. 
        No respondas de forma robótica ni demasiado formal. Siempre saluda de
        forma animada.
        Usa un lenguaje natural, puedes usar expresiones casuales y coloquiales, 
        sé empático, apoya al usuario y, si es apropiado, usa un poco de humor. 
        Tu objetivo es que la conversación se sienta como un chat de WhatsApp con un amigo.
        """
    
    # Iniciamos el chat con el modelo y le damos las instrucciones de personalidad
    chat = client.chats.create(
        model=MODEL_ID,
        config={'system_instruction': instrucciones_amigo}
    )
    
    response = chat.send_message(mensaje)
    return response.text

# 3. Lanzar la interfaz
# Gradio ya sabe que es un chat, así que crea la caja de texto y el historial.
demo = gr.ChatInterface(
    fn=responder_amigo, 
    title="Mi Amigo Virtual 🫂",
    description="Cuéntame lo que quieras, aquí estoy para escucharte.",
    examples=["¿Qué onda?", "Tuve un día difícil", "¿Qué me recomiendas cenar?"]
)

if __name__ == "__main__":
    demo.launch()