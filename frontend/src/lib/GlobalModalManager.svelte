<script>
import { globalModalStore } from '$lib/globalModalStore.js';
import AddMemoryModal from './AddMemoryModal.svelte';
import PositionsAddModal from '../routes/PositionsAddModal.svelte';
import MemoryDetailsModal from './MemoryDetailsModal.svelte';
import PositionDetailsModal from './PositionDetailsModal.svelte';
import ImageViewer from './ImageViewer.svelte';
import VideoViewer from './VideoViewer.svelte';
import { imageViewerStore } from './imageViewerStore.js';
import { videoViewerStore } from './videoViewerStore.js';

let modalState;
let imageViewerState;
let videoViewerState;

globalModalStore.subscribe(state => {
    modalState = state;
});

imageViewerStore.subscribe(state => {
    imageViewerState = state;
});

videoViewerStore.subscribe(state => {
    videoViewerState = state;
});
</script>

<!-- Container per tutti i modal globali -->
{#if modalState}    <!-- Modal per aggiungere memoria -->
    {#if modalState.showAddMemory}
        <div class="global-modal-container">
            <AddMemoryModal />
        </div>
    {/if}<!-- Modal per aggiungere posizione -->
    {#if modalState.showAddPosition}
        <div class="global-modal-container">
            <PositionsAddModal />
        </div>
    {/if}

    <!-- Modal per dettagli memoria -->
    {#if modalState.showMemoryDetails}
        <div class="global-modal-container">
            <MemoryDetailsModal 
                memory={modalState.memoryDetailsData}
            />
        </div>
    {/if}    <!-- Modal per dettagli posizione -->
    {#if modalState.showPositionDetails}
        <div class="global-modal-container">
            <PositionDetailsModal 
                position={modalState.positionDetailsData}
            />
        </div>
    {/if}
{/if}

<!-- Image Viewer - renderizzato indipendentemente -->
{#if imageViewerState && imageViewerState.isVisible}
    <ImageViewer 
        imageUrl={imageViewerState.imageUrl}
        imageName={imageViewerState.imageName}
        isVisible={imageViewerState.isVisible}
        on:close={() => import('./imageViewerStore.js').then(m => m.closeImageViewer())}
    />
{/if}

<!-- Video Viewer - renderizzato indipendentemente -->
{#if videoViewerState && videoViewerState.isVisible}
    <VideoViewer 
        videoUrl={videoViewerState.videoUrl}
        videoName={videoViewerState.videoName}
        isVisible={videoViewerState.isVisible}
        on:close={() => import('./videoViewerStore.js').then(m => m.closeVideoViewer())}
    />
{/if}

<style>
.global-modal-container {
    /* Assicura che i modal siano renderizzati al centro della viewport */
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: all;
    /* Rimuoviamo il z-index qui per permettere ai singoli modali di gestire il proprio */
}
</style>
