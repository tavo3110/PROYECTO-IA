# Sistema Inteligente de Identificación de Aves con Aprendizaje Reforzado, BirdNET y Filtrado Kalman

---

## Tabla de Contenidos

- [Descripción del proyecto](#descripción-del-proyecto)
- [Estructura del Repositorio](#estructura-del-repositorio)
- [Instalación y Requisitos](#instalación-y-requisitos)
- [Uso del Proyecto](#uso-del-proyecto)
- [Resultados del Proyecto](#Resultados-del-Proyecto)


# Descripción del Proyecto

Este proyecto se centra en mejorar la calidad de grabaciones ambientales (al aire libre) afectadas por ruido, con el objetivo de resaltar las vocalizaciones de aves presentes en los audios. Para lograrlo, se aplican técnicas de filtrado digital, específicamente:

- **Filtro pasabanda** para aislar las frecuencias típicas del canto de aves.
- **Filtro de Kalman** para suavizar la señal y reducir el ruido residual de forma adaptativa.

## Configuración de Filtros
Las configuraciones de estos filtros (parámetros `Q`, `R` y frecuencia de corte `fc`) fueron seleccionadas utilizando un enfoque de **aprendizaje por refuerzo (Reinforcement Learning)**. En este contexto:

- El agente explora diferentes combinaciones de filtros.
- La recompensa está basada en el nivel de confianza proporcionado por **BirdNET-R**, una herramienta de inferencia acústica para detección de especies.
- El objetivo del agente es aprender qué combinaciones optimizan la calidad de detección.

## Rol de BirdNET-R
El papel central de **BirdNET-R** en este proyecto consiste en medir objetivamente el impacto del preprocesamiento del audio, ya que una mayor confianza en la detección de especies sugiere una mejora en la calidad de la señal filtrada.

## Resumen
En resumen, este proyecto combina:
- Técnicas de procesamiento de señales
- Inteligencia artificial
- Análisis acústico

con el propósito de demostrar cómo el **aprendizaje por refuerzo** puede mejorar significativamente la calidad de las grabaciones de campo para estudios de biodiversidad.


---

## Descripción General

Este proyecto tiene como objetivo analizar grabaciones de audio ambientales utilizando BirdNET, procesar y segmentar los audios en base a energía, y aplicar un enfoque de aprendizaje por refuerzo para optimizar la selección de segmentos relevantes. Toda la lógica está organizada en un pipeline automatizado para facilitar su ejecución.

---

## Estructura del Repositorio
- ejecutable_proyecto.py               # Script principal que automatiza todo el pipeline
- cuaderno_interactivo.ipynb           # Notebook explicativo con análisis y resultados paso a paso
- resultados_proyecto/                 # Carpeta con los resultados organizados por etapa y experimento
  - experimento_1/                     # Resultados del experimento 1 (Numero de epocas y pasos necesarios para encontrar el mejor filtro.)
  - etapa_2_resultados/                # Resultados de la etapa 2 del pipeline
  - experimento_2/                     # Comparacion de espectogramas y confianza para audios sin filtro y luego con el mejor filtro encontrado
  - validacion_birdnet/                # Validacion de confianza de birdnet con audios etiquetados de el dataset Birdcleff
- requirements.txt                     # Requisitos y dependencias del entorno
- README.md                            # Documentación principal del proyecto

# Instalacion y requisitos

### Clonar el repositorio

git clone https://github.com/tavo3110/PROYECTO-IA.git

```bash
cd PROYECTO-IA
```


### Crear un entorno virtual (opcional pero recomendado)

```bash
python -m venv env
source env/bin/activate      # En Windows: env\Scripts\activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

## Descargar BIRDNET ANALYZER

Para procesar audios con el modelo de detección de aves BirdNET, sigue los siguientes pasos para descargar e instalar BirdNET Analyzer:

### Pasos para descargar:

1. **Descargar BirdNET Analyzer**  
   🔗 [Repositorio oficial de BirdNET](https://github.com/birdnet-team/BirdNET-Analyzer)  
   - Haz clic en el botón **"Code"**  
   - Luego selecciona **"Download ZIP"**  
   - Extrae el contenido del archivo en una carpeta conocida, por ejemplo:  
     `D:\BirdNET-Analyzer-main`

2. **Crear un entorno virtual con Python 3.11.13**  
   Puedes usar Conda u otro gestor de entornos. Con Conda:  

```bash
conda create -n birdnet python=3.11.13 -y
conda activate birdnet
```

3. **Ir a la carpeta donde se extrajo BirdNET Analyzer**

```bash
cd /d "D:\BirdNET-Analyzer-main"
```

4. **Instalar las dependencias necesarias**

```bash
pip install -e .
```

5. **Ejecutar BirdNET Analyzer sobre tu carpeta de audios**

Asegúrate de modificar las rutas según tu estructura de archivos:

```bash
python -m birdnet_analyzer.analyze "D:\Mi Escritorio\Proyecto de IA\Con kalman+IA" ^
--output "D:\Mi Escritorio\Proyecto de IA\Con kalman+IA\resultados" ^
--lat 10.45 --lon -73.25 --min_conf 0.6 --rtype csv
```

### NOTAS ADICIONALES

- Puedes modificar la carpeta de entrada y salida a conveniencia.
- Los parámetros --lat y --lon indican la ubicación geográfica (en este caso, Cesar - Colombia).
- El valor --min_conf 0.6 define la confianza mínima para aceptar una detección.
- El parámetro --rtype csv indica que los resultados se exportan en formato CSV.

## Descargar el dataset de BirdCLEF 2025

Para validar y probar el proyecto con datos reales, sigue estos pasos para obtener el dataset de la competencia BirdCLEF 2025:

### Pasos para descargar:
1. **Accede a la página oficial** del desafío en Kaggle:    
   🔗 [BirdCLEF 2025 Competition](https://www.kaggle.com/c/birdclef-2025)

2. **Ve a la sección de datos** mediante:  
   🔗 [Datos de BirdCLEF 2025](https://www.kaggle.com/c/birdclef-2025/data)  
   (O haz clic en la pestaña "Data" en la página de la competencia)

3. **Únete a la competencia** haciendo clic en el botón _"Join Competition"_  
   (Requisito para habilitar la descarga)

4. **Descarga el dataset completo**:
   - Desplázate al final de la página de datos
   - Haz clic en el botón de descarga todo el cual descargara un archivo(.zip)


Al descomprimir el archivo descargado encontrarás una carpeta llamada birdcleff-2025+ el cual tendra diferentes archivos pero para el proyecto los archivos importantes a tener en cuenta fueron la carpeta de train audio en donde se encontraban aquellas carpetas codificadas en las cuales se encontraban los audios etiquetados y el archivo csv llamado taxonomy en el cual se decia como estaba codificada cada carpeta y a que especie pertenecia

# Uso del Proyecto

Este proyecto se ejecuta de forma automática mediante el archivo `ejecutabl proyecto.py`, el cual recorre todas las etapas del pipeline:

1. Segmentación del audio
2. Filtrado de los fragmentos (pasabanda + Kalman)
3. Análisis con BirdNET-R a audios sin filtro y con filtros
4. Entrenamiento y evaluación del agente de Aprendizaje por Refuerzo (RL)
5. Comparacion entre confianza sin filtros y con filtros

## Requisitos previos

Antes de ejecutar el script, asegúrate de:

- Tener una carpeta de entrada que contenga:
  - El archivo de audio (.wav o .ogg) que deseas analizar
  - Una subcarpeta llamada `salida birdnet/` dentro de esa misma carpeta, donde se almacenarán los resultados del análisis original con BirdNET (sin filtros)

### Ejemplo de estructura esperada:

/mi_carpeta_audio/
├── fragmento_001.wav
└── salida_birdnet/

- Tener BirdNET correctamente instalado y funcional desde la terminal (debe poder ejecutarse sin errores)

## Ejecutar el pipeline completo

- Desde la terminal, ejecuta:

```bash
python ejecutable_proyecto.py
```

## Interacción con el Sistema

El sistema solicitará los siguientes datos durante la ejecución:

1. **Ruta del archivo de audio**  
   `Ingrese la ruta completa del archivo de audio (sin comillas):`

2. **Parámetros de configuración**  
   Se deberán establecer:
   - Duración de los fragmentos (en segundos)
   - Energía mínima para segmentar
   - Duración mínima de baja energía para realizar el corte

    *Nota:* Si no se introducen valores, se usarán los valores por defecto recomendados solo presionando enter.

## Parámetros Avanzados

Los siguientes parámetros pueden modificarse directamente editando el archivo `ejecutable proyecto.py`:

| Parámetro | Descripción |
|-----------|-------------|
| Número de épocas | Cantidad de iteraciones completas sobre el dataset |
| Definir las acciones | Posibles decisiones que puede tomar el agente RL es decir Q, R y fc|
| Máximos pasos por episodio | Límite de pasos por ciclo de entrenamiento |
| Rangos de búsqueda | Intervalos para exploración de hiperparámetros |

## Resultados Generados

Al finalizar la ejecución, el sistema creará los siguientes archivos y directorios:

- fragmentos_audio/                # Fragmentos generados del audio original
- temp_eval/                       # Carpeta temporal para procesamiento (se vacía automáticamente)
- temp_eval_result/                # Carpeta temporal para procesamiento (se vacía automáticamente)
- salida_birdnet/*.txt             # Resultados de BirdNET sin filtros (referencia)
- resultados_csv_birdnet/          # CSV con los resultados de BirdNET sobre audios filtrados
- comparacion_resultados.csv       # Comparación de puntuaciones de confianza entre fragmentos sin filtro y mejores filtrados por RL

# Resultados del Proyecto

Los resultados del proyecto se obtuvieron principalmente a partir del cuaderno interactivo (`cuaderno interactivo.ipynb`), el cual analiza y visualiza los datos generados por el pipeline. En este repositorio, se encuentran organizados en varias carpetas clave dentro del directorio `resultados proyecto/`, las cuales documentan el impacto del filtrado y la efectividad de BirdNET en distintos escenarios. A continuación se detallan:

### `etapa_2_resultados/`
Contiene los resultados principales del proyecto:

- `comparacion_resultados.csv`: Comparación de mejora de los 50 audios procesados por el pipeline. Muestra las diferencias de confianza de BirdNET antes y después del filtrado, junto con los filtros óptimos seleccionados.
- `comparacion_resultados.png`: Representación gráfica del archivo CSV anterior. Muestra, para cada audio, la mejora o desmejora en la confianza de detección tras el filtrado.

### `experimento_1/`
Permite analizar cómo afecta el número de épocas y pasos del algoritmo de aprendizaje por refuerzo (RL) en la confianza de detección de BirdNET:

- Archivos `.png` con gráficas de evolución de la confianza a lo largo de múltiples configuraciones de entrenamiento.
- Estas gráficas ayudan a identificar el número óptimo de épocas y pasos necesarios para una mejora significativa en los resultados.

### `experimento_2/`
Estudia visualmente el impacto de los filtros mediante espectrogramas:

- Espectrogramas en formato `.png` de audios sin filtrar y con filtrado aplicado.
- Permiten visualizar cómo los filtros modifican el contenido frecuencial del audio.
- Archivos `.csv` con la confianza de BirdNET en los audios originales y filtrados, como respaldo cuantitativo a los resultados visuales.

### `validacion_birdnet/`
Evalúa la precisión y confiabilidad de BirdNET usando audios previamente etiquetados (del dataset BirdCLEF):

- CSVs con resultados de predicciones de BirdNET en audios con etiquetas conocidas.
- Gráficas que muestran la tasa de aciertos de BirdNET comparando la especie real y la detectada.
- Esta validación fortalece la confianza en el uso de BirdNET como herramienta de análisis en el pipeline.

---

Estos resultados en conjunto permiten evaluar de forma visual, cuantitativa y comparativa el impacto del filtrado optimizado por aprendizaje por refuerzo, validando tanto el funcionamiento del pipeline como la confiabilidad de BirdNET.

