# Proyecto Ollama

## Instrucciones para ejecutar

Sigue estos pasos en Windows:

1. Crear el entorno virtual:

   ```powershell
   python -m venv .venv
   ```

2. Activar el entorno:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Instalar dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

4. Ejecutar la prueba de latencia:

   ```powershell
   python .\test_latencia.py
   ```


## Desde WSL / Ubuntu

Sigue estos pasos si usas WSL o Ubuntu:

1. Crear el entorno virtual:

   ```bash
   python3 -m venv .venv
   ```

2. Activar el entorno:

   ```bash
   source .venv/bin/activate
   ```

3. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutar la prueba de latencia:

   ```bash
   python3 ./test_latencia.py
   ```

## Para correr los modelos de Azure o Gemini

1. Se debe crear un archivo .env que contiene la API key correspondiente a cada uno
2. Cuando se corre el script se corren ambos modelos que se seleccionaron en cada plataforma, pero
si se quiere se puede pasar como parámetro el modelo a utilizar. Por ejemplo:

   ```bash
   python3 test_latencia.py --modelo models/gemini-2.5-flash
   ```

---

> Asegúrate de ejecutar estos comandos desde la carpeta del proyecto.