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

# Configuración CORS para producción
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # "https://tu-frontend.netlify.app",
    "https://anime-ratings-analysis.onrender.com/",
]

# En producción, puedes ser más específico con los origins
if os.getenv("ENVIRONMENT") == "production":
    origins = [
        "https://anime-ratings-analysis.onrender.com/",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
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

# Configuración del modelo
MODEL_CONFIG = {
    "google_drive_file_id": "TU_FILE_ID_AQUI",  # ⚠️ CAMBIAR POR TU FILE ID REAL
    "model_path": "anime_model.pkl"
}

# Startup event
@app.on_event("startup")
async def startup_event():
    global recommender
    recommender = AnimeRecommender()
    
    # Configuración del file ID desde variables de entorno o config
    file_id = os.getenv("MODEL_FILE_ID", MODEL_CONFIG["google_drive_file_id"])
    model_path = MODEL_CONFIG["model_path"]
    
    if file_id == "TU_FILE_ID_AQUI":
        print("⚠️  ADVERTENCIA: FILE_ID no configurado!")
        print("💡 Configura MODEL_FILE_ID como variable de entorno o cambia MODEL_CONFIG")
        return
    
    # Intentar descargar modelo si no existe
    if not os.path.exists(model_path):
        print("🔄 Modelo no encontrado localmente, descargando...")
        success = recommender.download_model(file_id, model_path)
        if not success:
            print("❌ Error descargando modelo desde Google Drive")
            return
    
    # Cargar modelo
    success = recommender.load_model(model_path)
    if success:
        print("✅ Modelo cargado exitosamente")
        print(f"📊 Animes disponibles: {len(recommender.get_anime_list())}")
    else:
        print("❌ Error cargando modelo")
        # Intentar eliminar archivo corrupto para próximo intento
        if os.path.exists(model_path):
            try:
                os.remove(model_path)
                print("🧹 Archivo corrupto eliminado")
            except:
                pass

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
        "model_loaded": model_loaded,
        "total_animes": len(recommender.get_anime_list()) if model_loaded else 0
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
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)