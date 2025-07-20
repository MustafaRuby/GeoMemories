<script>
    import { createEventDispatcher, onMount, onDestroy } from 'svelte';
    
    export let videoUrl = '';
    export let videoName = '';
    export let isVisible = false;
    
    const dispatch = createEventDispatcher();
    
    let videoElement;
    let videoContainer;
    let isPlaying = false;
    let currentTime = 0;
    let duration = 0;
    let volume = 1;
    let isMuted = false;
    let isFullscreen = false;
    let showControls = true;
    let hideControlsTimeout;
    let progressBarWidth = 0;
    let volumeBarWidth = 0;
    let isLoadingMeta = true;
    let isSeeking = false;
    
    function close() {
        // Pausa il video quando si chiude
        if (videoElement) {
            videoElement.pause();
        }
        dispatch('close');
    }
    
    function togglePlay() {
        if (!videoElement) return;
        
        if (isPlaying) {
            videoElement.pause();
        } else {
            videoElement.play();
        }
    }
    
    function toggleMute() {
        if (!videoElement) return;
        
        if (isMuted) {
            videoElement.volume = volume;
            isMuted = false;
        } else {
            videoElement.volume = 0;
            isMuted = true;
        }
    }
    
    function toggleFullscreen() {
        if (!videoContainer) return;
        
        if (!isFullscreen) {
            if (videoContainer.requestFullscreen) {
                videoContainer.requestFullscreen();
            } else if (videoContainer.webkitRequestFullscreen) {
                videoContainer.webkitRequestFullscreen();
            } else if (videoContainer.msRequestFullscreen) {
                videoContainer.msRequestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
        }
    }
    
    function handleTimeUpdate() {
        if (videoElement && !isSeeking) {
            currentTime = videoElement.currentTime;
        }
    }
    
    function handleLoadedMetadata() {
        if (videoElement) {
            duration = videoElement.duration;
            isLoadingMeta = false;
        }
    }
    
    function handlePlay() {
        isPlaying = true;
    }
    
    function handlePause() {
        isPlaying = false;
    }
    
    function handleVolumeChange() {
        if (videoElement) {
            volume = videoElement.volume;
            isMuted = videoElement.muted || videoElement.volume === 0;
        }
    }
    
    function seekTo(percentage) {
        if (videoElement && duration) {
            const newTime = (percentage / 100) * duration;
            videoElement.currentTime = newTime;
            currentTime = newTime;
        }
    }
    
    function setVolume(percentage) {
        if (videoElement) {
            const newVolume = percentage / 100;
            videoElement.volume = newVolume;
            volume = newVolume;
            if (newVolume > 0) {
                isMuted = false;
            }
        }
    }
    
    function handleProgressClick(event) {
        const rect = event.currentTarget.getBoundingClientRect();
        const percentage = ((event.clientX - rect.left) / rect.width) * 100;
        seekTo(percentage);
    }
    
    function handleVolumeClick(event) {
        const rect = event.currentTarget.getBoundingClientRect();
        const percentage = ((event.clientX - rect.left) / rect.width) * 100;
        setVolume(percentage);
    }
    
    function formatTime(seconds) {
        if (isNaN(seconds)) return '00:00';
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    function showControlsTemporarily() {
        showControls = true;
        if (hideControlsTimeout) clearTimeout(hideControlsTimeout);
        hideControlsTimeout = setTimeout(() => {
            if (isPlaying) {
                showControls = false;
            }
        }, 3000);
    }
    
    function handleMouseMove() {
        showControlsTemporarily();
    }
    
    function handleKeydown(event) {
        if (!isVisible) return;
        
        event.preventDefault();
        event.stopPropagation();
        
        switch(event.key) {
            case 'Escape':
                close();
                break;
            case ' ':
            case 'k':
                togglePlay();
                break;
            case 'm':
                toggleMute();
                break;
            case 'f':
                toggleFullscreen();
                break;
            case 'ArrowLeft':
                if (videoElement) {
                    videoElement.currentTime = Math.max(0, videoElement.currentTime - 10);
                }
                break;
            case 'ArrowRight':
                if (videoElement) {
                    videoElement.currentTime = Math.min(duration, videoElement.currentTime + 10);
                }
                break;
            case 'ArrowUp':
                if (videoElement) {
                    videoElement.volume = Math.min(1, videoElement.volume + 0.1);
                }
                break;
            case 'ArrowDown':
                if (videoElement) {
                    videoElement.volume = Math.max(0, videoElement.volume - 0.1);
                }
                break;
        }
        
        showControlsTemporarily();
    }
    
    function handleFullscreenChange() {
        isFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
    }
    
    onMount(() => {
        document.addEventListener('keydown', handleKeydown);
        document.addEventListener('fullscreenchange', handleFullscreenChange);
        document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
        document.addEventListener('msfullscreenchange', handleFullscreenChange);
        
        // Mostra i controlli inizialmente
        showControlsTemporarily();
    });
    
    onDestroy(() => {
        document.removeEventListener('keydown', handleKeydown);
        document.removeEventListener('fullscreenchange', handleFullscreenChange);
        document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
        document.removeEventListener('msfullscreenchange', handleFullscreenChange);
        
        if (hideControlsTimeout) {
            clearTimeout(hideControlsTimeout);
        }
    });
    
    $: if (duration > 0) {
        progressBarWidth = (currentTime / duration) * 100;
    }
    
    $: volumeBarWidth = volume * 100;
</script>

{#if isVisible}
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div 
        class="video-viewer-overlay" 
        on:click={close}
        on:keydown={handleKeydown}
        tabindex="0"
        role="dialog"
        aria-modal="true"
        aria-label="Video Viewer"
    >
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div 
            class="video-container {isFullscreen ? 'fullscreen' : ''}" 
            bind:this={videoContainer}
            on:click|stopPropagation
            on:mousemove={handleMouseMove}
            on:touchstart|passive={showControlsTemporarily}
        >
            <video 
                bind:this={videoElement}
                src={videoUrl}
                on:timeupdate={handleTimeUpdate}
                on:loadedmetadata={handleLoadedMetadata}
                on:play={handlePlay}
                on:pause={handlePause}
                on:volumechange={handleVolumeChange}
                on:click={togglePlay}
                class="video-element"
                preload="metadata"
                crossorigin="anonymous"
            >
                <track kind="captions" />
                Il tuo browser non supporta la riproduzione video.
            </video>
            
            {#if isLoadingMeta}
                <div class="loading-indicator">
                    <div class="loading-spinner"></div>
                    <span>Caricamento video...</span>
                </div>
            {/if}
            
            <!-- Controls Overlay -->
            <div class="controls-overlay {showControls ? 'visible' : ''}">
                <!-- Top bar with title and close button -->
                <div class="top-controls">
                    <div class="video-title">{videoName}</div>
                    <button class="close-btn" on:click={close} title="Chiudi (Esc)" aria-label="Chiudi video">
                        ✕
                    </button>
                </div>
                
                <!-- Bottom controls -->
                <div class="bottom-controls">
                    <!-- Progress bar -->
                    <div class="progress-container">
                        <!-- svelte-ignore a11y-no-static-element-interactions -->
                        <div class="progress-bar" on:click={handleProgressClick}>
                            <div class="progress-filled" style="width: {progressBarWidth}%"></div>
                            <div class="progress-handle" style="left: {progressBarWidth}%"></div>
                        </div>
                    </div>
                    
                    <!-- Control buttons and info -->
                    <div class="controls-row">
                        <div class="left-controls">
                            <button class="control-btn play-btn" on:click={togglePlay} title="{isPlaying ? 'Pausa (Spazio)' : 'Riproduci (Spazio)'}">
                                {#if isPlaying}
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                        <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                                    </svg>
                                {:else}
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                        <path d="M8 5v14l11-7z"/>
                                    </svg>
                                {/if}
                            </button>
                            
                            <div class="volume-controls">
                                <button class="control-btn volume-btn" on:click={toggleMute} title="{isMuted ? 'Riattiva audio (M)' : 'Disattiva audio (M)'}">
                                    {#if isMuted || volume === 0}
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                            <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
                                        </svg>
                                    {:else if volume < 0.5}
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                            <path d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"/>
                                        </svg>
                                    {:else}
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                                        </svg>
                                    {/if}
                                </button>
                                
                                <!-- Volume bar -->
                                <div class="volume-container">
                                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                                    <div class="volume-bar" on:click={handleVolumeClick}>
                                        <div class="volume-filled" style="width: {volumeBarWidth}%"></div>
                                        <div class="volume-handle" style="left: {volumeBarWidth}%"></div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="time-display">
                                {formatTime(currentTime)} / {formatTime(duration)}
                            </div>
                        </div>
                        
                        <div class="right-controls">
                            <button class="control-btn fullscreen-btn" on:click={toggleFullscreen} title="{isFullscreen ? 'Esci da schermo intero (F)' : 'Schermo intero (F)'}">
                                {#if isFullscreen}
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                        <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
                                    </svg>
                                {:else}
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                        <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
                                    </svg>
                                {/if}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Help text -->
            <div class="help-text {showControls ? 'visible' : ''}">
                <span>
                    • <strong>Spazio/K:</strong> Play/Pausa 
                    • <strong>M:</strong> Muto 
                    • <strong>F:</strong> Schermo intero 
                    • <strong>↑↓:</strong> Volume 
                    • <strong>←→:</strong> ±10s 
                    • <strong>Esc:</strong> Chiudi
                </span>
            </div>
        </div>
    </div>
{/if}

<style>
    .video-viewer-overlay {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background: rgba(0, 0, 0, 0.95) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        z-index: 2147483647 !important; /* Stessa priorità dell'ImageViewer */
        backdrop-filter: blur(8px) !important;
        cursor: pointer !important;
    }
    
    .video-container {
        position: relative;
        width: 90%;
        height: 90%;
        max-width: 1200px;
        max-height: 80vh;
        background: #000;
        border-radius: 12px;
        overflow: hidden;
        cursor: default;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    }
    
    .video-container.fullscreen {
        width: 100vw;
        height: 100vh;
        max-width: none;
        max-height: none;
        border-radius: 0;
    }
    
    .video-element {
        width: 100%;
        height: 100%;
        object-fit: contain;
        cursor: pointer;
    }
    
    .loading-indicator {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        color: #fff;
        font-size: 1rem;
        z-index: 10;
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-top: 3px solid #ffb86b;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .controls-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
        background: linear-gradient(
            to bottom,
            rgba(0, 0, 0, 0.7) 0%,
            transparent 25%,
            transparent 75%,
            rgba(0, 0, 0, 0.8) 100%
        );
    }
    
    .controls-overlay.visible {
        opacity: 1;
        pointer-events: auto;
    }
    
    .top-controls {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 2rem;
        pointer-events: auto;
    }
    
    .video-title {
        color: #fff;
        font-size: 1.2rem;
        font-weight: 600;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        max-width: 70%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .close-btn {
        background: rgba(0, 0, 0, 0.6);
        border: none;
        color: #fff;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        transition: all 0.2s ease;
        backdrop-filter: blur(10px);
    }
    
    .close-btn:hover {
        background: rgba(255, 0, 0, 0.7);
        transform: scale(1.1);
    }
    
    .bottom-controls {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1.5rem 2rem 2rem;
        pointer-events: auto;
    }
    
    .progress-container {
        margin-bottom: 1rem;
    }
    
    .progress-bar {
        position: relative;
        height: 6px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 3px;
        cursor: pointer;
        transition: height 0.2s ease;
    }
    
    .progress-bar:hover {
        height: 8px;
    }
    
    .progress-filled {
        height: 100%;
        background: linear-gradient(90deg, #ffb86b, #ff7eb3);
        border-radius: 3px;
        transition: width 0.1s ease;
    }
    
    .progress-handle {
        position: absolute;
        top: 50%;
        width: 14px;
        height: 14px;
        background: #fff;
        border-radius: 50%;
        transform: translate(-50%, -50%);
        opacity: 0;
        transition: opacity 0.2s ease;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }
    
    .progress-bar:hover .progress-handle {
        opacity: 1;
    }
    
    .controls-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .left-controls,
    .right-controls {
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    .control-btn {
        background: rgba(0, 0, 0, 0.6);
        border: none;
        color: #fff;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        backdrop-filter: blur(10px);
    }
    
    .control-btn:hover {
        background: rgba(255, 184, 107, 0.8);
        transform: scale(1.1);
    }
    
    .play-btn {
        width: 48px;
        height: 48px;
        background: rgba(255, 184, 107, 0.9);
    }
    
    .play-btn:hover {
        background: rgba(255, 184, 107, 1);
        transform: scale(1.15);
    }
    
    .volume-controls {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .volume-container {
        width: 80px;
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    
    .volume-controls:hover .volume-container {
        opacity: 1;
    }
    
    .volume-bar {
        position: relative;
        height: 4px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 2px;
        cursor: pointer;
    }
    
    .volume-filled {
        height: 100%;
        background: linear-gradient(90deg, #ffb86b, #ff7eb3);
        border-radius: 2px;
        transition: width 0.1s ease;
    }
    
    .volume-handle {
        position: absolute;
        top: 50%;
        width: 10px;
        height: 10px;
        background: #fff;
        border-radius: 50%;
        transform: translate(-50%, -50%);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    .time-display {
        color: #fff;
        font-size: 0.9rem;
        font-weight: 500;
        min-width: 100px;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    .help-text {
        position: absolute;
        bottom: 1rem;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.8);
        color: #fff;
        padding: 0.8rem 1.5rem;
        border-radius: 20px;
        font-size: 0.85rem;
        backdrop-filter: blur(10px);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
        max-width: 90%;
        text-align: center;
    }
    
    .help-text.visible {
        opacity: 1;
    }
    
    .help-text strong {
        color: #ffb86b;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .video-container {
            width: 100%;
            height: 100%;
            max-height: 100vh;
            border-radius: 0;
        }
        
        .top-controls,
        .bottom-controls {
            padding: 1rem;
        }
        
        .video-title {
            font-size: 1rem;
            max-width: 60%;
        }
        
        .controls-row {
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .left-controls {
            flex: 1;
            min-width: 250px;
        }
        
        .volume-container {
            width: 60px;
        }
        
        .time-display {
            font-size: 0.8rem;
            min-width: 80px;
        }
        
        .help-text {
            bottom: 0.5rem;
            padding: 0.6rem 1rem;
            font-size: 0.75rem;
        }
    }
    
    @media (max-width: 480px) {
        .controls-row {
            flex-direction: column;
            align-items: stretch;
            gap: 0.8rem;
        }
        
        .left-controls,
        .right-controls {
            justify-content: center;
        }
        
        .volume-controls {
            order: 1;
        }
        
        .time-display {
            order: 2;
            text-align: center;
        }
        
        .help-text span {
            font-size: 0.7rem;
        }
    }
</style>
