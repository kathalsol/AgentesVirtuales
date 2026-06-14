# Prueba de Latencia y Costo - Google Cloud TTS

Script para medir la latencia y calcular el costo de la síntesis de voz (TTS) de Google Cloud usando Neural2 voices.

## Características

- ✅ Síntesis de texto a voz usando Google Cloud Text-to-Speech
- ⏱️ Medición de latencia en milisegundos
- 💰 Cálculo automático del costo (Neural2: $16.00 USD por 1M de caracteres)
- 📊 Pruebas con textos de diferentes longitudes
- 📁 Generación de reporte JSON con resultados completos
- 🔊 Descarga de archivos de audio en WAV/LINEAR16
- 🌐 Soporte para múltiples idiomas

## Requisitos

- Python 3.7+
- Cuenta de Google Cloud con Text-to-Speech API habilitada
- Archivo JSON de credenciales de Google Cloud

## Instalación

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

### 1. Obtener credenciales de Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Text-to-Speech:
   - Ve a "APIs y servicios" → "Biblioteca"
   - Busca "Text-to-Speech"
   - Haz clic en "Habilitar"
4. Crea una cuenta de servicio:
   - Ve a "Credenciales"
   - Haz clic en "Crear credenciales" → "Cuenta de servicio"
   - Completa los detalles y haz clic en "Crear"
5. Genera una clave JSON:
   - En la página de la cuenta de servicio, ve a "Claves"
   - Haz clic en "Agregar clave" → "Crear nueva clave" → "JSON"
   - Se descargará un archivo JSON

### 2. Configurar variables de entorno

1. Copia el archivo `.env.example` a `.env`:
```bash
cp .env.example .env
```

2. Edita `.env` y actualiza la ruta a tu archivo JSON:
```
GOOGLE_APPLICATION_CREDENTIALS="C:/ruta/a/tu/credenciales.json"
```

## Uso

Ejecuta el script:
```bash
python test_latencia.py
```

### Ejemplo de uso personalizado

```python
from test_latencia import GoogleTTSLatencyTester

# Crear instancia
tester = GoogleTTSLatencyTester(credentials_path="ruta/a/credenciales.json")

# Sintetizar un texto
resultado = tester.synthesize_text("Hola, ¿cómo estás?")
print(f"Latencia: {resultado['latency_ms']}ms")
print(f"Costo: ${resultado['cost_usd']:.6f}")

# Generar reporte
tester.generate_report("mi_reporte.json")
```

## Salida

El script genera:

1. **Resumen en consola**: Muestra min/max/promedio de latencia y costo
2. **Archivos de audio**: `audio_output_TIMESTAMP.wav` (uno por prueba)
3. **Reporte JSON**: `tts_latency_report.json` con todos los detalles

### Ejemplo de reporte JSON

```json
{
  "test_date": "2026-06-13T10:30:45.123456",
  "provider": "Google Cloud",
  "voice_type": "Neural2",
  "total_tests": 3,
  "successful_tests": 3,
  "failed_tests": 0,
  "statistics": {
    "latency_ms": {
      "min": 150.25,
      "max": 520.18,
      "avg": 336.87
    },
    "cost_usd": {
      "min": 0.000288,
      "max": 0.001248,
      "total": 0.001840
    }
  },
  "results": [...]
}
```

## Precios de Google Cloud TTS

| Tipo | Precio (USD/1M caracteres) |
|------|---------------------------|
| Standard | $4.00 |
| Neural2 | $16.00 |
| Neural2-Premium | $24.00 |

*El script usa Neural2 por defecto (es-US-Neural2-A)*

## Voces disponibles

El script usa `es-US-Neural2-A` (voz neural en español). Para cambiar la voz, modifica en el código:

```python
self.voice_name = "es-US-Neural2-A"  # Cambiar aquí
```

Otras voces disponibles para español:
- `es-US-Neural2-B`
- `es-US-Neural2-C`
- `es-MX-Neural2-A` (Español mexicano)
- `es-MX-Neural2-C`
- Y más según disponibilidad

Consulta la [documentación de Google](https://cloud.google.com/text-to-speech/docs/voices) para la lista completa.

## Solución de problemas

### Error: GOOGLE_APPLICATION_CREDENTIALS no está configurada
- Verifica que hayas creado el archivo `.env`
- Confirma que la ruta sea correcta
- Reinicia el terminal después de crear `.env`

### Error: No se encontró el archivo de credenciales
- Verifica la ruta en `.env`
- Asegúrate de que el archivo JSON exista
- Usa rutas absolutas en lugar de relativas

### Error: Permission denied (Permisos insuficientes)
- Verifica que la cuenta de servicio tenga los permisos necesarios
- En Google Cloud Console, ve a IAM y asigna el rol "Editor de Text-to-Speech"

### Latencia muy alta (>1000ms)
- Puede deberse a latencia de red
- La primera solicitud puede ser más lenta (calentamiento)
- Ejecuta múltiples pruebas para obtener un promedio

### Error: API no habilitada
- Ve a Google Cloud Console
- Habilita la API de Text-to-Speech
- Espera unos minutos a que se propague

## Comparación con Azure TTS

| Aspecto | Google Cloud | Azure |
|--------|--------------|-------|
| Voz en es-CR | No disponible | ✅ es-CR-JuanNeural |
| Precio Neural | $16.00 / 1M chars | $24.00 / 1M chars |
| Latencia típica | 150-500ms | Similar |
| Calidad | Excelente | Excelente |

## Notas

- Los archivos de audio se guardan en el directorio actual
- El reporte JSON incluye marca de tiempo para cada prueba
- La latencia incluye: request, síntesis y descarga
- Google tiene cuota gratuita de 4 millones de caracteres/mes

## Licencia

Proyecto del Máster en Agentes Virtuales - UCR 2026
