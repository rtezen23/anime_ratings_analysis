# En main.py, agrega esta alternativa en startup_event():

# Alternativa: URL directa (si tienes el modelo en otro lugar)
ALTERNATIVE_MODEL_URLS = [
    "https://github.com/tu-usuario/tu-repo/releases/download/v1.0/anime_model.pkl",
    "https://dropbox.com/s/tu-link-directo/anime_model.pkl?dl=1",
    # Agrega más URLs de respaldo
]

async def download_from_alternative_sources(model_path):
    """Descarga desde fuentes alternativas"""
    for i, url in enumerate(ALTERNATIVE_MODEL_URLS):
        try:
            print(f"🔄 Intentando fuente alternativa {i+1}: {url[:50]}...")
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(model_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = os.path.getsize(model_path)
            if file_size > 1000:
                print(f"✅ Descarga exitosa desde fuente alternativa: {file_size/1024/1024:.1f}MB")
                return True
            else:
                os.remove(model_path)
                
        except Exception as e:
            print(f"❌ Error con fuente {i+1}: {e}")
            continue
    
    return False

# En startup_event(), después del intento con Google Drive:
if not success:
    print("🔄 Intentando fuentes alternativas...")
    success = await download_from_alternative_sources(model_path)