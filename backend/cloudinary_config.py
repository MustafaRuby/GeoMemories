import requests
import hashlib
import hmac
import time
from urllib.parse import urlparse
from cloudinary_credentials import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

def extract_public_id_from_url(cloudinary_url):
    """Estrae il public_id da un URL Cloudinary"""
    try:
        # Esempio URL: https://res.cloudinary.com/dkgxlxtew/auto/upload/v1234567890/project_diary/filename.jpg
        parsed = urlparse(cloudinary_url)
        path_parts = parsed.path.split('/')
        
        print(f"Debug - URL originale: {cloudinary_url}")
        print(f"Debug - Path parts: {path_parts}")
        
        # Trova la parte dopo /upload/
        if '/upload/' in parsed.path:
            upload_index = path_parts.index('upload')
            # Skip version se presente (v1234567890)
            start_index = upload_index + 1
            if len(path_parts) > start_index and path_parts[start_index].startswith('v'):
                start_index += 1
              # Ricostruisci il public_id (include tutto il path dopo la versione)
            public_id_parts = path_parts[start_index:]
            public_id_with_extension = '/'.join(public_id_parts)
            
            # Per i file raw (docx, pdf, etc.), prova sia con che senza estensione
            public_id_without_extension = public_id_with_extension
            if '.' in public_id_parts[-1]:
                public_id_parts_no_ext = public_id_parts.copy()
                public_id_parts_no_ext[-1] = public_id_parts_no_ext[-1].rsplit('.', 1)[0]
                public_id_without_extension = '/'.join(public_id_parts_no_ext)
            
            print(f"Debug - Public ID con estensione: {public_id_with_extension}")
            print(f"Debug - Public ID senza estensione: {public_id_without_extension}")
            
            # Ritorna sia la versione con estensione che quella senza
            # Per i file raw, spesso il public_id include l'estensione
            return public_id_with_extension, public_id_without_extension
    except Exception as e:
        print(f"Errore nell'estrazione del public_id: {e}")
    
    return None, None

def delete_file_from_cloudinary(cloudinary_url):
    """Elimina un file da Cloudinary usando l'URL"""
    public_id_with_ext, public_id_without_ext = extract_public_id_from_url(cloudinary_url)
    if not public_id_with_ext:
        print("Errore: impossibile estrarre public_id dall'URL")
        return False
    
    # Determina il resource_type basandosi sull'URL
    resource_type = "image"  # default
    
    if "/raw/upload/" in cloudinary_url:
        resource_type = "raw"
    elif "/video/upload/" in cloudinary_url:
        resource_type = "video"
    elif "/image/upload/" in cloudinary_url:
        resource_type = "image"
    elif "/auto/upload/" in cloudinary_url:
        # Per auto, prova prima raw (per documenti), poi image
        timestamp = int(time.time())
        data = {'timestamp': timestamp, 'api_key': CLOUDINARY_API_KEY}
        
        # Per file .docx e simili, prova prima con l'estensione (più probabile)
        print(f"Debug - Tentativo eliminazione con public_id con estensione: {public_id_with_ext}")
        success = _try_delete_with_resource_type(data, "raw", public_id_with_ext)
        
        # Se fallisce, prova senza estensione
        if not success and public_id_without_ext != public_id_with_ext:
            print(f"Debug - Tentativo eliminazione con public_id senza estensione: {public_id_without_ext}")
            success = _try_delete_with_resource_type(data, "raw", public_id_without_ext)
        
        # Se ancora fallisce, prova con image
        if not success:
            print(f"Debug - Tentativo eliminazione come image con estensione: {public_id_with_ext}")
            success = _try_delete_with_resource_type(data, "image", public_id_with_ext)
            if not success and public_id_without_ext != public_id_with_ext:
                print(f"Debug - Tentativo eliminazione come image senza estensione: {public_id_without_ext}")
                success = _try_delete_with_resource_type(data, "image", public_id_without_ext)
        
        return success
    
    # Genera timestamp e dati base
    timestamp = int(time.time())
    data = {'timestamp': timestamp, 'api_key': CLOUDINARY_API_KEY}
    
    # Prova prima con il public_id con estensione, poi senza
    print(f"Debug - Tentativo eliminazione con public_id con estensione: {public_id_with_ext}")
    success = _try_delete_with_resource_type(data, resource_type, public_id_with_ext)
    if not success and public_id_without_ext != public_id_with_ext:
        print(f"Debug - Tentativo eliminazione con public_id senza estensione: {public_id_without_ext}")
        success = _try_delete_with_resource_type(data, resource_type, public_id_without_ext)
    
    return success

def _try_delete_with_resource_type(data, resource_type, public_id):
    """Funzione helper per provare l'eliminazione con un resource_type specifico"""
    timestamp = data['timestamp']
    
    # Per l'eliminazione, la signature include SOLO public_id e timestamp
    # Il resource_type va nei dati della richiesta ma NON nella signature
    params_to_sign = {
        'public_id': public_id,
        'timestamp': timestamp
    }
    
    # Costruisci la stringa da firmare (parametri ordinati alfabeticamente)
    sorted_params = sorted(params_to_sign.items())
    params_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
    params_string += CLOUDINARY_API_SECRET
    
    print(f"Debug - String to sign: {params_string}")
    
    # Genera la signature
    signature = hashlib.sha1(params_string.encode('utf-8')).hexdigest()
    
    # Prepara i dati per la richiesta
    request_data = {
        'public_id': public_id,
        'timestamp': timestamp,
        'api_key': CLOUDINARY_API_KEY,
        'signature': signature
    }
    
    # Aggiungi resource_type ai dati della richiesta se necessario
    if resource_type != "image":
        request_data['resource_type'] = resource_type
    
    delete_url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/{resource_type}/destroy"
    
    print(f"Debug - Request URL: {delete_url}")
    print(f"Debug - Request data: {request_data}")
    
    try:
        response = requests.post(delete_url, data=request_data)
        result = response.json()
        
        print(f"Debug - Response: {result}")
        
        if result.get('result') == 'ok':
            print(f"File eliminato con successo da Cloudinary ({resource_type}): {public_id}")
            return True
        elif result.get('result') == 'not found':
            print(f"File non trovato su Cloudinary ({resource_type}): {public_id}")
            return False
        else:
            print(f"Errore nell'eliminazione da Cloudinary ({resource_type}): {result}")
            return False
            
    except Exception as e:
        print(f"Errore nella richiesta di eliminazione ({resource_type}): {e}")
        return False
