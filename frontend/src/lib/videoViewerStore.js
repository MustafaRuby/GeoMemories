import { writable } from 'svelte/store';

// Variabili per salvare lo stato originale del documento
let originalOverflow;
let originalPosition;
let originalTop;
let originalViewport;
let storedScrollY;
let viewportMeta;
let originalHtmlOverflow;
let originalHtmlScrollBehavior;

// Store per gestire lo stato del visualizzatore di video
export const videoViewerStore = writable({
    isVisible: false,
    videoUrl: '',
    videoName: ''
});

// Funzione per bloccare lo scrolling
function lockScrolling() {
    if (typeof document === 'undefined') return;
    
    // Store original body styles
    originalOverflow = document.body.style.overflow;
    originalPosition = document.body.style.position;
    originalTop = document.body.style.top;
    storedScrollY = window.scrollY;
    
    // Store original html styles
    const htmlElement = document.documentElement;
    originalHtmlOverflow = htmlElement.style.overflow;
    originalHtmlScrollBehavior = htmlElement.style.scrollBehavior;
    
    // Conserviamo anche le proprietà originali di html
    htmlElement.style.setProperty('overflow', 'hidden', 'important');
    htmlElement.style.setProperty('scrollBehavior', 'auto', 'important');
    
    // Store original viewport meta tag
    viewportMeta = document.querySelector('meta[name="viewport"]');
    originalViewport = viewportMeta ? viewportMeta.getAttribute('content') : '';
    
    // Prevent scrolling - usiamo !important per sovrascrivere qualsiasi altro stile
    document.body.style.setProperty('overflow', 'hidden', 'important');
    document.body.style.setProperty('position', 'fixed', 'important');
    document.body.style.setProperty('top', `-${storedScrollY}px`, 'important');
    document.body.style.setProperty('width', '100%', 'important');
    document.body.style.setProperty('touch-action', 'none', 'important');
    
    // Aggiungi una classe per ulteriori regole CSS
    document.body.classList.add('video-viewer-active');
    
    // Disable zoom on mobile
    if (viewportMeta) {
        viewportMeta.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
    } else {
        const newMeta = document.createElement('meta');
        newMeta.name = 'viewport';
        newMeta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
        document.head.appendChild(newMeta);
    }
}

// Funzione per sbloccare lo scrolling
function unlockScrolling() {
    if (typeof document === 'undefined') return;
    
    // Rimuovi la classe che blocca lo scrolling
    document.body.classList.remove('video-viewer-active');
    
    // Restore original styles and scroll position
    if (originalOverflow !== undefined) {
        document.body.style.removeProperty('overflow');
        document.body.style.overflow = originalOverflow;
    } else {
        document.body.style.removeProperty('overflow');
    }
    
    if (originalPosition !== undefined) {
        document.body.style.removeProperty('position');
        document.body.style.position = originalPosition;
    } else {
        document.body.style.removeProperty('position');
    }
    
    if (originalTop !== undefined) {
        document.body.style.removeProperty('top');
        document.body.style.top = originalTop;
    } else {
        document.body.style.removeProperty('top');
    }
    
    document.body.style.removeProperty('width');
    document.body.style.removeProperty('touch-action');
    
    // Ripristina anche gli stili di html
    const htmlElement = document.documentElement;
    htmlElement.style.removeProperty('overflow');
    htmlElement.style.removeProperty('scrollBehavior');
    
    if (originalHtmlOverflow !== undefined) {
        htmlElement.style.overflow = originalHtmlOverflow;
    }
    
    if (originalHtmlScrollBehavior !== undefined) {
        htmlElement.style.scrollBehavior = originalHtmlScrollBehavior;
    }
    
    // Restore original viewport
    const currentViewportMeta = document.querySelector('meta[name="viewport"]');
    if (currentViewportMeta) {
        if (originalViewport) {
            currentViewportMeta.setAttribute('content', originalViewport);
        } else {
            document.head.removeChild(currentViewportMeta);
        }
    }
    
    // Scroll back to the original position - utilizziamo un timeout per assicurarci che avvenga dopo il ripristino delle proprietà
    setTimeout(() => {
        window.scrollTo({
            top: storedScrollY || 0,
            behavior: 'auto'
        });
    }, 10);
    
    // Reset stored values
    originalOverflow = undefined;
    originalPosition = undefined;
    originalTop = undefined;
    originalViewport = undefined;
    originalHtmlOverflow = undefined;
    originalHtmlScrollBehavior = undefined;
    storedScrollY = undefined;
}

// Azioni per lo store
export const openVideoViewer = (videoUrl, videoName) => {
    lockScrolling();
    videoViewerStore.update(state => ({ 
        isVisible: true, 
        videoUrl, 
        videoName 
    }));
};

export const closeVideoViewer = () => {
    unlockScrolling();
    videoViewerStore.update(state => ({ 
        ...state, 
        isVisible: false 
    }));
};

// Helper per determinare se un file è un video
export const isVideoFile = (file) => {
    if (!file || !file.type) return false;
    return file.type.startsWith('video/') || 
           /\.(mp4|avi|mov|wmv|flv|webm|mkv|m4v|3gp|ogv)$/i.test(file.url || file.name || '');
};

// Helper per gestire l'apertura di un file video
export const handleVideoOpen = (file) => {
    if (isVideoFile(file)) {
        openVideoViewer(file.url, file.display_name || file.original_name || file.name);
    }
};
