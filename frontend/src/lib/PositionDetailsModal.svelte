<script>
import { closePositionDetailsModal } from '$lib/globalModalStore.js';
import * as popupStackModule from '../routes/popupStack';

export let position;

let isEditing = false;
let editPosition = {};
let errorMsg = '';

// Gestione popup stack
$: if (position) {
    popupStackModule.pushPopup(closePositionDetailsModal);
} else {
    popupStackModule.popPopup();
}

function handleModalKeydown(event) {
    if (event.key === 'Escape') {
        closePositionDetailsModal();
    }
}

function startEdit() {
    isEditing = true;
    editPosition = { ...position };
    errorMsg = '';
}

function cancelEdit() {
    isEditing = false;
    editPosition = {};
    errorMsg = '';
}

async function saveEdit() {
    if (!editPosition.title || !editPosition.latitude || !editPosition.longitude) {
        errorMsg = 'Tutti i campi sono obbligatori';
        return;
    }
    try {
        const res = await fetch(`/api/locations`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                old: {
                    title: position.title,
                    latitude: position.latitude,
                    longitude: position.longitude
                },
                updated: editPosition
            })
        });
        if (res.ok) {
            isEditing = false;
            errorMsg = '';
            // Aggiorna la posizione nel parent (opzionale: dispatch event)
            window.dispatchEvent(new CustomEvent('position-updated'));
            closePositionDetailsModal();
        } else {
            errorMsg = 'Errore durante il salvataggio';
        }
    } catch (e) {
        errorMsg = 'Errore di rete';
    }
}
</script>

<div
    class="memory-modal-backdrop"
    aria-label="Chiudi dettagli posizione"
    role="dialog"
    aria-modal="true"
    tabindex="0"
    on:click={closePositionDetailsModal}
    on:keydown={handleModalKeydown}
    style="display: flex; align-items: center; justify-content: center; position: fixed; top: 0; left: 0; right: 0; bottom: 0; width: 100vw; height: 100vh;"
>
    <div
        class="memory-modal"
        on:click|stopPropagation
        role="document"
    >
        <button class="close-modal-btn" on:click={closePositionDetailsModal} title="Chiudi">×</button>
        {#if isEditing}
            <h3>Modifica posizione</h3>
            <form on:submit|preventDefault={saveEdit} style="width:100%">
                <input class="input-beauty dark" type="text" bind:value={editPosition.title} placeholder="Titolo" required style="margin-bottom:0.7em;width:100%" />
                <input class="input-beauty dark" type="number" step="any" bind:value={editPosition.latitude} placeholder="Latitudine" required style="margin-bottom:0.7em;width:100%" />
                <input class="input-beauty dark" type="number" step="any" bind:value={editPosition.longitude} placeholder="Longitudine" required style="margin-bottom:0.7em;width:100%" />
                <textarea class="input-beauty dark" bind:value={editPosition.description} placeholder="Dettagli..." rows="3" style="margin-bottom:0.7em;width:100%"></textarea>
                {#if errorMsg}
                    <div style="color:#ff7eb3; margin-bottom:0.7em;">{errorMsg}</div>
                {/if}
                <div style="display:flex; gap:0.7em;">
                    <button type="submit" class="btn-dark">Salva</button>
                    <button type="button" class="btn-dark-outline btn-dark" on:click={cancelEdit}>Annulla</button>
                </div>
            </form>
        {:else}
            <h3>{position.title}</h3>
            <div class="modal-date">Lat: {position.latitude}, Lon: {position.longitude}</div>
            {#if position.date}
                <div class="modal-date">Data: {position.date}</div>
            {/if}
            {#if position.description && position.description.trim() !== ''}
                <div class="modal-text">{position.description}</div>
            {:else}
                <div class="modal-text" style="color:#8f9ba8;">Nessun dettaglio disponibile.</div>
            {/if}
            <div style="margin-top:1.2em; display:flex; gap:0.7em;">
                <button class="btn-dark" on:click={startEdit}>Modifica</button>
            </div>
        {/if}
    </div>
</div>

<style>
.memory-modal-backdrop {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(24, 28, 36, 0.72);
    z-index: 2147483620 !important;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.2s;
}

.memory-modal {
    background: #23272f;
    border-radius: 18px;
    box-shadow: 0 8px 40px #000a 0px 0px 0px 0px;
    padding: 2.2rem 2.1rem 1.7rem 2.1rem;
    min-width: 270px;
    max-width: 95vw;
    min-height: 120px;
    max-height: 90vh;
    overflow-y: auto;
    color: #fff;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    animation: modalIn 0.18s cubic-bezier(.4,1.6,.6,1) 1;
}

@keyframes modalIn {
    from { transform: scale(0.95) translateY(30px); opacity: 0; }
    to { transform: scale(1) translateY(0); opacity: 1; }
}

.close-modal-btn {
    position: absolute;
    top: 0.7rem;
    right: 1.1rem;
    background: none;
    border: none;
    color: #7ddaff;
    font-size: 2.1rem;
    font-weight: 700;
    cursor: pointer;
    z-index: 2;
    transition: color 0.18s;
    line-height: 1;
    padding: 0;
}

.close-modal-btn:hover {
    color: #ff7eb3;
}

.modal-text {
    margin-top: 1.1rem;
    font-size: 1.13rem;
    color: #fff;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
    white-space: pre-line;
    word-break: break-word;
    line-height: 1.5;
}

.memory-modal h3 {
    color: #ffb86b;
    font-size: 1.35rem;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
    font-weight: 700;
    margin-bottom: 0.5rem;
    margin-top: 0.2rem;
    letter-spacing: 0.2px;
}

.memory-modal .modal-date {
    color: #7ddaff;
    font-size: 1.01rem;
    margin-bottom: 0.2rem;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
    opacity: 0.85;
}

@media (max-width: 600px) {
    .memory-modal {
        padding: 1.1rem 0.7rem 1.1rem 0.7rem;
        min-width: 0;
        max-width: 99vw;
    }
    .close-modal-btn {
        top: 0.3rem;
        right: 0.5rem;
        font-size: 1.6rem;
    }
    .modal-text {
        font-size: 0.98rem;
    }
    .memory-modal h3 {
        font-size: 1.08rem;
    }
}
</style>
