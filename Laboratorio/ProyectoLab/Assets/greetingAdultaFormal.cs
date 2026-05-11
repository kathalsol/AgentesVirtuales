using UnityEngine;

public class Greeting : StateMachineBehaviour
{
    [Header("Audio")]
    public AudioClip greetingClip;

    [Header("Blendshape")]
    public int mouthBlendshapeIndex = 0;

    [Header("Settings")]
    public float sensitivity = 5000f;
    public float smoothSpeed = 15f;

    private AudioSource audioSource;
    private SkinnedMeshRenderer faceMesh;

    private float[] samples = new float[256];

    override public void OnStateEnter(
        Animator animator,
        AnimatorStateInfo stateInfo,
        int layerIndex)
    {
        // Buscar AudioSource
        audioSource = animator.GetComponent<AudioSource>();

        // Buscar automáticamente un mesh con blendshapes
        SkinnedMeshRenderer[] meshes =
            animator.GetComponentsInChildren<SkinnedMeshRenderer>();

        foreach (var mesh in meshes)
        {
            if (mesh.sharedMesh != null &&
                mesh.sharedMesh.blendShapeCount > 0)
            {
                faceMesh = mesh;

                Debug.Log("Face mesh encontrado: " + mesh.name);

                // Mostrar blendshapes disponibles
                for (int i = 0; i < mesh.sharedMesh.blendShapeCount; i++)
                {
                    Debug.Log(
                        "Blendshape " + i + ": " +
                        mesh.sharedMesh.GetBlendShapeName(i));
                }

                break;
            }
        }

        if (faceMesh == null)
        {
            Debug.LogError("No se encontró mesh con blendshapes");
            return;
        }

        if (mouthBlendshapeIndex >=
            faceMesh.sharedMesh.blendShapeCount)
        {
            Debug.LogError("Índice de blendshape inválido");
            return;
        }

        // Reproducir audio
        if (audioSource != null && greetingClip != null)
        {
            audioSource.clip = greetingClip;
            audioSource.Play();
        }
    }

    override public void OnStateUpdate(
        Animator animator,
        AnimatorStateInfo stateInfo,
        int layerIndex)
    {
        if (audioSource == null || faceMesh == null)
            return;

        if (audioSource.isPlaying)
        {
            AnimateMouth();
        }
        else
        {
            faceMesh.SetBlendShapeWeight(
                mouthBlendshapeIndex,
                0);
        }
    }

    private void AnimateMouth()
    {
        audioSource.GetOutputData(samples, 0);

        float volume = 0f;

        // Obtener promedio del volumen
        for (int i = 0; i < samples.Length; i++)
        {
            volume += Mathf.Abs(samples[i]);
        }

        volume /= samples.Length;

        // Amplificar muchísimo más
        volume *= sensitivity;

        // Crear apertura mínima
        float minMouthOpen = 10f;

        // Convertir volumen a peso del blendshape
        float targetWeight =
            Mathf.Clamp(minMouthOpen + (volume * 20f), 0, 100);

        // Obtener peso actual
        float currentWeight =
            faceMesh.GetBlendShapeWeight(mouthBlendshapeIndex);

        // Movimiento más rápido y natural
        float smoothWeight =
            Mathf.Lerp(
                currentWeight,
                targetWeight,
                Time.deltaTime * smoothSpeed);

        // Aplicar blendshape
        faceMesh.SetBlendShapeWeight(
            mouthBlendshapeIndex,
            smoothWeight);
    }

    override public void OnStateExit(
        Animator animator,
        AnimatorStateInfo stateInfo,
        int layerIndex)
    {
        if (faceMesh != null)
        {
            faceMesh.SetBlendShapeWeight(
                mouthBlendshapeIndex,
                0);
        }
    }
}