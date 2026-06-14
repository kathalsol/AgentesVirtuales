import requests
import time
import os
from datetime import datetime
import json
import wave
import urllib3
from dotenv import load_dotenv

# Desactivar advertencias de SSL para entornos de prueba
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()


class DeepgramSTTLatencyTester:
    """
    Prueba la latencia y costo del Speech-to-Text de Deepgram
    Configuración: Español (es, es-419)
    """
    
    # Precios de Deepgram (USD por minuto de audio)
    # Pay-as-you-go: $0.0043/minuto (Nova-2)
    # Growth: $0.0036/minuto
    PRICE_PER_MINUTE_NOVA2 = 0.0043
    PRICE_PER_MINUTE_ENHANCED = 0.0048
    PRICE_PER_SECOND = 0.0043 / 60  # ~$0.0000717 por segundo
    
    # URL de la API REST de Deepgram
    STT_API_URL = "https://api.deepgram.com/v1/listen"
    
    def __init__(self, api_key: str = None):
        """
        Inicializa el probador de STT de Deepgram
        
        Args:
            api_key: API key de Deepgram (opcional, se lee de .env si no se provee)
        """
        self.api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere DEEPGRAM_API_KEY en el archivo .env")
        self.results = []
        self.language_code = "es"  # Español
        self.model = "nova-2"  # Modelo más reciente y preciso
    
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
    
    def get_audio_info(self, audio_file: str) -> dict:
        """
        Obtiene información del archivo de audio WAV
        
        Args:
            audio_file: Ruta al archivo de audio
            
        Returns:
            Diccionario con info del audio
        """
        try:
            with wave.open(audio_file, 'rb') as wav:
                return {
                    "channels": wav.getnchannels(),
                    "sample_width": wav.getsampwidth(),
                    "sample_rate": wav.getframerate(),
                    "frames": wav.getnframes(),
                    "duration": wav.getnframes() / float(wav.getframerate())
                }
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_cost(self, duration_seconds: float, model: str = "nova-2") -> float:
        """
        Calcula el costo de transcripción para un audio
        
        Args:
            duration_seconds: Duración del audio en segundos
            model: Modelo a usar ("nova-2" o "enhanced")
            
        Returns:
            Costo en USD
        """
        if model == "enhanced":
            price_per_second = self.PRICE_PER_MINUTE_ENHANCED / 60
        else:
            price_per_second = self.PRICE_PER_SECOND
        
        cost = duration_seconds * price_per_second
        return cost
    
    def transcribe_audio(self, audio_file: str) -> dict:
        """
        Transcribe un archivo de audio y mide la latencia
        
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
            # Obtener información del audio
            audio_info = self.get_audio_info(audio_file)
            duration = audio_info.get("duration", 0)
            
            # Leer el audio como bytes
            with open(audio_file, 'rb') as f:
                audio_content = f.read()
            
            # Parámetros de la API de Deepgram
            params = {
                "model": self.model,
                "language": self.language_code,
                "punctuate": "true",
                "smart_format": "true"
            }
            
            # Headers con autenticación
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/wav"
            }
            
            # Medir tiempo de transcripción
            start_time = time.time()
            response = requests.post(
                self.STT_API_URL,
                params=params,
                headers=headers,
                data=audio_content,
                verify=False  # Desactivar verificación SSL para entornos con proxy/firewall
            )
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            cost = self.calculate_cost(duration)
            
            # Verificar respuesta
            if response.status_code != 200:
                error_msg = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get("err_msg", response.text)
                except:
                    pass
                raise Exception(f"Error API: {response.status_code} - {error_msg}")
            
            response_data = response.json()
            
            # Extraer transcripción de la respuesta de Deepgram
            results = response_data.get("results", {})
            channels = results.get("channels", [])
            
            if channels:
                alternatives = channels[0].get("alternatives", [])
                if alternatives:
                    full_transcription = alternatives[0].get("transcript", "")
                    confidence = alternatives[0].get("confidence", 0)
                    status = "SUCCESS" if full_transcription else "NO_MATCH"
                    error = None if full_transcription else "No se reconoció ningún habla"
                else:
                    full_transcription = None
                    confidence = 0
                    status = "NO_MATCH"
                    error = "No se encontraron alternativas"
            else:
                full_transcription = None
                confidence = 0
                status = "NO_MATCH"
                error = "No se reconoció ningún habla en el audio"
            
            result_dict = {
                "timestamp": datetime.now().isoformat(),
                "audio_file": os.path.basename(audio_file),
                "duration_seconds": round(duration, 2),
                "latency_ms": round(latency_ms, 2),
                "cost_usd": round(cost, 6),
                "transcription": full_transcription,
                "confidence": round(confidence, 4) if confidence else 0,
                "status": status,
                "error": error,
                "language": self.language_code,
                "model": self.model
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
        print("PRUEBAS DE LATENCIA - DEEPGRAM SPEECH-TO-TEXT")
        print("=" * 60)
        print(f"Idioma: {self.language_code}")
        print(f"Modelo: {self.model}")
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
        print(f"  Duración audio: {result.get('duration_seconds', 0)}s")
        if result['status'] == 'SUCCESS':
            print(f"  Latencia: {result['latency_ms']}ms")
            print(f"  Costo: ${result['cost_usd']:.6f}")
            print(f"  Confianza: {result.get('confidence', 0):.2%}")
            print(f"  Transcripción: \"{result['transcription']}\"")
        else:
            print(f"  Latencia: {result.get('latency_ms', 0)}ms")
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
                "provider": "Deepgram Speech-to-Text",
                "language": self.language_code,
                "model": self.model,
                "total_tests": len(self.results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(self.results) - len(successful_tests),
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
                    "price_per_minute_nova2": self.PRICE_PER_MINUTE_NOVA2,
                    "price_per_minute_enhanced": self.PRICE_PER_MINUTE_ENHANCED,
                    "note": "Pay-as-you-go, sin minutos gratis"
                },
                "results": self.results
            }
        else:
            report = {
                "test_date": datetime.now().isoformat(),
                "provider": "Deepgram Speech-to-Text",
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
            print("RESUMEN DE RESULTADOS - DEEPGRAM STT")
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
            print(f"  Precio: $0.0043/minuto (Nova-2)")
            print(f"  Costo total: ${sum(costs):.6f}")
            print("=" * 60 + "\n")


def main():
    """Función principal"""
    
    # Obtener API key
    api_key = os.getenv("DEEPGRAM_API_KEY")
    
    if not api_key:
        print("Error: DEEPGRAM_API_KEY no está configurada")
        print("\nConfigura en tu archivo .env:")
        print('  DEEPGRAM_API_KEY="tu-api-key-aqui"')
        print("\nPuedes obtener tu API key en: https://console.deepgram.com/")
        return
    
    try:
        # Crear probador
        tester = DeepgramSTTLatencyTester(api_key)
        
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
