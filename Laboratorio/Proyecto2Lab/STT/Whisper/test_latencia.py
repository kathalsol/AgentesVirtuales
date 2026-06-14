import time
import os
from datetime import datetime
import json
import wave

# Intentar importar Whisper
try:
    import whisper
except ImportError:
    print("Error: openai-whisper no está instalado")
    print("Instala con: pip install -U openai-whisper")
    print("\nTambién necesitas ffmpeg instalado:")
    print("  Windows (chocolatey): choco install ffmpeg")
    print("  Windows (scoop): scoop install ffmpeg")
    exit(1)


class WhisperSTTLatencyTester:
    """
    Prueba la latencia del Speech-to-Text de Whisper (modelo local)
    Configuración: Español
    Costo: GRATIS (ejecución local)
    """
    
    # Modelos disponibles de Whisper
    # tiny: ~39M parámetros, más rápido, menos preciso
    # base: ~74M parámetros
    # small: ~244M parámetros
    # medium: ~769M parámetros
    # large: ~1550M parámetros, más lento, más preciso
    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]
    
    def __init__(self, model_name: str = "base"):
        """
        Inicializa el probador de STT de Whisper
        
        Args:
            model_name: Nombre del modelo a usar (tiny, base, small, medium, large)
        """
        if model_name not in self.AVAILABLE_MODELS:
            print(f"Modelo '{model_name}' no válido. Usando 'base'.")
            model_name = "base"
        
        self.model_name = model_name
        self.model = None
        self.language = "es"  # Español
        self.results = []
        
        # Cargar modelo
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo de Whisper"""
        print(f"Cargando modelo Whisper '{self.model_name}'...")
        start_time = time.time()
        self.model = whisper.load_model(self.model_name)
        load_time = time.time() - start_time
        print(f"Modelo cargado en {load_time:.2f}s")
    
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
            # Si no es WAV, Whisper puede manejarlo con ffmpeg
            return 0.0
    
    def calculate_cost(self, duration_seconds: float) -> float:
        """
        Calcula el costo de transcripción para un audio
        Whisper es GRATIS (ejecución local)
        
        Args:
            duration_seconds: Duración del audio en segundos
            
        Returns:
            Costo en USD (siempre 0)
        """
        return 0.0
    
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
            
            # Medir tiempo de transcripción
            start_time = time.time()
            
            # Transcribir con Whisper
            result = self.model.transcribe(
                audio_file,
                language=self.language,
                fp16=False  # Usar fp32 para compatibilidad con CPU
            )
            
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            
            # Si no pudimos obtener la duración antes, usar la de Whisper
            if duration == 0 and "segments" in result and result["segments"]:
                last_segment = result["segments"][-1]
                duration = last_segment.get("end", 0)
            
            # Extraer transcripción
            full_transcription = result.get("text", "").strip()
            detected_language = result.get("language", self.language)
            
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
                "cost_usd": 0.0,
                "transcription": full_transcription,
                "detected_language": detected_language,
                "status": status,
                "error": error,
                "model": self.model_name,
                "is_local": True
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
                "error": str(e),
                "model": self.model_name,
                "is_local": True
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
                if f.endswith('.wav') or f.endswith('.mp3')
            ]
            audio_files.sort()
        
        if not audio_files:
            print("No se encontraron archivos de audio.")
            return []
        
        print("=" * 60)
        print("PRUEBAS DE LATENCIA - WHISPER STT (Local)")
        print("=" * 60)
        print(f"Modelo: {self.model_name}")
        print(f"Idioma: {self.language}")
        print(f"Costo: GRATIS (ejecución local)")
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
            print(f"  Costo: $0.00 (GRATIS)")
            print(f"  Idioma detectado: {result.get('detected_language', 'N/A')}")
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
            durations = [r['duration_seconds'] for r in successful_tests]
            
            report = {
                "test_date": datetime.now().isoformat(),
                "provider": "Whisper (Local)",
                "model": self.model_name,
                "language": self.language,
                "is_local": True,
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
                        "total": 0.0,
                        "note": "Whisper es gratuito (ejecución local)"
                    }
                },
                "results": self.results
            }
        else:
            report = {
                "test_date": datetime.now().isoformat(),
                "provider": "Whisper (Local)",
                "model": self.model_name,
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
            durations = [r['duration_seconds'] for r in successful]
            
            print("\n" + "=" * 60)
            print("RESUMEN DE RESULTADOS - WHISPER STT (Local)")
            print("=" * 60)
            print(f"Modelo: {self.model_name}")
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
            print(f"  Total: $0.00 (GRATIS - ejecución local)")
            print("=" * 60 + "\n")


def main():
    """Función principal"""
    
    # Modelo a usar (opciones: tiny, base, small, medium, large)
    # tiny/base son más rápidos pero menos precisos
    # medium/large son más precisos pero más lentos
    model_name = "base"  # Buen balance entre velocidad y precisión
    
    try:
        # Crear probador
        tester = WhisperSTTLatencyTester(model_name)
        
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
