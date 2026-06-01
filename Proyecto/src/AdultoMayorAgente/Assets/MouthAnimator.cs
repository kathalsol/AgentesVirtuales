using UnityEngine;

public class MouthAnimator : MonoBehaviour
{
    public int mouthBlendshapeIndex = 0;

    public float sensitivity = 15000f;
    public float smoothSpeed = 15f;

    private AudioSource audioSource;
    private SkinnedMeshRenderer faceMesh;

    private float[] samples = new float[256];

    void Start()
    {
        audioSource = GetComponent<AudioSource>();

        foreach (var mesh in GetComponentsInChildren<SkinnedMeshRenderer>())
        {
            if (mesh.sharedMesh != null &&
                mesh.sharedMesh.blendShapeCount > 0)
            {
                faceMesh = mesh;
                break;
            }
        }
    }

    void Update()
    {
        if (audioSource == null ||
            faceMesh == null)
            return;

        if (audioSource.isPlaying)
        {
            AnimateMouth();
        }
        else
        {
            faceMesh.SetBlendShapeWeight(mouthBlendshapeIndex, 0);
        }
    }

    private void AnimateMouth()
    {
        audioSource.GetOutputData(samples, 0);

        float volume = 0f;

        for (int i = 0; i < samples.Length; i++)
        {
            volume += Mathf.Abs(samples[i]);
        }

        volume /= samples.Length;

        float targetWeight = Mathf.Clamp(volume * sensitivity, 0, 100);

        float currentWeight = faceMesh.GetBlendShapeWeight(mouthBlendshapeIndex);

        float smoothWeight =
            Mathf.Lerp(currentWeight, targetWeight, Time.deltaTime * smoothSpeed);

        faceMesh.SetBlendShapeWeight(mouthBlendshapeIndex, smoothWeight);
    }
}