# ElevenLabs TTS - Pruebas de Latencia

Pruebas de latencia y costo para el servicio de Text-to-Speech de ElevenLabs.

## Configuración

1. Crea una cuenta en [ElevenLabs](https://elevenlabs.io/)
2. Obtén tu API key desde el dashboard
3. Crea un archivo `.env` en este directorio:

```env
ELEVENLABS_API_KEY="tu-api-key-aqui"
```

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python test_latencia.py
```

## Modelo y Voz

- **Modelo**: `eleven_multilingual_v2` (soporta español)
- **Voz por defecto**: Antoni (masculina)

## Voces disponibles predefinidas

| Nombre | Voice ID | Descripción |
|--------|----------|-------------|
| Antoni | ErXwobaYiN019PkySvjV | Voz masculina |
| Arnold | VR6AewLTigWG4xSOukaG | Voz masculina profunda |
| Bella | EXAVITQu4vr4xnSDxMaL | Voz femenina |
| Rachel | 21m00Tcm4TlvDq8ikWAM | Voz femenina clara |
| Adam | pNInz6obpgDQGcFmaJgB | Voz masculina |

## Precios (aproximados)

| Plan | Precio/mes | Caracteres | Costo/carácter |
|------|------------|------------|----------------|
| Starter | $5 | 30,000 | $0.000167 |
| Creator | $22 | 100,000 | $0.00022 |
| Pro | $99 | 500,000 | $0.000198 |
| Scale | $330 | 2,000,000 | $0.000165 |

## Resultados

Los resultados se guardan en:
- `tts_latency_report.json`: Reporte completo con estadísticas
- `audio_output_*.mp3`: Archivos de audio generados
