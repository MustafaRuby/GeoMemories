<script lang="ts">    import { slide } from 'svelte/transition';
    import AddMemoryButton from './AddMemoryButton.svelte';
    import { onMount, afterUpdate, onDestroy } from 'svelte';
    import * as popupStackModule from './popupStack';    import { handleFileOpen } from '$lib/imageViewerStore';    import { openMapPopup } from '$lib/cesiumMapPopupStore.js';
    import { openMemoryDetailsModal } from '$lib/globalModalStore.js';
    import { closeMenusForPopup, getCurrentMenuState } from '$lib/menuCloseStore.js';

    export let showMemory;
    export let onToggle = () => {};    let memories = [];
    let isLoading = false;
    let isLoadingMemories = false; // Flag per evitare chiamate simultanee
    let eventListenersEnabled = true; // Flag per evitare loop infiniti
    let userLocations = [];
    let tempSelectedLocation = null;
    let searchTitle = '';
    let searchDate = '';

    // Funzione di chiusura memoizzata per il menu ricordi
    const closeMemoryMenuIfOpen = () => {
        if (showMemory) onToggle();
    };    async function loadMemories() {
        // Evita chiamate simultanee
        if (isLoadingMemories) {
            console.log('LoadMemories chiamata ignorata - già in corso');
            return;
        }
        
        console.log('LoadMemories avviata');
        isLoadingMemories = true;
        isLoading = true;
        
        // Disabilita temporaneamente gli event listeners per evitare loop
        eventListenersEnabled = false;
        
        try {
            const res = await fetch('/api/memories');
            const newMemories = await res.json();
            console.log('Ricordi caricati:', newMemories.length);
            memories = newMemories; // Sostituisce completamente l'array
        } catch (error) {
            console.error('Error loading memories:', error);
        }
        
        isLoading = false;
        isLoadingMemories = false;
        
        // Riabilita gli event listeners dopo un breve delay
        setTimeout(() => {
            eventListenersEnabled = true;
        }, 1000);
        
        console.log('LoadMemories completata');
    }async function fetchLocations() {
        const response = await fetch('/api/locations', { credentials: 'include' });
        if (response.ok) {
            userLocations = await response.json();
        }
    }    function openMemoryDetails(memory) {
        // Ottiene lo stato attuale dei menu e li chiude memorizzandolo
        const currentState = getCurrentMenuState();
        closeMenusForPopup(currentState.memoryMenuOpen, currentState.positionsMenuOpen);
        
        const memoryWithLocations = { ...memory, locations: Array.isArray(memory.locations) ? memory.locations : [] };
        openMemoryDetailsModal(memoryWithLocations);
    }// Gestione stack popup per ESC
    let popupStackMenu = false;

    $: {
        // Gestione menu ricordi
        if (showMemory && !popupStackMenu) {
            popupStackModule.pushPopup(closeMemoryMenuIfOpen);
            popupStackMenu = true;
        } else if (!showMemory && popupStackMenu) {
            popupStackModule.popPopup();
            popupStackMenu = false;
        }    }

    $: filteredMemories = memories.filter(m =>
        (!searchTitle || m.title.toLowerCase().replace(/\s+/g, '').includes(searchTitle.toLowerCase().replace(/\s+/g, ''))) &&
        (!searchDate || m.date === searchDate)
    );    afterUpdate(() => {
        document.documentElement.style.overflowY = 'scroll';
        document.body.style.overflowY = 'scroll';
        window.dispatchEvent(new Event('resize'));
    });    // Funzione di aggiornamento dei ricordi (definita una sola volta) con debounce
    let updateTimeout;
    const handleMemoryUpdate = (event) => {
        if (!eventListenersEnabled) {
            console.log('Event listener disabilitato - ignorando evento:', event.type);
            return;
        }
        
        console.log('HandleMemoryUpdate chiamata per evento:', event.type);
        // Debounce per evitare chiamate multiple ravvicinate
        clearTimeout(updateTimeout);
        updateTimeout = setTimeout(() => {
            console.log('Debounce completato - chiamando loadMemories');
            loadMemories();
        }, 500); // Aumentato da 100ms a 500ms
    };

    onMount(() => {
        loadMemories();
        
        // Event listeners per ricaricare i ricordi quando vengono modificati o aggiunti
        window.addEventListener('memory-updated', handleMemoryUpdate);
        window.addEventListener('memory-added', handleMemoryUpdate);
    });    onDestroy(() => {
        // Cleanup event listeners
        window.removeEventListener('memory-updated', handleMemoryUpdate);
        window.removeEventListener('memory-added', handleMemoryUpdate);
        
        // Cleanup timeout
        clearTimeout(updateTimeout);
    });async function deleteMemory(memory) {
        if (!confirm('Eliminare definitivamente questo ricordo?')) return;
        
        // Ottiene lo stato attuale dei menu e li chiude memorizzandolo
        const currentState = getCurrentMenuState();
        closeMenusForPopup(currentState.memoryMenuOpen, currentState.positionsMenuOpen);
        
        try {
            const res = await fetch(
                `/api/memories/${encodeURIComponent(memory.title)}/${encodeURIComponent(memory.date)}/${encodeURIComponent(memory.text)}`,
                { method: 'DELETE' }
            );

            if (res.ok) {
                memories = memories.filter(m =>
                    !(m.title === memory.title &&
                      m.date === memory.date &&
                      m.text === memory.text)
                );
            } else {
                alert('Errore durante l\'eliminazione');
            }
        } catch (error) {
            console.error('Delete error:', error);
        }
    }

    // Gestione file associati (solo frontend, mock)
    // function handleFileSelect(e) {
    //     const files = Array.from(e.target.files);
    //     if (!editMemory.files) editMemory.files = [];
    //     editMemory.files = [...editMemory.files, ...files];
    //     // Reset input per permettere la stessa selezione più volte
    //     e.target.value = '';
    // }    // --- FILES CLOUDINARY UPLOAD ---
    // Configuration will be handled in global modal
</script>

<AddMemoryButton />
<div class="memories-search-row">
    <input class="input-beauty dark search-mem-input" type="text" placeholder="Cerca per titolo..." bind:value={searchTitle} />
    <input class="input-beauty dark search-mem-input" type="date" placeholder="Cerca per data..." bind:value={searchDate} />
</div>
{#if isLoading}
    <p class="loading-text">Caricamento...</p>
{:else if filteredMemories.length > 0}
    <div class="diary-grid">
        {#each filteredMemories as memory}
            <div class="diary-card" style="position: relative;">
                <button
                    type="button"
                    class="diary-item-btn"
                    on:click={() => openMemoryDetails(memory)}
                    style="display: flex; flex-direction: column; align-items: flex-start; background: none; border: none; width: 100%; text-align: left; padding: 0; cursor: pointer; gap: 0.3rem;"
                >
                    <span class="diary-dot" style="background: #ff7eb3"></span>
                    <span class="diary-title">{memory.title}</span>
                    <span class="diary-date">{memory.date}</span>
                </button>
                <button
                    class="delete-memory-btn"
                    title="Elimina ricordo"
                    aria-label="Elimina ricordo {memory.title}"
                    on:click|stopPropagation={() => deleteMemory(memory)}
                >
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                        <path d="M6 8V14M10 8V14M14 8V14M3 5H17M8 5V3H12V5" stroke="#ff7eb3" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                </button>
            </div>
        {/each}
    </div>
{:else}
    <p class="memory-placeholder">Nessun ricordo ancora presente.</p>
{/if}

<style>


.diary-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 0.4rem;
}


.diary-title {
    color: #ff7eb3;
    font-weight: 700;
    font-size: 1.13rem;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
    margin-bottom: 0.1rem;
    letter-spacing: 0.2px;
    white-space: normal !important;
    overflow-wrap: anywhere;
    max-width: 100%;
    text-shadow: 0 1px 6px #181c24cc;
}

.diary-date {
    color: #ffb86b;
    font-size: 0.98rem;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
    margin-bottom: 0.2rem;
    opacity: 0.85;
    letter-spacing: 0.1px;
}

.loading-text {
    color: #8f9ba8;
    text-align: center;
    padding: 1rem;
}

.memory-placeholder {
    color: #8f9ba8;
    font-style: italic;
    padding: 1rem;
    text-align: center;
}

.memories-search-row {
    display: flex;
    gap: 0.7rem;
    margin-bottom: 1.1rem;
    align-items: center;
    width: 100%;
}
.search-mem-input {
    flex: 1 1 0;
    min-width: 0;
    max-width: 220px;
}
@media (max-width: 600px) {
    .memories-search-row {
        flex-direction: column;
        gap: 0.4rem;
        align-items: stretch;
    }
    .search-mem-input {        max-width: 100%;
    }
}

.diary-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr); /* massimo 3 colonne su desktop */
    gap: 1.3rem 1.3rem;
    width: 100%;
    box-sizing: border-box;
    padding-bottom: 30px;
    padding-right: 16px; /* Spazio per la scrollbar, evita che le card siano coperte */
}
@media (max-width: 900px) {
    .diary-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
@media (max-width: 600px) {
    .diary-grid {
        grid-template-columns: 1fr;
        gap: 0.7rem 0.7rem;
    }
}
.diary-card {
    background: rgba(255,126,179,0.07);
    border-radius: 12px;
    padding: 1.1rem 1.5rem 1.1rem 1.5rem;
    box-shadow: 0 2px 12px rgba(255,126,179,0.10);
    border: 1.5px dashed #ff7eb3;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    position: relative;
    min-width: 0;
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    box-sizing: border-box;
}

/* Stili per il pulsante delete delle memory */
.delete-memory-btn {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: rgba(35, 39, 47, 0.9);
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s, transform 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.4rem;
    width: 24px;
    height: 24px;
}

.delete-memory-btn:hover {
    background: rgba(35, 39, 47, 1);
    transform: scale(1.1);
}

.delete-memory-btn svg {
    width: 16px;
    height: 16px;
}
</style>