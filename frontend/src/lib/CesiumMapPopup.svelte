<script>
import { onMount, onDestroy } from 'svelte';
import { browser } from '$app/environment';
import { showMapPopup, selectedPosition, closeMapPopup } from '$lib/cesiumMapPopupStore.js';
import * as popupStackModule from '../routes/popupStack';

// Import condizionale di Cesium solo lato client
let Cesium;
let CESIUM_TOKEN;

// Variabili
let cesiumContainer;
let viewer;
let isVisible = false;
let currentPosition = { lat: 0, lon: 0, title: '' };
let redMarkerEntity = null;
let popupStackRegistered = false;
let cesiumLoaded = false;
let viewerInitializing = false; // Flag per evitare inizializzazioni multiple
let initializationTimeout = null; // Timeout per l'inizializzazione ritardata

// Funzione per chiudere il popup (compatibile con popupStack)
const handleClosePopup = () => {
    // Assicurati di pulire anche durante la chiusura forzata
    if (viewerInitializing) {
        viewerInitializing = false;
    }
    closeMapPopup();
};

// Sottoscrizioni reattive
$: isVisible = $showMapPopup;
$: currentPosition = $selectedPosition;

// Gestione stack popup per ESC
$: {
    if (browser && isVisible && !popupStackRegistered) {
        popupStackModule.pushPopup(handleClosePopup);
        popupStackRegistered = true;
    } else if (browser && !isVisible && popupStackRegistered) {
        popupStackModule.popPopup();
        popupStackRegistered = false;
    }
}

// Reattività per aggiornare il marcatore quando cambia la posizione
$: if (browser && viewer && isVisible && currentPosition.lat !== 0 && currentPosition.lon !== 0) {
    updateRedMarker();
}

// Inizializzazione lato client di Cesium
async function loadCesium() {
    if (cesiumLoaded) return;
    
    try {
        // Import dinamici solo lato client
        const cesiumModule = await import('cesium');
        Cesium = cesiumModule;
        
        // Import dello stile Cesium
        await import('cesium/Build/Cesium/Widgets/widgets.css');
        
        // Import del token
        const tokenModule = await import('$lib/cesium_token');
        CESIUM_TOKEN = tokenModule.CESIUM_TOKEN;
        
        cesiumLoaded = true;
    } catch (err) {
        console.error('Errore nel caricamento di Cesium:', err);
    }
}

function updateRedMarker() {
    if (!browser || !viewer || !Cesium) return;
    
    try {
        // Rimuove il marcatore precedente se esiste
        if (redMarkerEntity) {
            viewer.entities.remove(redMarkerEntity);
            redMarkerEntity = null;
        }
        
        // Aggiunge il nuovo marcatore rosso utilizzando una combinazione di point e billboard per garantire la visibilità
        redMarkerEntity = viewer.entities.add({
            name: currentPosition.title,
            position: Cesium.Cartesian3.fromDegrees(currentPosition.lon, currentPosition.lat),
            billboard: {
                image: new URL('/location.svg', window.location.origin).href,
                scale: 0.5,
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
            },
            point: {
                pixelSize: 12,
                color: Cesium.Color.RED.withAlpha(0.8),
                outlineColor: Cesium.Color.WHITE,
                outlineWidth: 2,
                heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
                disableDepthTestDistance: Number.POSITIVE_INFINITY
            },
            label: {
                text: currentPosition.title,
                font: 'bold 16px sans-serif',
                fillColor: Cesium.Color.WHITE,
                outlineColor: Cesium.Color.BLACK,
                outlineWidth: 2,
                style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                verticalOrigin: Cesium.VerticalOrigin.TOP,
                pixelOffset: new Cesium.Cartesian2(0, -30),
                heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
                disableDepthTestDistance: Number.POSITIVE_INFINITY
            }
        });
        
        // Vola verso la posizione con una vista migliore
        viewer.camera.flyTo({
            destination: Cesium.Cartesian3.fromDegrees(currentPosition.lon, currentPosition.lat, 1000),
            duration: 1.5
        });
    } catch (err) {
        console.error('Errore nell\'aggiornamento del marker:', err);
    }
}

function initializeCesium() {
    if (!cesiumContainer || viewer || !cesiumLoaded || viewerInitializing) {
        console.log('Cesium initialization skipped:', { 
            hasContainer: !!cesiumContainer, 
            hasViewer: !!viewer, 
            cesiumLoaded,
            viewerInitializing 
        });
        return;
    }
    
    console.log('Initializing Cesium viewer');
    viewerInitializing = true;
    
    try {
        Cesium.Ion.defaultAccessToken = CESIUM_TOKEN;
    
        viewer = new Cesium.Viewer(cesiumContainer, {
            timeline: false,
            animation: false,
            baseLayerPicker: false,
            geocoder: false,
            homeButton: false,
            sceneModePicker: false,
            navigationHelpButton: false,
            fullscreenButton: false,
            infoBox: false,
            selectionIndicator: false,
            terrainProvider: new Cesium.EllipsoidTerrainProvider(),
            targetFrameRate: 60,
            contextOptions: {
                webgl: {
                    alpha: true,
                    antialias: true,
                    preserveDrawingBuffer: false, // Importante per liberare memoria
                    powerPreference: "default" // Usa GPU integrata se disponibile
                }
            },
            orderIndependentTranslucency: false, // Disabilitato per performance
            requestRenderMode: true, // Abilita render on-demand per performance
            maximumRenderTimeChange: Infinity
        });
      // Configurazione avanzata della scena
    viewer.scene.globe.enableLighting = true;
    viewer.scene.globe.depthTestAgainstTerrain = false; // Importante per vedere i marker sopra il terreno
    viewer.scene.postProcessStages.fxaa.enabled = true; // Miglior anti-aliasing
    
    // Configura gli eventi di input per evitare conflitti
    viewer.cesiumWidget.screenSpaceEventHandler.removeInputAction(Cesium.ScreenSpaceEventType.LEFT_CLICK);
    viewer.cesiumWidget.screenSpaceEventHandler.removeInputAction(Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);
    
    // Ripristina solo gli eventi necessari per la navigazione della camera
    viewer.cesiumWidget.screenSpaceEventHandler.setInputAction(function(event) {
        // Gestione del click per la navigazione, ma non blocca altri eventi
        viewer.camera.pickEllipsoid(event.position, viewer.scene.globe.ellipsoid);
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    
    // Assicurati che il contenitore Cesium non catturi tutti gli eventi
    if (cesiumContainer) {
        cesiumContainer.style.pointerEvents = 'auto';
        cesiumContainer.addEventListener('click', function(e) {
            e.stopPropagation();
        }, true);
    }
    
    // Configura il provider di immagini separatamente
    Cesium.IonImageryProvider.fromAssetId(3).then(provider => {
        viewer.imageryLayers.removeAll();
        viewer.imageryLayers.addImageryProvider(provider);
    }).catch(error => {
        console.warn('Errore nel caricamento del provider Bing Maps, uso OpenStreetMap:', error);
        // Fallback a OpenStreetMap se Bing non è disponibile
        const osmProvider = new Cesium.OpenStreetMapImageryProvider({
            url: 'https://a.tile.openstreetmap.org/'
        });
        viewer.imageryLayers.removeAll();
        viewer.imageryLayers.addImageryProvider(osmProvider);
    });
    
    // Abilita l'illuminazione del globo
    viewer.scene.globe.enableLighting = true;    // Aggiorna il marcatore se la posizione è già disponibile
    if (currentPosition.lat !== 0 && currentPosition.lon !== 0) {
        updateRedMarker();
    }
      viewerInitializing = false;
    console.log('Cesium viewer initialized successfully');
    
    // Debug: conta i context WebGL
    if (typeof console !== 'undefined') {
        setTimeout(debugWebGLContexts, 1000);
    }    } catch (error) {
        console.error('Error initializing Cesium:', error);
        viewerInitializing = false;
        
        // Se l'errore riguarda i context WebGL, avvisa l'utente
        if (error.message && error.message.includes('WebGL')) {
            console.warn('⚠️ ATTENZIONE: Troppi context WebGL attivi. Il popup della mappa potrebbe non funzionare correttamente.');
            console.warn('💡 SOLUZIONE: Ricarica la pagina per liberare i context WebGL.');
        }
        
        // Pulizia in caso di errore
        if (viewer) {
            try {
                viewer.destroy();
            } catch (destroyError) {
                console.warn('Error destroying failed viewer:', destroyError);
            }
            viewer = null;
        }
    }
}

function destroyCesium() {
    if (viewer) {
        console.log('Destroying Cesium viewer');
        try {
            // Rimuovi tutte le entità per liberare memoria
            viewer.entities.removeAll();
            
            // Rimuovi tutti i layer di imagery
            viewer.imageryLayers.removeAll();
            
            // Stoppa qualsiasi animazione in corso
            viewer.clock.shouldAnimate = false;
            
            // Distruggi il viewer (questo libera il context WebGL)
            viewer.destroy();
        } catch (error) {
            console.warn('Error destroying Cesium viewer:', error);
        } finally {
            viewer = null;
            redMarkerEntity = null;
            viewerInitializing = false;
        }
    }
    
    // Pulisci eventuali timeout in sospeso
    if (initializationTimeout) {
        clearTimeout(initializationTimeout);
        initializationTimeout = null;
    }
}

// Gestione eventi tastiera con gestione migliorata per Escape
function handleKeydown(event) {
    if (event.key === 'Escape' && isVisible) {
        // Solo se il popup è aperto, intercetta ESC
        event.stopPropagation();
        closeMapPopup();
        
        // Reimposta il focus sulla pagina principale per evitare problemi con altri popup
        setTimeout(() => {
            window.focus();
            document.body.focus();
        }, 100);
    }
}

// Gestione click fuori dall'area della mappa per chiudere il popup
function handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
        closeMapPopup();
    }
}

// Gestione specifica per il click del pulsante di chiusura
function handleCloseClick(event) {
    event.preventDefault();
    event.stopPropagation();
    closeMapPopup();
}

// Gestione specifica per evitare propagazione nel contenitore
function handleContainerClick(event) {
    event.stopPropagation();
}

// Funzione per debug - conta i context WebGL attivi
function debugWebGLContexts() {
    if (typeof window !== 'undefined' && window.console) {
        const canvas = document.getElementsByTagName('canvas');
        let webglCount = 0;
        for (let i = 0; i < canvas.length; i++) {
            try {
                const ctx = canvas[i].getContext('webgl') || canvas[i].getContext('webgl2');
                if (ctx) webglCount++;
            } catch (e) {
                // Ignora errori di accesso al context
            }
        }
        console.log(`WebGL contexts attivi: ${webglCount}`);
    }
}

onMount(() => {
    if (!browser) return;
    
    // Carica Cesium prima
    loadCesium().then(() => {
        // Inizializza Cesium se il popup è già visibile
        if (isVisible && cesiumLoaded && !viewer && !viewerInitializing) {
            initializationTimeout = setTimeout(initializeCesium, 150);
        }
    });
    
    // Aggiunge listener per i tasti
    window.addEventListener('keydown', handleKeydown);
});

onDestroy(() => {
    if (!browser) return;
    
    console.log('CesiumMapPopup onDestroy called');
    
    // Cleanup completo
    destroyCesium();
    window.removeEventListener('keydown', handleKeydown);
    
    // Rimuove dal popup stack se registrato
    if (popupStackRegistered) {
        popupStackModule.popPopup();
        popupStackRegistered = false;
    }
});

// Reattività per inizializzare/distruggere Cesium quando il popup si apre/chiude
$: if (browser) {
    if (isVisible && !viewer && cesiumLoaded && !viewerInitializing) {
        // Pulisci eventuali timeout precedenti
        if (initializationTimeout) {
            clearTimeout(initializationTimeout);
        }
        initializationTimeout = setTimeout(initializeCesium, 150);
    } else if (!isVisible && viewer) {
        // Distruggi immediatamente quando si chiude
        destroyCesium();
    }
}
</script>

{#if isVisible}
    <div 
        class="cesium-popup-backdrop"
        role="dialog"
        aria-modal="true"
        aria-labelledby="cesium-popup-title"
        on:click={handleBackdropClick}
        on:keydown={handleKeydown}
        tabindex="-1"
    >        <div class="cesium-popup-container" on:click={handleContainerClick}>
            <div class="cesium-popup-header">
                <h2 id="cesium-popup-title" class="cesium-popup-title">
                    📍 {currentPosition.title}
                </h2>
                <button 
                    class="cesium-popup-close"
                    on:click={handleCloseClick}
                    aria-label="Chiudi mappa"
                    title="Chiudi mappa (ESC)"
                >
                    ×
                </button>
            </div>
            <div class="cesium-popup-content">
                <div 
                    bind:this={cesiumContainer}
                    class="cesium-container-popup"
                ></div>
            </div>
        </div>
    </div>
{/if}

<style>
.cesium-popup-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(20, 20, 30, 0.95);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2147483640 !important; /* Alto z-index per popup mappa - sotto ImageViewer ma sopra altri modali */
    padding: 1rem;
    box-sizing: border-box;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

.cesium-popup-container {
    background: #23272f;
    border-radius: 20px;
    box-shadow: 
        0 20px 60px 0 rgba(0, 0, 0, 0.8),
        0 0 0 2px rgba(125, 218, 255, 0.3),
        0 0 40px 0 rgba(125, 218, 255, 0.2);
    width: 95vw;
    height: 90vh;
    max-width: 1400px;
    max-height: 900px;
    min-width: 320px;
    min-height: 400px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
}

.cesium-popup-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 2rem;
    background: linear-gradient(135deg, #23272f 0%, #2d3442 100%);
    border-bottom: 2px solid rgba(125, 218, 255, 0.2);
    border-radius: 20px 20px 0 0;
    position: relative;
    z-index: 2147483639; /* Appena sotto il pulsante di chiusura */
    pointer-events: auto; /* Assicura che l'header sia sempre interattivo */
}

.cesium-popup-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #7ddaff;
    font-family: 'Fira Mono', 'JetBrains Mono', 'Consolas', 'Menlo', monospace;
    margin: 0;
    text-shadow: 0 2px 8px rgba(125, 218, 255, 0.3);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.cesium-popup-close {
    background: rgba(255, 126, 179, 0.1);
    border: 2px solid rgba(255, 126, 179, 0.3);
    border-radius: 50%;
    color: #ff7eb3;
    font-size: 2rem;
    font-weight: 700;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    line-height: 1;
    padding: 0;
    position: relative;
    z-index: 2147483641; /* Sopra tutto nel popup mappa */
    pointer-events: auto; /* Forza la cliccabilità */
}

.cesium-popup-close:hover {
    background: rgba(255, 126, 179, 0.2);
    border-color: rgba(255, 126, 179, 0.6);
    transform: scale(1.1);
    box-shadow: 0 4px 20px rgba(255, 126, 179, 0.3);
}

.cesium-popup-close:focus {
    outline: 3px solid rgba(255, 126, 179, 0.5);
    outline-offset: 2px;
}

.cesium-popup-content {
    flex: 1;
    padding: 0;
    overflow: hidden;
    background: #23272f;
    border-radius: 0 0 20px 20px;
}

.cesium-container-popup {
    width: 100%;
    height: 100%;
    border-radius: 0 0 20px 20px;
    overflow: hidden;
    background: #23272f;
    position: relative;
    z-index: 1; /* Sotto l'header ma sopra il backdrop */
}

/* Assicura che il canvas Cesium non blocchi gli eventi dell'header */
:global(.cesium-container-popup canvas) {
    pointer-events: auto !important;
    position: relative !important;
    z-index: 1 !important;
}

/* Stili responsivi */
@media (max-width: 768px) {
    .cesium-popup-container {
        width: 98vw;
        height: 95vh;
        border-radius: 16px;
    }
    
    .cesium-popup-header {
        padding: 1rem 1.5rem;
        border-radius: 16px 16px 0 0;
    }
    
    .cesium-popup-title {
        font-size: 1.4rem;
    }
    
    .cesium-popup-close {
        width: 40px;
        height: 40px;
        font-size: 1.6rem;
    }
    
    .cesium-container-popup {
        border-radius: 0 0 16px 16px;
    }
}

@media (max-width: 480px) {
    .cesium-popup-backdrop {
        padding: 0.5rem;
    }
    
    .cesium-popup-container {
        width: 100vw;
        height: 98vh;
        border-radius: 12px;
        min-height: 300px;
    }
    
    .cesium-popup-header {
        padding: 0.8rem 1rem;
        border-radius: 12px 12px 0 0;
    }
    
    .cesium-popup-title {
        font-size: 1.2rem;
    }
    
    .cesium-popup-close {
        width: 36px;
        height: 36px;
        font-size: 1.4rem;
    }
    
    .cesium-container-popup {
        border-radius: 0 0 12px 12px;
    }
}

/* Prevenzione scroll globale quando il popup è attivo - versione non bloccante */
:global(body.cesium-popup-active) {
    /* Manteniamo lo scrolling normale, solo aggiungiamo una classe per stili specifici */
    scrollbar-gutter: stable;
}

:global(html.cesium-popup-active) {
    /* Manteniamo lo scrolling normale */
    scrollbar-gutter: stable;
}

/* Nasconde eventuali scrollbar del viewer Cesium */
:global(.cesium-container-popup .cesium-widget) {
    overflow: hidden !important;
}

:global(.cesium-container-popup .cesium-viewer) {
    overflow: hidden !important;
}

/* Personalizzazioni per il tema scuro di Cesium */
:global(.cesium-container-popup .cesium-toolbar-button) {
    background: rgba(35, 39, 47, 0.9) !important;
    border-color: rgba(125, 218, 255, 0.3) !important;
}

:global(.cesium-container-popup .cesium-toolbar-button:hover) {
    background: rgba(125, 218, 255, 0.2) !important;
    border-color: rgba(125, 218, 255, 0.6) !important;
}
</style>
