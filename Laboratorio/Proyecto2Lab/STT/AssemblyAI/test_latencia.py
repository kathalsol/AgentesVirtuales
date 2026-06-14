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


class AssemblyAISTTLatencyTester:
    """
    Prueba la latencia y costo del Speech-to-Text de AssemblyAI
    Configuración: Español (es)
    """
    
    # Precios de AssemblyAI (USD por segundo de audio)
    # Best: $0.00025/segundo = $0.015/minuto
    # Nano: $0.00009/segundo = $0.0054/minuto
    PRICE_PER_SECOND_BEST = 0.00025
    PRICE_PER_SECOND_NANO = 0.00009
    PRICE_PER_MINUTE_BEST = 0.015
    
    # URLs de la API de AssemblyAI
    UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
    TRANSCRIPT_URL = "https://api.assemblyai.com/v2/transcript"
    
    def __init__(self, api_key: str = None):
        """
        Inicializa el probador de STT de AssemblyAI
        
        Args:
            api_key: API key de AssemblyAI (opcional, se lee de .env)
        """
        self.api_key = api_key or os.getenv("ASSEMBLY_AI_API_KEY")
        
        if not self.api_key:
            raise ValueError("Se requiere ASSEMBLY_AI_API_KEY en el archivo .env")
        
        self.headers = {
            "authorization": self.api_key,
            "content-type": "application/json"
        }
        self.language_code = "es"  # Español
        self.speech_model = "best"  # Opciones: best, nano
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
    
    def calculate_cost(self, duration_seconds: float, model: str = "best") -> float:
        """
        Calcula el costo de transcripción para un audio
        
        Args:
            duration_seconds: Duración del audio en segundos
            model: Modelo a usar ("best" o "nano")
            
        Returns:
            Costo en USD
        """
        if model == "nano":
            price_per_second = self.PRICE_PER_SECOND_NANO
        else:
            price_per_second = self.PRICE_PER_SECOND_BEST
        
        cost = duration_seconds * price_per_second
        return cost
    
    def upload_audio(self, audio_file: str) -> str:
        """
        Sube un archivo de audio a AssemblyAI
        
        Args:
            audio_file: Ruta al archivo de audio
            
        Returns:
            URL del audio subido
        """
        headers = {
            "authorization": self.api_key
        }
        
        with open(audio_file, 'rb') as f:
            response = requests.post(
                self.UPLOAD_URL,
                headers=headers,
                data=f,
                verify=False
            )
        
        if response.status_code != 200:
            raise Exception(f"Error subiendo audio: {response.status_code} - {response.text}")
        
        return response.json()["upload_url"]
    
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
            # Obtener duración del audio
            duration = self.get_audio_duration(audio_file)
            
            # Medir tiempo total (incluyendo upload)
            start_time = time.time()
            
            # Paso 1: Subir el audio a AssemblyAI
            audio_url = self.upload_audio(audio_file)
            
            # Paso 2: Crear solicitud de transcripción
            transcript_request = {
                "audio_url": audio_url,
                "language_code": self.language_code,
                "punctuate": True,
                "format_text": True
            }
            
            response = requests.post(
                self.TRANSCRIPT_URL,
                headers=self.headers,
                json=transcript_request,
                verify=False
            )
            
            if response.status_code != 200:
                raise Exception(f"Error creando transcripción: {response.status_code} - {response.text}")
            
            transcript_id = response.json()["id"]
            
            # Paso 3: Esperar a que termine la transcripción
            polling_url = f"{self.TRANSCRIPT_URL}/{transcript_id}"
            
            while True:
                response = requests.get(polling_url, headers=self.headers, verify=False)
                result = response.json()
                status = result["status"]
                
                if status == "completed":
                    break
                elif status == "error":
                    raise Exception(f"Error en transcripción: {result.get('error', 'Unknown error')}")
                
                # Esperar antes de volver a consultar
                time.sleep(0.5)
            
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            cost = self.calculate_cost(duration, self.speech_model)
            
            # Extraer transcripción
            full_transcription = result.get("text", "")
            confidence = result.get("confidence", 0)
            
            if full_transcription:
                status = "SUCCESS"
                error = None
            else:
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
                "model": self.speech_model
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
        print("PRUEBAS DE LATENCIA - ASSEMBLYAI SPEECH-TO-TEXT")
        print("=" * 60)
        print(f"Idioma: {self.language_code}")
        print(f"Modelo: {self.speech_model}")
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
                "provider": "AssemblyAI Speech-to-Text",
                "language": self.language_code,
                "model": self.speech_model,
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
                    "price_per_minute_best": self.PRICE_PER_MINUTE_BEST,
                    "price_per_second_best": self.PRICE_PER_SECOND_BEST,
                    "price_per_second_nano": self.PRICE_PER_SECOND_NANO
                },
                "results": self.results
            }
        else:
            report = {
                "test_date": datetime.now().isoformat(),
                "provider": "AssemblyAI Speech-to-Text",
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
            print("RESUMEN DE RESULTADOS - ASSEMBLYAI STT")
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
            print(f"  Precio: $0.015/minuto (Best)")
            print(f"  Costo total: ${sum(costs):.6f}")
            print("=" * 60 + "\n")


def main():
    """Función principal"""
    
    # Verificar variables de entorno
    api_key = os.getenv("ASSEMBLY_AI_API_KEY")
    
    if not api_key:
        print("Error: ASSEMBLY_AI_API_KEY no está configurada")
        print("\nConfigura en tu archivo .env:")
        print('  ASSEMBLY_AI_API_KEY="tu-api-key-aqui"')
        print("\nPuedes obtener tu API key en: https://www.assemblyai.com/")
        return
    
    try:
        # Crear probador
        tester = AssemblyAISTTLatencyTester(api_key)
        
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
