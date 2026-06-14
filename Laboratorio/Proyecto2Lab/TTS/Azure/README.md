# Prueba de Latencia y Costo - Azure TTS

Script para medir la latencia y calcular el costo de la síntesis de voz (TTS) de Azure usando la voz neural `es-CR-JuanNeural`.

## Requisitos

- Python 3.7+
- Cuenta de Azure con Speech Services habilitado
- Clave de API y región de Azure

## Instalación

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

Configura tus credenciales de Azure como variables en un .env:
```cmd
AZURE_SPEECH_KEY="tu-clave-aqui"
AZURE_SPEECH_REGION="tu-region-aqui"
```