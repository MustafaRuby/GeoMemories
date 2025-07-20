<script>
import { closeMemoryDetailsModal } from '$lib/globalModalStore.js';
import { openMapPopup } from '$lib/cesiumMapPopupStore.js';
import { handleFileOpen } from '$lib/imageViewerStore.js';
import * as popupStackModule from '../routes/popupStack';
import { CONFIG } from '$lib/config.local.js';
import { closeMenusForPopup, getCurrentMenuState } from '$lib/menuCloseStore.js';

export let memory;

let isEditing = false;
let editMemory = {};
let tempSelectedLocation = null;
let userLocations = [];
let editSelectedFiles = [];
let editFileDisplayNames = [];

// Configurazione Cloudinary
const CLOUDINARY_URL = `https://api.cloudinary.com/v1_1/${import.meta.env.VITE_CLOUDINARY_CLOUD_NAME || CONFIG.CLOUDINARY.CLOUD_NAME}/auto/upload`;
const CLOUDINARY_UPLOAD_PRESET = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET || CONFIG.CLOUDINARY.UPLOAD_PRESET;

// Gestione popup stack
$: if (memory) {
    popupStackModule.pushPopup(closeMemoryDetailsModal);
} else {
    popupStackModule.popPopup();
}

// Carica posizioni quando si entra in modalità modifica
$: if (isEditing) {
    fetchLocations();
}

async function fetchLocations() {
    const response = await fetch('/api/locations', { credentials: 'include' });
    if (response.ok) {
        userLocations = await response.json();
    }
}

async function deleteMemory(mem) {
    if (!confirm('Eliminare definitivamente questo ricordo?')) return;
    
    // Ottiene lo stato attuale dei menu e li chiude memorizzandolo
    const currentState = getCurrentMenuState();
    closeMenusForPopup(currentState.memoryMenuOpen, currentState.positionsMenuOpen);
    
    try {
        const res = await fetch(
            `/api/memories/${encodeURIComponent(mem.title)}/${encodeURIComponent(mem.date)}/${encodeURIComponent(mem.text)}`,
            { method: 'DELETE' }
        );

        if (res.ok) {
            closeMemoryDetailsModal();
            
            // Emetti evento per ricaricare la lista dei ricordi
            window.dispatchEvent(new CustomEvent('memory-updated'));
        } else {
            alert('Errore durante l\'eliminazione del ricordo.');
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('Errore durante l\'eliminazione del ricordo.');
    }
}

function startEditMemory() {
    isEditing = true;
    editMemory = JSON.parse(JSON.stringify(memory));
    if (!Array.isArray(editMemory.locations)) editMemory.locations = [];
    // Prepara array per nuovi file
    editSelectedFiles = [];
    editFileDisplayNames = [];
}

function cancelEditMemory() {
    isEditing = false;
    editMemory = {};
    editSelectedFiles = [];
    editFileDisplayNames = [];
}

async function saveEditMemory() {
    if (!editMemory.title || !editMemory.date || !editMemory.text) return;
    
    let uploadedFiles = [];
    if (editSelectedFiles.length > 0) {
        uploadedFiles = await uploadFilesToCloudinary(editSelectedFiles, editFileDisplayNames);
    }
    
    // Unisci i file già presenti con quelli nuovi
    editMemory.files = [...(editMemory.files || []), ...uploadedFiles];
    
    const res = await fetch(`/api/memories/${encodeURIComponent(memory.title)}/${encodeURIComponent(memory.date)}/${encodeURIComponent(memory.text)}`,
        {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(editMemory)
        });
    
    if (res.ok) {
        // Aggiorna il memory corrente con i dati modificati
        memory = editMemory;
        isEditing = false;
        editMemory = {};
        editSelectedFiles = [];
        editFileDisplayNames = [];
        
        // Emetti evento per ricaricare la lista dei ricordi
        window.dispatchEvent(new CustomEvent('memory-updated'));
        
        alert('Ricordo salvato con successo!');
    } else {
        alert('Errore durante il salvataggio delle modifiche');
    }
}

function handleEditLocationSelect() {
    if (tempSelectedLocation && !editMemory.locations.some(l => 
        l.title === tempSelectedLocation.title && 
        l.latitude === tempSelectedLocation.latitude && 
        l.longitude === tempSelectedLocation.longitude
    )) {
        editMemory.locations = [...editMemory.locations, tempSelectedLocation];
        tempSelectedLocation = null;
    }
}

function removeLocationFromEdit(loc) {
    editMemory.locations = editMemory.locations.filter(l => !(
        l.title === loc.title && 
        l.latitude === loc.latitude && 
        l.longitude === loc.longitude
    ));
}

function handleEditFileSelect(e) {
    const input = e.target;
    if (!input.files) return;
    const files = Array.from(input.files);
    
    if ((editMemory.files?.length || 0) + editSelectedFiles.length + files.length > 5) {
        alert('Puoi associare al massimo 5 file per ricordo.');
        return;
    }
    
    const validFiles = files.filter(f => f.size <= 50 * 1024 * 1024);
    if (validFiles.length < files.length) {
        alert('Ogni file deve essere massimo 50 MB.');
    }
    
    editSelectedFiles = [...editSelectedFiles, ...validFiles];
    editFileDisplayNames = [...editFileDisplayNames, ...validFiles.map(f => f.name)];
    input.value = '';
}

function removeEditFile(idx) {
    editSelectedFiles = editSelectedFiles.filter((f, i) => i !== idx);
    editFileDisplayNames = editFileDisplayNames.filter((n, i) => i !== idx);
}

function handleEditDisplayNameChange(idx, value) {
    editFileDisplayNames[idx] = value;
}

function removeExistingFile(idx) {
    editMemory.files = editMemory.files.filter((f, i) => i !== idx);
}

async function uploadFilesToCloudinary(files, displayNames) {
    const uploaded = [];
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const display_name = displayNames[i] || file.name;
        const formData = new FormData();
        formData.append('file', file);
        formData.append('upload_preset', CLOUDINARY_UPLOAD_PRESET);
        
        try {
            const res = await fetch(CLOUDINARY_URL, {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (data.secure_url) {
                uploaded.push({
                    url: data.secure_url,
                    display_name,
                    original_name: file.name,
                    size: file.size,
                    type: file.type
                });
            }
        } catch (err) {
            alert('Errore durante l\'upload di ' + file.name);
        }
    }
    return uploaded;
}

function handleFileOpenWrapper(file) {
    // Ottiene lo stato attuale dei menu e li chiude memorizzandolo
    const currentState = getCurrentMenuState();
    closeMenusForPopup(currentState.memoryMenuOpen, currentState.positionsMenuOpen);
    
    // Use the centralized handleFileOpen function that supports both images and videos
    handleFileOpen(file);
}

function handleModalKeydown(event) {
    if (event.key === 'Escape') {
        if (isEditing) {
            cancelEditMemory();
        } else {
            closeMemoryDetailsModal();
        }
    }
}
</script>

<div
    class="memory-modal-backdrop"
    aria-label="Chiudi il modal"
    tabindex="0"
    aria-modal="true"
    on:click={closeMemoryDetailsModal}    on:keydown={handleModalKeydown}
    style="display: flex; align-items: center; justify-content: center; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(24, 28, 36, 0.72); z-index: 2147483635 !important;"
>    <div class="memory-modal" on:click|stopPropagation>
        <!-- Pulsante Elimina -->
        <button 
            class="delete-in-modal-top"
            on:click|stopPropagation={() => {
                deleteMemory(memory);
            }}
            title="Elimina ricordo"
            aria-label="Elimina ricordo"
        >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M6 8V14M10 8V14M14 8V14M3 5H17M8 5V3H12V5" 
                    stroke="#ff7eb3" 
                    stroke-width="1.7"
                    stroke-linecap="round"
                    stroke-linejoin="round"/>
            </svg>
        </button>

        <!-- Pulsante Chiudi -->
        <button class="close-modal-btn" on:click={isEditing ? cancelEditMemory : closeMemoryDetailsModal} title="Chiudi" aria-label="Chiudi il modal">×</button>
        
        {#if isEditing}
            <!-- Modalità modifica -->
            <h3>Modifica ricordo</h3>
            <form on:submit|preventDefault={saveEditMemory} class="edit-form">
                <input 
                    type="text" 
                    bind:value={editMemory.title} 
                    placeholder="Titolo" 
                    required 
                    class="input-beauty dark"
                />
                <input 
                    type="date" 
                    bind:value={editMemory.date} 
                    required 
                    class="input-beauty dark"
                />

                <!-- Gestione posizioni per la modifica -->
                <div class="location-select-row">
                    <select 
                        bind:value={tempSelectedLocation}
                        class="input-beauty dark"
                        aria-label="Scegli una posizione da associare"
                    >
                        <option value={null}>Seleziona una posizione</option>
                        {#each userLocations as location}
                            {#if !editMemory.locations.some(l => l.title === location.title && l.latitude === location.latitude && l.longitude === location.longitude)}
                                <option value={location}>
                                    {location.title} ({location.latitude}, {location.longitude})
                                </option>
                            {/if}
                        {/each}
                    </select>
                    <button type="button" class="btn-dark-outline" on:click={handleEditLocationSelect} disabled={!tempSelectedLocation}>Aggiungi</button>
                </div>

                {#if editMemory.locations && editMemory.locations.length > 0}
                    <div class="memory-location-list styled-location-list">
                        <span><img src="/internal-map.svg" alt="location icon" style="width: 2.5em; height: 2.5em; margin-right: 0.4em; opacity: 0.85; display: inline; vertical-align: middle;" /> Posizioni associate:</span>
                        <ul>
                            {#each editMemory.locations as loc}
                                <li>
                                    <img src="/location.svg" alt="location icon" style="width: 1.1em; height: 1.1em; margin-right: 0.4em; opacity: 0.85; display: inline; vertical-align: middle;" />
                                    <b>{loc.title}</b> ({loc.latitude}, {loc.longitude})
                                    {#if loc.description}
                                        - {loc.description}
                                    {/if}
                                    <button type="button" class="remove-loc-btn" on:click={() => removeLocationFromEdit(loc)} title="Rimuovi">×</button>
                                </li>
                            {/each}
                        </ul>
                    </div>
                {/if}

                <!-- Sezione file esistenti e nuovi -->
                <div class="memory-files-list styled-files-list">
                    <span class="files-label"><img src="/searching.svg" alt="file icon" style="width: 2em; height: 2em; margin-right: 0.4em; opacity: 0.85; display: inline; vertical-align: middle;" /> File associati:</span>
                    
                    <!-- File esistenti -->
                    {#if editMemory.files && editMemory.files.length > 0}
                        <div class="existing-files">
                            <h4>File esistenti:</h4>
                            <ul>
                                {#each editMemory.files as file, idx}
                                    <li style="display: flex; align-items: center; gap: 0.5em;">
                                        <span style="font-weight: 600; color: #7fdfff;">{file.display_name || file.original_name || file.name}</span>
                                        <button type="button" class="remove-loc-btn" on:click={() => removeExistingFile(idx)} title="Rimuovi">×</button>
                                    </li>
                                {/each}
                            </ul>
                        </div>
                    {/if}

                    <!-- Aggiungi nuovi file -->
                    <div style="display: flex; align-items: center; gap: 0.7rem; margin: 0.5rem 0;">
                        <input id="edit-add-files" type="file" multiple style="display:none" on:change={handleEditFileSelect} />
                        <button type="button" class="btn-dark-outline file-add-btn" on:click={() => document.getElementById('edit-add-files').click()}>Aggiungi file</button>
                    </div>

                    <!-- Nuovi file selezionati -->
                    {#if editSelectedFiles.length > 0}
                        <div class="new-files">
                            <h4>Nuovi file da aggiungere:</h4>
                            <ul>
                                {#each editSelectedFiles as file, idx}
                                    <li style="display: flex; align-items: center; gap: 0.5em;">
                                        <input 
                                            type="text" 
                                            class="input-beauty dark" 
                                            style="max-width: 180px;" 
                                            bind:value={editFileDisplayNames[idx]} 
                                            on:input={(e) => handleEditDisplayNameChange(idx, e.target.value)} 
                                            placeholder="Nome da mostrare" 
                                        />
                                        <span style="font-size: 0.98em; color: #aaa;">({file.name})</span>
                                        <button type="button" class="remove-loc-btn" on:click={() => removeEditFile(idx)} title="Rimuovi">×</button>
                                    </li>
                                {/each}
                            </ul>
                        </div>
                    {/if}
                </div>

                <textarea 
                    bind:value={editMemory.text} 
                    placeholder="Descrizione..." 
                    rows="5" 
                    class="input-beauty dark"
                ></textarea>

                <div class="modal-actions">
                    <button type="submit" class="btn-dark">Salva modifiche</button>
                    <button type="button" class="btn-dark-outline" on:click={cancelEditMemory}>Annulla</button>
                </div>
            </form>        {:else}
            <!-- Modalità visualizzazione -->
            <div class="view-mode">
                <div class="memory-header">
                    <h3>{memory.title}</h3>
                </div>
                
                <div class="modal-date">{memory.date}</div>

                <!-- Posizioni associate -->
                {#if memory.locations && memory.locations.length > 0}
                    <div class="memory-location-list">
                        <span><img src="/internal-map.svg" alt="location icon" style="width: 2.5em; height: 2.5em; margin-right: 0.4em; opacity: 0.85; display: inline; vertical-align: middle;" /> Posizioni associate:</span>
                        <ul>
                            {#each memory.locations as loc}
                                <li>
                                    <img src="/location.svg" alt="location icon" style="width: 1.1em; height: 1.1em; margin-right: 0.4em; opacity: 0.85; display: inline; vertical-align: middle;" />
                                    <b>{loc.title}</b> ({loc.latitude}, {loc.longitude})
                                    {#if loc.description}
                                        - {loc.description}
                                    {/if}                                    <button 
                                        class="map-3d-btn-memory" 
                                        title="Visualizza sulla mappa 3D" 
                                        aria-label="Visualizza {loc.title} sulla mappa 3D" 
                                        on:click|stopPropagation={() => {
                                            const currentState = getCurrentMenuState();
                                            closeMenusForPopup(currentState.memoryMenuOpen, currentState.positionsMenuOpen);
                                            openMapPopup(loc.latitude, loc.longitude, loc.title);
                                        }}
                                    >
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#ffb86b" stroke-width="2" stroke-linejoin="round"/>
                                            <path d="M2 17L12 22L22 17" stroke="#ffb86b" stroke-width="2" stroke-linejoin="round"/>
                                            <path d="M2 12L12 17L22 12" stroke="#ffb86b" stroke-width="2" stroke-linejoin="round"/>
                                        </svg>
                                    </button>
                                </li>
                            {/each}
                        </ul>
                    </div>
                {/if}

                <!-- File associati -->
                {#if memory.files && memory.files.length > 0}
                    <div class="memory-files-list">
                        <span class="files-label"><img src="/searching.svg" alt="file icon" style="width: 2em; height: 2em; margin-right: 0.4em; opacity: 0.85; display: inline; vertical-align: middle;" /> File associati:</span>
                        <ul>
                            {#each memory.files as file}
                                <li style="display: flex; align-items: center; gap: 0.5em;">
                                    <span style="font-weight: 600; color: #7fdfff;">{file.display_name || file.original_name || file.name}</span>
                                    {#if file.url}                                        <button 
                                            type="button" 
                                            class="file-open-btn" 
                                            on:click={() => handleFileOpenWrapper(file)}
                                            style="margin-left: 0.5em; color: #ffb86b; font-size: 0.95em;"
                                        >
                                            [Apri]
                                        </button>
                                    {/if}
                                </li>
                            {/each}
                        </ul>
                    </div>
                {/if}

                <!-- Testo del ricordo -->
                <div class="modal-text">{memory.text}</div>

                <!-- Bottone Modifica in fondo -->
                <div class="modal-edit-footer">
                    <button class="edit-memory-btn" on:click={startEditMemory}>
                        Modifica
                    </button>
                </div>
            </div>
        {/if}
    </div>
</div>

<style>
.memory-modal-backdrop {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(24, 28, 36, 0.72);
    z-index: 2147483635 !important;
    display: flex;
    align-items: center;
    justify-content: center;
}

.memory-modal {
    background: #23272f;
    border-radius: 16px;
    box-shadow: 0 4px 32px #000a;
    padding: 1.2rem 1.2rem 2rem 2.5rem;
    border: 2px solid #ff7eb3;
    min-width: 420px;
    max-width: 540px;
    min-height: 260px;
    max-height: 70vh;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    color: #fff;
    overflow-y: auto;
    overflow-x: hidden;
    box-sizing: border-box;
}

.memory-modal h3 {
    color: #ff7eb3;
    margin-bottom: 0.7rem;
    font-family: 'Fira Mono', monospace;
    font-size: 1.3rem;
}

.memory-modal .modal-date {
    color: #8f9ba8;
    font-size: 0.98rem;
    margin-bottom: 1.1rem;
}

.memory-modal .modal-text {
    white-space: pre-wrap;
    word-break: break-word;
    font-size: 1.08rem;
    color: #fff;
    max-width: 100%;
    overflow-wrap: break-word;
}

.memory-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
    min-width: 0;
}

.edit-form {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-width: 0;
}

.input-beauty {
    padding: 0.75rem;
    border-radius: 8px;
    border: 2px solid #444;
    background: #1a1e26;
    color: #fff;
    font-size: 1rem;
    transition: border-color 0.2s;
    width: 100%;
    box-sizing: border-box;
}

.input-beauty:focus {
    outline: none;
    border-color: #ff7eb3;
}

.input-beauty.dark {
    background: #23272f;
    border-color: #444;
}

.location-select-row {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    min-width: 0;
}

.location-select-row select {
    flex: 1;
    min-width: 0;
}

.btn-dark-outline {
    background: transparent;
    border: 2px solid #ff7eb3;
    color: #ff7eb3;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
}

.btn-dark-outline:hover {
    background: #ff7eb3;
    color: #23272f;
}

.btn-dark-outline:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-dark {
    background: #ff7eb3;
    border: 2px solid #ff7eb3;
    color: #23272f;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 600;
}

.btn-dark:hover {
    background: #ff9ec7;
    border-color: #ff9ec7;
}

.styled-location-list ul {
    list-style: none;
    padding: 0;
    margin: 0.7rem 0 0 0;
}

.styled-location-list li {
    margin-bottom: 0.3rem;
    font-size: 0.98rem;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    word-break: break-word;
    position: relative;
    overflow-wrap: break-word;
    min-width: 0;
}

.remove-loc-btn {
    background: rgba(255, 126, 179, 0.2);
    border: 1px solid #ff7eb3;
    color: #ff7eb3;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 14px;
    line-height: 1;
    margin-left: auto;
    transition: all 0.2s;
}

.remove-loc-btn:hover {
    background: #ff7eb3;
    color: #23272f;
}

.styled-files-list {
    width: 100%;
    min-width: 0;
}

.styled-files-list .existing-files,
.styled-files-list .new-files {
    margin: 0.5rem 0;
}

.styled-files-list h4 {
    color: #7ddaff;
    font-size: 0.9rem;
    margin: 0.5rem 0 0.3rem 0;
}

.styled-files-list ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.styled-files-list li {
    margin-bottom: 0.3rem;
    font-size: 0.98rem;
}

.file-add-btn {
    font-size: 0.9rem;
    padding: 0.4rem 0.8rem;
}

.modal-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 1rem;
    width: 100%;
}

.close-modal-btn {
    position: sticky;
    top: 0.5rem;
    right: 0.5rem;
    align-self: flex-end;
    color: #ff7eb3;
    font-size: 2.1rem;
    background: none;
    border: none;
    transition: color 0.2s;
    cursor: pointer;
    z-index: 2;
    margin: 0;
}

.close-modal-btn:hover {
    color: #fff;
}

.delete-in-modal-top {
    position: absolute;
    left: 1.5rem;
    top: 1.5rem;
    background: none;
    border: none;
    padding: 0.3rem;
    cursor: pointer;
    z-index: 3;
    transition: all 0.2s;
}

.delete-in-modal-top:hover {
    background: rgba(255, 126, 179, 0.1) !important;
    border-radius: 6px;
}

.memory-location-list {
    color: #ffb86b;
    font-size: 1.04rem;
    margin-bottom: 1.1rem;
    padding: 0.7rem 0.7rem 0.7rem 1.1rem;
    background: rgba(255, 126, 179, 0.10);
    border-radius: 10px;
    border: 1.5px dashed #ff7eb3;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
}

.memory-location-list ul {
    list-style: none;
    padding: 0;
    margin: 0.7rem 0 0 0;
}

.memory-location-list li {
    margin-bottom: 0.3rem;
    font-size: 0.98rem;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    word-break: break-word;
    position: relative;
    overflow-wrap: break-word;
    min-width: 0;
}

.memory-files-list {
    color: #7ddaff;
    font-size: 1.04rem;
    margin-bottom: 1.1rem;
    padding: 0.7rem 0.7rem 0.7rem 1.1rem;
    background: rgba(125, 218, 255, 0.10);
    border-radius: 10px;
    border: 1.5px dashed #7ddaff;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
}

.memory-files-list ul {
    list-style: none;
    padding: 0;
    margin: 0.7rem 0 0 0;
}

.memory-files-list li {
    margin-bottom: 0.3rem;
    font-size: 0.98rem;
    word-break: break-word;
    overflow-wrap: break-word;
    min-width: 0;
}

.map-3d-btn-memory {
    position: relative;
    background: rgba(255, 184, 107, 0.1);
    border: 1px solid rgba(255, 184, 107, 0.3);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    padding: 0.2rem;
    margin-left: 0.5rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.map-3d-btn-memory:hover {
    background: rgba(255, 184, 107, 0.2);
    border-color: rgba(255, 184, 107, 0.6);
    transform: scale(1.1);
}

.file-open-btn {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    padding: 0;
    font-size: inherit;
    text-decoration: underline;
    transition: opacity 0.2s ease;
}

.file-open-btn:hover {
    opacity: 0.8;
}

/* Stili per il footer del bottone modifica */
.modal-edit-footer {
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(125, 218, 255, 0.2);
    display: flex;
    justify-content: center;
}

.edit-memory-btn {
    background: linear-gradient(135deg, #ff7eb3 0%, #ff9ec7 100%);
    border: none;
    color: #23272f;
    padding: 0.85rem 2.5rem;
    border-radius: 12px;
    cursor: pointer;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
    box-shadow: 
        0 4px 15px rgba(255, 126, 179, 0.3),
        0 2px 8px rgba(255, 126, 179, 0.2);
    position: relative;
    overflow: hidden;
}

.edit-memory-btn:hover {
    background: linear-gradient(135deg, #ff9ec7 0%, #ffb3d1 100%);
    transform: translateY(-2px);
    box-shadow: 
        0 6px 20px rgba(255, 126, 179, 0.4),
        0 4px 12px rgba(255, 126, 179, 0.3);
}

.edit-memory-btn:active {
    transform: translateY(0);
    box-shadow: 
        0 2px 8px rgba(255, 126, 179, 0.3),
        0 1px 4px rgba(255, 126, 179, 0.2);
}

.edit-memory-btn:focus {
    outline: 3px solid rgba(255, 126, 179, 0.4);
    outline-offset: 2px;
}

/* Regole per prevenire overflow e migliorare il wrapping del testo */
.view-mode {
    width: 100%;
    min-width: 0;
    overflow-wrap: break-word;
}

/* Migliora il contenimento degli span con testo lungo */
.memory-location-list span,
.memory-files-list span,
.files-label {
    overflow-wrap: break-word;
    word-break: break-word;
    max-width: 100%;
}

/* Gestione specifica per gli input di modifica nel modal */
.styled-files-list li input[type="text"] {
    min-width: 0;
    flex-shrink: 1;
}

/* Assicura che i bottoni non causino overflow */
.map-3d-btn-memory,
.file-open-btn,
.remove-loc-btn {
    flex-shrink: 0;
}

/* Migliora il comportamento delle coordinate lunghe */
.memory-files-list li > span {
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
}

@media (max-width: 600px) {
    .memory-modal {
        min-width: 90vw;
        max-width: 98vw;
        min-height: 180px;
        max-height: 80vh;
        padding: 1.2rem 0.7rem 1.2rem 0.7rem;
    }
    
    .location-select-row {
        flex-direction: column;
        align-items: stretch;
    }
    
    .modal-actions {
        flex-direction: column;
    }
    
    .memory-location-list,
    .memory-files-list {
        padding: 0.5rem;
        margin-bottom: 0.8rem;
    }
    
    .memory-location-list li,
    .memory-files-list li {
        flex-wrap: wrap;
        gap: 0.2rem;
    }
    
    .styled-files-list li {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.3rem;
    }
}
</style>
