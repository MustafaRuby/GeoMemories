<svelte:head>
    <style>
         :global(html) {
            overflow-y: scroll !important; /* Forza scrollbar permanente */
            scrollbar-gutter: stable both-edges; /* Nuova proprietà CSS */
        }

        :global(body) {
            margin: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: overlay !important; /* Scroll moderno */
        }

        .main-container {
            flex: 1;
            overflow: visible !important;
        }
        /* Variabili e stili globali */        :root {
            --memory-color: #ff7eb3;
            --memory-shadow: rgba(255, 126, 179, 0.2);
        }

        .input-beauty.dark {
            background: #343a46;
            border: 1px solid #454d5e;
            color: #fff;
            font-family: 'Fira Mono', monospace;
            border-radius: 6px; /* Aggiunto per coerenza con lo stile */
            padding: 8px 12px;
        }
        
        /* Stile per impedire lo scrolling quando il visualizzatore è aperto */
        body.viewer-active {
            overflow: hidden !important;
            position: fixed !important;
            width: 100% !important;
            height: 100% !important;
        }
          /* Stile per bloccare lo scrolling quando i menu sono aperti */
        :global(html.scroll-locked),
        :global(body.scroll-locked) {
            /* Manteniamo le scrollbar visibili ma non funzionanti per evitare shift di layout */
            overflow: hidden !important;
            /* stable permetterà di evitare salti di layout quando rimuoviamo la scrollbar */
            scrollbar-gutter: stable !important;
        }
          /* Stile specifico per i bottoni laterali, per evitare che siano influenzati dal padding-right */
        :global(.map-btn-modern),
        :global(.book-btn-modern) {
            position: fixed !important;
            /* Assicuriamo che i bottoni non risentano dello shift causato dal padding-right */
            margin-left: 30px !important;
        }
        
        /* Posizionamento specifico per i bottoni per garantire la corretta distanza */
        :global(.book-btn-modern) {
            top: 24px !important;
        }
        
        :global(.map-btn-modern) {
            top: 95px !important;
        }

        @import url('https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;500;700&display=swap');
    </style>
</svelte:head>

<script>
    import ImageViewer from '$lib/ImageViewer.svelte';
    import CesiumMapPopup from '$lib/CesiumMapPopup.svelte';
    import GlobalModalManager from '$lib/GlobalModalManager.svelte';
    import { imageViewerStore, closeImageViewer } from '$lib/imageViewerStore';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { browser } from '$app/environment';

    // Intercetta fetch globalmente per aggiungere JWT
    if (browser) {
        const originalFetch = window.fetch;
        window.fetch = async (input, init = {}) => {
            if (typeof input === 'string' && input.startsWith('/api')) {
                const token = localStorage.getItem('token');
                if (token) {
                    init.headers = init.headers || {};
                    if (typeof init.headers.set === 'function') {
                        init.headers.set('Authorization', `Bearer ${token}`);
                    } else {
                        init.headers = { ...init.headers, Authorization: `Bearer ${token}` };
                    }
                }
            }
            return originalFetch(input, init);
        };
    }
    
    // Ottieni lo stato del visualizzatore di immagini
    let viewerState;
    imageViewerStore.subscribe(state => {
        viewerState = state;
    });
    
    // Handler per la chiusura del visualizzatore
    function handleClose() {
        closeImageViewer();
    }

    onMount(() => {
        // Se la route non è login o register, controlla autenticazione
        const publicRoutes = ['/login', '/register'];
        if (!publicRoutes.includes(window.location.pathname)) {
            const token = localStorage.getItem('token');
            if (!token) {
                goto('/login');
            }
        }
    });
</script>

<div class="main-container">
    <slot />
</div>

<!-- Modal containers globali, renderizzati al livello più alto del DOM -->
<div id="global-modals-container">
    <!-- Visualizzatore di immagini globale -->
    {#if viewerState && viewerState.isVisible}
        <div class="global-image-viewer-container" role="dialog" aria-modal="true">
            <ImageViewer 
                bind:isVisible={viewerState.isVisible}
                imageUrl={viewerState.imageUrl}
                imageName={viewerState.imageName}
                on:close={handleClose}
            />
        </div>
    {/if}

    <!-- Popup della mappa Cesium globale -->
    <CesiumMapPopup />
    
    <!-- Manager per tutti i modal globali -->
    <GlobalModalManager />
</div>

<style>    .global-image-viewer-container {
        /* Questa classe garantisce che il visualizzatore sia renderizzato al livello più alto del DOM */
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 2147483647; /* Massimo z-index per ImageViewer - stesso valore del componente */
        isolation: isolate;
        /* Proprietà per garantire che sia sopra tutto */
        position: fixed !important;
        contain: layout;
        pointer-events: all;
    }
    
    .global-image-viewer-container :global(.image-viewer-overlay) {
        /* Ripristina gli eventi per il visualizzatore effettivo */
        pointer-events: auto;
    }
    
    /* Container per i modal globali */
    #global-modals-container {
        /* Assicura che tutti i modal siano renderizzati al livello più alto */
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none; /* Permette il click-through quando non ci sono modal attivi */
        /* Rimuoviamo il z-index qui per permettere ai singoli modali di gestire il proprio */
    }
    
    /* Gli stili per i modal verranno ereditati dai loro componenti originali */
</style>