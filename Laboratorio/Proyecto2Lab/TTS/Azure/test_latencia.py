import azure.cognitiveservices.speech as speechsdk
import time
import os
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

class AzureTTSLatencyTester:
    """
    Prueba la latencia y costo del TTS de Azure
    Configuración: Neural voice es-CR-JuanNeural
    """
    
    # Precios de Azure TTS Neural (USD por 1 millón de caracteres)
    NEURAL_PRICE_PER_MILLION_CHARS = 24.00
    
    def __init__(self, speech_key: str, speech_region: str):
        """
        Inicializa el probador de TTS
        
        Args:
            speech_key: Clave de Azure Speech
            speech_region: Región de Azure (ej: "eastus")
        """
        self.speech_key = speech_key
        self.speech_region = speech_region
        self.results = []
        
        # Configurar Speech Service
        self.speech_config = speechsdk.SpeechConfig(
            subscription=speech_key, 
            region=speech_region
        )
        self.speech_config.speech_synthesis_voice_name = "es-CR-JuanNeural"
    
    def calculate_cost(self, text: str) -> float:
        """
        Calcula el costo de síntesis para un texto
        
        Args:
            text: Texto a sintetizar
            
        Returns:
            Costo en USD
        """
        char_count = len(text)
        cost = (char_count / 1_000_000) * self.NEURAL_PRICE_PER_MILLION_CHARS
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
        output_file = None
        
        if save_audio:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            output_file = f"audio_output_{timestamp}.wav"
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
        else:
            audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
        
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, 
            audio_config=audio_config
        )
        
        # Medir tiempo de síntesis
        start_time = time.time()
        result = synthesizer.speak_text_async(text).get()
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        cost = self.calculate_cost(text)
        
        result_dict = {
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "text_length": len(text),
            "latency_ms": round(latency_ms, 2),
            "cost_usd": round(cost, 6),
            "audio_file": output_file if save_audio else None,
            "status": "SUCCESS" if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted else "FAILED",
            "reason": str(result.reason)
        }
        
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            result_dict["error"] = result.error_details
        
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
        print("PRUEBAS DE LATENCIA - AZURE TTS (es-CR-JuanNeural)")
        print("=" * 60)
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
        print(f"  Latencia: {result['latency_ms']}ms")
        print(f"  Costo: ${result['cost_usd']:.6f}")
        if result['audio_file']:
            print(f"  Archivo: {result['audio_file']}")
    
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
            print("RESUMEN DE RESULTADOS")
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
    
    # Obtener credenciales de variables de entorno
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")
    
    if not speech_key:
        print("Error: AZURE_SPEECH_KEY no está configurada en las variables de entorno")
        print("Por favor, configura:")
        print('  set AZURE_SPEECH_KEY="tu-clave"')
        print('  set AZURE_SPEECH_REGION="tu-region"  (default: eastus)')
        return
    
    # Crear probador
    tester = AzureTTSLatencyTester(speech_key, speech_region)
    
    # Ejecutar pruebas
    try:
        tester.test_various_lengths()
        tester.print_summary()
        tester.generate_report()
    except Exception as e:
        print(f"Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
