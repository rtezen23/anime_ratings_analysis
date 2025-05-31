from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from anime_recommender import AnimeRecommender
import os

# Inicializar FastAPI
app = FastAPI(
    title="Anime Recommendation API",
    description="Sistema de recomendación de anime basado en contenido",
    version="1.0.0"
)

# CORS para permitir requests desde React
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # En producción, especifica tus dominios
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global recommender instance
recommender = None

# Pydantic models
class RecommendationRequest(BaseModel):
    anime_name: str
    num_recommendations: Optional[int] = 10

class RecommendationItem(BaseModel):
    rank: int
    name: str
    rating: float
    genre: str
    similarity_score: float

class RecommendationResponse(BaseModel):
    success: bool
    message: str
    data: List[RecommendationItem]
    total_recommendations: int

class AnimeListResponse(BaseModel):
    success: bool
    message: str
    animes: List[str]
    total_count: int

# Startup event
@app.on_event("startup")
async def startup_event():
    global recommender
    recommender = AnimeRecommender()
    
    # Intentar cargar modelo pre-entrenado
    model_path = "anime_model.pkl"
    if os.path.exists(model_path):
        success = recommender.load_model(model_path)
        if success:
            print("✅ Modelo pre-entrenado cargado exitosamente")
        else:
            print("❌ Error cargando modelo pre-entrenado")
            # Aquí podrías entrenar desde cero si es necesario
    else:
        print("⚠️  No se encontró modelo pre-entrenado")
        print("💡 Asegúrate de tener 'anime_model.pkl' en el directorio")

# Routes
@app.get("/")
async def root():
    return {
        "message": "Anime Recommendation API",
        "status": "active",
        "version": "1.0.0",
        "endpoints": ["/animes", "/recommend"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_loaded = recommender is not None and recommender.sig_matrix is not None
    return {
        "status": "healthy" if model_loaded else "model_not_loaded",
        "model_loaded": model_loaded
    }

@app.get("/animes", response_model=AnimeListResponse)
async def get_anime_list():
    """Obtiene lista completa de animes disponibles"""
    if recommender is None or recommender.sig_matrix is None:
        raise HTTPException(
            status_code=503, 
            detail="Modelo no disponible. El servidor se está inicializando."
        )
    
    try:
        anime_list = recommender.get_anime_list()
        return AnimeListResponse(
            success=True,
            message="Lista de animes obtenida exitosamente",
            animes=anime_list,
            total_count=len(anime_list)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Genera recomendaciones para un anime específico"""
    if recommender is None or recommender.sig_matrix is None:
        raise HTTPException(
            status_code=503, 
            detail="Modelo no disponible. El servidor se está inicializando."
        )
    
    # Validar número de recomendaciones
    if request.num_recommendations < 1 or request.num_recommendations > 50:
        raise HTTPException(
            status_code=400, 
            detail="num_recommendations debe estar entre 1 y 50"
        )
    
    try:
        result = recommender.recommend(
            request.anime_name, 
            n_recommendations=request.num_recommendations
        )
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        # Convertir a formato de respuesta
        recommendations = [
            RecommendationItem(**item) for item in result["data"]
        ]
        
        return RecommendationResponse(
            success=True,
            message=result["message"],
            data=recommendations,
            total_recommendations=len(recommendations)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/anime/{anime_name}")
async def get_anime_info(anime_name: str):
    """Obtiene información específica de un anime"""
    if recommender is None or recommender.anime_data is None:
        raise HTTPException(
            status_code=503, 
            detail="Modelo no disponible."
        )
    
    try:
        anime_info = recommender.anime_data[
            recommender.anime_data["name"].str.contains(anime_name, case=False)
        ]
        
        if anime_info.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"Anime '{anime_name}' no encontrado"
            )
        
        # Tomar el primer resultado si hay múltiples matches
        anime = anime_info.iloc[0]
        
        return {
            "success": True,
            "data": {
                "name": anime["name"],
                "rating": float(anime["rating"]),
                "genre": anime["genre"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint no encontrado", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Error interno del servidor", "status_code": 500}

if __name__ == "__main__":
    print("🚀 Iniciando Anime Recommendation API...")
    print("📡 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",  # Cambia "main" por el nombre de tu archivo
        host="0.0.0.0",
        port=8000,
        reload=True  # Solo para desarrollo
    )