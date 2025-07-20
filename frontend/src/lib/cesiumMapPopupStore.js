// Store per gestire il popup della mappa Cesium
import { writable } from 'svelte/store';
import { restoreMenuState } from './menuCloseStore.js';

// Store per controllare la visibilità del popup
export const showMapPopup = writable(false);

// Store per la posizione selezionata (lat, lon, title)
export const selectedPosition = writable({ lat: 0, lon: 0, title: '' });

// Verifica se siamo in ambiente browser (client-side)
const isBrowser = typeof window !== 'undefined';

// Funzioni di controllo del popup
export function openMapPopup(lat, lon, title) {
    selectedPosition.set({ lat, lon, title });
    showMapPopup.set(true);
    
    // Previene lo scrolling del documento principale solo lato client
    if (isBrowser) {
        lockScrolling();
    }
}

export function closeMapPopup() {
    showMapPopup.set(false);
    selectedPosition.set({ lat: 0, lon: 0, title: '' });
    
    // Ripristina lo scrolling del documento principale solo lato client
    if (isBrowser) {
        unlockScrolling();
    }
    
    // Ripristina lo stato dei menu quando si chiude il popup
    restoreMenuState();
}

// Funzioni per gestire il popup della mappa senza bloccare lo scrolling della pagina
function lockScrolling() {
    if (!isBrowser) return;
    
    // Aggiungi una classe per mantenere il layout ed eventuali stili CSS
    document.body.classList.add('cesium-popup-active');
    
    // Non blocchiamo più lo scrolling per mantenere un comportamento normale
    // Imposta solo uno stile per garantire che non ci siano salti/spostamenti
    document.body.style.scrollbarGutter = 'stable';
}

function unlockScrolling() {
    if (!isBrowser) return;
    
    // Rimuove solo la classe CSS
    document.body.classList.remove('cesium-popup-active');
    
    // Trigger window resize per garantire che la UI si aggiusti correttamente
    window.dispatchEvent(new Event('resize'));
}
