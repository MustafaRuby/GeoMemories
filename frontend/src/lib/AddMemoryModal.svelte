<!-- AddMemoryModal.svelte -->
<script>
import { closeAddMemoryModal } from '$lib/globalModalStore.js';

let title = '';
let text = '';
let date = '';
let userLocations = [];
let tempSelectedLocation = null;
let selectedLocations = [];
let selectedFiles = [];
let fileDisplayNames = [];

// Import configurazione Cloudinary
import { CONFIG } from '$lib/config.local.js';

const CLOUDINARY_URL = `https://api.cloudinary.com/v1_1/${import.meta.env.VITE_CLOUDINARY_CLOUD_NAME || CONFIG.CLOUDINARY.CLOUD_NAME}/auto/upload`;
const CLOUDINARY_UPLOAD_PRESET = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET || CONFIG.CLOUDINARY.UPLOAD_PRESET;

// Gestisce la chiusura del modal
function handleClose() {
    closeAddMemoryModal();
    resetForm();
}

function resetForm() {
    title = '';
    text = '';
    date = '';
    tempSelectedLocation = null;
    selectedLocations = [];
    selectedFiles = [];
    fileDisplayNames = [];
}

// Gestione posizioni
function addLocationToMemory() {
    if (tempSelectedLocation && !selectedLocations.some(l => 
        l.title === tempSelectedLocation.title && 
        l.latitude === tempSelectedLocation.latitude && 
        l.longitude === tempSelectedLocation.longitude
    )) {
        selectedLocations = [...selectedLocations, tempSelectedLocation];
        tempSelectedLocation = null;
    }
}

function removeLocationFromMemory(loc) {
    selectedLocations = selectedLocations.filter(l => !(
        l.title === loc.title && 
        l.latitude === loc.latitude && 
        l.longitude === loc.longitude
    ));
}

// Gestione file
function handleFileSelect(e) {
    const input = e.target;
    if (!input.files) return;
    const files = Array.from(input.files);
    
    // Limite di 5 file totali
    if (selectedFiles.length + files.length > 5) {
        alert('Puoi associare al massimo 5 file per ricordo.');
        return;
    }
    
    // Limite di 10 MB per file
    const validFiles = files.filter(f => f.size <= 50 * 1024 * 1024);
    if (validFiles.length < files.length) {
        alert('Ogni file deve essere massimo 50 MB.');
    }
    
    selectedFiles = [...selectedFiles, ...validFiles];
    fileDisplayNames = [...fileDisplayNames, ...validFiles.map(f => f.name)];
    input.value = '';
}

function removeFileFromSelected(file, idx) {
    selectedFiles = selectedFiles.filter((f, i) => i !== idx);
    fileDisplayNames = fileDisplayNames.filter((n, i) => i !== idx);
}

function handleDisplayNameChange(idx, value) {
    fileDisplayNames[idx] = value;
}

// Upload file su Cloudinary
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

// Gestisce l'invio del form
async function handleSubmit() {
    if (!title.trim() || !text.trim() || !date) {
        alert('Compila tutti i campi richiesti');
        return;
    }

    try {
        let uploadedFiles = [];
        if (selectedFiles.length > 0) {
            uploadedFiles = await uploadFilesToCloudinary(selectedFiles, fileDisplayNames);
        }

        const memoryData = {
            title: title.trim(),
            text: text.trim(),
            date,
            locations: selectedLocations,
            files: uploadedFiles
        };

        const res = await fetch('/api/memories', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(memoryData)
        });

        if (res.ok) {
            handleClose();
            // Trigger refresh of memories list
            window.dispatchEvent(new CustomEvent('memory-added'));
        } else {
            const error = await res.text();
            alert(`Errore durante il salvataggio: ${error}`);
        }
    } catch (error) {
        console.error('Save error:', error);
        alert('Errore di connessione');
    }
}

// Carica le posizioni dell'utente
async function fetchLocations() {
    try {
        const response = await fetch('/api/locations', { credentials: 'include' });
        if (response.ok) {
            userLocations = await response.json();
        }
    } catch (error) {
        console.error('Error loading locations:', error);
    }
}

// Carica le posizioni quando il componente viene montato
fetchLocations();
</script>

<div class="modal-add-mem">
    <div class="modal-content">
        <h3>Aggiungi nuovo ricordo</h3>        <form on:submit|preventDefault={handleSubmit}>
            <div class="modal-controls">
                <input
                    class="input-beauty dark"
                    type="text"
                    placeholder="Titolo del ricordo..."
                    bind:value={title}
                    required
                />
                <input
                    class="input-beauty dark"
                    type="date"
                    bind:value={date}
                    required
                />
                
                <!-- Gestione posizioni -->
                <div class="location-select-row">
                    <select 
                        bind:value={tempSelectedLocation}
                        class="input-beauty dark"
                        aria-label="Scegli una posizione da associare"
                    >
                        <option value={null}>Seleziona una posizione</option>
                        {#each userLocations as location}
                            {#if !selectedLocations.some(l => l.title === location.title && l.latitude === location.latitude && l.longitude === location.longitude)}
                                <option value={location}>
                                    {location.title} ({location.latitude}, {location.longitude})
                                </option>
                            {/if}
                        {/each}
                    </select>
                    <button type="button" class="btn-dark-outline" on:click={addLocationToMemory} disabled={!tempSelectedLocation}>Aggiungi</button>
                </div>
                
                <!-- Lista posizioni selezionate -->
                {#if selectedLocations.length > 0}
                    <div class="memory-location-list styled-location-list">
                        <span><img src="/internal-map.svg" alt="location icon" style="width: 2.5em; height: 2.5em; margin-right: 0.4em; opacity: 0.85; display: inline; vertical-align: middle;" /> Posizioni associate:</span>
                        <ul>
                            {#each selectedLocations as loc}
                                <li>
                                    <img src="/location.svg" alt="location icon" style="width: 1.1em; height: 1.1em; margin-right: 0.4em; opacity: 0.85; display: inline; vertical-align: middle;" />
                                    <b>{loc.title}</b> ({loc.latitude}, {loc.longitude})
                                    {#if loc.description}
                                        - {loc.description}
                                    {/if}
                                    <button type="button" class="remove-loc-btn" on:click={() => removeLocationFromMemory(loc)} title="Rimuovi">×</button>
                                </li>
                            {/each}
                        </ul>
                    </div>
                {/if}

                <!-- Sezione file associati -->
                <div class="memory-files-list styled-files-list">
                    <span class="files-label"><img src="/searching.svg" alt="file icon" style="width: 2em; height: 2em; margin-right: 0.4em; opacity: 0.85; display: inline; vertical-align: middle;" /> File associati:</span>
                    <div style="display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.5rem;">
                        <input id="add-files" type="file" multiple style="display:none" on:change={handleFileSelect} />
                        <button type="button" class="btn-dark-outline file-add-btn" on:click={() => document.getElementById('add-files').click()}>Associa file</button>
                    </div>
                    {#if selectedFiles.length > 0}
                        <ul>
                            {#each selectedFiles as file, idx}
                                <li style="display: flex; align-items: center; gap: 0.5em;">
                                    <input type="text" class="input-beauty dark" style="max-width: 180px;" bind:value={fileDisplayNames[idx]} on:input={(e) => handleDisplayNameChange(idx, e.target.value)} placeholder="Nome da mostrare" />
                                    <span style="font-size: 0.98em; color: #aaa;">({file.name})</span>
                                    <button type="button" class="remove-loc-btn" on:click={() => removeFileFromSelected(file, idx)} title="Rimuovi">×</button>
                                </li>
                            {/each}
                        </ul>
                    {:else}
                        <div class="no-files-msg">Nessun file associato. Usa il bottone sopra per aggiungerli.</div>
                    {/if}
                </div>

                <textarea
                    class="input-beauty dark"
                    placeholder="Descrizione del ricordo..."
                    bind:value={text}
                    required
                    rows="4"
                ></textarea>
            </div>
            <div class="modal-actions">
                <button type="submit" class="btn-dark">Salva</button>
                <button type="button" class="btn-dark-outline" on:click={handleClose}>Annulla</button>
            </div>
        </form>
        <button class="close-modal-btn" on:click={handleClose} title="Chiudi">×</button>
    </div>
</div>

<style>
.modal-add-mem {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2147483620 !important;
    background: rgba(24, 28, 36, 0.92);
    overscroll-behavior: contain;
}

.modal-content {
    background: #23272f;
    border-radius: 16px;
    box-shadow: 0 4px 32px #000a;
    padding: 2rem 2.5rem;
    border: 2px solid #ff7eb3;
    min-width: 400px;
    max-width: 95vw;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
    display: flex;
    flex-direction: column;
}

.modal-content h3 {
    color: #ff7eb3;
    margin-bottom: 1.5rem;
    font-family: 'Fira Mono', monospace;
    font-size: 1.3rem;
}

.modal-controls {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
}

textarea {
    resize: vertical;
    min-height: 100px;
}

.modal-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 1.5rem;
}

.location-select-row {
    display: flex;
    gap: 0.7rem;
    align-items: center;
}

.btn-dark, .btn-dark-outline {
    border-radius: 10px;
    font-size: 1.13rem;
    font-family: 'Fira Mono', monospace;
    font-weight: 600;
    padding: 0.7rem 1.5rem;
    box-shadow: 0 2px 8px rgba(255,184,107,0.13);
    margin: 0 0.2rem;
    transition: background 0.18s, color 0.18s, box-shadow 0.18s, border 0.18s;
    outline: none;
    border-width: 2px;
    cursor: pointer;
}

.btn-dark {
    background: linear-gradient(90deg, #ffb86b 0%, #ff7eb3 100%);
    color: #23272f;
    border: 2px solid #ffb86b;
}

.btn-dark:hover, .btn-dark:focus {
    background: linear-gradient(90deg, #ff7eb3 0%, #ffb86b 100%);
    color: #fff;
    box-shadow: 0 4px 16px #ffb86b33;
    border-color: #ff7eb3;
}

.btn-dark-outline {
    background: transparent;
    color: #ff7eb3;
    border: 2px solid #ff7eb3;
}

.btn-dark-outline:hover, .btn-dark-outline:focus {
    background: #ff7eb3;
    color: #23272f;
    box-shadow: 0 4px 16px #ffb86b;
    border-color: #ffb86b;
}

.close-modal-btn {
    position: absolute;
    top: 0.7rem;
    right: 1.1rem;
    color: #ff7eb3;
    font-size: 2.1rem;
    background: none;
    border: none;
    transition: color 0.2s;
    cursor: pointer;
}

.close-modal-btn:hover {
    color: #fff;
}

.input-beauty.dark {
    padding: 0.8rem 1.2rem;
    border-radius: 10px;
    border: 1.5px solid #2d3a4a;
    background: #23272f;
    color: #e0e6ed;
    font-size: 1.09rem;
    transition: border 0.2s, box-shadow 0.2s, background 0.2s;
    box-shadow: 0 2px 8px rgba(20, 20, 40, 0.10);
    outline: none;
}

.input-beauty.dark:focus {
    border: 2px solid #ff7eb3;
    box-shadow: 0 4px 16px #ff7eb333;
    background: #23272f;
}

.input-beauty.dark::placeholder {
    color: #8f9ba8;
    opacity: 1;
    font-style: italic;
    font-size: 1.04rem;
}

textarea.input-beauty.dark {
    min-height: 2.5em;
    max-height: 8em;
    resize: vertical;
}

select.input-beauty.dark {
    background: #1a1d23;
    border: 1px solid #ff7eb3;
    color: white;
    padding: 0.8rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}

/* Stili per i quadrati di sezione - posizioni */
.memory-location-list.styled-location-list {
    color: #ffb86b;
    font-size: 1.04rem;
    margin-bottom: 1.1rem;
    padding: 0.7rem 0.7rem 0.7rem 1.1rem;
    background: rgba(255, 126, 179, 0.10);
    border-radius: 10px;
    border: 1.5px dashed #ff7eb3;
    box-shadow: 0 2px 8px #ff7eb322;
    font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;
}

.memory-location-list.styled-location-list > span {
    font-weight: 600;
    color: #ff7eb3;
    font-size: 1.08rem;
    margin-bottom: 0.3rem;
    display: block;
    letter-spacing: 0.1px;
}

.memory-location-list.styled-location-list ul {
    margin: 0.2rem 0 0 0.7rem;
    padding: 0;
    list-style: disc inside;
}

.memory-location-list.styled-location-list li {
    margin-bottom: 0.18rem;
    color: #f6f7fa;
    font-size: 1.01rem;
    font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    line-height: 1.5;
    background: rgba(127, 222, 255, 0.07);
    border-radius: 6px;
    padding: 0.18em 0.7em 0.18em 0.3em;
    display: flex;
    align-items: center;
    gap: 0.3em;
}

.memory-location-list.styled-location-list li b {
    color: #ffb86b;
    font-weight: 600;
    margin-right: 0.2em;
}

/* Stili per i quadrati di sezione - file */
.memory-files-list.styled-files-list {
    color: #ffb86b;
    font-size: 1.04rem;
    margin-bottom: 1.1rem;
    padding: 0.7rem 0.7rem 0.7rem 1.1rem;
    background: rgba(127, 222, 255, 0.07);
    border-radius: 10px;
    border: 1.5px dashed #7fdfff;
    box-shadow: 0 2px 8px #7fdfff22;
    font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;
}

.memory-files-list.styled-files-list .files-label {
    font-weight: 600;
    color: #7fdfff;
    font-size: 1.08rem;
    margin-bottom: 0.3rem;
    display: block;
    letter-spacing: 0.1px;
}

.memory-files-list.styled-files-list ul {
    margin: 0.2rem 0 0 0.7rem;
    padding: 0;
    list-style: disc inside;
}

.memory-files-list.styled-files-list li {
    margin-bottom: 0.18rem;
    color: #f6f7fa;
    font-size: 1.01rem;
    font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    line-height: 1.5;
    background: rgba(255, 126, 179, 0.07);
    border-radius: 6px;
    padding: 0.18em 0.7em 0.18em 0.3em;
    display: flex;
    align-items: center;
    gap: 0.3em;
}

.memory-files-list.styled-files-list .no-files-msg {
    color: #8f9ba8;
    font-style: italic;
    margin-top: 0.5rem;
}

/* Stili per i bottoni di rimozione */
.memory-location-list.styled-location-list li .remove-loc-btn,
.memory-files-list.styled-files-list li .remove-loc-btn {
    background: none;
    border: none;
    color: #ff7eb3;
    font-size: 1.2rem;
    cursor: pointer;
    margin-left: auto;
    padding: 0.2rem;
    border-radius: 4px;
    transition: background 0.2s;
}

.memory-location-list.styled-location-list li .remove-loc-btn:hover,
.memory-files-list.styled-files-list li .remove-loc-btn:hover {
    background: rgba(255, 126, 179, 0.1);
}

@media (max-width: 900px) {
    .modal-content {
        min-width: 90vw;
        max-width: 95vw;
        padding: 1.5rem 1.2rem;
        margin: 1rem;
    }
}

@media (max-width: 600px) {
    .modal-content {
        min-width: 95vw;
        max-width: 98vw;
        max-height: 95vh;
        padding: 1.2rem 0.8rem;
        margin: 0.5rem;
    }
    
    .modal-content h3 {
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    .close-modal-btn {
        top: 0.5rem;
        right: 0.8rem;
        font-size: 1.8rem;
    }
}
</style>
