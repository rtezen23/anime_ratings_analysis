import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import sigmoid_kernel
import joblib
import os
import requests
import time

class AnimeRecommender:
    def __init__(self):
        self.sig_matrix = None
        self.rec_indices = None
        self.anime_data = None
        self.tfv = None
        
    def download_model(self, file_id, model_path="anime_model.pkl", max_retries=3):
        """
        Descarga el modelo desde Google Drive con manejo mejorado
        
        Args:
            file_id: ID del archivo en Google Drive
            model_path: Ruta donde guardar el modelo
            max_retries: Número máximo de intentos
        """
        if os.path.exists(model_path):
            file_size = os.path.getsize(model_path)
            if file_size > 1000:  # Archivo válido (> 1KB)
                print(f"📂 Modelo ya existe localmente: {model_path} ({file_size/1024/1024:.1f}MB)")
                return True
            else:
                print(f"🗑️ Eliminando archivo corrupto: {model_path}")
                os.remove(model_path)
        
        print("🔄 Descargando modelo desde Google Drive...")
        
        for attempt in range(max_retries):
            try:
                print(f"📥 Intento {attempt + 1}/{max_retries}")
                
                # URLs para probar (Google Drive tiene diferentes formatos)
                urls_to_try = [
                    f"https://drive.google.com/uc?export=download&id={file_id}",
                    f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t",
                    f"https://docs.google.com/uc?export=download&id={file_id}",
                ]
                
                success = False
                for i, url in enumerate(urls_to_try):
                    try:
                        print(f"🌐 Probando URL {i+1}: {url[:50]}...")
                        
                        # Headers para simular un navegador
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate',
                            'Connection': 'keep-alive',
                        }
                        
                        # Primera petición para obtener cookies/tokens si es necesario
                        session = requests.Session()
                        response = session.get(url, headers=headers, stream=True, timeout=30)
                        
                        # Verificar si necesitamos confirmar descarga (archivos grandes)
                        if 'download_warning' in response.text or 'virus scan warning' in response.text:
                            print("⚠️ Detectada advertencia de Google Drive, intentando bypass...")
                            # Buscar token de confirmación
                            for line in response.text.split('\n'):
                                if 'confirm=' in line and 'download' in line:
                                    import re
                                    confirm_token = re.search(r'confirm=([a-zA-Z0-9\-_]+)', line)
                                    if confirm_token:
                                        confirm_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={confirm_token.group(1)}"
                                        response = session.get(confirm_url, headers=headers, stream=True, timeout=60)
                                        break
                        
                        response.raise_for_status()
                        
                        # Verificar que la respuesta tenga contenido
                        content_length = response.headers.get('content-length')
                        if content_length:
                            size_mb = int(content_length) / 1024 / 1024
                            print(f"📊 Tamaño esperado: {size_mb:.1f}MB")
                        
                        # Descargar archivo
                        downloaded = 0
                        chunk_size = 32768  # 32KB chunks
                        
                        with open(model_path, "wb") as f:
                            for chunk in response.iter_content(chunk_size=chunk_size):
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    
                                    # Mostrar progreso cada 10MB
                                    if downloaded % (10 * 1024 * 1024) == 0:
                                        progress_mb = downloaded / 1024 / 1024
                                        print(f"📥 Descargando... {progress_mb:.1f}MB")
                        
                        # Verificar que el archivo se descargó correctamente
                        file_size = os.path.getsize(model_path)
                        if file_size < 1000:  # Menos de 1KB indica error
                            print(f"⚠️ Archivo muy pequeño ({file_size} bytes), probablemente corrupto")
                            if os.path.exists(model_path):
                                os.remove(model_path)
                            continue
                        
                        print(f"✅ Modelo descargado exitosamente: {model_path} ({file_size/1024/1024:.1f}MB)")
                        success = True
                        break
                        
                    except requests.exceptions.RequestException as e:
                        print(f"❌ Error con URL {i+1}: {e}")
                        continue
                    except Exception as e:
                        print(f"❌ Error inesperado con URL {i+1}: {e}")
                        continue
                
                if success:
                    return True
                    
                # Si falló, esperar antes del siguiente intento
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"⏳ Esperando {wait_time}s antes del siguiente intento...")
                    time.sleep(wait_time)
                
            except Exception as e:
                print(f"❌ Error en intento {attempt + 1}: {e}")
                if os.path.exists(model_path):
                    try:
                        os.remove(model_path)
                    except:
                        pass
                
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        print("❌ Error: No se pudo descargar el modelo después de todos los intentos")
        print("💡 Posibles soluciones:")
        print("   1. Verificar que el FILE_ID sea correcto")
        print("   2. Asegurarse que el archivo sea público en Google Drive")
        print("   3. Verificar la conectividad de red")
        return False
        
    def fit(self, data):
        """
        Entrena el modelo con los datos de anime
        data: DataFrame con columnas ['name', 'genre', 'rating']
        """
        print("🔄 Entrenando modelo de recomendación...")
        
        # 1. Limpiar datos
        self.anime_data = data.copy()
        self.anime_data.drop_duplicates(subset="name", keep="first", inplace=True)
        self.anime_data.reset_index(drop=True, inplace=True)
        
        # 2. Procesar géneros
        genres = self.anime_data["genre"].str.split(", | , | ,").astype(str)
        
        # 3. TF-IDF
        self.tfv = TfidfVectorizer(
            min_df=3, 
            max_features=None, 
            strip_accents="unicode",
            analyzer="word", 
            token_pattern=r"\w{1,}", 
            ngram_range=(1, 3), 
            stop_words="english"
        )
        
        tfv_matrix = self.tfv.fit_transform(genres)
        
        # 4. Calcular similitud (UNA SOLA VEZ)
        print("🧮 Calculando matriz de similitud...")
        self.sig_matrix = sigmoid_kernel(tfv_matrix, tfv_matrix)
        
        # 5. Crear índice de búsqueda
        self.rec_indices = pd.Series(
            self.anime_data.index, 
            index=self.anime_data["name"]
        ).drop_duplicates()
        
        print("✅ Modelo entrenado exitosamente!")
        print(f"📊 Total de animes: {len(self.anime_data)}")
        
    def get_anime_list(self):
        """Retorna lista de todos los animes disponibles"""
        if self.anime_data is None:
            return []
        return sorted(self.anime_data["name"].tolist())
    
    def recommend(self, title, n_recommendations=10):
        """
        Genera recomendaciones para un anime
        
        Args:
            title: Nombre del anime
            n_recommendations: Número de recomendaciones (default: 10)
            
        Returns:
            dict: {"success": bool, "data": list, "message": str}
        """
        try:
            # Validar que el modelo esté entrenado
            if self.sig_matrix is None:
                return {
                    "success": False, 
                    "data": [], 
                    "message": "Modelo no entrenado. Ejecuta fit() primero."
                }
            
            # Validar que el anime existe
            if title not in self.rec_indices:
                available_animes = [name for name in self.rec_indices.index if title.lower() in name.lower()]
                suggestion = f" ¿Quisiste decir: {available_animes[:3]}?" if available_animes else ""
                return {
                    "success": False, 
                    "data": [], 
                    "message": f"Anime '{title}' no encontrado.{suggestion}"
                }
            
            # Obtener índice del anime
            idx = self.rec_indices[title]
            
            # Calcular similitudes
            sig_scores = list(enumerate(self.sig_matrix[idx]))
            sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
            
            # Obtener top N (excluyendo el mismo anime)
            sig_scores = sig_scores[1:n_recommendations+1]
            anime_indices = [i[0] for i in sig_scores]
            
            # Crear lista de recomendaciones
            recommendations = []
            for i, anime_idx in enumerate(anime_indices):
                rec = {
                    "rank": i + 1,
                    "name": self.anime_data.iloc[anime_idx]["name"],
                    "rating": float(self.anime_data.iloc[anime_idx]["rating"]),
                    "genre": self.anime_data.iloc[anime_idx]["genre"],
                    "similarity_score": round(float(sig_scores[i][1]), 3)
                }
                recommendations.append(rec)
            
            return {
                "success": True,
                "data": recommendations,
                "message": f"Recomendaciones generadas para '{title}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"Error interno: {str(e)}"
            }
    
    def save_model(self, filepath="anime_recommender_model.pkl"):
        """Guarda el modelo entrenado"""
        if self.sig_matrix is None:
            print("❌ No hay modelo entrenado para guardar")
            return False
        
        model_data = {
            'sig_matrix': self.sig_matrix,
            'rec_indices': self.rec_indices,
            'anime_data': self.anime_data,
            'tfv': self.tfv
        }
        
        joblib.dump(model_data, filepath)
        print(f"💾 Modelo guardado en: {filepath}")
        return True
    
    def load_model(self, filepath="anime_model.pkl"):
        """Carga un modelo pre-entrenado con mejor manejo de errores"""
        if not os.path.exists(filepath):
            print(f"❌ Archivo no encontrado: {filepath}")
            return False
        
        # Verificar tamaño del archivo
        file_size = os.path.getsize(filepath)
        if file_size < 1000:  # Menos de 1KB
            print(f"❌ Archivo muy pequeño ({file_size} bytes), probablemente corrupto")
            try:
                os.remove(filepath)
                print("🗑️ Archivo corrupto eliminado")
            except:
                pass
            return False
        
        try:
            print(f"📚 Cargando modelo de {file_size/1024/1024:.1f}MB...")
            model_data = joblib.load(filepath)
            
            # Verificar que los datos estén completos
            required_keys = ['sig_matrix', 'rec_indices', 'anime_data', 'tfv']
            for key in required_keys:
                if key not in model_data:
                    print(f"❌ Clave faltante en modelo: {key}")
                    return False
            
            self.sig_matrix = model_data['sig_matrix']
            self.rec_indices = model_data['rec_indices']
            self.anime_data = model_data['anime_data']
            self.tfv = model_data['tfv']
            
            print(f"📂 Modelo cargado exitosamente desde: {filepath}")
            print(f"📊 Animes en modelo: {len(self.anime_data) if self.anime_data is not None else 0}")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            print(f"💡 Tipo de error: {type(e).__name__}")
            
            # Limpiar archivo corrupto
            try:
                os.remove(filepath)
                print("🗑️ Archivo corrupto eliminado")
            except:
                pass
            return False

# Test de descarga (solo para debug)
def test_download(file_id):
    """Función de prueba para verificar descarga"""
    recommender = AnimeRecommender()
    success = recommender.download_model(file_id, "test_model.pkl")
    
    if success and os.path.exists("test_model.pkl"):
        file_size = os.path.getsize("test_model.pkl")
        print(f"✅ Test exitoso: {file_size/1024/1024:.1f}MB descargados")
        # Limpiar archivo de prueba
        os.remove("test_model.pkl")
    else:
        print("❌ Test fallido")
    
    return success

# Ejemplo de uso
if __name__ == "__main__":
    # Para probar descarga:
    # test_download("tu_file_id_aqui")
    pass