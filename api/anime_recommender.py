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
        """
        if os.path.exists(model_path):
            file_size = os.path.getsize(model_path)
            if file_size > 10000:  # Archivo válido (> 10KB)
                print(f"📂 Modelo ya existe localmente: {model_path} ({file_size/1024/1024:.1f}MB)")
                return True
            else:
                print(f"🗑️ Eliminando archivo corrupto: {model_path}")
                os.remove(model_path)
        
        print("🔄 Descargando modelo desde Google Drive...")
        
        for attempt in range(max_retries):
            try:
                print(f"📥 Intento {attempt + 1}/{max_retries}")
                
                # URL correcta para descarga directa de Google Drive
                url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
                
                print(f"🌐 URL de descarga: {url[:60]}...")
                
                # Session con headers mejorados
                session = requests.Session()
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/octet-stream,*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                # Primera petición
                print("🔍 Obteniendo información del archivo...")
                response = session.get(url, headers=headers, stream=True, timeout=60)
                response.raise_for_status()
                
                # Verificar si es una página HTML (error común)
                content_type = response.headers.get('content-type', '')
                if 'text/html' in content_type.lower():
                    print("⚠️ Recibida página HTML en lugar del archivo")
                    print("💡 Esto indica que el enlace no está configurado correctamente")
                    
                    # Intentar obtener el enlace de descarga real del HTML
                    html_content = response.text
                    if 'download' in html_content and 'confirm=' in html_content:
                        print("🔄 Buscando enlace de confirmación...")
                        import re
                        # Buscar patrones de descarga
                        patterns = [
                            r'href="(/uc\?export=download[^"]*)"',
                            r'"downloadUrl":"([^"]*)"',
                            r'confirm=([a-zA-Z0-9\-_]+)',
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, html_content)
                            if matches:
                                print(f"✅ Encontrado patrón: {pattern}")
                                if pattern.startswith('confirm='):
                                    confirm_token = matches[0]
                                    new_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={confirm_token}"
                                    print(f"🔄 Reintentando con token: {new_url[:60]}...")
                                    response = session.get(new_url, headers=headers, stream=True, timeout=60)
                                    response.raise_for_status()
                                    break
                                else:
                                    new_url = "https://drive.google.com" + matches[0]
                                    response = session.get(new_url, headers=headers, stream=True, timeout=60)
                                    response.raise_for_status()
                                    break
                    
                    # Si aún es HTML, el enlace está mal configurado
                    if 'text/html' in response.headers.get('content-type', '').lower():
                        print("❌ El archivo sigue devolviendo HTML")
                        print("💡 Verifica que:")
                        print("   1. El archivo sea público (Cualquiera con el enlace)")
                        print("   2. El FILE_ID sea correcto")
                        print("   3. El archivo no esté en la papelera")
                        continue
                
                # Verificar tamaño esperado
                content_length = response.headers.get('content-length')
                if content_length:
                    size_mb = int(content_length) / 1024 / 1024
                    print(f"📊 Tamaño esperado: {size_mb:.1f}MB")
                    
                    # Verificar que no sea demasiado pequeño
                    if int(content_length) < 10000:  # Menos de 10KB
                        print("⚠️ Archivo muy pequeño, posiblemente corrupto")
                        continue
                else:
                    print("⚠️ No se pudo determinar el tamaño del archivo")
                
                # Descargar archivo
                print("📥 Descargando archivo...")
                downloaded = 0
                chunk_size = 32768  # 32KB chunks
                
                with open(model_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Mostrar progreso cada 5MB
                            if downloaded % (5 * 1024 * 1024) == 0:
                                progress_mb = downloaded / 1024 / 1024
                                print(f"📥 Progreso: {progress_mb:.1f}MB")
                
                # Verificar archivo descargado
                file_size = os.path.getsize(model_path)
                if file_size < 10000:  # Menos de 10KB
                    print(f"❌ Archivo muy pequeño ({file_size} bytes)")
                    if os.path.exists(model_path):
                        os.remove(model_path)
                    continue
                
                # Verificar que sea un archivo pickle válido
                try:
                    with open(model_path, 'rb') as f:
                        # Leer los primeros bytes para verificar formato pickle
                        header = f.read(20)
                        if not header.startswith(b'\x80'):  # Pickle protocol marker
                            print("❌ El archivo no parece ser un pickle válido")
                            os.remove(model_path)
                            continue
                except Exception as e:
                    print(f"❌ Error verificando archivo: {e}")
                    if os.path.exists(model_path):
                        os.remove(model_path)
                    continue
                
                print(f"✅ Modelo descargado exitosamente: {file_size/1024/1024:.1f}MB")
                return True
                        
            except requests.exceptions.RequestException as e:
                print(f"❌ Error de red en intento {attempt + 1}: {e}")
            except Exception as e:
                print(f"❌ Error inesperado en intento {attempt + 1}: {e}")
            
            # Limpiar archivo corrupto
            if os.path.exists(model_path):
                try:
                    os.remove(model_path)
                except:
                    pass
            
            # Esperar antes del siguiente intento
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"⏳ Esperando {wait_time}s antes del siguiente intento...")
                time.sleep(wait_time)
        
        print("❌ Error: No se pudo descargar el modelo después de todos los intentos")
        print("\n💡 SOLUCIONES POSIBLES:")
        print("1. Verificar que el archivo sea público en Google Drive:")
        print("   - Clic derecho en el archivo > Compartir")
        print("   - Cambiar a 'Cualquiera con el enlace puede ver'")
        print("   - Copiar el ID del enlace (la parte después de /d/ y antes de /view)")
        print("\n2. Usar un servicio alternativo:")
        print("   - Subir el modelo a GitHub LFS")
        print("   - Usar Dropbox o OneDrive")
        print("   - Usar un bucket de AWS S3")
        print("\n3. Reducir el tamaño del modelo si es muy grande")
        
        return False
        
    def fit(self, data):
        """Entrena el modelo con los datos de anime"""
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
        
        # 4. Calcular similitud
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
        """Genera recomendaciones para un anime"""
        try:
            if self.sig_matrix is None:
                return {
                    "success": False, 
                    "data": [], 
                    "message": "Modelo no entrenado. Ejecuta fit() primero."
                }
            
            if title not in self.rec_indices:
                available_animes = [name for name in self.rec_indices.index if title.lower() in name.lower()]
                suggestion = f" ¿Quisiste decir: {available_animes[:3]}?" if available_animes else ""
                return {
                    "success": False, 
                    "data": [], 
                    "message": f"Anime '{title}' no encontrado.{suggestion}"
                }
            
            idx = self.rec_indices[title]
            sig_scores = list(enumerate(self.sig_matrix[idx]))
            sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
            sig_scores = sig_scores[1:n_recommendations+1]
            anime_indices = [i[0] for i in sig_scores]
            
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
        
        file_size = os.path.getsize(filepath)
        if file_size < 10000:  # Menos de 10KB
            print(f"❌ Archivo muy pequeño ({file_size} bytes), probablemente corrupto")
            try:
                os.remove(filepath)
                print("🗑️ Archivo corrupto eliminado")
            except:
                pass
            return False
        
        try:
            print(f"📚 Cargando modelo de {file_size/1024/1024:.1f}MB...")
            
            # Verificar que sea un archivo pickle válido antes de cargarlo
            with open(filepath, 'rb') as f:
                header = f.read(20)
                if not header.startswith(b'\x80'):
                    print("❌ El archivo no es un pickle válido")
                    os.remove(filepath)
                    return False
            
            model_data = joblib.load(filepath)
            
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
            
            try:
                os.remove(filepath)
                print("🗑️ Archivo corrupto eliminado")
            except:
                pass
            return False

def test_download(file_id):
    """Función de prueba para verificar descarga"""
    print(f"🧪 Probando descarga con FILE_ID: {file_id[:20]}...")
    recommender = AnimeRecommender()
    success = recommender.download_model(file_id, "test_model.pkl")
    
    if success and os.path.exists("test_model.pkl"):
        file_size = os.path.getsize("test_model.pkl")
        print(f"✅ Test exitoso: {file_size/1024/1024:.1f}MB descargados")
        
        # Probar cargar el modelo
        load_success = recommender.load_model("test_model.pkl")
        print(f"📚 Carga de modelo: {'✅ Exitosa' if load_success else '❌ Fallida'}")
        
        # Limpiar archivo de prueba
        os.remove("test_model.pkl")
    else:
        print("❌ Test fallido")
    
    return success

if __name__ == "__main__":
    # Para probar descarga:
    # test_download("tu_file_id_aqui")
    pass