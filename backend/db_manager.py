import os
from pymongo import MongoClient
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from cloudinary_config import delete_file_from_cloudinary

# Sostituisci con la tua stringa di connessione MongoDB
# Assicurati di avere la variabile d'ambiente MONGO_URI impostata correttamente
MONGO_URI = os.environ.get('MONGO_URI', '')
DB_NAME = 'diario'
COLLECTION_NAME = 'locations'
USERS_COLLECTION = 'users'
MEMORIES_COLLECTION = 'memories'

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
locations_collection = db[COLLECTION_NAME]
users_collection = db[USERS_COLLECTION]
memories_collection = db[MEMORIES_COLLECTION]

def add_user(email, name, password):
    if users_collection.find_one({'email': email}):
        return False  # Email già registrata
    hashed = generate_password_hash(password)
    user = {'email': email, 'name': name, 'password': hashed}
    users_collection.insert_one(user)
    return True

def verify_user(email, password):
    user = users_collection.find_one({'email': email})
    if user and check_password_hash(user['password'], password):
        return user
    return None

def get_user_by_email(email):
    return users_collection.find_one({'email': email})

def add_location(title, latitude, longitude, user_email, description=None):
    location = {
        'title': title,
        'latitude': latitude,
        'longitude': longitude,
        'description': description or '',
        'created_at': datetime.utcnow(),
        'user_email': user_email
    }
    result = locations_collection.insert_one(location)
    return str(result.inserted_id)

def get_locations(user_email):
    locations = list(locations_collection.find({'user_email': user_email}, {'_id': 0}))
    return locations

def delete_location(title, latitude, longitude, user_email):
    result = locations_collection.delete_one({
        'title': title,
        'latitude': float(latitude),
        'longitude': float(longitude),
        'user_email': user_email
    })
    return result.deleted_count > 0

def update_location(old, updated, user_email):
    query = {
        'title': old['title'],
        'latitude': float(old['latitude']),
        'longitude': float(old['longitude']),
        'user_email': user_email
    }
    update_fields = {
        'title': updated['title'],
        'latitude': float(updated['latitude']),
        'longitude': float(updated['longitude']),
        'description': updated.get('description', '')
    }
    result = locations_collection.update_one(query, {'$set': update_fields})
    return result.matched_count > 0

#------------------------------------------------------------------
def add_memory(title, date, text, user_email, locations=None, files=None):
    memory = {
        'title': title,
        'date': datetime.strptime(date, '%Y-%m-%d'),
        'text': text,
        'user_email': user_email,
        'created_at': datetime.utcnow(),
        'locations': [
            {
                'title': loc['title'],
                'latitude': loc['latitude'],
                'longitude': loc['longitude'],
                'description': loc.get('description', '')
            } for loc in (locations or [])
        ] if locations else [],
        'files': [
            {
                'url': file_data['url'],
                'display_name': file_data.get('display_name', file_data.get('original_name', 'File senza nome')),
                'original_name': file_data.get('original_name', ''),
                'size': file_data.get('size', 0),
                'type': file_data.get('type', ''),
                'uploaded_at': datetime.utcnow()
            } for file_data in (files or [])
        ] if files else []
    }
    result = memories_collection.insert_one(memory)
    return str(result.inserted_id)

def get_memories(user_email):
    memories = list(memories_collection.find(
        {'user_email': user_email},
        {'_id': 0, 'created_at': 0}
    ))
    for mem in memories:
        mem['date'] = mem['date'].strftime('%Y-%m-%d')
    return memories

def delete_memories(title, date, text, user_email):
    """Elimina un ricordo e tutti i suoi file associati da Cloudinary"""
    # Prima recupera il ricordo per ottenere i file
    memory = memories_collection.find_one({
        'title': title,
        'date': datetime.strptime(date, '%Y-%m-%d'),
        'text': text,
        'user_email': user_email
    })
    
    if not memory:
        return False
    
    # Elimina tutti i file da Cloudinary
    files_to_delete = memory.get('files', [])
    for file_data in files_to_delete:
        file_url = file_data.get('url')
        if file_url:
            try:
                delete_success = delete_file_from_cloudinary(file_url)
                if not delete_success:
                    print(f"Avviso: Non è stato possibile eliminare il file da Cloudinary: {file_url}")
            except Exception as e:
                print(f"Errore nell'eliminazione da Cloudinary: {e}")
    
    # Elimina il ricordo dal database
    result = memories_collection.delete_one({
        'title': title,
        'date': datetime.strptime(date, '%Y-%m-%d'),
        'text': text,
        'user_email': user_email
    })
    return result.deleted_count > 0

def update_memory(old_title, old_date, old_text, user_email, new_data):
    # Cerca il ricordo da aggiornare
    query = {
        'title': old_title,
        'date': datetime.strptime(old_date, '%Y-%m-%d'),
        'text': old_text,
        'user_email': user_email
    }
    
    # Se stiamo aggiornando i file, controlla se dobbiamo eliminare file da Cloudinary
    if 'files' in new_data:
        # Recupera il ricordo attuale per vedere i file esistenti
        current_memory = memories_collection.find_one(query)
        if current_memory:
            current_files = current_memory.get('files', [])
            new_files = new_data['files'] or []
            
            # Trova file che sono stati rimossi
            current_urls = {f.get('url') for f in current_files}
            new_urls = {f.get('url') for f in new_files}
            removed_urls = current_urls - new_urls
            
            # Elimina i file rimossi da Cloudinary
            for removed_url in removed_urls:
                if removed_url:
                    try:
                        delete_success = delete_file_from_cloudinary(removed_url)
                        if not delete_success:
                            print(f"Avviso: Non è stato possibile eliminare il file da Cloudinary: {removed_url}")
                    except Exception as e:
                        print(f"Errore nell'eliminazione da Cloudinary: {e}")
    
    update_fields = {}
    if 'title' in new_data:
        update_fields['title'] = new_data['title']
    if 'date' in new_data:
        update_fields['date'] = datetime.strptime(new_data['date'], '%Y-%m-%d')
    if 'text' in new_data:
        update_fields['text'] = new_data['text']
    if 'locations' in new_data:
        update_fields['locations'] = [
            {
                'title': loc['title'],
                'latitude': loc['latitude'],
                'longitude': loc['longitude'],
                'description': loc.get('description', '')
            } for loc in (new_data['locations'] or [])
        ]
    if 'files' in new_data:
        update_fields['files'] = [
            {
                'url': file_data['url'],
                'display_name': file_data.get('display_name', file_data.get('original_name', 'File senza nome')),
                'original_name': file_data.get('original_name', ''),
                'size': file_data.get('size', 0),
                'type': file_data.get('type', ''),
                'uploaded_at': datetime.utcnow()
            } for file_data in (new_data['files'] or [])
        ]
    if not update_fields:
        return False
    result = memories_collection.update_one(query, {'$set': update_fields})
    return result.modified_count > 0

def get_memory_files(title, date, text, user_email):
    """Recupera i file associati a un ricordo specifico"""
    memory = memories_collection.find_one({
        'title': title,
        'date': datetime.strptime(date, '%Y-%m-%d'),
        'text': text,
        'user_email': user_email
    })
    return memory.get('files', []) if memory else []

def update_file_display_name(title, date, text, user_email, file_url, new_display_name):
    """Aggiorna il display_name di un file specifico in un ricordo"""
    query = {
        'title': title,
        'date': datetime.strptime(date, '%Y-%m-%d'),
        'text': text,
        'user_email': user_email,
        'files.url': file_url
    }
    update = {
        '$set': {
            'files.$.display_name': new_display_name
        }
    }
    result = memories_collection.update_one(query, update)
    return result.modified_count > 0

def remove_file_from_memory(title, date, text, user_email, file_url):
    """Rimuove un file specifico da un ricordo e lo elimina da Cloudinary"""
    # Prima recupera il file per verificare che esista
    memory = memories_collection.find_one({
        'title': title,
        'date': datetime.strptime(date, '%Y-%m-%d'),
        'text': text,
        'user_email': user_email
    })
    
    if not memory:
        return False
    
    # Trova il file con l'URL specificato
    file_found = None
    for file_data in memory.get('files', []):
        if file_data.get('url') == file_url:
            file_found = file_data
            break
    
    if not file_found:
        return False
    
    # Rimuove dal database
    query = {
        'title': title,
        'date': datetime.strptime(date, '%Y-%m-%d'),
        'text': text,
        'user_email': user_email
    }
    update = {
        '$pull': {
            'files': {'url': file_url}
        }
    }
    result = memories_collection.update_one(query, update)
    
    # Se rimosso dal database con successo, elimina da Cloudinary
    if result.modified_count > 0:
        try:
            delete_success = delete_file_from_cloudinary(file_url)
            if not delete_success:
                print(f"Avviso: File rimosso dal database ma non da Cloudinary: {file_url}")
        except Exception as e:
            print(f"Errore nell'eliminazione da Cloudinary: {e}")
        
        return True
    
    return False

def add_file_to_memory(title, date, text, user_email, file_data):
    """Aggiunge un file a un ricordo esistente"""
    query = {
        'title': title,
        'date': datetime.strptime(date, '%Y-%m-%d'),
        'text': text,
        'user_email': user_email
    }
    file_obj = {
        'url': file_data['url'],
        'display_name': file_data.get('display_name', file_data.get('original_name', 'File senza nome')),
        'original_name': file_data.get('original_name', ''),
        'size': file_data.get('size', 0),
        'type': file_data.get('type', ''),
        'uploaded_at': datetime.utcnow()
    }
    update = {
        '$push': {
            'files': file_obj
        }
    }
    result = memories_collection.update_one(query, update)
    return result.modified_count > 0