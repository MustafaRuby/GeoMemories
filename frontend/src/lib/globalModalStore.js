import { writable } from 'svelte/store';
import { restoreMenuState } from './menuCloseStore.js';

/*
 * GERARCHIA Z-INDEX DEI MODALI (dal più alto al più basso):
 * 
 * 1. ImageViewer:           2147483647 !important - Il più alto per visualizzazione immagini
 * 2. VideoViewer:           2147483647 !important - Stessa priorità delle immagini per visualizzazione video
 * 3. CesiumMapPopup:        2147483640 !important - Popup mappa 3D
 * 4. MemoryDetailsModal:    2147483635 !important - Dettagli ricordi (aumentato per risolvere conflitto menu)
 * 5. Altri modali globali:  2147483620 !important - AddMemory, AddPosition, PositionDetails
 *
 * 6. Menu laterali e bottoni (valori bassi):
 *    - Bottoni principali:    520-530   - BookButton, MapButton
 *    - Container bottoni:     502, 512  - Wrapper dei bottoni nei menu
 *    - Menu laterali:         500-511   - Menu ricordi e posizioni
 *    - Menu backdrops:        499       - Backdrop dei menu (sotto i menu per interazione)
 * 
 * Questa gerarchia assicura che:
 * - Le immagini e i video siano sempre in primo piano con stessa priorità
 * - La mappa 3D possa aprirsi sopra i dettagli del ricordo
 * - I modali di dettaglio siano sopra quelli di creazione/editing
 * - TUTTI i modali (2+ milioni) siano sopra menu e bottoni (500-600)
 *
 * AGGIORNAMENTO: Rimosso z-index dai container globali (GlobalModalManager e layout)
 * per permettere ai singoli modali di gestire autonomamente il proprio z-index.
 * Ridotti drasticamente i z-index dei menu laterali per garantire che tutti i modali
 * appaiano sempre sopre di essi. Corretti z-index dei backdrop menu da 1999 a 499.
 * RISOLTO stacking context: Sostituito transform con margin-left sui menu per evitare
 * la creazione di nuovi stacking context che impedivano ai modal di apparire sopra.
 *
 * AGGIUNTO !IMPORTANT: Tutti i popup critici ora usano !important per garantire
 * priorità assoluta e prevenire override da altre regole CSS o librerie esterne.
 *
 * GESTIONE POINTER-EVENTS: Aggiunto sistema per disabilitare l'interazione con i menu
 * quando sono aperti modal globali per evitare click simultanei su menu e modal.
 *
 * AGGIUNTO VideoViewer: Viewer per video con stessa priorità dell'ImageViewer per
 * garantire che i contenuti multimediali siano sempre in primo piano.
 */

// Store per gestire i modal a livello globale
export const globalModalStore = writable({
    showAddMemory: false,
    showAddPosition: false,
    showMemoryDetails: false,
    showPositionDetails: false,
    addMemoryData: null,
    addPositionData: null,
    memoryDetailsData: null,
    positionDetailsData: null
});

// Store derivato per controllare se ci sono modal aperti
export const hasOpenModals = writable(false);

// Aggiorna hasOpenModals quando cambiano i modal
globalModalStore.subscribe(state => {
    const isAnyModalOpen = state.showAddMemory || 
                          state.showAddPosition || 
                          state.showMemoryDetails || 
                          state.showPositionDetails;
    hasOpenModals.set(isAnyModalOpen);
});

// Funzioni helper per gestire i modal
export function openAddMemoryModal(data = null) {
    globalModalStore.update(state => ({
        ...state,
        showAddMemory: true,
        addMemoryData: data
    }));
}

export function closeAddMemoryModal() {
    globalModalStore.update(state => ({
        ...state,
        showAddMemory: false,
        addMemoryData: null
    }));
    // Ripristina lo stato dei menu quando si chiude il modal
    restoreMenuState();
}

export function openAddPositionModal(data = null) {
    globalModalStore.update(state => ({
        ...state,
        showAddPosition: true,
        addPositionData: data
    }));
}

export function closeAddPositionModal() {
    globalModalStore.update(state => ({
        ...state,
        showAddPosition: false,
        addPositionData: null
    }));
    // Ripristina lo stato dei menu quando si chiude il modal
    restoreMenuState();
}

export function openMemoryDetailsModal(memory) {
    globalModalStore.update(state => ({
        ...state,
        showMemoryDetails: true,
        memoryDetailsData: memory
    }));
}

export function closeMemoryDetailsModal() {
    globalModalStore.update(state => ({
        ...state,
        showMemoryDetails: false,
        memoryDetailsData: null
    }));
    // Ripristina lo stato dei menu quando si chiude il modal
    restoreMenuState();
}

export function openPositionDetailsModal(position) {
    globalModalStore.update(state => ({
        ...state,
        showPositionDetails: true,
        positionDetailsData: position
    }));
}

export function closePositionDetailsModal() {
    globalModalStore.update(state => ({
        ...state,
        showPositionDetails: false,
        positionDetailsData: null
    }));
    // Ripristina lo stato dei menu quando si chiude il modal
    restoreMenuState();
}
