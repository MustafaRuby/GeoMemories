from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory, send_file
from flask_cors import CORS
from flask_session import Session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from db_manager import add_location, add_memory, get_locations, add_user, get_memories, verify_user, get_user_by_email, delete_location, delete_memories, update_memory, get_memory_files, add_file_to_memory, remove_file_from_memory, update_file_display_name
import os

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'http://localhost:3000'])
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwtsecretkey')
Session(app)
jwt = JWTManager(app)

# Serve the main frontend application (SPA catch-all)
@app.route('/')
def index():
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except FileNotFoundError:
        return "Frontend build not found. Please run 'npm run build' in the frontend directory.", 404

# Serve static assets (CSS, JS, images, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    try:
        return send_from_directory(app.static_folder, filename)
    except FileNotFoundError:
        # If it's not a static file, serve index.html for SPA routing
        if not filename.startswith('api/') and '.' not in filename.split('/')[-1]:
            try:
                return send_from_directory(app.static_folder, 'index.html')
            except FileNotFoundError:
                return "Frontend build not found. Please run 'npm run build' in the frontend directory.", 404
        return "File not found", 404

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = verify_user(email, password)
    if user:
        access_token = create_access_token(identity=email)
        return jsonify({'access_token': access_token, 'email': email, 'name': user['name']}), 200
    else:
        return jsonify({'error': 'Email o password errati'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    if add_user(email, name, password):
        access_token = create_access_token(identity=email)
        return jsonify({'access_token': access_token, 'email': email, 'name': name}), 201
    else:
        return jsonify({'error': 'Email già registrata'}), 409

@app.route('/api/locations', methods=['GET'])
@jwt_required()
def api_get_locations():
    email = get_jwt_identity()
    locations = get_locations(email)
    return jsonify(locations)

@app.route('/api/locations', methods=['POST'])
@jwt_required()
def api_add_location():
    email = get_jwt_identity()
    data = request.json
    location_id = add_location(
        data.get('title'),
        data.get('latitude'),
        data.get('longitude'),
        email,
        data.get('description')  # Passa anche la descrizione
    )
    return jsonify({'location_id': location_id}), 201

@app.route('/api/locations/<title>/<lat>/<lon>', methods=['DELETE'])
@jwt_required()
def api_delete_location(title, lat, lon):
    email = get_jwt_identity()
    ok = delete_location(title, lat, lon, email)
    if ok:
        return jsonify({'status': 'deleted'})
    else:
        return jsonify({'error': 'Not found'}), 404

#------------------------------------------------------------------------
@app.route('/api/memories', methods=['POST'])
@jwt_required()
def api_add_memory():
    email = get_jwt_identity()
    data = request.json 
    memory_id = add_memory(
        data.get('title'),
        data.get('date'),
        data.get('text'),
        email, 
        data.get('locations'),  # lista di posizioni
        data.get('files')       # lista di file with display_names
        )
    return jsonify({'status': 'success', 'memory_id': memory_id}), 201

@app.route('/api/memories', methods=['GET'])
@jwt_required()
def api_get_memory():
    email = get_jwt_identity()
    memories = get_memories(email)
    return jsonify(memories)

@app.route('/api/memories/<title>/<date>/<text>', methods=['DELETE'])
@jwt_required()
def api_delete_memories(title, date, text):
    email = get_jwt_identity()
    ok = delete_memories(title, date, text, email)
    if ok:
        return jsonify({'status': 'deleted'})
    else:
        return jsonify({'error': 'Not found'}), 404

@app.route('/api/memories/<title>/<date>/<text>', methods=['PUT'])
@jwt_required()
def api_update_memory(title, date, text):
    email = get_jwt_identity()
    data = request.json
    ok = update_memory(title, date, text, email, data)
    if ok:
        return jsonify({'status': 'updated'})
    else:
        return jsonify({'error': 'Not found or not updated'}), 404

#------------------------------------------------------------------------
# API specifiche per la gestione dei file
@app.route('/api/memories/<title>/<date>/<text>/files', methods=['GET'])
@jwt_required()
def api_get_memory_files(title, date, text):
    email = get_jwt_identity()
    files = get_memory_files(title, date, text, email)
    return jsonify(files)

@app.route('/api/memories/<title>/<date>/<text>/files', methods=['POST'])
@jwt_required()
def api_add_file_to_memory(title, date, text):
    email = get_jwt_identity()
    data = request.json
    ok = add_file_to_memory(title, date, text, email, data)
    if ok:
        return jsonify({'status': 'file added'})
    else:
        return jsonify({'error': 'Memory not found or file not added'}), 404

@app.route('/api/memories/<title>/<date>/<text>/files/<path:file_url>', methods=['DELETE'])
@jwt_required()
def api_remove_file_from_memory(title, date, text, file_url):
    email = get_jwt_identity()
    ok = remove_file_from_memory(title, date, text, email, file_url)
    if ok:
        return jsonify({'status': 'file removed'})
    else:
        return jsonify({'error': 'Memory or file not found'}), 404

@app.route('/api/memories/<title>/<date>/<text>/files/<path:file_url>/display-name', methods=['PUT'])
@jwt_required()
def api_update_file_display_name(title, date, text, file_url):
    email = get_jwt_identity()
    data = request.json
    new_display_name = data.get('display_name')
    if not new_display_name:
        return jsonify({'error': 'display_name is required'}), 400
    ok = update_file_display_name(title, date, text, email, file_url, new_display_name)
    if ok:
        return jsonify({'status': 'display name updated'})
    else:
        return jsonify({'error': 'Memory or file not found'}), 404

#------------------------------------------------------------------------
@app.route('/api/locations', methods=['PUT'])
@jwt_required()
def api_update_location():
    email = get_jwt_identity()
    data = request.json
    old = data.get('old')
    updated = data.get('updated')
    if not old or not updated:
        return jsonify({'error': 'Dati mancanti'}), 400
    from db_manager import update_location
    ok = update_location(old, updated, email)
    if not ok:
        return jsonify({'error': 'Posizione non trovata'}), 404
    return jsonify({'status': 'updated'})

@app.errorhandler(404)
def not_found(e):
    # For API routes, return JSON
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    # Serve SPA solo se non è una richiesta per file statico
    if '.' not in request.path.split('/')[-1]:
        try:
            return send_from_directory(app.static_folder, 'index.html')
        except FileNotFoundError:
            return "Frontend build not found. Please run 'npm run build' in the frontend directory.", 404
    return "File not found", 404

@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return "Internal server error", 500

@app.errorhandler(400)
def bad_request(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Bad request'}), 400
    return "Bad request", 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)