from google.cloud import texttospeech
import time
import os
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

class GoogleTTSLatencyTester:
    """
    Prueba la latencia y costo del TTS de Google Cloud
    Configuración: Neural2 voice es-US (Spanish - United States)
    """
    
    # Precios de Google Cloud TTS Neural2 (USD por 1 millón de caracteres)
    # Neural2: $16.00, Neural2 Premium: $24.00
    NEURAL2_PRICE_PER_MILLION_CHARS = 16.00
    NEURAL2_PREMIUM_PRICE_PER_MILLION_CHARS = 24.00
    
    def __init__(self, credentials_path: str = None):
        """
        Inicializa el probador de TTS de Google
        
        Args:
            credentials_path: Ruta al archivo JSON de credenciales de Google.
                            Si no se proporciona, busca en GOOGLE_APPLICATION_CREDENTIALS
        """
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        elif not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            raise ValueError(
                "No se encontró GOOGLE_APPLICATION_CREDENTIALS. "
                "Proporciona el parámetro credentials_path o configura la variable de entorno."
            )
        
        self.client = texttospeech.TextToSpeechClient()
        self.results = []
        self.voice_name = "es-US-Neural2-A"  # Voz en español
        self.voice_type = "Neural2"
    
    def calculate_cost(self, text: str, voice_type: str = "Neural2") -> float:
        """
        Calcula el costo de síntesis para un texto
        
        Args:
            text: Texto a sintetizar
            voice_type: Tipo de voz ("Neural2" o "Neural2-Premium")
            
        Returns:
            Costo en USD
        """
        char_count = len(text)
        
        if voice_type == "Neural2-Premium":
            price = self.NEURAL2_PREMIUM_PRICE_PER_MILLION_CHARS
        else:
            price = self.NEURAL2_PRICE_PER_MILLION_CHARS
        
        cost = (char_count / 1_000_000) * price
        return cost
    
    def synthesize_text(self, text: str, save_audio: bool = True) -> dict:
        """
        Sintetiza un texto y mide la latencia
        
        Args:
            text: Texto a sintetizar
            save_audio: Si guardar el archivo de audio
            
        Returns:
            Diccionario con resultados de latencia y costo
        """
        try:
            # Preparar solicitud
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code="es-US",
                name=self.voice_name
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                speaking_rate=1.0,
                pitch=0.0
            )
            
            # Medir tiempo de síntesis
            start_time = time.time()
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            cost = self.calculate_cost(text, self.voice_type)
            
            # Guardar audio si se solicita
            output_file = None
            if save_audio and response.audio_content:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                output_file = f"audio_output_{timestamp}.wav"
                with open(output_file, 'wb') as out:
                    out.write(response.audio_content)
            
            result_dict = {
                "timestamp": datetime.now().isoformat(),
                "text": text,
                "text_length": len(text),
                "latency_ms": round(latency_ms, 2),
                "cost_usd": round(cost, 6),
                "audio_file": output_file if save_audio else None,
                "status": "SUCCESS",
                "voice_name": self.voice_name,
                "voice_type": self.voice_type
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
                "voice_name": self.voice_name,
                "voice_type": self.voice_type
            }
            self.results.append(result_dict)
            return result_dict
    
    def test_various_lengths(self) -> list:
        """
        Prueba síntesis con textos de diferentes longitudes
        
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
        print("PRUEBAS DE LATENCIA - GOOGLE CLOUD TTS (Neural2)")
        print("=" * 60)
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n[Prueba {i}] Sintetizando texto de {len(text)} caracteres...")
            result = self.synthesize_text(text, save_audio=True)
            self._print_result(result)
        
        return self.results
    
    def _print_result(self, result: dict):
        """Imprime un resultado formateado"""
        print(f"  Status: {result['status']}")
        if result['status'] == 'SUCCESS':
            print(f"  Latencia: {result['latency_ms']}ms")
            print(f"  Costo: ${result['cost_usd']:.6f}")
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
            costs = [r['cost_usd'] for r in successful_tests]
            
            report = {
                "test_date": datetime.now().isoformat(),
                "provider": "Google Cloud",
                "voice_type": self.voice_type,
                "voice_name": self.voice_name,
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
                        "min": round(min(costs), 6),
                        "max": round(max(costs), 6),
                        "total": round(sum(costs), 6)
                    }
                },
                "results": self.results
            }
        else:
            report = {
                "test_date": datetime.now().isoformat(),
                "provider": "Google Cloud",
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
            
            print("\n" + "=" * 60)
            print("RESUMEN DE RESULTADOS - GOOGLE CLOUD TTS")
            print("=" * 60)
            print(f"Total de pruebas: {len(self.results)}")
            print(f"Pruebas exitosas: {len(successful)}")
            print(f"Pruebas fallidas: {len(self.results) - len(successful)}")
            print("\nLATENCIA:")
            print(f"  Mínima: {min(latencies):.2f}ms")
            print(f"  Máxima: {max(latencies):.2f}ms")
            print(f"  Promedio: {sum(latencies)/len(latencies):.2f}ms")
            print("\nCOSTO:")
            print(f"  Costo mínimo: ${min(costs):.6f}")
            print(f"  Costo máximo: ${max(costs):.6f}")
            print(f"  Costo total: ${sum(costs):.6f}")
            print("=" * 60 + "\n")


def main():
    """Función principal"""
    
    # Obtener ruta de credenciales
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not credentials_path:
        print("Error: GOOGLE_APPLICATION_CREDENTIALS no está configurada")
        print("\nConfigura en tu archivo .env:")
        print('  GOOGLE_APPLICATION_CREDENTIALS="/ruta/al/archivo/credenciales.json"')
        print("\nO configura la variable de entorno directamente:")
        print('  set GOOGLE_APPLICATION_CREDENTIALS="C:\\ruta\\credenciales.json"')
        return
    
    # Verificar que el archivo exista
    if not os.path.exists(credentials_path):
        print(f"Error: No se encontró el archivo de credenciales en: {credentials_path}")
        return
    
    try:
        # Crear probador
        tester = GoogleTTSLatencyTester(credentials_path)
        
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
