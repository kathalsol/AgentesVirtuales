import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Configurar estilo
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10

print("=" * 80)
print("🎨 Generando Gráficos de Latencia vs Costo")
print("=" * 80)

# ======================== DATOS STT ========================
stt_data = {
    'Servicio': ['Deepgram Nova-2', 'Google STT', 'AssemblyAI', 'Azure STT', 'Whisper Base'],
    'Latencia_ms': [1423.16, 2020.16, 3869.41, 4492.55, 6700],
    'Costo_por_minuto': [0.0043, 0.024, 0.015, 1.0/60, 0.0],
}
df_stt = pd.DataFrame(stt_data)
print("\n✅ STT Data loaded")

# ======================== DATOS TTS ========================
tts_data = {
    'Servicio': ['Azure Neural Voice', 'ElevenLabs v2', 'Cartesia Sonic-2', 'Google Neural2', 'CoquiTTS/Piper'],
    'Latencia_ms': [1146.55, 2103.84, 3821.34, 1413, 430],
    'Costo_por_minuto': [0.001667, 0.030, 0.007, 0.001, 0.0],
    'Voz_Nativa': ['Sí', 'No', 'No', 'No', 'No']
}
df_tts = pd.DataFrame(tts_data)
print("✅ TTS Data loaded")

# ======================== DATOS LLM ========================
llm_data = {
    'Modelo': ['GPT-4.1-mini', 'GPT-4.1', 'Gemini 3.5-flash', 'Gemini 2.5-flash', 'Qwen3:8B (CPU)'],
    'TTFT_segundos': [1.25, 2.19, 5.05, 5.15, 24.69],
    'Costo_por_llamada': [0.000075, 0.001172, 0.000053, 0.000049, 0.0],
}
df_llm = pd.DataFrame(llm_data)
print("✅ LLM Data loaded")

# ======================== GRÁFICO 1: STT ========================
print("\n📊 Generating STT graph...")
fig, ax = plt.subplots(figsize=(12, 7))

colors = {'Deepgram Nova-2': '#2ecc71', 'Google STT': '#3498db', 'AssemblyAI': '#f39c12', 
          'Azure STT': '#e74c3c', 'Whisper Base': '#9b59b6'}

for idx, row in df_stt.iterrows():
    ax.scatter(row['Latencia_ms'], row['Costo_por_minuto'], 
              s=400, alpha=0.7, color=colors.get(row['Servicio'], '#95a5a6'),
              edgecolors='black', linewidth=2)
    
    offset = 150 if row['Servicio'] == 'Deepgram Nova-2' else (200 if row['Costo_por_minuto'] > 0.5 else 100)
    marker = '✅' if row['Servicio'] == 'Deepgram Nova-2' else ('⚠️' if row['Servicio'] == 'Azure STT' else '→')
    ax.annotate(f"{marker} {row['Servicio']}\n{row['Latencia_ms']:.0f}ms",
               xy=(row['Latencia_ms'], row['Costo_por_minuto']),
               xytext=(offset, 20), textcoords='offset points',
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=colors.get(row['Servicio'], '#95a5a6'), alpha=0.3),
               arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

ax.axhline(y=df_stt['Costo_por_minuto'].median(), color='gray', linestyle='--', linewidth=1, alpha=0.5)
ax.axvline(x=df_stt['Latencia_ms'].median(), color='gray', linestyle='--', linewidth=1, alpha=0.5)

rect = Rectangle((0, 0), 2000, 0.01, alpha=0.1, facecolor='green')
ax.add_patch(rect)

ax.set_xlabel('Latencia (ms)', fontsize=12, fontweight='bold')
ax.set_ylabel('Costo ($/minuto)', fontsize=12, fontweight='bold')
ax.set_title('Comparativa STT: Latencia vs Costo\n(5 iteraciones × 3 archivos)', 
            fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
ax.set_xlim(-200, 7000)

plt.tight_layout()
plt.savefig('STT_Latencia_vs_Costo.png', dpi=300, bbox_inches='tight')
print("   → Guardado: STT_Latencia_vs_Costo.png")
plt.close()

# ======================== GRÁFICO 2: TTS ========================
print("📊 Generating TTS graph...")
fig, ax = plt.subplots(figsize=(12, 7))

colors_tts = {'Azure Neural Voice': '#2ecc71', 'ElevenLabs v2': '#3498db', 'Cartesia Sonic-2': '#e74c3c',
              'Google Neural2': '#f39c12', 'CoquiTTS/Piper': '#9b59b6'}

for idx, row in df_tts.iterrows():
    marker_size = 500 if row['Servicio'] == 'Azure Neural Voice' else 400
    
    ax.scatter(row['Latencia_ms'], row['Costo_por_minuto'], 
              s=marker_size, alpha=0.7, color=colors_tts.get(row['Servicio'], '#95a5a6'),
              edgecolors='black', linewidth=2)
    
    offset = 150 if row['Servicio'] == 'Azure Neural Voice' else 100
    marker = '✅' if row['Servicio'] == 'Azure Neural Voice' else ('⚠️' if row['Servicio'] == 'Cartesia Sonic-2' else '→')
    voz = '🇨🇷' if row['Voz_Nativa'] == 'Sí' else ''
    
    ax.annotate(f"{marker} {row['Servicio']} {voz}\n{row['Latencia_ms']:.0f}ms",
               xy=(row['Latencia_ms'], row['Costo_por_minuto']),
               xytext=(offset, 20), textcoords='offset points',
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=colors_tts.get(row['Servicio'], '#95a5a6'), alpha=0.3),
               arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

ax.axhline(y=df_tts['Costo_por_minuto'].median(), color='gray', linestyle='--', linewidth=1, alpha=0.5)
ax.axvline(x=df_tts['Latencia_ms'].median(), color='gray', linestyle='--', linewidth=1, alpha=0.5)

rect = Rectangle((0, 0), 1500, 0.002, alpha=0.1, facecolor='green')
ax.add_patch(rect)

ax.set_xlabel('Latencia (ms)', fontsize=12, fontweight='bold')
ax.set_ylabel('Costo ($/minuto)', fontsize=12, fontweight='bold')
ax.set_title('Comparativa TTS: Latencia vs Costo | 🇨🇷 = Voz costarricense\n(5 iteraciones × 3 textos)',
            fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('TTS_Latencia_vs_Costo.png', dpi=300, bbox_inches='tight')
print("   → Guardado: TTS_Latencia_vs_Costo.png")
plt.close()

# ======================== GRÁFICO 3: LLM ========================
print("📊 Generating LLM graph...")
fig, ax = plt.subplots(figsize=(12, 7))

colors_llm = {'GPT-4.1-mini': '#2ecc71', 'GPT-4.1': '#f39c12', 'Gemini 3.5-flash': '#3498db',
              'Gemini 2.5-flash': '#e67e22', 'Qwen3:8B (CPU)': '#9b59b6'}

for idx, row in df_llm.iterrows():
    marker_size = 600 if row['Modelo'] == 'GPT-4.1-mini' else (450 if row['Modelo'] == 'GPT-4.1' else 350)
    marker_style = '*' if row['Modelo'] == 'GPT-4.1-mini' else ('D' if row['Modelo'] == 'GPT-4.1' else 'o')
    
    costo_plot = row['Costo_por_llamada'] if row['Costo_por_llamada'] > 0 else 1e-7
    
    ax.scatter(row['TTFT_segundos'], costo_plot, 
              s=marker_size, alpha=0.7, color=colors_llm.get(row['Modelo'], '#95a5a6'),
              edgecolors='black', linewidth=2, marker=marker_style)
    
    offset_x = -150 if row['Modelo'] == 'GPT-4.1-mini' else 100
    marker = '✅' if row['Modelo'] == 'GPT-4.1-mini' else ('🚨' if row['Modelo'] == 'GPT-4.1' else '→')
    
    ax.annotate(f"{marker} {row['Modelo']}\n{row['TTFT_segundos']:.2f}s",
               xy=(row['TTFT_segundos'], costo_plot),
               xytext=(offset_x, 20), textcoords='offset points',
               fontsize=9, ha='center',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=colors_llm.get(row['Modelo'], '#95a5a6'), alpha=0.3),
               arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

ax.set_yscale('log')

ax.axvline(x=2.0, color='gray', linestyle=':', linewidth=1.5, alpha=0.5)
ax.axhline(y=0.0001, color='gray', linestyle=':', linewidth=1.5, alpha=0.5)

rect = Rectangle((0, 1e-7), 2.0, 0.0001, alpha=0.1, facecolor='green')
ax.add_patch(rect)

ax.set_xlabel('Latencia TTFT (segundos)', fontsize=12, fontweight='bold')
ax.set_ylabel('Costo por llamada ($) [Escala Log]', fontsize=12, fontweight='bold')
ax.set_title('Comparativa LLM: Latencia vs Costo | ✅=Recomendado, 🚨=Crisis, →=Alternativa\n(5 iteraciones)',
            fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, which='both')
ax.set_xlim(-0.5, 27)

plt.tight_layout()
plt.savefig('LLM_Latencia_vs_Costo.png', dpi=300, bbox_inches='tight')
print("   → Guardado: LLM_Latencia_vs_Costo.png")
plt.close()

# ======================== GRÁFICO 4: DASHBOARD ========================
print("📊 Generating consolidated dashboard...")
fig, axes = plt.subplots(1, 3, figsize=(20, 6))
fig.suptitle('Dashboard Consolidado: Latencia vs Costo\n' + 
             'Benchmark empírico: STT (15 pruebas), TTS (15 pruebas), LLM (15 pruebas)', 
             fontsize=16, fontweight='bold', y=1.02)

# SubPlot 1: STT
ax = axes[0]
for idx, row in df_stt.iterrows():
    ax.scatter(row['Latencia_ms'], row['Costo_por_minuto'], 
              s=350, alpha=0.7, color=colors.get(row['Servicio'], '#95a5a6'),
              edgecolors='black', linewidth=2)
    ax.text(row['Latencia_ms'], row['Costo_por_minuto'], 
           row['Servicio'].split()[0][:4], ha='center', va='center', fontsize=8, fontweight='bold')

ax.set_xlabel('Latencia (ms)', fontsize=11, fontweight='bold')
ax.set_ylabel('Costo ($/min)', fontsize=11, fontweight='bold')
ax.set_title('STT: Speech-to-Text', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

# SubPlot 2: TTS
ax = axes[1]
for idx, row in df_tts.iterrows():
    marker_size = 400 if row['Servicio'] == 'Azure Neural Voice' else 350
    ax.scatter(row['Latencia_ms'], row['Costo_por_minuto'], 
              s=marker_size, alpha=0.7, color=colors_tts.get(row['Servicio'], '#95a5a6'),
              edgecolors='black', linewidth=2)
    label = row['Servicio'].split()[0][:3]
    ax.text(row['Latencia_ms'], row['Costo_por_minuto'], 
           label, ha='center', va='center', fontsize=8, fontweight='bold')

ax.set_xlabel('Latencia (ms)', fontsize=11, fontweight='bold')
ax.set_ylabel('Costo ($/min)', fontsize=11, fontweight='bold')
ax.set_title('TTS: Text-to-Speech', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

# SubPlot 3: LLM (Log scale)
ax = axes[2]
for idx, row in df_llm.iterrows():
    marker_size = 450 if row['Modelo'] == 'GPT-4.1-mini' else 350
    marker_style = '*' if row['Modelo'] == 'GPT-4.1-mini' else 'o'
    costo_plot = row['Costo_por_llamada'] if row['Costo_por_llamada'] > 0 else 1e-7
    
    ax.scatter(row['TTFT_segundos'], costo_plot, 
              s=marker_size, alpha=0.7, color=colors_llm.get(row['Modelo'], '#95a5a6'),
              edgecolors='black', linewidth=2, marker=marker_style)
    label = row['Modelo'].split('-')[0][:3]
    ax.text(row['TTFT_segundos'], costo_plot, label, ha='center', va='center', fontsize=8, fontweight='bold')

ax.set_yscale('log')
ax.set_xlabel('Latencia TTFT (seg)', fontsize=11, fontweight='bold')
ax.set_ylabel('Costo ($/llamada) [Log]', fontsize=11, fontweight='bold')
ax.set_title('LLM: Large Language Models', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, which='both')

plt.tight_layout()
plt.savefig('Dashboard_Consolidado_Latencia_Costo.png', dpi=300, bbox_inches='tight')
print("   → Guardado: Dashboard_Consolidado_Latencia_Costo.png")
plt.close()

print("\n" + "=" * 80)
print("✅ TODOS LOS GRÁFICOS GENERADOS EXITOSAMENTE")
print("=" * 80)
print("\n📁 Archivos generados:")
print("   1. STT_Latencia_vs_Costo.png")
print("   2. TTS_Latencia_vs_Costo.png")
print("   3. LLM_Latencia_vs_Costo.png")
print("   4. Dashboard_Consolidado_Latencia_Costo.png")
print("\n📍 Ubicación: Laboratorio/Proyecto2Lab/")
print("=" * 80)
