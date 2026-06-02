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

## Video de demostración

https://youtu.be/4BFylup-Vu8 

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

### Solución de Problemas

| Problema | Solución |
|----------|----------|
| Error de versión de Unity | Verificar `ProjectSettings/ProjectVersion.txt` e instalar la versión correcta |
| Paquetes no encontrados | Hacer clic en **Assets** → **Reimport All** para recargar los paquetes |
| Scripts con errores de compilación | Verificar que todos los paquetes de NuGet estén instalados correctamente |
| El proyecto no se abre | Eliminar la carpeta `Library/` y permitir que Unity la regenere |

