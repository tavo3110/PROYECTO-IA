# Sistema Inteligente de Identificación de Aves con Aprendizaje Reforzado, BirdNET y Filtrado Kalman

---

## Tabla de Contenidos

- [Descripción del proyecto](#descripción-del-proyecto)
- [Estructura del Repositorio](#estructura-del-repositorio)
- [Instalación y Requisitos](#instalación-y-requisitos)
- [Uso del Proyecto](#uso-del-proyecto)
- [Explicación Detallada del Pipeline](#explicación-detallada-del-pipeline)
- [Resultados](#resultados)


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
├── ejecutable_proyecto.py            # Script principal que automatiza todo el pipeline
├── cuaderno_explicativo.ipynb        # Notebook explicativo con análisis y resultados paso a paso
├── resultados_proyecto/              # Carpeta con los resultados organizados por etapa y experimento
│   ├── experimento_1/                # Resultados del experimento 1 (Numero de epocas y pasos necesarios para encontrar el mejor filtro.)
│   ├── etapa_2_resultados/           # Resultados de la etapa 2 del pipeline
│   ├── experimento_2/                # Comparacion de espectogramas y confianza para audios sin filtro y luego con el mejor filtro encontrado
│   └── validacion_birdnet/           # Validacion de confianza de birdnet con audios etiquetados de el dataset Birdcleff
├── requirements.txt                  # Requisitos y dependencias del entorno
└── README.md                         # Documentación principal del proyecto

## Instalacion y requisitos