import time
import os
from datetime import datetime
import json
import wave
import threading
from dotenv import load_dotenv

# Intentar importar Azure Speech SDK
try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("Error: azure-cognitiveservices-speech no está instalado")
    print("Instala con: pip install azure-cognitiveservices-speech")
    exit(1)

load_dotenv()


class AzureSTTLatencyTester:
    """
    Prueba la latencia y costo del Speech-to-Text de Azure
    Configuración: Español (es-ES, es-MX, es-CR)
    """
    
    # Precios de Azure Speech-to-Text (USD por hora de audio)
    # Standard: $1.00/hora = $0.0167/minuto = $0.000278/segundo
    # Con compromiso: $0.74/hora
    PRICE_PER_HOUR_STANDARD = 1.00
    PRICE_PER_SECOND = 1.00 / 3600  # ~$0.000278 por segundo
    
    def __init__(self, speech_key: str = None, speech_region: str = None):
        """
        Inicializa el probador de STT de Azure
        
        Args:
            speech_key: API key de Azure Speech (opcional, se lee de .env)
            speech_region: Región de Azure (opcional, se lee de .env)
        """
        self.speech_key = speech_key or os.getenv("AZURE_SPEECH_KEY")
        self.speech_region = speech_region or os.getenv("AZURE_SPEECH_REGION")
        
        if not self.speech_key or not self.speech_region:
            raise ValueError("Se requiere AZURE_SPEECH_KEY y AZURE_SPEECH_REGION en el archivo .env")
        
        # Configurar Azure Speech
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key, 
            region=self.speech_region
        )
        # Configurar idioma español
        self.speech_config.speech_recognition_language = "es-MX"
        
        self.results = []
    
    def get_audio_duration(self, audio_file: str) -> float:
        """
        Obtiene la duración de un archivo de audio WAV en segundos
        
        Args:
            audio_file: Ruta al archivo de audio
            
        Returns:
            Duración en segundos
        """
        try:
            with wave.open(audio_file, 'rb') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception as e:
            print(f"Error leyendo duración del audio: {e}")
            return 0.0
    
    def calculate_cost(self, duration_seconds: float) -> float:
        """
        Calcula el costo de transcripción para un audio
        
        Args:
            duration_seconds: Duración del audio en segundos
            
        Returns:
            Costo en USD
        """
        cost = duration_seconds * self.PRICE_PER_SECOND
        return cost
    
    def transcribe_audio(self, audio_file: str) -> dict:
        """
        Transcribe un archivo de audio completo y mide la latencia
        Usa reconocimiento continuo para capturar todo el audio con pausas
        
        Args:
            audio_file: Ruta al archivo de audio
            
        Returns:
            Diccionario con resultados de latencia, transcripción y costo
        """
        if not os.path.exists(audio_file):
            return {
                "timestamp": datetime.now().isoformat(),
                "audio_file": audio_file,
                "duration_seconds": 0,
                "latency_ms": 0,
                "cost_usd": 0,
                "transcription": None,
                "status": "FAILED",
                "error": f"Archivo no encontrado: {audio_file}"
            }
        
        try:
            # Obtener duración del audio
            duration = self.get_audio_duration(audio_file)
            
            # Configurar entrada de audio
            audio_config = speechsdk.AudioConfig(filename=audio_file)
            
            # Crear reconocedor
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config, 
                audio_config=audio_config
            )
            
            # Variables para almacenar resultados del reconocimiento continuo
            transcriptions = []
            done = threading.Event()
            errors = []
            first_result_time = None
            
            def recognized_cb(evt):
                """Callback cuando se reconoce una frase completa"""
                nonlocal first_result_time
                if first_result_time is None:
                    first_result_time = time.time()
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    transcriptions.append(evt.result.text)
            
            def canceled_cb(evt):
                """Callback cuando se cancela el reconocimiento"""
                if evt.reason == speechsdk.CancellationReason.Error:
                    errors.append(f"Error: {evt.error_details}")
                done.set()
            
            def stopped_cb(evt):
                """Callback cuando termina el reconocimiento"""
                done.set()
            
            # Conectar callbacks
            speech_recognizer.recognized.connect(recognized_cb)
            speech_recognizer.canceled.connect(canceled_cb)
            speech_recognizer.session_stopped.connect(stopped_cb)
            
            # Medir tiempo de transcripción
            start_time = time.time()
            
            # Iniciar reconocimiento continuo
            speech_recognizer.start_continuous_recognition()
            
            # Esperar a que termine (con timeout basado en duración del audio + margen)
            timeout = max(duration * 2, 30)  # Al menos 30 segundos o 2x la duración
            done.wait(timeout=timeout)
            
            # Detener reconocimiento
            speech_recognizer.stop_continuous_recognition()
            
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            cost = self.calculate_cost(duration)
            
            # Combinar todas las transcripciones
            if transcriptions:
                full_transcription = " ".join(transcriptions)
                status = "SUCCESS"
                error = None
            elif errors:
                full_transcription = None
                status = "FAILED"
                error = "; ".join(errors)
            else:
                full_transcription = None
                status = "NO_MATCH"
                error = "No se reconoció ningún habla en el audio"
            
            result_dict = {
                "timestamp": datetime.now().isoformat(),
                "audio_file": os.path.basename(audio_file),
                "duration_seconds": round(duration, 2),
                "latency_ms": round(latency_ms, 2),
                "cost_usd": round(cost, 6),
                "transcription": full_transcription,
                "phrases_detected": len(transcriptions),
                "status": status,
                "error": error,
                "language": self.speech_config.speech_recognition_language
            }
            
            self.results.append(result_dict)
            return result_dict
            
        except Exception as e:
            result_dict = {
                "timestamp": datetime.now().isoformat(),
                "audio_file": os.path.basename(audio_file),
                "duration_seconds": 0,
                "latency_ms": 0,
                "cost_usd": 0,
                "transcription": None,
                "status": "FAILED",
                "error": str(e)
            }
            self.results.append(result_dict)
            return result_dict
    
    def test_audio_files(self, audio_files: list = None, iterations: int = 5) -> list:
        """
        Prueba transcripción con múltiples archivos de audio
        
        Args:
            audio_files: Lista de rutas a archivos de audio (opcional)
            iterations: Número de iteraciones para cada archivo (default: 5)
            
        Returns:
            Lista de resultados
        """
        # Si no se especifican archivos, buscar WAV en el directorio actual
        if audio_files is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            audio_files = [
                os.path.join(current_dir, f) 
                for f in os.listdir(current_dir) 
                if f.endswith('.wav')
            ]
            audio_files.sort()
        
        if not audio_files:
            print("No se encontraron archivos de audio WAV.")
            return []
        
        print("=" * 60)
        print("PRUEBAS DE LATENCIA - AZURE SPEECH-TO-TEXT")
        print("=" * 60)
        print(f"Idioma: {self.speech_config.speech_recognition_language}")
        print(f"Región: {self.speech_region}")
        print(f"Archivos a procesar: {len(audio_files)}")
        print(f"Iteraciones por archivo: {iterations}")
        print(f"Total de transcripciones: {len(audio_files) * iterations}")
        
        test_count = 0
        for iteration in range(1, iterations + 1):
            print(f"\n{'=' * 60}")
            print(f"ITERACIÓN {iteration} de {iterations}")
            print(f"{'=' * 60}")
            
            for i, audio_file in enumerate(audio_files, 1):
                test_count += 1
                print(f"\n[Prueba {test_count}] Iteración {iteration}, Archivo {i}/{len(audio_files)}: {os.path.basename(audio_file)}...")
                result = self.transcribe_audio(audio_file)
                self._print_result(result)
        
        return self.results
    
    def _print_result(self, result: dict):
        """Imprime un resultado formateado"""
        print(f"  Status: {result['status']}")
        if result['status'] == 'SUCCESS':
            print(f"  Duración audio: {result['duration_seconds']}s")
            print(f"  Latencia: {result['latency_ms']}ms")
            print(f"  Costo: ${result['cost_usd']:.6f}")
            print(f"  Frases detectadas: {result.get('phrases_detected', 1)}")
            print(f"  Transcripción: \"{result['transcription']}\"")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
    
    def generate_report(self, filename: str = "stt_latency_report.json"):
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
            costs = [r['cost_usd'] for r in successful_tests]
            durations = [r['duration_seconds'] for r in successful_tests]
            
            report = {
                "test_date": datetime.now().isoformat(),
                "provider": "Azure Speech-to-Text",
                "language": self.speech_config.speech_recognition_language,
                "region": self.speech_region,
                "total_tests": len(self.results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(self.results) - len(successful_tests),
                "test_iterations": len(self.results) // max(1, len(successful_tests) // len(successful_tests)) if successful_tests else 1,
                "statistics": {
                    "audio_duration_seconds": {
                        "min": round(min(durations), 2),
                        "max": round(max(durations), 2),
                        "total": round(sum(durations), 2)
                    },
                    "latency_ms": {
                        "min": round(min(latencies), 2),
                        "max": round(max(latencies), 2),
                        "avg": round(sum(latencies) / len(latencies), 2)
                    },
                    "cost_usd": {
                        "min": round(min(costs), 6),
                        "max": round(max(costs), 6),
                        "total": round(sum(costs), 6)
                    }
                },
                "pricing_info": {
                    "price_per_hour": self.PRICE_PER_HOUR_STANDARD,
                    "price_per_second": round(self.PRICE_PER_SECOND, 6)
                },
                "results": self.results
            }
        else:
            report = {
                "test_date": datetime.now().isoformat(),
                "provider": "Azure Speech-to-Text",
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
            costs = [r['cost_usd'] for r in successful]
            durations = [r['duration_seconds'] for r in successful]
            
            print("\n" + "=" * 60)
            print("RESUMEN DE RESULTADOS - AZURE SPEECH-TO-TEXT")
            print("=" * 60)
            print(f"Total de pruebas: {len(self.results)}")
            print(f"Pruebas exitosas: {len(successful)}")
            print(f"Pruebas fallidas: {len(self.results) - len(successful)}")
            print("\nDURACIÓN DE AUDIO:")
            print(f"  Total procesado: {sum(durations):.2f}s")
            print("\nLATENCIA:")
            print(f"  Mínima: {min(latencies):.2f}ms")
            print(f"  Máxima: {max(latencies):.2f}ms")
            print(f"  Promedio: {sum(latencies)/len(latencies):.2f}ms")
            print("\nCOSTO:")
            print(f"  Precio: $1.00/hora de audio")
            print(f"  Costo total: ${sum(costs):.6f}")
            print("=" * 60 + "\n")


def main():
    """Función principal"""
    
    # Verificar variables de entorno
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")
    
    if not speech_key:
        print("Error: AZURE_SPEECH_KEY no está configurada")
        print("\nConfigura en tu archivo .env:")
        print('  AZURE_SPEECH_KEY="tu-api-key-aqui"')
        print('  AZURE_SPEECH_REGION="eastus"')
        return
    
    if not speech_region:
        print("Error: AZURE_SPEECH_REGION no está configurada")
        print("\nConfigura en tu archivo .env:")
        print('  AZURE_SPEECH_REGION="eastus"')
        return
    
    try:
        # Crear probador
        tester = AzureSTTLatencyTester(speech_key, speech_region)
        
        # Ejecutar pruebas con los archivos de audio en la carpeta
        tester.test_audio_files()
        tester.print_summary()
        tester.generate_report()
        
    except Exception as e:
        print(f"Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
