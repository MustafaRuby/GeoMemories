/**
 * Utility per gestire il blocco dello scrolling della pagina
 * in modo sicuro, senza causare salti o problemi di layout.
 */

// Verifica se siamo in ambiente browser
const isBrowser = typeof window !== 'undefined';

// Stato interno
let scrollPosition = 0;
let scrollLocked = false;
let scrollbarWidth = 0;

/**
 * Blocca lo scrolling della pagina, salvando la posizione corrente
 */
export function lockScroll() {
  if (!isBrowser) return;
  
  // Se lo scrolling è già bloccato, non riapplicare tutto il meccanismo
  // ma assicuriamoci che la configurazione sia corretta
  if (scrollLocked) {
    document.documentElement.classList.add('scroll-locked');
    document.body.classList.add('scroll-locked');
    document.body.style.position = 'fixed';
    document.body.style.top = `-${scrollPosition}px`;
    document.body.style.width = '100%';
    document.body.style.overflowY = 'scroll';
    document.body.style.paddingRight = `${scrollbarWidth}px`;
    return;
  }
  
  // Salva la posizione di scroll attuale
  scrollPosition = window.scrollY;
  
  // Calcola la larghezza della scrollbar per compensare
  scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
  
  // Aggiungi classe per stili CSS e blocco scrolling
  document.documentElement.classList.add('scroll-locked');
  document.body.classList.add('scroll-locked');
  
  // Applica stili inline per bloccare lo scrolling mantenendo la posizione visiva
  // Importante: manteniamo la scrollbar visibile ma non funzionante con overflow-y: scroll
  document.body.style.top = `-${scrollPosition}px`;
  document.body.style.position = 'fixed';
  document.body.style.width = '100%';
  document.body.style.overflowY = 'scroll';
  
  // Aggiunge padding-right per compensare la scrollbar e prevenire lo shift
  document.body.style.paddingRight = `${scrollbarWidth}px`;
  
  scrollLocked = true;
}

/**
 * Sblocca lo scrolling della pagina, ripristinando la posizione precedente
 */
export function unlockScroll() {
  if (!isBrowser || !scrollLocked) return;
  
  // Rimuovi classi CSS
  document.documentElement.classList.remove('scroll-locked');
  document.body.classList.remove('scroll-locked');
  
  // Ripristina lo stile normale
  document.body.style.position = '';
  document.body.style.top = '';
  document.body.style.width = '';
  document.body.style.overflowY = '';
  document.body.style.paddingRight = ''; // Rimuove il padding-right aggiunto
  
  // Ripristina la posizione di scrolling
  window.scrollTo(0, scrollPosition);
  
  scrollLocked = false;
  
  // Trigger un resize event per garantire che i componenti si ridisegnino correttamente
  setTimeout(() => {
    window.dispatchEvent(new Event('resize'));
  }, 100);
}
