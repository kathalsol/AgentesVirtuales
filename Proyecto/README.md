# Proyecto: Agentes virtuales como medio de comunicación para ayudar a combatir la soledad en adultos mayores

## Descripción General
Este proyecto propone el diseño de un **agente virtual de compañía con avatar**, cuyo objetivo es **reducir la soledad en adultos mayores** mediante conversaciones fluidas y actividades interactivas. Se fundamenta en una revisión de literatura sobre el impacto de la soledad en la salud y el potencial de las tecnologías como el uso de agentes virtuales inteligentes para mitigarla.

## Definición del Problema
- La soledad y el aislamiento social afectan negativamente la salud física, mental y emocional de los adultos mayores.  
- Las estrategias tradicionales de acompañamiento no siempre logran cubrir las necesidades de interacción cotidiana.  
- Se requiere explorar soluciones tecnológicas innovadoras que complementen el apoyo humano y promuevan el bienestar.  

## Estructura del proyecto

- `docs/`: carpeta para los documentos del proyecto, donde se subirán todos los entregables.
- `src/`: carpeta donde eventualmente estará el código necesario para la creación del agente virtual y los archivos de unity.

## Video de demostración Entregable 2

https://youtu.be/4BFylup-Vu8 

## Video de demostración Entregable 3

Video del escenario 1: https://youtu.be/cm4ADQCP50k

Video del escenario 2: https://youtu.be/lAB_iOGvM8M

## Instrucciones de Ejecución del PoC

### Requisitos Previos

- **Unity Hub**: Descargar desde [unity.com](https://unity.com/download)
- **Unity Editor**: Versión compatible (consultar `ProjectVersion.txt` en `src/AdultoMayorAgente/ProjectSettings/`)
- **Sistema Operativo**: Windows, macOS o Linux
- **Especificaciones Mínimas**:
  - 4GB de RAM
  - 5GB de espacio en disco
  - Procesador moderno

### Pasos para Ejecutar

1. **Descargar/Clonar el Proyecto**
   ```bash
   git clone <repository-url>
   cd Proyecto
   ```

2. **Abrir el Proyecto en Unity**
   - Abrir **Unity Hub**
   - Hacer clic en **"Add"** → **"Add project from disk"**
   - Navegar a `src/AdultoMayorAgente/` y seleccionar la carpeta
   - Unity descargará e instalará las dependencias automáticamente (esperar a que termine)

3. **Restaurar Dependencias (si es necesario)**
   - En Unity, ir a **Window** → **TextMesh Pro** → **Import TMP Essential Resources** (si aparece el diálogo)
   - Unity descargará e instalará automáticamente los paquetes especificados en `Packages/manifest.json`

4. **Abrir la Escena Principal**
   - En la ventana **Project**, navegar a `Assets/Scenes/`
   - Hacer doble clic en la escena principal (generalmente `Main.unity` o similar)

5. **Ejecutar el PoC**
   - Hacer clic en el botón **Play** (▶) en el centro de la barra de herramientas de Unity
   - El PoC se ejecutará en la ventana **Game** de Unity

6. **Detener la Ejecución**
   - Hacer clic en el botón **Stop** (◼) o presionar `Ctrl + P` para detener la ejecución

### Configuración del Speech Agent

Antes de ejecutar el PoC, es necesario configurar las credenciales de los servicios de Azure en el script `SpeechAgent` de Unity.

#### Acceder al Script SpeechAgent en Unity

1. En la ventana **Hierarchy** de Unity, localizar el GameObject que contiene el componente **SpeechAgent Script**
2. Seleccionar el GameObject (generalmente se llama `SpeechAgent` o similar)
3. En la ventana **Inspector** (lado derecho), ubicar el componente **Speech Agent (Script)**
4. Verá los siguientes campos que requieren configuración:

#### Configurar Credenciales de Azure

El componente **Speech Agent** requiere las credenciales de tres servicios de Azure:

**1. Azure Speech Services**
   - `Speech Key`: La clave de API de Azure Speech Services
   - `Speech Region`: La región donde se desplegó el servicio (ej. `centralus`, `eastus`, `westeurope`)
   - *Obtener credenciales*: Ir a [Azure Portal](https://portal.azure.com/) → Buscar "Speech Services" → Crear o seleccionar un recurso existente → Copiar la clave y región desde la pestaña "Keys and Endpoint"

**2. Azure OpenAI**
   - `Azure Api Key`: La clave de API de Azure OpenAI
   - *Obtener credenciales*: Ir a [Azure Portal](https://portal.azure.com/) → Buscar "Azure OpenAI" → Seleccionar el recurso → Copiar la clave desde la pestaña "Keys and Endpoint"

**3. Azure OpenAI Endpoint**
   - `Azure Endpoint`: La URL del endpoint de Azure OpenAI (ej. `https://iva-gpt.openai.azure.com/openai/deployments/adulto-mayor-gpt/chat/completions?api-version=2025-01-01-preview`)
   - *Obtener endpoint*: En Azure Portal → Azure OpenAI → Pestaña "Keys and Endpoint" → Copiar el endpoint

**Pasos para configurar:**
1. En el Inspector de Unity, en el componente **Speech Agent (Script)**, pegue cada credencial en su respectivo campo
2. Asegúrese de que:
   - El **Avatar Audio Source** esté asignado (debe apuntar a un AudioSource en la escena)
   - El **Conversation Text** esté asignado (debe apuntar a un componente de texto UI para mostrar la conversación)
3. Una vez configuradas todas las credenciales, el agente estará listo para funcionar

### Solución de Problemas

| Problema | Solución |
|----------|----------|
| Error de versión de Unity | Verificar `ProjectSettings/ProjectVersion.txt` e instalar la versión correcta |
| Paquetes no encontrados | Hacer clic en **Assets** → **Reimport All** para recargar los paquetes |
| Scripts con errores de compilación | Verificar que todos los paquetes de NuGet estén instalados correctamente |
| El proyecto no se abre | Eliminar la carpeta `Library/` y permitir que Unity la regenere |

