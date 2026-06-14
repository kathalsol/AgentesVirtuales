import time
import os
from datetime import datetime
import json
import wave
import struct
import tempfile

# Intentar importar piper
try:
    from piper import PiperVoice
except ImportError:
    print("Error: piper-tts no está instalado")
    print("Instala con: pip install piper-tts")
    exit(1)

# Intentar importar pydub para conversión a MP3
try:
    from pydub import AudioSegment
    # Verificar si ffmpeg está disponible
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        PYDUB_AVAILABLE = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        PYDUB_AVAILABLE = False
        print("Aviso: FFmpeg no está instalado. Los archivos se guardarán como WAV.")
        print("Para MP3, instala FFmpeg: winget install ffmpeg")
except ImportError:
    PYDUB_AVAILABLE = False
    print("Aviso: pydub no está instalado. Los archivos se guardarán como WAV.")
    print("Para MP3, instala: pip install pydub")


class PiperTTSLatencyTester:
    """
    Prueba la latencia del TTS de Piper (modelo local)
    Configuración: Modelo en español
    Costo: GRATIS (ejecución local)
    """
    
    # Modelos disponibles para español
    # Se descargan automáticamente de https://huggingface.co/rhasspy/piper-voices
    SPANISH_MODELS = {
        "es_ES-davefx-medium": "es_ES-davefx-medium",
        "es_ES-sharvard-medium": "es_ES-sharvard-medium",
        "es_MX-ald-medium": "es_MX-ald-medium",  # Español mexicano
    }
    
    def __init__(self, model_path: str = None):
        """
        Inicializa el probador de TTS de Piper
        
        Args:
            model_path: Ruta al archivo .onnx del modelo (opcional)
        """
        self.model_path = model_path
        self.voice = None
        self.model_name = "Piper Local"
        self.results = []
        self.sample_rate = 22050  # Sample rate por defecto de Piper
        
        if model_path and os.path.exists(model_path):
            self._load_model(model_path)
    
    def _load_model(self, model_path: str):
        """Carga el modelo de Piper"""
        try:
            self.voice = PiperVoice.load(model_path)
            self.model_name = os.path.basename(model_path).replace(".onnx", "")
            print(f"Modelo cargado: {self.model_name}")
        except Exception as e:
            print(f"Error cargando modelo: {e}")
            raise
    
    def download_model(self, model_name: str = "es_ES-davefx-medium") -> str:
        """
        Descarga un modelo de Piper desde Hugging Face
        
        Args:
            model_name: Nombre del modelo a descargar
            
        Returns:
            Ruta al modelo descargado
        """
        import urllib.request
        import os
        
        # Directorio para modelos
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(models_dir, exist_ok=True)
        
        # URLs de Hugging Face
        base_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/davefx/medium/"
        
        # Mapeo de modelos a sus URLs
        model_urls = {
            "es_ES-davefx-medium": {
                "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx",
                "json": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json"
            },
            "es_MX-ald-medium": {
                "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/ald/medium/es_MX-ald-medium.onnx",
                "json": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/ald/medium/es_MX-ald-medium.onnx.json"
            }
        }
        
        if model_name not in model_urls:
            print(f"Modelo {model_name} no encontrado. Usando es_ES-davefx-medium")
            model_name = "es_ES-davefx-medium"
        
        urls = model_urls[model_name]
        onnx_path = os.path.join(models_dir, f"{model_name}.onnx")
        json_path = os.path.join(models_dir, f"{model_name}.onnx.json")
        
        # Descargar si no existe
        if not os.path.exists(onnx_path):
            print(f"Descargando modelo {model_name}...")
            print(f"  Descargando archivo .onnx (~60MB)...")
            urllib.request.urlretrieve(urls["onnx"], onnx_path)
            print(f"  Descargando archivo .json...")
            urllib.request.urlretrieve(urls["json"], json_path)
            print(f"Modelo descargado en: {models_dir}")
        else:
            print(f"Modelo ya existe en: {onnx_path}")
        
        self.model_path = onnx_path
        self._load_model(onnx_path)
        return onnx_path
    
    def calculate_cost(self, text: str) -> float:
        """
        Calcula el costo de síntesis para un texto
        Piper es GRATIS (ejecución local)
        
        Args:
            text: Texto a sintetizar
            
        Returns:
            Costo en USD (siempre 0)
        """
        return 0.0
    
    def synthesize_text(self, text: str, save_audio: bool = True) -> dict:
        """
        Sintetiza un texto y mide la latencia
        
        Args:
            text: Texto a sintetizar
            save_audio: Si guardar el archivo de audio
            
        Returns:
            Diccionario con resultados de latencia y costo
        """
        if not self.voice:
            return {
                "timestamp": datetime.now().isoformat(),
                "text": text,
                "text_length": len(text),
                "latency_ms": 0,
                "cost_usd": 0,
                "audio_file": None,
                "status": "FAILED",
                "error": "Modelo no cargado. Usa download_model() primero.",
                "model_name": self.model_name
            }
        
        try:
            # Preparar archivo de salida
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            output_file = f"audio_output_{timestamp}.mp3" if save_audio and PYDUB_AVAILABLE else (f"audio_output_{timestamp}.wav" if save_audio else None)
            
            # Medir tiempo de síntesis
            start_time = time.time()
            
            # Sintetizar audio - synthesize devuelve un iterable de AudioChunk
            audio_chunks = []
            sample_rate = None
            sample_width = None
            sample_channels = None
            
            for chunk in self.voice.synthesize(text):
                audio_chunks.append(chunk.audio_int16_bytes)
                if sample_rate is None:
                    sample_rate = chunk.sample_rate
                    sample_width = chunk.sample_width
                    sample_channels = chunk.sample_channels
            
            # Combinar todos los chunks de audio
            audio_bytes = b''.join(audio_chunks)
            
            end_time = time.time()
            
            # Guardar audio si se solicita
            if save_audio and audio_bytes:
                # Crear archivo WAV temporal
                temp_wav_path = f"temp_{timestamp}.wav"
                
                # Escribir archivo WAV
                with wave.open(temp_wav_path, 'wb') as wav_file:
                    wav_file.setnchannels(sample_channels or 1)
                    wav_file.setsampwidth(sample_width or 2)
                    wav_file.setframerate(sample_rate or self.voice.config.sample_rate)
                    wav_file.writeframes(audio_bytes)
                
                # Convertir a MP3 si pydub está disponible
                if PYDUB_AVAILABLE:
                    audio = AudioSegment.from_wav(temp_wav_path)
                    audio.export(output_file, format="mp3", bitrate="192k")
                    os.remove(temp_wav_path)  # Eliminar WAV temporal
                else:
                    # Si no hay pydub, mantener como WAV
                    os.rename(temp_wav_path, output_file)
            
            latency_ms = (end_time - start_time) * 1000
            cost = self.calculate_cost(text)
            
            result_dict = {
                "timestamp": datetime.now().isoformat(),
                "text": text,
                "text_length": len(text),
                "latency_ms": round(latency_ms, 2),
                "cost_usd": cost,
                "audio_file": output_file,
                "status": "SUCCESS",
                "model_name": self.model_name,
                "is_local": True
            }
            
            self.results.append(result_dict)
            return result_dict
            
        except Exception as e:
            result_dict = {
                "timestamp": datetime.now().isoformat(),
                "text": text,
                "text_length": len(text),
                "latency_ms": 0,
                "cost_usd": 0,
                "audio_file": None,
                "status": "FAILED",
                "error": str(e),
                "model_name": self.model_name,
                "is_local": True
            }
            self.results.append(result_dict)
            return result_dict
    
    def test_various_lengths(self, iterations: int = 5) -> list:
        """
        Prueba síntesis con textos de diferentes longitudes
        
        Args:
            iterations: Número de iteraciones para cada texto (default: 5)
        
        Returns:
            Lista de resultados
        """
        test_texts = [
            # Corto
            "Hola, ¿cómo estás?",
            # Medio
            "Buenos días. Soy Juan, tu compañero virtual. ¿Cómo te sientes hoy? Me gustaría conversar contigo.",
            # Largo (simulando una respuesta completa)
            "¡Hola! Soy Juan, un compañero y asistente virtual costarricense especializado en acompañar personas adultas mayores. Mi misión principal es mitigar la soledad no deseada, estimular el bienestar cognitivo y promover el bienestar emocional. Estoy aquí para conversar, compartir historias y hacerte compañía."
        ]
        
        print("=" * 60)
        print("PRUEBAS DE LATENCIA - PIPER TTS (Local)")
        print("=" * 60)
        print(f"Modelo: {self.model_name}")
        print(f"Costo: GRATIS (ejecución local)")
        print(f"Iteraciones por texto: {iterations}")
        print(f"Total de síntesis: {len(test_texts) * iterations}")
        
        test_count = 0
        for iteration in range(1, iterations + 1):
            print(f"\n{'=' * 60}")
            print(f"ITERACIÓN {iteration} de {iterations}")
            print(f"{'=' * 60}")
            
            for i, text in enumerate(test_texts, 1):
                test_count += 1
                print(f"\n[Prueba {test_count}] Iteración {iteration}, Texto {i}/{len(test_texts)}: {len(text)} caracteres...")
                result = self.synthesize_text(text, save_audio=True)
                self._print_result(result)
        
        return self.results
    
    def _print_result(self, result: dict):
        """Imprime un resultado formateado"""
        print(f"  Status: {result['status']}")
        if result['status'] == 'SUCCESS':
            print(f"  Latencia: {result['latency_ms']}ms")
            print(f"  Costo: $0.00 (GRATIS)")
            if result['audio_file']:
                print(f"  Archivo: {result['audio_file']}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
    
    def generate_report(self, filename: str = "tts_latency_report.json"):
        """
        Genera un reporte con todos los resultados
        
        Args:
            filename: Nombre del archivo de reporte
        """
        if not self.results:
            print("No hay resultados para reportar.")
            return
        
        # Calcular estadísticas
        successful_tests = [r for r in self.results if r['status'] == 'SUCCESS']
        
        if successful_tests:
            latencies = [r['latency_ms'] for r in successful_tests]
            
            report = {
                "test_date": datetime.now().isoformat(),
                "provider": "Piper (Local)",
                "model_name": self.model_name,
                "is_local": True,
                "total_tests": len(self.results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(self.results) - len(successful_tests),
                "statistics": {
                    "latency_ms": {
                        "min": round(min(latencies), 2),
                        "max": round(max(latencies), 2),
                        "avg": round(sum(latencies) / len(latencies), 2)
                    },
                    "cost_usd": {
                        "total": 0.0,
                        "note": "Piper es gratuito (ejecución local)"
                    }
                },
                "results": self.results
            }
        else:
            report = {
                "test_date": datetime.now().isoformat(),
                "provider": "Piper (Local)",
                "model_name": self.model_name,
                "total_tests": len(self.results),
                "successful_tests": 0,
                "failed_tests": len(self.results),
                "results": self.results
            }
        
        # Guardar reporte
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nReporte guardado en: {filename}")
        return report
    
    def print_summary(self):
        """Imprime un resumen de los resultados"""
        if not self.results:
            print("No hay resultados.")
            return
        
        successful = [r for r in self.results if r['status'] == 'SUCCESS']
        
        if successful:
            latencies = [r['latency_ms'] for r in successful]
            
            print("\n" + "=" * 60)
            print("RESUMEN DE RESULTADOS - PIPER TTS (Local)")
            print("=" * 60)
            print(f"Total de pruebas: {len(self.results)}")
            print(f"Pruebas exitosas: {len(successful)}")
            print(f"Pruebas fallidas: {len(self.results) - len(successful)}")
            print("\nLATENCIA:")
            print(f"  Mínima: {min(latencies):.2f}ms")
            print(f"  Máxima: {max(latencies):.2f}ms")
            print(f"  Promedio: {sum(latencies)/len(latencies):.2f}ms")
            print("\nCOSTO:")
            print(f"  Total: $0.00 (GRATIS - ejecución local)")
            print("=" * 60 + "\n")


def main():
    """Función principal"""
    
    try:
        # Crear probador
        tester = PiperTTSLatencyTester()
        
        # Descargar modelo en español (si no existe)
        # Opciones: "es_ES-davefx-medium", "es_MX-ald-medium"
        print("Verificando modelo de voz...")
        tester.download_model("es_ES-davefx-medium")
        
        print()
        
        # Ejecutar pruebas
        tester.test_various_lengths()
        tester.print_summary()
        tester.generate_report()
        
    except Exception as e:
        print(f"Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
