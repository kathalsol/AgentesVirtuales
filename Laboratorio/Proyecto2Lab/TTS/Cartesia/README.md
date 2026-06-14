# Cartesia TTS - Pruebas de Latencia

Pruebas de latencia y costo para el servicio de Text-to-Speech de Cartesia.

## Configuración

1. Crea una cuenta en [Cartesia](https://play.cartesia.ai/)
2. Obtén tu API key desde el dashboard
3. Crea un archivo `.env` en este directorio:

```env
CARTESIA_API_KEY="tu-api-key-aqui"
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

- **Modelo**: `sonic-2` (modelo más reciente y rápido)
- **Voz**: `5ee9feff-1265-424a-9d7f-8e4d431a12c7` (voz en español)

## Características de Cartesia

- **Baja latencia**: Optimizado para aplicaciones en tiempo real
- **Streaming**: Soporta streaming de audio
- **Multilingüe**: Soporta múltiples idiomas incluyendo español

## Precios (aproximados)

| Plan | Costo/carácter |
|------|----------------|
| Starter | $0.000050 |
| Growth | $0.000040 |
| Enterprise | Personalizado |

## Resultados

Los resultados se guardan en:
- `tts_latency_report.json`: Reporte completo con estadísticas
- `audio_output_*.wav`: Archivos de audio generados
