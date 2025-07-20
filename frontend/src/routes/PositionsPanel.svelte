<script lang="ts">
import { createEventDispatcher } from 'svelte';
import { slide } from 'svelte/transition';
import { onMount, afterUpdate, onDestroy } from 'svelte';
import * as popupStackModule from './popupStack';
import { openMapPopup } from '$lib/cesiumMapPopupStore.js';
import { openAddPositionModal, openPositionDetailsModal } from '$lib/globalModalStore.js';
import { closeMenusForPopup, getCurrentMenuState } from '$lib/menuCloseStore.js';

export let showPositions;
export let onToggle = () => {};
export let markerTitle = '';
export let markerLat = '';
export let markerLon = '';
export let markerDetails = '';
export let markerList = [];
export let addMarker = () => {};
export let flyToPosition: (lat: number, lon: number) => void;

let searchTerm = '';
const dispatch = createEventDispatcher();

// Funzione di chiusura memoizzata per il menu posizioni
const closePositionsMenuIfOpen = () => {
    if (showPositions) onToggle();
};

let popupStackMenu = false;

// Espone la funzione openAddModal per essere richiamata dal parent tramite ref
export function openAddModal() {
    // Ottiene lo stato attuale dei menu e li chiude memorizzandolo
    const currentState = getCurrentMenuState();
    closeMenusForPopup(currentState.memoryMenuOpen, currentState.positionsMenuOpen);
    
    openAddPositionModal({
        markerTitle,
        markerLat,
        markerLon,
        markerDetails,
        onAdd: handleAdd,
        onTitleInput: handleTitleInput,
        onLatInput: handleLatInput,
        onLonInput: handleLonInput,
        onDetailsInput: handleDetailsInput
    });
}

function handleAdd() {
    addMarker();
}

function handleTitleInput(v: string) {
    dispatch('updateTitle', v);
}

function handleLatInput(v: string) {
    dispatch('updateLat', v);
}

function handleLonInput(v: string) {
    dispatch('updateLon', v);
}

function handleDetailsInput(v: string) {
    markerDetails = v;
    dispatch('updateDetails', v);
}

function deletePosition(m) {
    if (!confirm('Eliminare questa posizione?')) return;
    
    // Ottiene lo stato attuale dei menu e li chiude memorizzandolo
    const currentState = getCurrentMenuState();
    closeMenusForPopup(currentState.memoryMenuOpen, currentState.positionsMenuOpen);
    
    fetch(`/api/locations/${encodeURIComponent(m.title)}/${encodeURIComponent(m.latitude)}/${encodeURIComponent(m.longitude)}`, {
        method: 'DELETE'
    }).then(res => {
        if (res.ok) {
            // Aggiorna la lista localmente senza ricaricare tutto
            markerList = markerList.filter(pos =>
                !(pos.title === m.title && pos.latitude === m.latitude && pos.longitude === m.longitude)
            );
        } else {
            alert('Errore durante l\'eliminazione della posizione.');
        }
    });
}

function openDetailsModal(pos) {
    // Ottiene lo stato attuale dei menu e li chiude memorizzandolo
    const currentState = getCurrentMenuState();
    closeMenusForPopup(currentState.memoryMenuOpen, currentState.positionsMenuOpen);
    openPositionDetailsModal(pos);
}

// Funzione per aggiornare la lista delle posizioni dal backend
async function refreshPositions() {
    try {
        const res = await fetch('/api/locations');
        if (res.ok) {
            markerList = await res.json();
        }
    } catch (e) {
        // opzionale: gestione errore
    }
}

onMount(() => {
    // Listener per aggiornamento lista posizioni dopo modifica
    const handlePositionUpdated = () => {
        refreshPositions();
    };
    window.addEventListener('position-updated', handlePositionUpdated);

    return () => {
        window.removeEventListener('position-updated', handlePositionUpdated);
    };
});

// Gestione stack popup per ESC
$: {
    // Gestione menu posizioni
    if (showPositions && !popupStackMenu) {
        popupStackModule.pushPopup(closePositionsMenuIfOpen);
        popupStackMenu = true;
    } else if (!showPositions && popupStackMenu) {
        popupStackModule.popPopup();
        popupStackMenu = false;
    }
}

afterUpdate(() => {
    document.documentElement.style.overflowY = 'scroll';
    document.body.style.overflowY = 'scroll';
    window.dispatchEvent(new Event('resize'));
});
</script>

<div class="add-pos-row">
    <button class="add-pos-square" on:click={openAddModal} title="Aggiungi posizione">
        <span class="plus-sign" style="font-weight: 700; font-size: 1.3rem; margin-right: 0.7em;">+</span> Aggiungi posizione
    </button>
</div>

<div class="positions-search-row">
    <input
        type="text"
        class="input-beauty dark search-pos-input"
        placeholder="Cerca posizione per nome..."
        bind:value={searchTerm}
    />
</div>

<div class="positions-grid">
    {#each markerList.filter(m => m.title.toLowerCase().replace(/\s+/g, ' ').includes(searchTerm.toLowerCase().trim().replace(/\s+/g, ' '))) as m}        <div class="position-card">            <button
                type="button"
                class="position-item-btn"
                on:click={() => {
                    const currentState = getCurrentMenuState();
                    closeMenusForPopup(currentState.memoryMenuOpen, currentState.positionsMenuOpen);
                    flyToPosition(m.latitude, m.longitude);
                }}
                style="display: flex; flex-direction: column; align-items: flex-start; background: none; border: none; width: 100%; text-align: left; padding: 0; cursor: pointer; gap: 0.3rem;"
            >
                <span class="position-dot" style="background: #7ddaff"></span>
                <span class="position-title">{m.title}</span>
                <span class="position-coords">({m.latitude}, {m.longitude})</span>
            </button>            <button class="map-3d-btn" title="Visualizza sulla mappa 3D" aria-label="Visualizza {m.title} sulla mappa 3D" on:click|stopPropagation={() => {
                const currentState = getCurrentMenuState();
                closeMenusForPopup(currentState.memoryMenuOpen, currentState.positionsMenuOpen);
                openMapPopup(m.latitude, m.longitude, m.title);
            }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#ffb86b" stroke-width="2" stroke-linejoin="round"/>
                    <path d="M2 17L12 22L22 17" stroke="#ffb86b" stroke-width="2" stroke-linejoin="round"/>
                    <path d="M2 12L12 17L22 12" stroke="#ffb86b" stroke-width="2" stroke-linejoin="round"/>
                </svg>
            </button>
            <button class="delete-pos-btn" title="Elimina posizione" aria-label="Elimina posizione {m.title}" on:click|stopPropagation={() => deletePosition(m)}>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                    <path d="M6 8V14M10 8V14M14 8V14M3 5H17M8 5V3H12V5" stroke="#ff7eb3" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
            <button class="info-pos-btn info-pos-btn-bottom" title="Dettagli posizione" aria-label="Dettagli posizione {m.title}" on:click|stopPropagation={() => openDetailsModal(m)}>
                <svg width="18" height="18" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="10" cy="10" r="9" stroke="#7ddaff" stroke-width="2" fill="none"/>
                    <rect x="9.1" y="8.2" width="1.8" height="5.2" rx="0.9" fill="#7ddaff"/>
                    <rect x="9.1" y="5.2" width="1.8" height="1.8" rx="0.9" fill="#7ddaff"/>
                </svg>
            </button>
        </div>
    {/each}
    {#if markerList.filter(m => m.title.toLowerCase().replace(/\s+/g, ' ').includes(searchTerm.toLowerCase().trim().replace(/\s+/g, ' '))).length === 0}
        <p class="position-placeholder">Nessuna posizione ancora presente.</p>
    {/if}
</div>

<style>
/* Positions sidebar menu styles */

/* Search input */
.positions-search-row {
    padding: 0 1rem;
    margin-bottom: 1rem;
}

.search-pos-input {
    width: 100%;
    padding: 0.7rem 1rem;
    border: 2px solid #7ddaff44;
    border-radius: 10px;
    background: rgba(125, 218, 255, 0.08);
    color: #fff;
    font-size: 1rem;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
    transition: border-color 0.2s, background 0.2s;
}

.search-pos-input:focus {
    border-color: #7ddaff;
    background: rgba(125, 218, 255, 0.12);
    outline: none;
}

.search-pos-input::placeholder {
    color: #8f9ba8;
}

/* Positions grid */
.positions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    padding: 0 1rem 2rem 1rem;
}

.position-card {
    background: rgba(125, 218, 255, 0.08);
    border: 2px solid #7ddaff22;
    border-radius: 12px;
    padding: 1rem;
    transition: all 0.2s;
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.position-card:hover {
    background: rgba(125, 218, 255, 0.12);
    border-color: #7ddaff44;
    transform: translateY(-2px);
}

.position-item-btn {
    background: none;
    border: none;
    cursor: pointer;
    color: inherit;
    font-family: inherit;
    transition: opacity 0.2s;
}

.position-item-btn:hover {
    opacity: 0.8;
}

.position-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-bottom: 0.3rem;
    box-shadow: 0 0 8px currentColor;
}

.position-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #7ddaff;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
}

.position-coords {
    font-size: 0.9rem;
    color: #8f9ba8;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
}

.position-placeholder {
    grid-column: 1 / -1;
    text-align: center;
    color: #8f9ba8;
    font-size: 1.1rem;
    margin: 2rem 0;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
}

/* Button controls */
.info-pos-btn, .delete-pos-btn, .map-3d-btn {
    position: absolute;
    background: rgba(35, 39, 47, 0.9);
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s, transform 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.4rem;
}

.map-3d-btn {
    top: 0.5rem;
    right: 4.5rem;
    background: rgba(255, 184, 107, 0.1);
    border: 1px solid rgba(255, 184, 107, 0.3);
}

.map-3d-btn:hover {
    background: rgba(255, 184, 107, 0.2);
    border-color: rgba(255, 184, 107, 0.6);
    transform: scale(1.1);
    box-shadow: 0 4px 20px rgba(255, 184, 107, 0.3);
}

.info-pos-btn {
    top: 0.5rem;
    right: 2.5rem;
}

.delete-pos-btn {
    top: 0.5rem;
    right: 0.5rem;
}

.info-pos-btn:hover, .delete-pos-btn:hover {
    background: rgba(35, 39, 47, 1);
    transform: scale(1.1);
}

.info-pos-btn-bottom {
    top: auto !important;
    right: 0.5rem !important;
    bottom: 0.5rem !important;
    left: auto !important;
    z-index: 2;
}

@media (max-width: 900px) {
    .positions-grid {
        grid-template-columns: 1fr;
        gap: 0.8rem;
        padding: 0 0.5rem 2rem 0.5rem;
    }
    
    .positions-search-row {
        padding: 0 0.5rem;
    }
    
    /* Riorganizza i pulsanti su mobile per evitare sovrapposizioni */
    .map-3d-btn {
        top: 2.5rem;
        right: 2.5rem;
    }
    
    .info-pos-btn {
        top: 2.5rem;
        right: 0.5rem;
    }
    
    .delete-pos-btn {
        top: 0.5rem;
        right: 0.5rem;
    }
}
.add-pos-row {
    display: flex;
    align-items: center;
    gap: 1.1rem;
    margin: 1.1rem 0 1.2rem 0;
    /* Assicura che il contenuto non esca mai dalla sezione */
    overflow: visible;
    width: 100%;
    box-sizing: border-box;
    justify-content: flex-start;
}
.add-pos-square {
    background: linear-gradient(90deg, #ffb86b 0%, #ff7eb3 100%);
    color: #23272f;
    border-radius: 10px;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.2s, color 0.2s, transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 4px 16px 0 rgba(255,184,107,0.25), 0 0 0 4px #ffb86b44;
    padding: 0.7rem 1.2rem;
    border: none;
    height: 48px;
    min-width: 48px;
    max-width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.7rem;
    margin-left: 1rem;
    /* Per evitare che l'effetto hover lo faccia uscire dalla sezione */
    will-change: transform, box-shadow;
    position: relative;
    z-index: 1;
    box-sizing: border-box;
}
.add-pos-square:hover {
    background: linear-gradient(90deg, #ff7eb3 0%, #ffb86b 100%);
    color: #fff;
    transform: scale(1.07);
    box-shadow: 0 6px 24px 0 rgba(255,184,107,0.35), 0 0 0 6px #ffb86b66;
    z-index: 2;
}
@media (max-width: 900px) {
    .add-pos-row {
        gap: 0.7rem;
        flex-direction: column;
        align-items: stretch;
    }
    .add-pos-square {
        width: 100%;
        min-width: 0;
        max-width: 100%;
        justify-content: center;
        font-size: 1.1rem;
        padding: 0.7rem 0;
        margin-left: 0;    }
}
</style>
