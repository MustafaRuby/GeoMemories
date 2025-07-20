// Store globale per gestire la chiusura automatica dei menu laterali
import { writable } from 'svelte/store';

// Variabili per tenere traccia delle funzioni di chiusura
let closeMemoryMenuFn = null;
let closePositionsMenuFn = null;

// Funzione di unlock scroll registrata dal componente principale
let unlockScrollFn = null;

// Variabili per tracciare lo stato attuale dei menu
let currentMemoryMenuOpen = false;
let currentPositionsMenuOpen = false;

// Stato memorizzato dei menu prima dell'apertura di popup
let menuStateBeforePopup = {
    memoryMenuWasOpen: false,
    positionsMenuWasOpen: false,
    stateStored: false
};

// Store per notificare quando i menu devono essere chiusi
export const shouldCloseMenus = writable(false);

// Registra le funzioni di chiusura menu dal componente principale
export function registerMenuCloseFunctions(memoryCloseFn, positionsCloseFn, unlockScroll = null) {
    closeMemoryMenuFn = memoryCloseFn;
    closePositionsMenuFn = positionsCloseFn;
    unlockScrollFn = unlockScroll;
}

// Funzione per aggiornare lo stato corrente dei menu (chiamata dal componente principale)
export function updateMenuState(memoryMenuOpen, positionsMenuOpen) {
    currentMemoryMenuOpen = memoryMenuOpen;
    currentPositionsMenuOpen = positionsMenuOpen;
}

// Funzione per ottenere lo stato attuale dei menu
export function getCurrentMenuState() {
    return {
        memoryMenuOpen: currentMemoryMenuOpen,
        positionsMenuOpen: currentPositionsMenuOpen
    };
}

// Funzione per memorizzare lo stato attuale dei menu
export function storeMenuState(memoryMenuOpen, positionsMenuOpen) {
    menuStateBeforePopup = {
        memoryMenuWasOpen: memoryMenuOpen,
        positionsMenuWasOpen: positionsMenuOpen,
        stateStored: true
    };
    console.log('Menu state stored:', menuStateBeforePopup);
}

// Funzione per ripristinare lo stato dei menu memorizzato
export function restoreMenuState() {
    if (!menuStateBeforePopup.stateStored) {
        console.log('No menu state to restore');
        return;
    }
    
    console.log('Restoring menu state:', menuStateBeforePopup);
    
    // Ripristina i menu che erano aperti
    if (menuStateBeforePopup.memoryMenuWasOpen && openMemoryMenuFn) {
        openMemoryMenuFn();
    }
    if (menuStateBeforePopup.positionsMenuWasOpen && openPositionsMenuFn) {
        openPositionsMenuFn();
    }
    
    // Reset dello stato memorizzato
    menuStateBeforePopup = {
        memoryMenuWasOpen: false,
        positionsMenuWasOpen: false,
        stateStored: false
    };
}

// Funzione per cancellare lo stato memorizzato senza ripristinare
export function clearStoredMenuState() {
    menuStateBeforePopup = {
        memoryMenuWasOpen: false,
        positionsMenuWasOpen: false,
        stateStored: false
    };
    console.log('Menu state cleared');
}

// Variabili per le funzioni di apertura menu
let openMemoryMenuFn = null;
let openPositionsMenuFn = null;

// Registra anche le funzioni di apertura menu
export function registerMenuOpenFunctions(memoryOpenFn, positionsOpenFn) {
    openMemoryMenuFn = memoryOpenFn;
    openPositionsMenuFn = positionsOpenFn;
}

// Funzione per chiudere tutti i menu aperti (con opzione per memorizzare stato)
export function closeAllMenus(storeState = false) {
    let menusClosed = false;
    
    if (closeMemoryMenuFn) {
        closeMemoryMenuFn();
        menusClosed = true;
    }
    if (closePositionsMenuFn) {
        closePositionsMenuFn();
        menusClosed = true;
    }
    
    // Sblocca lo scroll quando vengono chiusi i menu tramite interazione
    if (menusClosed && unlockScrollFn) {
        // Delay per assicurarsi che le chiusure siano completate
        setTimeout(() => {
            unlockScrollFn();
        }, 100);
    }
}

// Nuova funzione per chiudere i menu e memorizzare lo stato per popup
export function closeMenusForPopup(memoryMenuOpen, positionsMenuOpen) {
    // Memorizza lo stato solo se almeno un menu è aperto
    if (memoryMenuOpen || positionsMenuOpen) {
        storeMenuState(memoryMenuOpen, positionsMenuOpen);
        closeAllMenus();
        console.log('Menus closed for popup, state stored');
    }
}

// Funzione per chiudere solo il menu ricordi
export function closeMemoryMenu() {
    if (closeMemoryMenuFn) {
        closeMemoryMenuFn();
    }
}

// Funzione per chiudere solo il menu posizioni
export function closePositionsMenu() {
    if (closePositionsMenuFn) {
        closePositionsMenuFn();
    }
}

// Funzione di utilità per chiudere i menu quando l'utente interagisce con elementi specifici
export function closeMenusOnInteraction() {
    // Chiude i menu con un piccolo delay per garantire che l'azione principale venga completata
    setTimeout(() => {
        closeAllMenus();
    }, 50);
}
