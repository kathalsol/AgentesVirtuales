# 🫂 Mi Amigo Virtual (Gemini Chat)

Este es un chatbot personalizado que utiliza la tecnología de **Google Gemini 2.5** para interactuar como un amigo cercano y relajado. Cuenta con una interfaz gráfica moderna construida con **Gradio**.

## 🚀 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:
* **Python 3.9** o superior.
* Una **API Key** de Google Gemini (puedes obtenerla gratis en [Google AI Studio](https://aistudio.google.com/)).

## 🛠️ Instalación

Sigue estos pasos para configurar el proyecto en tu computadora:

1. **Clona este repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)
   cd Tareas/MiPropioChatGPT

### 2. Configuración del Entorno Virtual (Aislado)
Es fundamental usar un entorno virtual para que las librerías de este proyecto no choquen con otras que tengas en tu computadora.

* **Crear el entorno:**
    ```bash
    python3 -m venv env
    ```
* **Activar el entorno:**
    * En **Linux/Ubuntu/macOS**: `source env/bin/activate`
    * En **Windows**: `env\Scripts\activate`

### 3. Instalación de Dependencias
Una vez activado el entorno (verás un `(env)` en tu terminal), instala las librerías necesarias:

```bash
pip install google-genai gradio python-dotenv
pip install gradio
```

O más sencillo corre el siguiente comando:
```bash
pip install -r requirements.txt
```

### 4. Configuración de Seguridad (Variables de Entorno)
Para evitar que tu API Key sea visible en el código utilicé un archivo de configuración oculto.

1. En la carpeta raíz de tu proyecto, crea un archivo llamado `.env` (sin nombre, solo la extensión).
2. Abre el archivo con cualquier editor de texto y pega tu clave así:
   ```text
   GEMINI_API_KEY=tu_clave_real_aqui_sin_comillas

### 5. Ejecución y Puesta en Marcha
Una vez que las dependencias instaladas, es momento de ver tu chat en acción.

#### Ejecutar el script
Desde tu terminal, con el entorno virtual activo `(env)`, ejecuta:
```bash
python chatgipiti.py
```

Al ejecutar el comando, verás unos mensajes en la terminal. Busca el LocalURL que Gradio te muestra, algo como `http://127.0.0.1:7860`

Copia esa dirección y pégala en tu navegador favorito (Chrome, Firefox, Edge). ¡Listo! Ya puedes empezar a chatear con tu "amigo" virtual.