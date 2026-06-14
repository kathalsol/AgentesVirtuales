# Piper TTS - Pruebas de Latencia (Local)

Pruebas de latencia para el servicio de Text-to-Speech de Piper (modelo local, gratuito).

## ¿Qué es Piper?

[Piper](https://github.com/rhasspy/piper) es un sistema TTS local, rápido y de alta calidad que utiliza modelos ONNX. Es completamente gratuito y no requiere conexión a internet una vez descargado el modelo.

## Instalación

```bash
pip install piper-tts
```

## Uso

```bash
python test_latencia.py
```

El script descargará automáticamente el modelo en español la primera vez (~60MB).

## Modelos disponibles para español

| Modelo | Descripción |
|--------|-------------|
| es_ES-davefx-medium | Español de España (masculino) |
| es_ES-sharvard-medium | Español de España |
| es_MX-ald-medium | Español de México |

## Características

- **100% Local**: No requiere internet después de descargar el modelo
- **Gratuito**: Sin costos de API
- **Rápido**: Optimizado con ONNX para baja latencia
- **Privado**: Los datos no salen de tu máquina

## Costo

| Concepto | Precio |
|----------|--------|
| Por carácter | $0.00 |
| Por uso | $0.00 |
| Mensual | $0.00 |

**GRATIS** - Ejecución completamente local.

