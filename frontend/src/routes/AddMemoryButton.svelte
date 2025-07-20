<script lang="ts">
import { createEventDispatcher } from 'svelte';
import { openAddMemoryModal } from '$lib/globalModalStore.js';
import { closeMenusForPopup, getCurrentMenuState } from '$lib/menuCloseStore.js';

const dispatch = createEventDispatcher();

export let label = 'Aggiungi ricordo';

function handleAddMemory() {
    // Ottiene lo stato attuale dei menu e li chiude memorizzandolo
    const currentState = getCurrentMenuState();
    closeMenusForPopup(currentState.memoryMenuOpen, currentState.positionsMenuOpen);
    openAddMemoryModal();
}

// Listen for memory-added events
if (typeof window !== 'undefined') {
    window.addEventListener('memory-added', () => {
        dispatch('added');
    });
}
</script>

<div class="add-memory-row" style="justify-content: center;">
    <button class="add-memory-square" on:click={handleAddMemory} title={label}>
        <span class="plus-sign" style="font-weight: 700; font-size: 1.3rem; margin-right: 0.7em;">+</span> Aggiungi ricordo
    </button>
</div>

<style>
.add-memory-row {
    display: flex;
    align-items: center;
    gap: 1.1rem;
    margin: 1.1rem 0 1.2rem 0;
    overflow: visible;
    width: 100%;
    box-sizing: border-box;
    justify-content: flex-start;
}

.add-memory-square {
    background: linear-gradient(90deg, #ff7eb3 0%, #7ddaff 100%);
    color: #23272f;
    border-radius: 10px;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.2s, color 0.2s, transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 4px 16px 0 rgba(127,222,255,0.18), 0 0 0 4px #ff7eb344;
    padding: 0.7rem 1.2rem;
    border: none;
    height: 48px;
    min-width: 48px;
    max-width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.7rem;
    margin-left: 0;
    will-change: transform, box-shadow;
    position: relative;
    z-index: 1;
    box-sizing: border-box;
}

.add-memory-square:hover {
    background: linear-gradient(90deg, #7ddaff 0%, #ff7eb3 100%);
    color: #fff;
    transform: scale(1.07);
    box-shadow: 0 6px 24px 0 rgba(127,222,255,0.28), 0 0 0 6px #ff7eb366;
    z-index: 2;
}

@media (max-width: 900px) {
    .add-memory-row {
        gap: 0.7rem;
        flex-direction: column;
        align-items: stretch;
        margin: 0.8rem 0 1rem 0;
    }
    
    .add-memory-square {
        width: 100%;
        min-width: 0;
        max-width: 100%;
        justify-content: center;
        font-size: 1.1rem;
        padding: 0.7rem 0;
        margin-left: 0;
    }
}
</style>