<script lang="ts">
import { onMount, createEventDispatcher } from 'svelte';
import { CESIUM_TOKEN } from '$lib/cesium_token';
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';

export let onViewerReady: (viewer: any) => void = () => {};
const dispatch = createEventDispatcher();
let viewer: any;

onMount(() => {
    Cesium.Ion.defaultAccessToken = CESIUM_TOKEN;
    
    viewer = new Cesium.Viewer('cesiumContainer', {
        timeline: false,
        animation: false,
        baseLayerPicker: false,
        geocoder: false,
        homeButton: false,
        sceneModePicker: false,
        navigationHelpButton: false,
        terrainProvider: new Cesium.EllipsoidTerrainProvider()
    });
    
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
    
    viewer.scene.globe.enableLighting = true;
    dispatch('ready', { viewer });
    onViewerReady(viewer);
});
</script>

<div id="cesiumContainer" class="dark"></div>

<style>
#cesiumContainer.dark {
    width: 80vw;
    height: 70vh;
    margin: 2rem auto 1rem auto;
    border-radius: 18px;
    box-shadow: 0 8px 32px 0 rgba(20, 20, 40, 0.45);
    overflow: hidden;
    background: #23272f;
}
</style>
