import os
import sys
import shutil
import random
import subprocess
import numpy as np
import pandas as pd
import librosa
import soundfile as sf
import matplotlib.pyplot as plt
from itertools import product
from scipy.signal import butter, lfilter
from datetime import datetime

# -------------------- CONFIGURACIÓN GLOBAL --------------------
BASE_DIR = r"D:\GUSTAVO\CARPETA BASE\base"
TEMP_EVAL = os.path.join(BASE_DIR, "temp_eval")
TEMP_RESULT = os.path.join(BASE_DIR, "temp_eval_result")
RESULTS_CSV = os.path.join(BASE_DIR, "resultados_csv_birdnet")
ORIGINAL_CSV_DIR = r"D:\GUSTAVO\CARPETA BASE\base\salida birdnet"
SEGMENTOS_DIR = os.path.join(BASE_DIR, "fragmentos_audio")

for d in [BASE_DIR, TEMP_EVAL, TEMP_RESULT, RESULTS_CSV, SEGMENTOS_DIR]:
    os.makedirs(d, exist_ok=True)

Q_VALS = [0.002, 0.003, 0.004, 0.005, 0.0065]
R_VALS = [0.0035, 0.0045, 0.0055, 0.0065, 0.007]
F_VALS = [500, 1000, 1500, 2000, 2500]

ALPHA, GAMMA, EPSILON = 0.1, 0.9, 1.0
EPSILON_DECAY, EPSILON_MIN = 0.98, 0.01

LAT, LON, MIN_CONF = 10.45, -73.25, 0.1

NUM_EPOCHS = 3
STEPS_PER_EPOCH = 20

# -------------------- SEGMENTACIÓN POR ENERGÍA --------------------
def dividir_audio_por_energia(audio_path, duracion_seg, umbral_energia, tiempo_sostenido, carpeta_salida):
    audio, sr = librosa.load(audio_path, sr=None, mono=True)
    duracion_audio = librosa.get_duration(y=audio, sr=sr)
    
    if duracion_audio <= duracion_seg:
        print(f"Audio corto ({duracion_audio:.2f}s), no se fragmenta: {audio_path}")
        nombre = os.path.splitext(os.path.basename(audio_path))[0]
        destino = os.path.join(carpeta_salida, f"{nombre}.wav")
        sf.write(destino, audio, sr)
        return [destino]
    
    frame_length = int(0.025 * sr)
    hop_length = int(0.010 * sr)
    energia = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]

    muestras_minimas = int((tiempo_sostenido * sr) / hop_length)
    fragmentos = []
    contador = 0

    for i in range(len(energia)):
        if energia[i] > umbral_energia:
            contador += 1
            if contador >= muestras_minimas:
                inicio = max(0, (i - muestras_minimas) * hop_length)
                fin = inicio + int(duracion_seg * sr)
                if fin > len(audio):
                    fin = len(audio)
                fragmento = audio[inicio:fin]
                nombre = os.path.splitext(os.path.basename(audio_path))[0]
                frag_path = os.path.join(carpeta_salida, f"{nombre}_fragmento_{i}.wav")
                sf.write(frag_path, fragmento, sr)
                fragmentos.append(frag_path)
                contador = 0
        else:
            contador = 0

    return fragmentos

# -------------------- FILTROS --------------------
def filtro_kalman(y, Q, R):
    x, P = y[0], 1.0
    x_est = np.zeros(len(y))
    for k in range(1, len(y)):
        x_pred, P_pred = x, P + Q
        K = P_pred / (P_pred + R)
        x = x_pred + K * (y[k] - x_pred)
        P = (1 - K) * P_pred
        x_est[k] = x
    return x_est

def filtro_pasabanda(y, lowcut, sr, highcut=8000):
    nyq = 0.5 * sr
    b, a = butter(4, [lowcut/nyq, highcut/nyq], btype='band')
    return lfilter(b, a, y)

# -------------------- AGENTE Q-LEARNING --------------------
class QLearningAgent:
    def __init__(self, actions):
        self.actions = actions
        self.q_table = pd.DataFrame({
            'Action': actions,
            'Q-Value': 0.0,
            'Last_Species': 'N/A',
            'Last_Reward': 0.0
        })
        self.alpha, self.gamma = ALPHA, GAMMA
        self.epsilon, self.eps_decay, self.eps_min = EPSILON, EPSILON_DECAY, EPSILON_MIN

    def choose_action(self):
        if np.random.rand() < self.epsilon:
            return random.randint(0, len(self.actions)-1)
        return self.q_table['Q-Value'].argmax()

    def learn(self, idx, reward, species):
        q_pred = self.q_table.loc[idx, 'Q-Value']
        q_target = reward + self.gamma * self.q_table['Q-Value'].max()
        self.q_table.loc[idx, 'Q-Value'] += self.alpha * (q_target - q_pred)
        if reward > self.q_table.loc[idx, 'Last_Reward']:
            self.q_table.loc[idx, ['Last_Reward', 'Last_Species']] = reward, species

    def decay_epsilon(self):
        if self.epsilon > self.eps_min:
            self.epsilon *= self.eps_decay

# -------------------- BIRDNET --------------------
def llamar_birdnet(temp_audio, epoch, step, Q, R, F, audio_name):
    subprocess.run([
        sys.executable, "-m", "birdnet_analyzer.analyze",
        TEMP_EVAL, "--output", TEMP_RESULT,
        "--lat", str(LAT), "--lon", str(LON),
        "--min_conf", str(MIN_CONF), "--rtype", "csv"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    resultado_csv = next((os.path.join(TEMP_RESULT, f) for f in os.listdir(TEMP_RESULT)
                         if f.endswith(".BirdNET.results.csv")), None)

    reward, species = 0.0, "N/A"

    if resultado_csv:
        df = pd.read_csv(resultado_csv)
        df['File'] = df['File'].astype(str)
        df_filtrado = df[df['File'].str.contains(os.path.basename(temp_audio))]

        if not df_filtrado.empty:
            best = df_filtrado.loc[df_filtrado['Confidence'].idxmax()]
            reward, species = best['Confidence'], best['Scientific name']

        dest_csv = os.path.join(
            RESULTS_CSV,
            f"{audio_name}_epoch{epoch+1}_step{step+1}_Q{Q}_R{R}_F{F}.csv"
        )
        shutil.move(resultado_csv, dest_csv)

    return reward, species

# -------------------- ENTRENAMIENTO --------------------
def entrenar_audio(audio_path):
    acciones = list(product(Q_VALS, R_VALS, F_VALS))
    agente = QLearningAgent(acciones)

    y, sr = librosa.load(audio_path, sr=None)
    audio_name = os.path.splitext(os.path.basename(audio_path))[0]

    mejor_global = 0.0
    mejor_filtros = (0, 0, 0)
    mejor_especie = "N/A"

    for epoch in range(NUM_EPOCHS):
        for step in range(STEPS_PER_EPOCH):
            action_idx = agente.choose_action()
            Q, R, f_low = acciones[action_idx]

            y_k = filtro_kalman(y, Q, R)
            y_f = filtro_pasabanda(y_k, f_low, sr)

            nombre_temp = f"{audio_name}_Q{Q}_R{R}_F{f_low}.wav"
            temp_audio = os.path.join(TEMP_EVAL, nombre_temp)
            sf.write(temp_audio, y_f, sr)

            reward, species = llamar_birdnet(temp_audio, epoch, step, Q, R, f_low, audio_name)

            if reward > mejor_global:
                mejor_global = reward
                mejor_filtros = (Q, R, f_low)
                mejor_especie = species

            agente.learn(action_idx, reward, species)
            os.remove(temp_audio)

        agente.decay_epsilon()

    print(f"\n {audio_name} completado. Mejor confianza: {mejor_global:.3f}")
    return audio_name, mejor_global, mejor_filtros, mejor_especie

# -------------------- COMPARACIÓN --------------------
def comparar_resultados(mejores_conf):
    tabla = []
    for audio_name, (mejor_conf, (q, r, f), mejor_especie) in mejores_conf.items():
        original_txt = os.path.join(ORIGINAL_CSV_DIR, f"{audio_name}.BirdNET.selection.table.txt")
        if os.path.exists(original_txt):
            try:
               
                df = pd.read_csv(original_txt)

                if 'Scientific name' in df.columns and not df.empty:
                    df['Scientific name'] = df['Scientific name'].astype(str).str.lower().str.strip()
                    mejor_especie_proc = mejor_especie.lower().strip()
                    especie_match = df[df['Scientific name'] == mejor_especie_proc]
                    if not especie_match.empty:
                        original_conf = especie_match['Confidence'].max()
                        coinciden = '✅'
                    else:
                        original_conf, coinciden = 0.0, '❌'
                else:
                    original_conf, coinciden = 0.0, '❌'
            except Exception as e:
                print(f" Error leyendo {original_txt}: {e}")
                original_conf, coinciden = np.nan, '❌'
        else:
            original_conf, coinciden = np.nan, '❌'

        tabla.append({
            'Audio': audio_name,
            'Original_Conf': original_conf,
            'Con_Filtros_Conf': mejor_conf,
            'Mejora': mejor_conf - original_conf if pd.notnull(original_conf) else np.nan,
            'Q': q, 'R': r, 'F': f,
            'Coinciden': coinciden
        })

    df_result = pd.DataFrame(tabla)
    df_result.to_csv(os.path.join(BASE_DIR, "comparacion_resultados.csv"), index=False)

    print("\n Comparación de resultados:")
    print(df_result)

def generar_resultados_originales_sin_filtro(fragmentos):
    print("\nGenerando CSV originales sin filtros con BirdNET...")
    for frag_path in fragmentos:
        nombre = os.path.splitext(os.path.basename(frag_path))[0]
        temp_audio = os.path.join(TEMP_EVAL, f"{nombre}.wav")  
        shutil.copy(frag_path, temp_audio)

        subprocess.run([
            sys.executable, "-m", "birdnet_analyzer.analyze",
            TEMP_EVAL, "--output", TEMP_RESULT,
            "--lat", str(LAT), "--lon", str(LON),
            "--min_conf", str(MIN_CONF), "--rtype", "csv"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        resultado_csv = next((os.path.join(TEMP_RESULT, f) for f in os.listdir(TEMP_RESULT)
                             if f.endswith(".BirdNET.results.csv")), None)

        if resultado_csv:
            destino_csv = os.path.join(ORIGINAL_CSV_DIR, f"{nombre}.BirdNET.selection.table.txt") 
            shutil.move(resultado_csv, destino_csv)

        os.remove(temp_audio)



if __name__ == "__main__":
    print("=== Procesamiento de audio con Q-learning y BirdNET ===")
    
    ruta_audio = input(" Ingresa la ruta del archivo de audio (.wav o .ogg): ").strip()
    umbral = float(input(" Ingresa el umbral de energía (recomendado 0.05): ").strip() or 0.05)
    duracion = int(input(" Ingresa la duración de los fragmentos en segundos (recomendado 6): ").strip() or 6)
    tiempo = int(input(" Ingresa el tiempo sostenido en segundos por encima del umbral (recomendado 2): ").strip() or 2)

    if not os.path.isfile(ruta_audio):
        print(f" Error: no se encontró el archivo '{ruta_audio}'")
        sys.exit(1)

    fragmentos = dividir_audio_por_energia(ruta_audio, duracion, umbral, tiempo, SEGMENTOS_DIR)

    generar_resultados_originales_sin_filtro(fragmentos)

    mejores_confianzas = {}
    for frag in fragmentos:
        nombre, mejor, filtros, especie = entrenar_audio(frag)
        mejores_confianzas[nombre] = (mejor, filtros, especie)

    comparar_resultados(mejores_confianzas)

