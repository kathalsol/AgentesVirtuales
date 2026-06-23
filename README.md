# Agentes Virtuales como Medio de Comunicación para Combatir la Soledad en Adultos Mayores

## 📋 Descripción del Proyecto

Este repositorio contiene el desarrollo de un **agente virtual de compañía con avatar** diseñado para reducir la soledad en adultos mayores mediante conversaciones fluidas y actividades interactivas. El proyecto combina tecnologías de inteligencia artificial, síntesis de voz (TTS), reconocimiento de voz (STT) y modelos de lenguaje grandes (LLMs) para crear una experiencia de interacción natural y empática.

### Objetivos Principales
- Diseñar e implementar un agente virtual inteligente con interfaz de avatar
- Evaluar la efectividad del agente en la reducción de la soledad en adultos mayores
- Comparar el desempeño de diferentes modelos de LLM, STT y TTS
- Validar la experiencia del usuario a través de métricas de latencia y cuestionarios de satisfacción

### Justificación
La soledad y el aislamiento social impactan negativamente la salud física, mental y emocional de los adultos mayores. Este proyecto explora soluciones tecnológicas innovadoras que complementen el apoyo humano y promuevan el bienestar integral de esta población.

---

## 📁 Estructura del Repositorio

```
AgentesVirtuales/
├── README.md                    # Este archivo
├── Proyecto/                    # Proyecto teórico del curso
│   ├── docs/                    # Entregables y documentación
│   │   └── Entregable 3 Proyecto_Paper.pdf  # Artículo científico completo
│   └── src/                     # Código fuente del Agente Virtual
│       └── AdultoMayorAgente/   # Proyecto Unity del agente virtual
├── Laboratorio/                 # Proyecto de laboratorio
│   ├── Proyecto2Lab/            # Evaluación de modelos (LLM, STT, TTS)
│   │   ├── LLMs/                # Pruebas de latencia - Modelos de lenguaje
│   │   ├── STT/                 # Pruebas de latencia - Speech-to-Text
│   │   └── TTS/                 # Pruebas de latencia - Text-to-Speech
│   └── ProyectoLab/             # Selección y preparación de avatares en Unity
└── Tareas/                      # Ejercicios y actividades del curso
```

---

## 🔧 Requisitos del Sistema

### Para el Proyecto Teórico (PoC en Unity)
- **Unity Hub**: Descargar desde [unity.com](https://unity.com/download)
- **Unity Editor**: Versión compatible (ver `ProjectSettings/ProjectVersion.txt`)
- **Sistema Operativo**: Windows, macOS o Linux
- **Especificaciones Mínimas**:
  - RAM: 4 GB
  - Espacio en disco: 5 GB
  - Procesador: Moderno (2020 en adelante recomendado)

### Credenciales Requeridas
- **Azure Speech Services**: Clave de API y región
- **Azure OpenAI**: Clave de API y endpoint
- Crear cuentas en [Azure Portal](https://portal.azure.com/)

### Para el Laboratorio (Evaluación de Modelos)
- **Python**: 3.8 o superior
- **pip**: Gestor de paquetes de Python
- Credenciales de APIs según el modelo a probar:
  - OpenAI API Key (para GPT)
  - Google API Key (para Gemini)
  - AssemblyAI API Key (para STT)
  - Deepgram API Key (para STT)
  - ElevenLabs API Key (para TTS)
  - Azure credenciales (para Azure Speech y OpenAI)

---

## 📦 Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/AgentesVirtuales.git
cd AgentesVirtuales
```

### 2. Para el Proyecto Teórico (Unity PoC)
```bash
# Navegar a la carpeta del proyecto
cd Proyecto/src/AdultoMayorAgente

# Abrir en Unity Hub
# 1. Abrir Unity Hub
# 2. Clic en "Add" → "Add project from disk"
# 3. Seleccionar la carpeta AdultoMayorAgente
# 4. Esperar a que se descarguen las dependencias
```

### 3. Para el Laboratorio (Evaluación de Modelos)
```bash
cd Laboratorio/Proyecto2Lab

# Instalar dependencias para LLMs
cd LLMs/Azure && pip install -r requirements.txt

# O para STT/TTS según lo que necesites
cd STT/AssemblyAI && pip install -r requirements.txt
cd TTS/ElevenLabs && pip install -r requirements.txt
```

---

## 🚀 Ejecución

### Ejecutar el PoC en Unity

1. **Abrir el Proyecto**
   - En Unity Hub, seleccionar el proyecto `AdultoMayorAgente`
   - Esperar a que se cargue completamente

2. **Configurar Credenciales de Azure**
   - En la jerarquía de Unity, buscar el GameObject `SpeechAgent`
   - En el Inspector, completar los campos:
     - `Speech Key`: Clave de Azure Speech Services
     - `Speech Region`: Región (ej. `centralus`)
     - `Azure Api Key`: Clave de Azure OpenAI
     - `Azure Endpoint`: URL del endpoint de Azure OpenAI

3. **Ejecutar**
   - Hacer clic en el botón **Play** (▶) en la barra de herramientas
   - El PoC se ejecutará en la ventana **Game** de Unity
   - Presionar **Stop** (◼) o `Ctrl+P` para detener

### Ejecutar Pruebas de Latencia

```bash
# Ejemplo: Probar latencia de Azure Speech Services (STT)
cd Laboratorio/Proyecto2Lab/STT/Azure
python test_latencia.py

# Ejemplo: Probar latencia de ElevenLabs (TTS)
cd Laboratorio/Proyecto2Lab/TTS/ElevenLabs
python test_latencia.py
```

---

## 🎬 Demostraciones en Video

### Entregable 2 - Demostración Inicial
https://youtu.be/4BFylup-Vu8 

### Entregable 3 - Demostración Final

**Escenario 1**: Interacción con avatar adulta formal
https://youtu.be/cm4ADQCP50k

**Escenario 2**: Interacción con avatar adulto mayor
https://youtu.be/lAB_iOGvM8M

---

## 📄 Documentación

- ** Artículo Científico Completo**: [Entregable 3 Proyecto_Paper.pdf](Proyecto/docs/Entregable%203%20Proyecto_Paper.pdf)
- **Proyecto Teórico**: Ver [Proyecto/README.md](Proyecto/README.md)
- **Laboratorio**: Ver [Laboratorio/README.md](Laboratorio/README.md)

---

## 🔍 Contenido de Carpetas

### `/Proyecto`
- Proyecto del curso teórico
- Propuesta de agente virtual para adultos mayores
- Código fuente del PoC en Unity
- Documentación y entregables

### `/Laboratorio`
- Proyecto del curso de laboratorio
- **Proyecto2Lab**: Evaluación y comparación de modelos
  - Pruebas de latencia para LLMs (Azure, Gemini, Ollama)
  - Pruebas de latencia para STT (AssemblyAI, Azure, Deepgram, Google, Whisper)
  - Pruebas de latencia para TTS (Azure, Cartesia, CoquiTTS, ElevenLabs, Google)
- **ProyectoLab**: Preparación de modelos 3D de avatares en Unity

### `/Tareas`
- Ejercicios y actividades prácticas del curso


