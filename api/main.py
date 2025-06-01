# api/main.py

import os
import joblib
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from sklearn.metrics.pairwise import sigmoid_kernel
from pathlib import Path # Para construir rutas de forma más robusta

# --- Configuración de la Aplicación FastAPI ---
app = FastAPI(
    title="Anime Recommendation API",
    description="Una API simple para obtener recomendaciones de anime basadas en géneros.",
    version="0.1.0"
)

# --- Configuración de CORS ---

origins = [
    "http://localhost", # Si tu frontend corre en localhost sin puerto específico (raro)
    "http://localhost:3000", # Ejemplo para React, Vue, Angular en desarrollo
    "http://localhost:5173", # Ejemplo para Vite en desarrollo
    "http://127.0.0.1:5500", # Ejemplo si abres un HTML con Live Server de VS Code
    "https://simple-anime-recommender.netlify.app", # ¡AÑADE LA URL DE TU FRONTEND EN PRODUCCIÓN!
]

# Si vas a desplegar tu frontend en Render también, Render te dará una URL para él.
# Ejemplo: "https://mi-frontend-anime.onrender.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # O usa ["*"] para permitir todos durante el desarrollo inicial
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], # Métodos HTTP permitidos
    allow_headers=["*"], # Cabeceras HTTP permitidas
)

# --- Cargar Modelos y Datos al Inicio ---
# Determinar la ruta base de la aplicación (donde se encuentra main.py)
BASE_DIR = Path(__file__).resolve().parent
MODEL_ASSETS_DIR = BASE_DIR / "model_assets"

# Variables globales para almacenar los artefactos cargados
TFV = None
TFV_MATRIX = None
ANIME_NAME_INDICES = None
ANIME_METADATA = None

@app.on_event("startup")
async def load_model_assets():
    global TFV, TFV_MATRIX, ANIME_NAME_INDICES, ANIME_METADATA
    print(f"Cargando artefactos desde: {MODEL_ASSETS_DIR}")
    try:
        TFV = joblib.load(MODEL_ASSETS_DIR / 'tfv.pkl')
        TFV_MATRIX = joblib.load(MODEL_ASSETS_DIR / 'tfv_matrix.pkl')
        ANIME_NAME_INDICES = joblib.load(MODEL_ASSETS_DIR / 'anime_name_indices.pkl')
        ANIME_METADATA = pd.read_parquet(MODEL_ASSETS_DIR / 'anime_metadata.parquet')
        print("Artefactos del modelo cargados exitosamente.")
    except FileNotFoundError as e:
        print(f"Error: No se encontró un archivo de modelo esencial: {e}")
        # Podrías decidir detener la aplicación o manejarlo de otra forma
        # Por ahora, la aplicación podría iniciarse pero los endpoints fallarían.
        # Para un producto real, querrías un manejo de errores más robusto aquí.
    except Exception as e:
        print(f"Error cargando los artefactos del modelo: {e}")

# --- Lógica de Recomendación ---
def get_anime_recommendations(name: str, top_n: int = 10):
    if not all([TFV_MATRIX is not None, ANIME_NAME_INDICES is not None, ANIME_METADATA is not None]):
        raise HTTPException(status_code=503, detail="Model assets no están cargados. Por favor, revisa los logs del servidor.")

    if name not in ANIME_NAME_INDICES:
        # Intenta buscar con una coincidencia parcial o insensible a mayúsculas/minúsculas
        # Esto es opcional pero mejora la experiencia de usuario
        potential_matches = [idx_name for idx_name in ANIME_NAME_INDICES.index if name.lower() in idx_name.lower()]
        if not potential_matches:
            raise HTTPException(status_code=404, detail=f"Anime '{name}' no encontrado en nuestra base de datos.")
        # Si hay múltiples coincidencias, podrías devolverlas o tomar la primera
        # Por simplicidad, tomamos la primera si existe alguna
        actual_name = potential_matches[0]
        print(f"Input '{name}' no encontrado. Usando coincidencia: '{actual_name}'")

    else:
        actual_name = name

    try:
        current_name_idx = ANIME_NAME_INDICES[actual_name]
    except KeyError:
         # Este caso no debería ocurrir si la lógica anterior de potential_matches funciona
         # o si el nombre original estaba en los índices.
        raise HTTPException(status_code=404, detail=f"Error interno al obtener el índice para '{actual_name}'.")


    # Calcular similitud solo para el anime actual
    # sig_score_row es un array 1D con las similitudes del anime actual contra todos los demás
    sig_score_row = sigmoid_kernel(TFV_MATRIX[current_name_idx], TFV_MATRIX).flatten()

    # Formatear los valores de similitud
    sig_scores_with_indices = list(enumerate(sig_score_row))

    # Ordenar por descendente
    sig_scores_with_indices = sorted(sig_scores_with_indices, key=lambda x: x[1], reverse=True)

    # Seleccionar top_n (omitir el primero, que es el mismo anime con score 1.0)
    # Asegurarse de no pedir más recomendaciones de las disponibles (menos el propio anime)
    num_available_recommendations = len(sig_scores_with_indices) - 1
    actual_top_n = min(top_n, num_available_recommendations)
    
    sig_scores_with_indices = sig_scores_with_indices[1 : actual_top_n + 1]


    # Obtener solo los índices originales del DataFrame
    recommendation_original_indices = [x[0] for x in sig_scores_with_indices]

    # Encontrar los datos de recomendación usando los índices y el DataFrame de metadatos cargado
    recommendations_df = ANIME_METADATA.iloc[recommendation_original_indices]

    # Formatear como lista de diccionarios para la respuesta JSON
    recommendations_list = []
    for i, (original_idx, score_tuple) in enumerate(zip(recommendation_original_indices, sig_scores_with_indices)):
        anime_data = ANIME_METADATA.iloc[original_idx] # Acceder por el índice original
        recommendations_list.append({
            "rank": i + 1,
            "anime_name": anime_data["name"],
            "rating": anime_data["rating"] if pd.notna(anime_data["rating"]) else "N/A", # Manejar NaN en rating
            "similarity_score": round(score_tuple[1], 4) # Opcional: devolver el score
        })
    
    return {
        "input_anime": actual_name,
        "recommendations": recommendations_list
        }

# --- Endpoints de la API ---
@app.get("/")
async def read_root():
    return {"message": "Bienvenido a la API de Recomendación de Anime. Usa el endpoint /recommendations/{anime_name}"}

@app.get("/recommendations/{anime_name}")
async def recommend_anime(anime_name: str, top_n: int = 10):
    """
    Obtiene recomendaciones de anime para un anime dado.
    - **anime_name**: Nombre del anime para el cual obtener recomendaciones.
    - **top_n**: (Opcional) Número de recomendaciones a devolver (por defecto 10).
    """
    if top_n <= 0:
        raise HTTPException(status_code=400, detail="top_n debe ser un entero positivo.")
    
    recommendations = get_anime_recommendations(anime_name, top_n)
    return recommendations

# --- Para ejecutar la aplicación (si ejecutas este archivo directamente) ---
# Esto es útil para desarrollo. Para producción, usarías un servidor ASGI como Uvicorn directamente.
# Ejemplo: uvicorn main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    # Cargar modelos manualmente si no se usa el evento de startup de FastAPI (al ejecutar con python main.py)
    # En un entorno de producción con Uvicorn, el evento "startup" se encargará de esto.
    # Sin embargo, para facilitar la ejecución directa "python main.py", podrías llamar a load_model_assets aquí
    # o simplemente dejar que Uvicorn lo maneje.
    # Para este ejemplo, asumimos que Uvicorn gestionará el evento de startup.
    
    uvicorn.run(app, host="0.0.0.0", port=8000)