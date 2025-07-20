<script lang="ts">
import { writable } from 'svelte/store';
import MapSection from './MapSection.svelte';
import SearchBar from './SearchBar.svelte';
import PositionsPanel from './PositionsPanel.svelte';
import showFloatingAddBtn from './positionsPanelStore.js';
import MemoriesPanel from './MemoriesPanel.svelte';
import { onMount, afterUpdate } from 'svelte';
import * as Cesium from 'cesium';
import { goto } from '$app/navigation';
import BookButton from './book.svelte';
import MapButton from './MapButton.svelte';
import { lockScroll, unlockScroll } from '$lib/scrollLock.js';
import { hasOpenModals } from '$lib/globalModalStore.js';
import { registerMenuCloseFunctions, registerMenuOpenFunctions, updateMenuState } from '$lib/menuCloseStore.js';

// @ts-ignore
import * as popupStackModule from './popupStack';

let viewer;
let locations = [];
let markerTitle = '';
let markerLat = '';
let markerLon = '';
let searchQuery = '';
let markerList = [];
let tempSelectionEntity = null;
let basemap = 'bing';
let showMemory = writable(false);
let user = undefined;
let title = '';
let date = '';
let text = '';
let markerEntities = {};
let positionsPanelRef;
let showMemoryMenu = false;
let showPositionsMenu = false;
let markerDetails = '';
let areModalsOpen = false;

// Sottoscrizione ai modal globali per disabilitare menu quando necessario
hasOpenModals.subscribe(value => {
    areModalsOpen = value;
});

// Funzioni reattive per gestire lo scroll lock quando i menu cambiano stato
$: {
    // Gestione scroll lock per il menu ricordi
    if (showMemoryMenu) {
        lockScroll();
    } else if (!showPositionsMenu) {
        // Sblocca solo se anche l'altro menu è chiuso
        unlockScroll();
    }
    // Aggiorna lo stato dei menu nel store globale
    updateMenuState(showMemoryMenu, showPositionsMenu);
}

$: {
    // Gestione scroll lock per il menu posizioni
    if (showPositionsMenu) {
        lockScroll();
    } else if (!showMemoryMenu) {
        // Sblocca solo se anche l'altro menu è chiuso
        unlockScroll();
    }
    // Aggiorna lo stato dei menu nel store globale
    updateMenuState(showMemoryMenu, showPositionsMenu);
}

// Aggiornamento dello stato dei menu nel store globale
$: updateMenuState(showMemoryMenu, showPositionsMenu);

function openAddPositionModal() {
    positionsPanelRef?.openAddModal?.();
}

function toggleMemoryMenu() {
    // Impedisce l'apertura del menu se ci sono modal aperti
    if (areModalsOpen && !showMemoryMenu) {
        return;
    }
    
    if (showPositionsMenu) {
        showPositionsMenu = false;
    }
    showMemoryMenu = !showMemoryMenu;
}

function togglePositionsMenu() {
    // Impedisce l'apertura del menu se ci sono modal aperti
    if (areModalsOpen && !showPositionsMenu) {
        return;
    }
    
    if (showMemoryMenu) {
        showMemoryMenu = false;
    }
    showPositionsMenu = !showPositionsMenu;
}

onMount(() => {
    registerMenuCloseFunctions(
        () => { showMemoryMenu = false; },
        () => { showPositionsMenu = false; },
        () => { unlockScroll(); }
    );
    registerMenuOpenFunctions(
        () => { showMemoryMenu = true; },
        () => { showPositionsMenu = true; }
    );
    // Nuova logica: controllo solo presenza e validità del token JWT
    const token = localStorage.getItem('token');
    if (!token) {
        goto('/login');
        return;
    }
    // (Opzionale) Decodifica e controllo scadenza JWT lato client
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.exp && Date.now() / 1000 > payload.exp) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            goto('/login');
            return;
        }
        user = JSON.parse(localStorage.getItem('user')) || { name: payload.name || payload.username || 'Utente' };
        fetchLocations();
    } catch (e) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        goto('/login');
    }
});

onMount(() => {
    const escListener = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
            // Chiude solo il popup più sopra, se presente
            const closed = popupStackModule.closeTopPopup();
            if (!closed) {
                // Se nessun popup era aperto, deseleziona il marcatore blu
                handleDeselectTempMarker();
            }
        }
    };
    window.addEventListener('keydown', escListener);
    
    // Handler per assicurarsi che lo scrolling sia sbloccato quando l'utente lascia la pagina
    const handleBeforeUnload = () => {
        unlockScroll();
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
        window.removeEventListener('keydown', escListener);
        window.removeEventListener('beforeunload', handleBeforeUnload);
        // Assicuriamoci che lo scrolling sia sbloccato quando il componente viene distrutto
        unlockScroll();
    };
});

async function fetchLocations() {
    try {
        const res = await fetch('/api/locations');
        if (res.status === 404) {
            goto('/404');
            return;
        } else if (res.status === 400) {
            goto('/400');
            return;
        } else if (res.status === 500) {
            goto('/500');
            return;
        }
        locations = await res.json();
        markerList = locations;
        addPointsToMap();
    } catch (err) {
        goto('/500');
    }
}

function addPointsToMap() {
    if (!viewer) return;
    // Crea una mappa delle chiavi attuali
    const currentKeys = new Set(locations.map(loc => `${loc.title}_${loc.latitude}_${loc.longitude}`));
    // Rimuovi entità che non sono più presenti
    for (const key in markerEntities) {
        if (!currentKeys.has(key)) {
            viewer.entities.remove(markerEntities[key]);
            delete markerEntities[key];
        }
    }
    // Aggiungi nuove entità se non già presenti
    locations.forEach(loc => {
        const key = `${loc.title}_${loc.latitude}_${loc.longitude}`;
        if (!markerEntities[key]) {
            const entity = viewer.entities.add({
                position: Cesium.Cartesian3.fromDegrees(parseFloat(loc.longitude), parseFloat(loc.latitude)),
                point: {
                    pixelSize: 14,
                    color: Cesium.Color.fromCssColorString('#a259ff'),
                    outlineColor: Cesium.Color.WHITE,
                    outlineWidth: 2
                },
                label: {
                    text: loc.title,
                    fillColor: Cesium.Color.WHITE,
                    outlineColor: Cesium.Color.BLACK,
                    outlineWidth: 4,
                    pixelOffset: new Cesium.Cartesian2(0, -20),
                    font: 'bold 16px sans-serif'
                }
            });
            markerEntities[key] = entity;
        }
    });
}

function resetForm() {
    markerTitle = '';
    markerLat = '';
    markerLon = '';
    markerDetails = '';
}

async function addMarker() {
    if (!markerTitle || !markerLat || !markerLon) return;
    const marker = {
        title: markerTitle,
        latitude: parseFloat(markerLat),
        longitude: parseFloat(markerLon),
        description: markerDetails
    };
    try {
        const res = await fetch('/api/locations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(marker)
        });
        if (res.status === 404) {
            goto('/404');
            return;
        } else if (res.status === 400) {
            goto('/400');
            return;
        } else if (res.status === 500) {
            goto('/500');
            return;
        }
        resetForm();
        await fetchLocations();
        if (tempSelectionEntity) {
            viewer.entities.remove(tempSelectionEntity);
            tempSelectionEntity = null;
        }
        showFloatingAddBtn.set(false); // Nascondi il bottone fisso
    } catch (err) {
        goto('/500');
    }
}

async function searchPlace(e) {
    e.preventDefault();
    if (!searchQuery) return;
    try {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}`;
        // Cambia lingua in inglese per risultati più accurati
        const res = await fetch(url, { headers: { 'Accept-Language': 'en' } });
        if (!res.ok) {
            goto('/500');
            return;
        }
        const data = await res.json();
        if (data.length === 0) {
            alert('No results found.');
        } else {
            const place = data[0];
            const lat = parseFloat(place.lat).toFixed(6);
            const lon = parseFloat(place.lon).toFixed(6);
            let zoom = 50000;
            if (place.boundingbox) {
                const [lat1, lat2, lon1, lon2] = place.boundingbox.map(Number);
                const latDiff = Math.abs(lat1 - lat2);
                const lonDiff = Math.abs(lon1 - lon2);
                const maxDiff = Math.max(latDiff, lonDiff);
                if (maxDiff < 0.01) zoom = 1000;
                else if (maxDiff < 0.1) zoom = 20000;
                else if (maxDiff < 1) zoom = 100000;
                else zoom = 500000;
            }
            viewer.camera.flyTo({ destination: Cesium.Cartesian3.fromDegrees(parseFloat(lon), parseFloat(lat), zoom) });
            markerLat = lat.toString();
            markerLon = lon.toString();
        }
    } catch (err) {
        goto('/500');
    }
}

function changeBasemap(e) {
    const imageryLayers = viewer.imageryLayers;
    imageryLayers.removeAll();
    if (basemap === 'bing') {
        Cesium.IonImageryProvider.fromAssetId(3).then(provider => {
            imageryLayers.addImageryProvider(provider);
        });
    } else {
        imageryLayers.addImageryProvider(new Cesium.OpenStreetMapImageryProvider({ url: 'https://a.tile.openstreetmap.org/' }));
    }
}

function handleViewerReady(e) {
    viewer = e.detail.viewer;
    fetchLocations();
    setTimeout(() => {
        basemap = 'osm';
        changeBasemap({});
        setTimeout(() => {
            basemap = 'bing';
            changeBasemap({});
        }, 500);
    }, 500);
    viewer.screenSpaceEventHandler.setInputAction(function (movement) {
        const cartesian = viewer.camera.pickEllipsoid(movement.position);
        if (cartesian) {
            const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
            const lat = Cesium.Math.toDegrees(cartographic.latitude).toFixed(6);
            const lon = Cesium.Math.toDegrees(cartographic.longitude).toFixed(6);
            markerLat = lat.toString();
            markerLon = lon.toString();
            if (tempSelectionEntity) viewer.entities.remove(tempSelectionEntity);
            tempSelectionEntity = viewer.entities.add({
                position: Cesium.Cartesian3.fromDegrees(parseFloat(lon), parseFloat(lat)),
                point: { pixelSize: 14, color: Cesium.Color.BLUE, outlineColor: Cesium.Color.WHITE, outlineWidth: 2 }
            });
            showFloatingAddBtn.set(true); // Mostra il bottone fisso
        }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
}

// Gestione evento custom per ESC/deselezione
function handleDeselectTempMarker() {
    if (tempSelectionEntity) {
        viewer.entities.remove(tempSelectionEntity);
        tempSelectionEntity = null;
    }
    showFloatingAddBtn.set(false);
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

function flyToPosition(lat, lon) {
    if (!viewer) return;
    viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(parseFloat(lon), parseFloat(lat), 350), // zoom leggermente meno vicino
        duration: 1.2
    });
}
</script>

<style>
:global(body) {
    background: #181c24;
    color: #e0e6ed;
    font-family: 'Fira Mono', 'JetBrains Mono', 'Consolas', 'Menlo', monospace;
}
.page-container.dark {
    background: linear-gradient(120deg, #23272f 0%, #181c24 100%);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.main-title {
    margin-top: 0.5rem;
    margin-bottom: 0.8rem;
    color: #ffb86b;
    font-size: 2.7rem;
    letter-spacing: 1px;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
    text-shadow: 0 2px 8px #0a0a0a;
    background: linear-gradient(90deg, #ffb86b 10%, #7ddaff 90%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
:global(.expand-section) {
    display: flex;
    flex-direction: column;
    min-height: 64px;
    background: rgba(35,39,47,0.95);
    border-radius: 14px;
    box-shadow: 0 2px 12px rgba(255,184,107,0.06);
    padding: 0.5rem 1.2rem 1.2rem 1.2rem;
    overflow: hidden;
    position: relative;
    margin-bottom: 1.2rem;
}
:global(.expand-content) {
    display: flex;
    flex-direction: column;
    flex: 1 1 auto;
    overflow-y: auto;
    min-height: 0;
    max-height: 350px;
    transition: max-height 0.35s cubic-bezier(0.4,0,0.2,1), opacity 0.35s cubic-bezier(0.4,0,0.2,1);
    opacity: 1;
    will-change: max-height, opacity;
}
:global(.expand-content.hide) {
    max-height: 0 !important;
    opacity: 0;
    pointer-events: none;
}
:global(.expand-btn) {
    width: 100%;
    background: none;
    border: none;
    color: #ffb86b;
    font-size: 1.25rem;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
    font-weight: 700;
    text-align: left;
    padding: 0.7rem 0 0.7rem 0.2rem;
    cursor: pointer;
    outline: none;
    transition: color 0.2s;
}
:global(.expand-btn.memory) {
    color: #ff7eb3;
}
:global(.expand-btn:hover) {
    color: #fff;
}
:global(.marker-list.dark.diary-list) {
    margin-top: 1rem;
    background: #23272f;
    border-radius: 16px;
    padding: 1.2rem 2.2rem;
    box-shadow: 0 2px 12px rgba(255,184,107,0.08);
    width: 100%;
    max-width: 100%;
    border: 1.5px dashed #ffb86b;
    overflow-y: auto;
    overflow-x: hidden;
    max-height: 200px;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    box-sizing: border-box;
}
:global(.marker-item) {
    display: flex;
    align-items: center;
    margin-bottom: 0.7rem;
    font-size: 1.13rem;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
    background: rgba(255,184,107,0.07);
    border-radius: 8px;
    padding: 0.3rem 0.7rem;
    min-width: 0;
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    box-sizing: border-box;
    cursor: pointer;
    border: none;
    background-clip: padding-box;
}
:global(.marker-item:focus) {
    outline: 2px solid #ffb86b;
    outline-offset: 2px;
}
:global(.diary-item) {
    display: flex;
    align-items: center;
    margin-bottom: 0.7rem;
    font-size: 1.13rem;
    font-family: 'Fira Mono', 'JetBrains Mono', monospace;
    background: rgba(255,126,179,0.07);
    border-radius: 8px;
    padding: 0.3rem 0.7rem;
    min-width: 0;
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    box-sizing: border-box;
    cursor: pointer;
    border: none;
    background-clip: padding-box;
}
:global(.diary-item:focus) {
    outline: 2px solid #ffb86b;
    outline-offset: 2px;
}
:global(.marker-dot.diary-dot) {
    width: 13px;
    height: 13px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ffb86b 0%, #ff7eb3 100%);
    margin-right: 10px;
    box-shadow: 0 0 8px #ffb86b99;
}
:global(.marker-title.diary-title) {
    color: #ffb86b;
    font-weight: 700;
    margin-right: 8px;
}
:global(.marker-coords.diary-coords) {
    color: #b0b8c1;
    font-size: 0.98rem;
}
:global(.diary-list.dark) {
    margin-top: 1rem;
    background: #23272f;
    border-radius: 16px;
    padding: 1.2rem 2.2rem;
    box-shadow: 0 2px 12px rgba(255,126,179,0.18); /* glowing rosa */
    width: 100%;
    max-width: 100%;
    border: 1.5px dashed #ff7eb3;
    overflow-y: auto;
    overflow-x: hidden;
    max-height: 200px;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    box-sizing: border-box;
}
:global(.diary-dot) {
    width: 13px;
    height: 13px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff7eb3 0%, #ffb86b 100%);
    margin-right: 10px;
    box-shadow: 0 0 8px #ff7eb399;
}
:global(.diary-title) {
    color: #ff7eb3;
    font-weight: 700;
    margin-right: 8px;
}
:global(.diary-date) {
    color: #b0b8c1;
    font-size: 0.98rem;
}
:global(.memory-section) {
    margin-top: 0.5rem;
    background: rgba(255,184,107,0.04);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
}
:global(.memory-placeholder) {
    color: #b0b8c1;
    font-style: italic;
    margin-top: 0.7rem;
}
:global(.controls) {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}
:global(.input-beauty.dark) {
    padding: 0.7rem 1.2rem;
    border-radius: 10px;
    border: 1.5px solid #2d3a4a;
    background: #23272f;
    color: #e0e6ed;
    font-size: 1.1rem;
    margin-right: 0.5rem;
    transition: border 0.2s, box-shadow 0.2s;
    box-shadow: 0 2px 8px rgba(20, 20, 40, 0.13);
}
:global(.input-beauty.dark:focus) {
    border: 2px solid #ffb86b;
    outline: none;
    box-shadow: 0 4px 16px rgba(255,184,107,0.13);
    background: #23272f;
}
:global(.btn-dark) {
    background: linear-gradient(90deg, #23272f 0%, #2d3a4a 100%);
    color: #7ddaff;
    border: none;
    border-radius: 10px;
    padding: 0.7rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(20, 20, 40, 0.13);
    cursor: pointer;
    transition: background 0.2s, transform 0.2s;
}
:global(.btn-dark:hover) {
    background: linear-gradient(90deg, #2d3a4a 0%, #23272f 100%);
    color: #fff;
    transform: translateY(-2px) scale(1.04);
}
:global(.btn-memory) {
    background: linear-gradient(90deg, #ffb86b 0%, #ff7eb3 100%);
    color: #23272f;
    border: none;
    border-radius: 10px;
    padding: 0.7rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(255,184,107,0.13);
    cursor: pointer;
    transition: background 0.2s, color 0.2s, transform 0.2s;
}
:global(.btn-memory:hover) {
    background: linear-gradient(90deg, #ff7eb3 0%, #ffb86b 100%);
    color: #fff;
    transform: translateY(-2px) scale(1.04);
}
.user-bar {
    position: absolute;
    top: 1.2rem;
    right: 2.2rem;
    font-size: 1.1rem;
    color: #ffb86b;
    font-family: 'Fira Mono', monospace;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    z-index: 10;
}
.logout-btn {
    background: none;
    border: none;
    color: #ffb86b;
    font-size: 1.05rem;
    font-family: inherit;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s, transform 0.2s;
}
.logout-btn:hover {
    background-color: rgba(255, 184, 107, 0.1);
    transform: scale(1.1);
}
.logout-btn:focus {
    outline: 2px solid #ffb86b;
    outline-offset: 2px;
}
.logout-icon {
    width: 40px;
    height: 40px;
    filter: brightness(0) saturate(100%) invert(78%) sepia(45%) saturate(466%) hue-rotate(346deg) brightness(107%) contrast(101%);
    transition: filter 0.2s;
}
.logout-btn:hover .logout-icon {
    filter: brightness(0) saturate(100%) invert(70%) sepia(89%) saturate(6444%) hue-rotate(299deg) brightness(104%) contrast(97%);
}
.searchbar-row {
    display: flex;
    align-items: stretch;
    gap: 1.2rem;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
    justify-content: flex-start;
    flex-wrap: wrap;
}
.add-pos-near-search, .cancel-pos-near-search {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    border-radius: 10px;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.2s, color 0.2s, transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 4px 16px 0 rgba(255,184,107,0.25), 0 0 0 4px #ffb86b44;
    padding: 0.7rem 1.2rem; 
    border: none;
    height: 48px;
    box-sizing: border-box;
}
.add-pos-near-search {
    background: linear-gradient(90deg, #ffb86b 0%, #ff7eb3 100%);
    color: #23272f;
    animation: pulse 1.2s infinite alternate;
}
.add-pos-near-search .plus-sign {
    font-size: 1.5rem;
    font-weight: bold;
}
.add-pos-near-search:hover {
    background: linear-gradient(90deg, #ff7eb3 0%, #ffb86b 100%);
    color: #fff;
    transform: scale(1.07);
    box-shadow: 0 6px 24px 0 rgba(255,184,107,0.35), 0 0 0 6px #ffb86b66;
}
.cancel-pos-near-search {
    background: #2d3a4a;
    color: #ffb86b;
    margin-left: 0.7rem;
    font-size: 1.5rem;
    font-weight: 900;
    width: 48px;
    min-width: 48px;
    max-width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(20, 20, 40, 0.13);
    padding: 0;
    /* Allinea verticalmente con gli altri bottoni */
    margin-top: 0;
    box-sizing: border-box;
}
@media (max-width: 900px) {
    .searchbar-row {
        flex-direction: column;
        align-items: stretch;
        gap: 0.7rem;
    }
    .add-pos-near-search, .cancel-pos-near-search {
        width: 100%;
        justify-content: center;
        font-size: 1.1rem;
        padding: 0.7rem 0;
    }
    .cancel-pos-near-search {
        margin-left: 0;
        margin-top: 0.3rem;
    }
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 #ffb86b44; }
    100% { box-shadow: 0 0 0 8px #ffb86b22; }
}
.memory-menu-container {
    position: fixed;
    top: 24px;
    left: 0;
    height: auto;
    width: auto;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    z-index: 500;
    pointer-events: none;
}
.memory-menu-container.open {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 100vw;
    pointer-events: none;
    z-index: 500;
}
.memory-menu-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(20, 20, 30, 0.82);
    z-index: 499;
    cursor: pointer;
    transition: background 0.25s;
}
.memory-menu-backdrop:focus {
    outline: 2px solid #ffb86b;
    outline-offset: 2px;
}
.memory-menu {
    width: 0;
    min-width: 0;
    max-width: 100vw;
    overflow: hidden;
    background: #23272f;
    box-shadow: 4px 0 24px 0 #0006;
    height: 100vh;
    transition: width 0.35s cubic-bezier(0.4,0,0.2,1), box-shadow 0.2s;
    border-top-right-radius: 18px;
    border-bottom-right-radius: 18px;
    position: relative;
    z-index: 501;
    pointer-events: auto;
    margin-left: 84px;
    display: flex;
    flex-direction: column;
    align-items: stretch;
}
.memory-menu.open {
    width: 580px;
    min-width: 480px;
    max-width: calc(98vw - 84px);
    overflow-y: auto;
    max-height: 100vh;
    box-shadow: 4px 0 32px 0 #ffb86b33, 0 0 0 2px #ffb86b22;
    padding: 1.5rem 1.2rem 1.5rem 2.0rem;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    border-left: 3px solid #ffb86b;
}
@media (max-width: 900px) {
    .memory-menu.open {
        width: calc(95vw - 84px);
        min-width: 0;
        max-width: calc(100vw - 84px);
        border-radius: 0 18px 18px 0;
        padding: 1.2rem 0.5rem 1.5rem 0.5rem;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        overflow-y: auto;
        max-height: 100vh;
    }
}
@media (max-width: 600px) {
    .memory-menu.open {
        width: 100vw;
        min-width: 0;
        max-width: 100vw;
        border-radius: 0 0 14px 14px;
        padding: 0.7rem 0.2rem 1.2rem 0.2rem;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        overflow-y: auto;
        max-height: 100vh;
    }
}

/* Positions menu styles */
.positions-menu-container {
    position: fixed;
    top: 95px; /* Posizionamento verticale allineato con il bottone posizioni */
    left: 0;
    height: auto;
    width: auto;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    z-index: 510;
    pointer-events: none;
}

.positions-menu-container.open {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 100vw;
    pointer-events: none;
    z-index: 510;
}

.positions-menu {
    width: 0;
    min-width: 0;
    max-width: 100vw;
    overflow: hidden;
    background: #23272f;
    box-shadow: 4px 0 24px 0 #0006;
    height: 100vh;
    transition: width 0.35s cubic-bezier(0.4,0,0.2,1), box-shadow 0.2s;
    border-top-right-radius: 18px;
    border-bottom-right-radius: 18px;    position: relative;
    z-index: 511;
    pointer-events: auto;
    margin-left: 84px; /* Sposta il menu a destra del bottone (54px larghezza bottone + 30px margine) */
}

.positions-menu.open {
    width: 600px;
    min-width: 480px;
    max-width: 98vw;
    overflow-y: auto;
    box-shadow: 4px 0 32px 0 #7ddaff33, 0 0 0 2px #7ddaff22;
    padding: 1.5rem 0 1.5rem 0;
    display: flex;
    flex-direction: column;
    align-items: stretch;
}

@media (max-width: 900px) {
    .positions-menu-container {
        top: 55px;
    }
    
    .positions-menu.open {
        width: 95vw;
        min-width: 0;
        max-width: 100vw;
        border-radius: 0 0 18px 18px;
        padding: 1.2rem 0 1.5rem 0;
    }
}

@media (max-width: 600px) {
    .positions-menu-container {
        top: 95px; /* Manteniamo l'allineamento verticale con il bottone anche su mobile */
    }
    
    .positions-menu.open {
        width: calc(100vw - 84px); /* Sottraiamo lo spazio occupato dal bottone e dalla sua trasformazione */
        min-width: 0;
        max-width: calc(100vw - 84px);
        border-radius: 0 14px 14px 0; /* Arrotondamento solo sul lato destro */
        padding: 0.7rem 0 1.2rem 0;    }
}

/* Container per i bottoni del menu - renderizzati indipendentemente */
.menu-buttons-container {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000; /* Z-index molto alto per garantire che i bottoni siano sempre sopra i menu */
    pointer-events: none; /* Permette agli eventi di passare attraverso tranne sui bottoni stessi */
}

.menu-buttons-container.disabled {
    pointer-events: none !important;
}

.menu-buttons-container.disabled :global(.book-btn-modern),
.menu-buttons-container.disabled :global(.map-btn-modern) {
    pointer-events: none !important;
    cursor: not-allowed !important;
    opacity: 0.5 !important;
    filter: grayscale(50%) !important;
}

.copyright-footer {
    margin-top: auto;
    padding: 1rem 0;
    color: #8f9ba8;
    font-size: 0.9rem;
    text-align: center;
    width: 100%;
    background: rgba(24, 28, 36, 0.7);
    position: relative;
    z-index: 0;
}

@media (max-width: 600px) {
    .copyright-footer {
        font-size: 0.8rem;
        padding: 0.7rem 0;
    }
}
</style>

<div class="page-container dark">
    <div class="searchbar-row">
        <SearchBar bind:searchQuery onSearch={searchPlace} bind:basemap onBasemapChange={changeBasemap} />
        {#if $showFloatingAddBtn}
            <button class="add-pos-near-search" on:click={openAddPositionModal} title="Aggiungi posizione selezionata">
                <span class="plus-sign">+</span> Aggiungi posizione
            </button>
            <button class="cancel-pos-near-search" on:click={handleDeselectTempMarker} title="Annulla selezione posizione">×</button>
        {/if}
    </div>
    <MapSection on:ready={handleViewerReady} />
    <h1 class="main-title">GeoMemories</h1>
    <div class="user-bar">        {#if user}
            <span>Benvenuto {user.name}</span>
            <button on:click={logout} class="logout-btn" title="Logout" aria-label="Logout">
                <img src="/logout.svg" alt="Logout" class="logout-icon" />
            </button>
        {/if}
    </div>
    {#if showMemoryMenu}
        <div
            class="memory-menu-backdrop"
            role="button"
            tabindex="0"
            aria-label="Chiudi menu ricordi"
            on:click={() => showMemoryMenu = false}
            on:keydown={(e) => {
                if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') {
                    showMemoryMenu = false;
                }
            }}        ></div>
    {/if}
    {#if showPositionsMenu}
        <div
            class="memory-menu-backdrop"
            role="button"
            tabindex="0"
            aria-label="Chiudi menu posizioni"
            on:click={() => showPositionsMenu = false}
            on:keydown={(e) => {
                if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') {
                    showPositionsMenu = false;
                }
            }}
        ></div>
    {/if}    <!-- Bottoni del menu renderizzati indipendentemente per garantire z-index corretto -->
    <div class="menu-buttons-container {areModalsOpen ? 'disabled' : ''}">
        <BookButton open={showMemoryMenu} on:click={toggleMemoryMenu} ariaLabel="Apri/chiudi ricordi" />
        <MapButton open={showPositionsMenu} on:click={togglePositionsMenu} ariaLabel="Apri/chiudi posizioni" count={markerList.length} />
    </div>

    <!-- Container menu senza bottoni -->
    <div class="memory-menu-container {showMemoryMenu ? 'open' : ''}">
        <aside class:open={showMemoryMenu} class="memory-menu" style="pointer-events: auto;">
            <MemoriesPanel
                showMemory={showMemoryMenu}
                onToggle={toggleMemoryMenu}
            />
        </aside>
    </div>

    <div class="positions-menu-container {showPositionsMenu ? 'open' : ''}">
        <aside class:open={showPositionsMenu} class="positions-menu" style="pointer-events: auto;">
            <PositionsPanel
                {markerTitle} {markerLat} {markerLon} {markerList}
                markerDetails={markerDetails}
                showPositions={showPositionsMenu}
                addMarker={addMarker}
                onToggle={togglePositionsMenu}
                on:updateTitle={e => markerTitle = e.detail}
                on:updateLat={e => markerLat = e.detail}
                on:updateLon={e => markerLon = e.detail}
                on:updateDetails={e => markerDetails = e.detail}
                flyToPosition={flyToPosition}
                on:deselectTempMarker={handleDeselectTempMarker}
                bind:this={positionsPanelRef}
            />
        </aside>
    </div>
    
    <footer class="copyright-footer">
        © {new Date().getFullYear()} Abou Elkhir Mostafa, Trysh Alessandro, Barsa Dan. Tutti i diritti riservati.
    </footer>
</div>
