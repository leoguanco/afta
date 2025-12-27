# Tesina – Software de Análisis de Fútbol con IA (Video + Datos + LLM)

> Documento maestro (Markdown) con **todo lo acordado**: objetivos, marco teórico, arquitectura, roadmap, datasets, evaluación y próximos pasos. Listo para usar como base de tesina y para el repositorio.

---

## 1. Resumen Ejecutivo
Desarrollar un software de análisis táctico de fútbol que combine **visión por computadora** (detección + tracking), **datos estructurados** (eventos de partido) y **modelos de lenguaje (LLM)** para generar **reportes tácticos automáticos**: patrones, debilidades y recomendaciones.

**Output**: dashboard + informe (JSON/PDF) con visualizaciones y análisis en lenguaje natural.

---

## 2. Objetivos
### Objetivo General
Construir un sistema híbrido (video + datos + LLM) capaz de detectar patrones de juego y generar análisis táctico accionable.

### Objetivos Específicos
- Detectar y trackear jugadores y pelota desde video.
- Proyectar posiciones a coordenadas reales del campo.
- Integrar eventos (pases, tiros) y métricas (xT, PPDA, compactness).
- Clasificar fases del juego y patrones recurrentes.
- Generar reportes automáticos con un LLM (RAG).

---

## 3. Marco Teórico (Análisis Táctico)
### 3.1 Estructuras y Formaciones
- Diferencia entre estructura inicial y estructura en fase.
- Conceptos: amplitud, profundidad, densidad, altura del bloque.

### 3.2 Fases del Juego
- Ataque organizado
- Defensa organizada
- Transición ataque–defensa
- Transición defensa–ataque

### 3.3 Principios Ofensivos
- Superioridades (numérica, posicional, cualitativa)
- Juego entre líneas, tercer hombre, triangulaciones

### 3.4 Principios Defensivos
- Presión (alta/media/baja)
- Basculación y coberturas
- Altura y sincronización de la línea defensiva

### 3.5 Métricas Modernas
- xG, xT (Expected Threat)
- PPDA
- Pases progresivos
- Compactness

---

## 4. Arquitectura del Sistema (End-to-End)

```
[Video] ----\
              > Ingesta -> Video Processor -> Tracks (x,y,t)
[Eventos] --/                               |
                                             v
                                   Feature Extraction
                                             |
                                 ML (clasificación/clustering)
                                             |
                                   Indexación (RAG)
                                             |
                                          LLM
                                             |
                               Reporte JSON/PDF + Dashboard
```

### 4.1 Componentes
- **Ingesta**: videos y eventos (StatsBomb/Metrica)
- **Video Processor**: YOLO + ByteTrack + Homografía
- **Feature Extractor**: métricas posicionales y de eventos
- **ML Models**: clasificación de fases y patrones
- **RAG + LLM**: interpretación y generación de reportes
- **API/Dashboard**: visualización y exportes

---

## 5. Stack Tecnológico
- **Lenguaje**: Python
- **CV**: OpenCV, Ultralytics YOLOv8, ByteTrack
- **Datos**: pandas, numpy, parquet
- **ML**: scikit-learn, PyTorch
- **LLM/RAG**: LangChain, FAISS/Chroma
- **API**: FastAPI
- **Infra**: Docker, docker-compose, MinIO/S3, Postgres

---

## 6. Esquemas de Datos
### Tracks
```json
{ "frame": 123, "time_s": 45.2, "track_id": 7, "x_m": 34.2, "y_m": 18.6 }
```

### Evento Enriquecido
```json
{ "type": "pass", "time_s": 45.8, "from": 7, "to": 10, "start": [32,20], "end": [55,22] }
```

### Snippet para RAG
```json
{ "text": "Salida por banda derecha con 8 pases y xT 0.05", "tags": ["salida_banda"] }
```

---

## 7. Roadmap de Implementación (8 semanas)
- **S1**: Fundamentos tácticos + setup
- **S2**: Detección (YOLO) + pruebas
- **S3**: Tracking + homografía
- **S4**: Ingesta de eventos + sincronización
- **S5**: Features + métricas
- **S6**: ML (clasificación/clustering)
- **S7**: RAG + LLM
- **S8**: Evaluación + redacción tesina

---

## 8. Evaluación
- **Detección**: mAP@0.5
- **Tracking**: IDF1, MOTA
- **Proyección**: RMSE (m)
- **Clasificación**: Accuracy/F1
- **LLM**: evaluación humana (utilidad, coherencia)

---

## 9. Consideraciones Éticas
- Respeto de licencias de datos y video
- Anonimización si corresponde
- Uso responsable de análisis automatizado

---

## 10. Fuentes y Recursos
### Datasets
- StatsBomb Open Data
- Metrica Sports Sample Data

### Táctica
- *Soccermatics* – David Sumpter
- *Juego de Posición* – Óscar Cano
- Canales: Tifo Football, Friends of Tracking

### CV y ML
- Ultralytics YOLO Docs
- OpenCV Homography
- ByteTrack GitHub

### LLM/RAG
- LangChain Docs
- FAISS / Chroma

---

## 11. Próximos Pasos
- Crear repositorio Git con esta estructura
- Implementar MVP de tracking + features
- Integrar RAG y generar primer reporte
- Preparar demo y slides de defensa

---

**Autor**: (tu nombre)
**Universidad**: (completar)
**Año**: 2025
