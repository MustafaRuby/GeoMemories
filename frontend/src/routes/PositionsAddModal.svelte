<script lang="ts">
import { onMount, onDestroy } from 'svelte';
import * as popupStackModule from './popupStack';
import { closeAddPositionModal, globalModalStore } from '$lib/globalModalStore.js';

let markerTitle = '';
let markerLat = '';
let markerLon = '';
let markerDetails = '';
let onAdd = () => {};
let onTitleInput = (v: string) => {};
let onLatInput = (v: string) => {};
let onLonInput = (v: string) => {};
let onDetailsInput = (v: string) => {};

// Subscribe to global modal store to get the data
globalModalStore.subscribe(state => {
    if (state.addPositionData) {
        const data = state.addPositionData;
        markerTitle = data.markerTitle || '';
        markerLat = data.markerLat || '';
        markerLon = data.markerLon || '';
        markerDetails = data.markerDetails || '';
        onAdd = data.onAdd || (() => {});
        onTitleInput = data.onTitleInput || ((v: string) => {});
        onLatInput = data.onLatInput || ((v: string) => {});
        onLonInput = data.onLonInput || ((v: string) => {});
        onDetailsInput = data.onDetailsInput || ((v: string) => {});
    }
});

function handleAdd() {
    onAdd();
    closeAddPositionModal();
}

function handleClose() {
    closeAddPositionModal();
}

// Gestione popup stack
onMount(() => {
    popupStackModule.pushPopup(handleClose);
    document.body.classList.add('modal-open');
});

onDestroy(() => {
    popupStackModule.popPopup();
    document.body.classList.remove('modal-open');
});
</script>

<div class="modal-add-pos">
    <div class="modal-content">
        <h3>Aggiungi una posizione</h3>
        <form on:submit|preventDefault={handleAdd} class="controls modal-controls">
            <input type="text" bind:value={markerTitle} placeholder="Nome posizione" required class="input-beauty dark" on:input={e => onTitleInput((e.target as HTMLInputElement).value)} />
            <input type="number" bind:value={markerLat} placeholder="Latitudine" step="any" required class="input-beauty dark" style="width:120px;" on:input={e => onLatInput((e.target as HTMLInputElement).value)} />
            <input type="number" bind:value={markerLon} placeholder="Longitudine" step="any" required class="input-beauty dark" style="width:120px;" on:input={e => onLonInput((e.target as HTMLInputElement).value)} />
            <textarea bind:value={markerDetails} placeholder="Dettagli (facoltativo)" class="input-beauty dark" rows="3" style="resize:vertical;" on:input={e => onDetailsInput((e.target as HTMLTextAreaElement).value)}></textarea>
            <div class="modal-actions">
                <button type="submit" class="btn-dark">Salva</button>
                <button type="button" class="btn-dark-outline" on:click={handleClose}>Annulla</button>
            </div>
        </form>
        <button class="close-modal-btn" on:click={handleClose} title="Chiudi">×</button>
    </div>
</div>

<style>
.modal-add-pos {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2147483620 !important;
    pointer-events: all;
    background: rgba(24, 28, 36, 0.72);
    /* Blocca lo scroll della pagina sottostante */
    overscroll-behavior: contain;
}
.modal-content {
    background: #23272f;
    border-radius: 16px;
    box-shadow: 0 4px 32px #000a;
    padding: 2.2rem 2.5rem 2rem 2.5rem;
    border: 2px solid #ffb86b;
    min-width: 340px;
    min-height: 180px;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.modal-content h3 {
    color: #ffb86b;
    margin-bottom: 1.2rem;
    font-family: 'Fira Mono', monospace;
    font-size: 1.3rem;
}
.modal-controls {
    flex-direction: column;
    gap: 1.1rem;
    margin-bottom: 0.5rem;
    width: 100%;
}
.modal-actions {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    margin-top: 1rem;
}
.close-modal-btn {
    position: absolute;
    top: 0.7rem;
    right: 1.1rem;
    background: none;
    border: none;
    color: #ffb86b;
    font-size: 2.1rem;
    cursor: pointer;
    font-family: inherit;
    transition: color 0.2s;
}
.close-modal-btn:hover {
    color: #fff;
}
:global(body.modal-open) {
    overflow: hidden !important;
}
.btn-dark, .btn-dark-outline{
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
    box-shadow: 0 4px 16px #ff7eb333;
    border-color: #ffb86b;
}
.input-beauty.dark {
    padding: 0.8rem 1.2rem;
    border-radius: 10px;
    border: 1.5px solid #2d3a4a;
    background: #23272f;
    color: #e0e6ed;
    font-size: 1.09rem;
    margin-right: 0.5rem;
    margin-bottom: 0.2rem;
    transition: border 0.2s, box-shadow 0.2s, background 0.2s;
    box-shadow: 0 2px 8px rgba(20, 20, 40, 0.10);
    outline: none;
}
.input-beauty.dark:focus {
    border: 2px solid #ffb86b;
    box-shadow: 0 4px 16px #ffb86b33;
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
</style>
