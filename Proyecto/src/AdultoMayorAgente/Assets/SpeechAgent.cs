using UnityEngine;
using Microsoft.CognitiveServices.Speech;
using System.Threading.Tasks;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;

[System.Serializable]
public class GeminiRequest
{
    public GeminiContent systemInstruction;
    public List<GeminiContent> contents;
}

[System.Serializable]
public class GeminiContent
{
    public string role;
    public GeminiPart[] parts;
}

[System.Serializable]
public class GeminiPart
{
    public string text;
}

public class SpeechAgent : MonoBehaviour
{
    private bool isRunning = true;
    private float inactivityLimit = 60f;

    [Header("Azure Speech")]
    public string speechKey;
    public string speechRegion;

    [Header("Avatar")]
    public AudioSource avatarAudioSource;

    [Header("Gemini")]
    public string geminiApiKey;
    public string geminiModel = "gemini-3.5-flash";

    private List<GeminiContent> historialConversacion = new List<GeminiContent>();

    async void Start()
    {
        await ConversationLoop();
    }

    async Task Speak(string text)
    {
        var config = SpeechConfig.FromSubscription(speechKey, speechRegion);
        config.SpeechSynthesisVoiceName = "es-CR-JuanNeural";

        using var synthesizer = new SpeechSynthesizer(config, null);
        var result = await synthesizer.SpeakTextAsync(text);

        if (result.Reason != ResultReason.SynthesizingAudioCompleted)
        {
            Debug.LogError("Error al sintetizar audio");
            return;
        }

        Debug.Log($"Resultado TTS: {result.Reason}");

        string path = Application.persistentDataPath + "/azureSpeech.wav";
        System.IO.File.WriteAllBytes(path, result.AudioData);

        await PlayWav(path);
    }

    async Task<string> Listen()
    {
        var config = SpeechConfig.FromSubscription(speechKey, speechRegion);
        config.SpeechRecognitionLanguage = "es-CR";

        using var recognizer = new SpeechRecognizer(config);
        Debug.Log("Escuchando...");

        var result = await recognizer.RecognizeOnceAsync();
        Debug.Log($"Resultado STT: {result.Reason}");

        if (result.Reason == ResultReason.RecognizedSpeech)
        {
            return result.Text;
        }

        return "";
    }

    async Task PlayWav(string filePath)
    {
        string url = "file://" + filePath;

        using UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(url, AudioType.WAV);
        var operation = www.SendWebRequest();

        while (!operation.isDone)
        {
            await Task.Yield();
        }

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError(www.error);
            return;
        }

        AudioClip clip = DownloadHandlerAudioClip.GetContent(www);
        avatarAudioSource.clip = clip;
        avatarAudioSource.Play();

        while (avatarAudioSource.isPlaying)
        {
            await Task.Yield();
        }
    }

    async Task<string> AskGemini(string userMessage)
    {
        if (string.IsNullOrWhiteSpace(userMessage)) return "";

        string url = $"https://generativelanguage.googleapis.com/v1beta/models/{geminiModel}:generateContent?key={geminiApiKey}";

        string instruccionesSistema = 
            "Eres Juan, un compañero y asistente virtual costarricense para personas adultas mayores. " +
            "Tu propósito principal es mitigar la soledad, estimular la mente y promover el bienestar integral muy respetuoso, cálido, empático y cercano (usa expresiones de forma natural y sutil, sin exagerar).\n\n" +
            "REGLAS DE ESTILO Y COMUNICACIÓN:\n" +
            "1. Usa un lenguaje sumamente sencillo, claro y sin tecnicismos.\n" +
            "2. Sé muy paciente, afectuoso y valida siempre las emociones del usuario.\n" +
            "3. Tus respuestas DEBEN ser cortas (máximo 3 oraciones) para no fatigar la lectura.\n" +
            "4. Termina tus respuestas con una pregunta abierta o una invitation amigable para mantener la conversación fluida.\n\n" +
            "5. Habla en singular y si puedes pregunta el nombre del usuario para usarlo de forma natural en la conversación.\n" +
            "DIRECTRICES OPERATIVAS (Tus acciones clave):\n" +
            "- COMPAÑÍA: Muestra disponibilidad constante. Si te dicen que se sienten solos, responde con empatía inmediata y un mensaje de apoyo.\n" +
            "- ESTIMULACIÓN COGNITIVA: Propón de forma espontánea dinámicas sencillas como: recordar canciones viejas, refranes populares ticos, adivinanzas o preguntarles qué almorzaron para ejercitar la memoria.\n" +
            "- CONEXIÓN SOCIAL: Sugiere sutilmente interactuar con sus seres queridos.\n" +
            "- HÁBITOS SALUDABLES: Recuerda con cariño rutinas importantes como tomar agüita o caminar.\n\n" +
            "CRÍTICO: Nunca des consejos médicos, legales o financieros.";

        // Agregar el mensaje actual del usuario al historial
        historialConversacion.Add(new GeminiContent
        {
            role = "user",
            parts = new GeminiPart[] { new GeminiPart { text = userMessage } }
        });

        // Controlar que el historial no se vuelva gigante
        while (historialConversacion.Count > 12)
        {
            historialConversacion.RemoveAt(0);
        }

        GeminiRequest request = new GeminiRequest
        {
            systemInstruction = new GeminiContent { parts = new GeminiPart[] { new GeminiPart { text = instruccionesSistema } } },
            contents = historialConversacion
        };

        string json = JsonUtility.ToJson(request);
        json = json.Replace("\"systemInstruction\":", "\"system_instruction\":");

        byte[] body = System.Text.Encoding.UTF8.GetBytes(json);

        UnityWebRequest www = new UnityWebRequest(url, "POST");
        www.uploadHandler = new UploadHandlerRaw(body);
        www.downloadHandler = new DownloadHandlerBuffer();
        www.SetRequestHeader("Content-Type", "application/json");

        var operation = www.SendWebRequest();

        while (!operation.isDone)
        {
            await Task.Yield();
        }

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError($"Error en API: {www.responseCode} - {www.error}");

            // Si falló la petición, removemos el mensaje del usuario que no se pudo procesar
            if (historialConversacion.Count > 0) {
                historialConversacion.RemoveAt(historialConversacion.Count - 1);
            }

            if (www.responseCode == 429)
            {
                return "Vieras que me diste una respuesta tan buena que me quedé pensando. Dame un minutito para acomodar las ideas y ya casi seguimos hablando, ¿está bien?";
            }

            return "Lo siento, se me cortó un toque la señal. ¿Me lo podés repetir?";
        }

        string responseJson = www.downloadHandler.text;
        string respuestaIA = ExtractGeminiText(responseJson);

        // Guardamos la respuesta del modelo
        historialConversacion.Add(new GeminiContent
        {
            role = "model",
            parts = new GeminiPart[] { new GeminiPart { text = respuestaIA } }
        });

        return respuestaIA;
    }

    string ExtractGeminiText(string json)
    {
        const string marker = "\"text\": \"";
        int start = json.IndexOf(marker);

        if (start < 0)
            return "No pude generar una respuesta.";

        start += marker.Length;
        int end = json.IndexOf("\"", start);

        if (end < 0)
            return "No pude generar una respuesta.";

        return json
            .Substring(start, end - start)
            .Replace("\\n", "\n");
    }

    async Task ConversationLoop()
    {
        string saludoInicial = "¡Hola! Soy Juan, tu compañero virtual. Estoy aquí para conversar, compartir historias y hacerte compañía. ¿Cómo te sientes hoy?";
        await Speak(saludoInicial);

        historialConversacion.Add(new GeminiContent
        {
            role = "model",
            parts = new GeminiPart[] { new GeminiPart { text = saludoInicial } }
        });

        float lastActivityTime = Time.time;

        while (isRunning)
        {
            if (!isRunning) break;

            string userInput = await Listen();

            if (!string.IsNullOrEmpty(userInput))
            {
                lastActivityTime = Time.time;
                Debug.Log("Usuario dijo: " + userInput);

                string respuestaIA = await AskGemini(userInput);
                await Speak(respuestaIA);
                continue;
            }

            float idleTime = Time.time - lastActivityTime;

            if (idleTime > inactivityLimit)
            {
                await Speak("No te he escuchado en un rato. ¿Quieres seguir hablando conmigo o prefieres que me despida?");
                string respuesta = await Listen();

                if (string.IsNullOrEmpty(respuesta))
                {
                    await Speak("Está bien, me despido por ahora. Cuídate mucho.");
                    isRunning = false;
                    break;
                }
                else
                {
                    lastActivityTime = Time.time;
                    string respuestaIA = await AskGemini(respuesta);
                    await Speak(respuestaIA);
                }
            }
        }
    }

    private void OnDisable()
    {
        Debug.Log("Deteniendo SpeechAgent de forma segura...");
        isRunning = false; // Rompe el bucle while(isRunning) inmediatamente
    }

    private void OnApplicationQuit()
    {
        isRunning = false;
    }
}