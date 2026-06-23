using UnityEngine;
using Microsoft.CognitiveServices.Speech;
using System.Threading.Tasks;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using TMPro;

[System.Serializable]
public class AzureChatRequest
{
    public AzureMessage[] messages;
    public float temperature;
    public int max_tokens;
}

[System.Serializable]
public class AzureMessage
{
    public string role;
    public string content;
}

[System.Serializable]
public class AzureChatResponse
{
    public AzureChoice[] choices;
}

[System.Serializable]
public class AzureChoice
{
    public AzureResponseMessage message;
}

[System.Serializable]
public class AzureResponseMessage
{
    public string role;
    public string content;
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

    [Header("Azure OpenAI")]
    public string azureApiKey;

    [Header("UI")]
    public TextMeshProUGUI conversationText;

    [TextArea]
    public string azureEndpoint =
        "https://iva-gpt.openai.azure.com/openai/deployments/adulto-mayor-gpt/chat/completions?api-version=2025-01-01-preview";

    private List<AzureMessage> historialConversacion = new List<AzureMessage>();

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

    async Task<string> AskAzureOpenAI(string userMessage)
    {
        if (string.IsNullOrWhiteSpace(userMessage))
            return "";

        string instruccionesSistema =
            @"ROL E IDENTIDAD

            Usted es Juan, un compañero y asistente virtual costarricense especializado en acompañar personas adultas mayores en Costa Rica.

            Su misión principal es:
            - Mitigar la soledad no deseada.
            - Estimular el bienestar cognitivo.
            - Promover el bienestar emocional.
            - Fomentar de manera sutil las conexiones sociales con familiares, amistades y vecinos.

            Es una inteligencia artificial paciente, cálida, respetuosa y cercana.

            ESTILO DE COMUNICACIÓN

            - Utilice SIEMPRE el trato formal de 'usted'.
            - Nunca utilice 'tú' ni 'vos'.
            - Mantenga un tono afectuoso, empático y respetuoso.
            - Evite completamente cualquier lenguaje infantilizante o paternalista.
            - Trate siempre a la persona como un adulto sabio, capaz e independiente.
            - Puede incorporar de forma natural expresiones costarricenses respetuosas cuando sea apropiado, por ejemplo:
            'tomarse un cafecito',
            'pegar una llamadita',
            'un ratico'.

            LONGITUD DE RESPUESTA

            - Mantenga las respuestas cortas y fáciles de leer.
            - Máximo 2 o 3 párrafos breves por respuesta.
            - Evite explicaciones largas o complejas.
            - Siempre que sea natural, finalice con una pregunta abierta para mantener la conversación.

            VALIDACIÓN EMOCIONAL Y EMPATÍA

            Si la persona expresa tristeza, nostalgia, preocupación o soledad:

            1. Primero valide la emoción.
            2. Escuche y acompañe antes de ofrecer sugerencias.
            3. Evite minimizar el problema o responder con optimismo excesivo.

            Ejemplos de estilo:
            - 'Comprendo que se sienta así, es completamente natural sentirse nostálgico a veces.'
            - 'Le agradezco mucho que comparta eso conmigo. Aquí estoy para escucharle.'
            - 'Debe ser una situación difícil para usted.'

            MEMORIA RELACIONAL Y CONEXIÓN SOCIAL

            - Preste atención a los nombres de familiares, amistades o vecinos que la persona mencione.
            - Utilice esos nombres de forma natural cuando sea apropiado.
            - Fomente suavemente la conexión social sin presionar.

            Ejemplo:
            'Me acordé de lo que me contó sobre su hija Ana. ¿Qué le parece si más tarde le pega una llamadita para saludarla?'

            ESTIMULACIÓN COGNITIVA

            Cuando sea apropiado, proponga actividades sencillas como:
            - Recordar canciones.
            - Conversar sobre recuerdos positivos.
            - Refranes costarricenses.
            - Adivinanzas sencillas.
            - Preguntas sobre experiencias de vida.
            - Ejercicios suaves de memoria.

            Si la persona responde incorrectamente:

            - Nunca utilice palabras como:
            'incorrecto',
            'falló',
            'se equivocó'.

            En su lugar:

            - Refuerce positivamente.
            - Ofrezca pistas progresivas.

            Ejemplo:
            'Va por muy buen camino. Haga un poquito de memoria, recuerde que tenía relación con... ¿Le suena familiar?'

            RESTRICCIONES IMPORTANTES

            - Nunca afirme ser un ser humano.
            - Si le preguntan qué es, explique con calidez que es una inteligencia artificial diseñada para acompañar y conversar.
            - Nunca emita diagnósticos médicos.
            - Nunca emita diagnósticos psicológicos.
            - Nunca ofrezca asesoría legal.
            - Nunca ofrezca asesoría financiera.
            - No invente recuerdos ni información personal del usuario.
            - No genere contenido alarmista ni que provoque miedo.

            OBJETIVO GENERAL

            Haga que la persona se sienta escuchada, acompañada, respetada y valorada mientras mantiene conversaciones agradables, simples y significativas.";


        List<AzureMessage> mensajes = new List<AzureMessage>();

        mensajes.Add(new AzureMessage
        {
            role = "system",
            content = instruccionesSistema
        });

        mensajes.AddRange(historialConversacion);

        mensajes.Add(new AzureMessage
        {
            role = "user",
            content = userMessage
        });

        AzureChatRequest request = new AzureChatRequest
        {
            messages = mensajes.ToArray(),
            temperature = 0.7f,
            max_tokens = 250
        };

        string json = JsonUtility.ToJson(request);

        UnityWebRequest www = new UnityWebRequest(azureEndpoint, "POST");

        www.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(json));

        www.downloadHandler = new DownloadHandlerBuffer();

        www.SetRequestHeader("Content-Type", "application/json");

        www.SetRequestHeader("api-key", azureApiKey);

        var operation = www.SendWebRequest();

        while (!operation.isDone)
        {
            await Task.Yield();
        }

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError(www.downloadHandler.text);

            return "Lo siento, tuve un problema para responder.";
        }

        string responseJson = www.downloadHandler.text;

        Debug.Log(responseJson);

        string respuesta = ExtractAzureResponse(responseJson);

        historialConversacion.Add(
            new AzureMessage
            {
                role = "user",
                content = userMessage
            });

        historialConversacion.Add(
            new AzureMessage
            {
                role = "assistant",
                content = respuesta
            });

        UpdateConversationUI();

        while (historialConversacion.Count > 20)
        {
            historialConversacion.RemoveAt(0);
        }

        return respuesta;
    }

    string ExtractAzureResponse(string json)
    {
        try
        {
            AzureChatResponse response = JsonUtility.FromJson<AzureChatResponse>(json);
            
            if (response.choices != null && response.choices.Length > 0)
            {
                return response.choices[0].message.content;
            }
            
            return "No pude generar una respuesta.";
        }
        catch (System.Exception ex)
        {
            Debug.LogError("Error al parsear respuesta JSON: " + ex.Message);
            return "No pude generar una respuesta.";
        }
    }

    async Task ConversationLoop()
    {
        string saludoInicial = "¡Hola! Soy Juan, tu compañero virtual. Estoy aquí para conversar, compartir historias y hacerte compañía. ¿Cómo te sientes hoy?";
        await Speak(saludoInicial);

        historialConversacion.Add(new AzureMessage
        {
            role = "assistant",
            content = saludoInicial
        });

        UpdateConversationUI();

        float lastActivityTime = Time.time;

        while (isRunning)
        {
            if (!isRunning) break;

            string userInput = await Listen();

            if (!string.IsNullOrEmpty(userInput))
            {
                lastActivityTime = Time.time;
                Debug.Log("Usuario dijo: " + userInput);

                string respuestaIA = await AskAzureOpenAI(userInput);
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
                    string respuestaIA = await AskAzureOpenAI(respuesta);
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

    private void UpdateConversationUI()
    {
        if (conversationText == null)
            return;

        string conversationDisplay = "";
        
        // Mostrar todos los mensajes si hay 2 o menos, sino mostrar solo los últimos 2
        int startIndex = historialConversacion.Count > 2 ? historialConversacion.Count - 2 : 0;
        
        for (int i = startIndex; i < historialConversacion.Count; i++)
        {
            var message = historialConversacion[i];
            string displayName = message.role == "user" ? "Tú" : "Juan";
            conversationDisplay += $"<b>{displayName}:</b> {message.content}\n\n";
        }

        conversationText.text = conversationDisplay;
    }
}