import requests
import time
import os
from datetime import datetime
import json
import urllib3
from dotenv import load_dotenv

# Desactivar advertencias de SSL para entornos de prueba
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class ElevenLabsTTSLatencyTester:
    """
    Prueba la latencia y costo del TTS de ElevenLabs
    Configuración: Voz en español con modelo multilingual_v2
    """
    
    # Precios de ElevenLabs (USD aproximado por carácter basado en planes)
    # Creator plan: $22/mes por 100,000 caracteres = $0.00022 por carácter
    # Pro plan: $99/mes por 500,000 caracteres = $0.000198 por carácter
    PRICE_PER_CHAR_CREATOR = 0.00022
    PRICE_PER_CHAR_PRO = 0.000198
    
    # URL base de la API de ElevenLabs
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    # Voces predefinidas de ElevenLabs (algunas buenas para español)
    DEFAULT_VOICES = {
        "Antoni": "ErXwobaYiN019PkySvjV",      # Voz masculina
        "Arnold": "VR6AewLTigWG4xSOukaG",      # Voz masculina profunda
        "Bella": "EXAVITQu4vr4xnSDxMaL",       # Voz femenina
        "Rachel": "21m00Tcm4TlvDq8ikWAM",      # Voz femenina clara
        "Domi": "AZnzlk1XvdvUeBnXmlld",        # Voz femenina
        "Adam": "pNInz6obpgDQGcFmaJgB",        # Voz masculina
    }
    
    def __init__(self, api_key: str = None, voice_id: str = None):
        """
        Inicializa el probador de TTS de ElevenLabs
        
        Args:
            api_key: API key de ElevenLabs (opcional, se lee de .env si no se provee)
            voice_id: ID de la voz a usar (opcional, usa Antoni por defecto)
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere ELEVENLABS_API_KEY en el archivo .env")
        
        self.voice_id = voice_id or self.DEFAULT_VOICES["Antoni"]
        self.voice_name = "Antoni"  # Nombre por defecto
        self.model_id = "eleven_multilingual_v2"  # Modelo multilingüe para español
        self.results = []
    
    def get_available_voices(self) -> list:
        """
        Obtiene la lista de voces disponibles en la cuenta
        
        Returns:
            Lista de voces disponibles
        """
        url = f"{self.BASE_URL}/voices"
        headers = {"xi-api-key": self.api_key}
        
        try:
            response = requests.get(url, headers=headers, verify=False)
            if response.status_code == 200:
                voices = response.json().get("voices", [])
                return [{"name": v["name"], "voice_id": v["voice_id"]} for v in voices]
            else:
                print(f"Error obteniendo voces: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def calculate_cost(self, text: str, plan: str = "creator") -> float:
        """
        Calcula el costo de síntesis para un texto
        
        Args:
            text: Texto a sintetizar
            plan: Plan de ElevenLabs ("creator" o "pro")
            
        Returns:
            Costo en USD
        """
        char_count = len(text)
        
        if plan == "pro":
            price = self.PRICE_PER_CHAR_PRO
        else:
            price = self.PRICE_PER_CHAR_CREATOR
        
        cost = char_count * price
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
            # URL del endpoint de síntesis
            url = f"{self.BASE_URL}/text-to-speech/{self.voice_id}"
            
            # Headers
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg"
            }
            
            # Body de la solicitud
            request_body = {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            # Medir tiempo de síntesis
            start_time = time.time()
            response = requests.post(
                url,
                json=request_body,
                headers=headers,
                verify=False  # Desactivar verificación SSL para entornos con proxy/firewall
            )
            end_time = time.time()
            
            # Verificar respuesta
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("detail", {}).get("message", response.text)
                except:
                    pass
                raise Exception(f"Error API: {response.status_code} - {error_detail}")
            
            audio_content = response.content
            
            latency_ms = (end_time - start_time) * 1000
            cost = self.calculate_cost(text)
            
            # Guardar audio si se solicita
            output_file = None
            if save_audio and audio_content:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                output_file = f"audio_output_{timestamp}.mp3"
                with open(output_file, 'wb') as out:
                    out.write(audio_content)
            
            result_dict = {
                "timestamp": datetime.now().isoformat(),
                "text": text,
                "text_length": len(text),
                "latency_ms": round(latency_ms, 2),
                "cost_usd": round(cost, 6),
                "audio_file": output_file if save_audio else None,
                "status": "SUCCESS",
                "voice_id": self.voice_id,
                "voice_name": self.voice_name,
                "model_id": self.model_id
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
                "voice_id": self.voice_id,
                "voice_name": self.voice_name,
                "model_id": self.model_id
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
        print("PRUEBAS DE LATENCIA - ELEVENLABS TTS (Multilingual v2)")
        print("=" * 60)
        print(f"Voz: {self.voice_name} ({self.voice_id})")
        print(f"Modelo: {self.model_id}")
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
                "provider": "ElevenLabs",
                "model_id": self.model_id,
                "voice_id": self.voice_id,
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
                "provider": "ElevenLabs",
                "model_id": self.model_id,
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
            print("RESUMEN DE RESULTADOS - ELEVENLABS TTS")
            print("=" * 60)
            print(f"Total de pruebas: {len(self.results)}")
            print(f"Pruebas exitosas: {len(successful)}")
            print(f"Pruebas fallidas: {len(self.results) - len(successful)}")
            print("\nLATENCIA:")
            print(f"  Mínima: {min(latencies):.2f}ms")
            print(f"  Máxima: {max(latencies):.2f}ms")
            print(f"  Promedio: {sum(latencies)/len(latencies):.2f}ms")
            print("\nCOSTO (estimado plan Creator):")
            print(f"  Costo mínimo: ${min(costs):.6f}")
            print(f"  Costo máximo: ${max(costs):.6f}")
            print(f"  Costo total: ${sum(costs):.6f}")
            print("=" * 60 + "\n")


def main():
    """Función principal"""
    
    # Obtener API key
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("Error: ELEVENLABS_API_KEY no está configurada")
        print("\nConfigura en tu archivo .env:")
        print('  ELEVENLABS_API_KEY="tu-api-key-aqui"')
        print("\nPuedes obtener tu API key en: https://elevenlabs.io/")
        return
    
    try:
        # Crear probador
        tester = ElevenLabsTTSLatencyTester(api_key)
        
        # Mostrar voces disponibles (opcional)
        print("Obteniendo voces disponibles...")
        voices = tester.get_available_voices()
        if voices:
            print(f"Voces disponibles: {len(voices)}")
            for v in voices[:5]:  # Mostrar solo las primeras 5
                print(f"  - {v['name']}: {v['voice_id']}")
            if len(voices) > 5:
                print(f"  ... y {len(voices) - 5} más")
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
