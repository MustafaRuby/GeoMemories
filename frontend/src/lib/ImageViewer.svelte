<script>
    import { createEventDispatcher, onMount, onDestroy } from 'svelte';
    
    export let imageUrl = '';
    export let imageName = '';
    export let isVisible = false;
    
    const dispatch = createEventDispatcher();
    
    let scale = 1;
    let translateX = 0;
    let translateY = 0;
    let isDragging = false;
    let lastMouseX = 0;
    let lastMouseY = 0;
    let imageContainer;
    let wheelTimeout;
    let touchTimeout;
    let keyTimeout;
    
    const MIN_SCALE = 0.1;
    const MAX_SCALE = 5;
    const ZOOM_STEP = 0.2;
    
    function close() {
        dispatch('close');
    }
    
    function zoomIn() {
        scale = Math.min(scale + ZOOM_STEP, MAX_SCALE);
    }
    
    function zoomOut() {
        scale = Math.max(scale - ZOOM_STEP, MIN_SCALE);
    }
    
    function resetZoom() {
        scale = 1;
        translateX = 0;
        translateY = 0;
    }
    
    function fitToWindow() {
        if (imageContainer) {
            const containerRect = imageContainer.getBoundingClientRect();
            const img = imageContainer.querySelector('img');
            if (img) {
                const imgAspectRatio = img.naturalWidth / img.naturalHeight;
                const containerAspectRatio = containerRect.width / containerRect.height;
                
                if (imgAspectRatio > containerAspectRatio) {
                    // Image is wider than container
                    scale = (containerRect.width * 0.9) / img.naturalWidth;
                } else {
                    // Image is taller than container
                    scale = (containerRect.height * 0.9) / img.naturalHeight;
                }
                
                translateX = 0;
                translateY = 0;
            }
        }
    }
    
    function handleMouseDown(event) {
        if (scale > 1) {
            isDragging = true;
            lastMouseX = event.clientX;
            lastMouseY = event.clientY;
            event.preventDefault();
            event.stopPropagation();
        }
    }
    
    function handleMouseMove(event) {
        if (isDragging && scale > 1) {
            const deltaX = event.clientX - lastMouseX;
            const deltaY = event.clientY - lastMouseY;
            
            translateX += deltaX;
            translateY += deltaY;
            
            lastMouseX = event.clientX;
            lastMouseY = event.clientY;
            
            event.preventDefault();
            event.stopPropagation();
        }
    }
    
    function handleMouseUp(event) {
        if (isDragging) {
            event.preventDefault();
            event.stopPropagation();
            isDragging = false;
        }
    }
    
    function handleWheel(event) {
        event.preventDefault();
        event.stopPropagation();
        
        // Piccolo ritardo per evitare conflitti con lo scrolling del documento
        if (wheelTimeout) clearTimeout(wheelTimeout);
        wheelTimeout = setTimeout(() => {
            if (event.deltaY < 0) {
                zoomIn();
            } else {
                zoomOut();
            }
        }, 10);
    }
    
    // Touch events for mobile pinch zoom
    let initialDistance = 0;
    
    function handleTouchStart(event) {
        // Assicuriamoci di acquisire il focus per evitare conflitti con altri elementi
        event.currentTarget.focus();
        
        if (event.touches.length === 2) {
            // Quando ci sono due dita sullo schermo, è un gesto di pinch
            event.preventDefault();
            event.stopPropagation();
            initialDistance = getTouchDistance(event.touches);
        } else if (event.touches.length === 1 && scale > 1) {
            // Singolo tocco quando lo zoom è attivo - per il trascinamento
            event.preventDefault();
            isDragging = true;
            const touch = event.touches[0];
            lastMouseX = touch.clientX;
            lastMouseY = touch.clientY;
        }
    }
    
    function handleTouchMove(event) {
        if (event.touches.length === 2) {
            // Gestione del pinch-to-zoom
            event.preventDefault();
            event.stopPropagation();
            
            // Piccolo ritardo per evitare zoom troppo rapidi
            if (touchTimeout) clearTimeout(touchTimeout);
            touchTimeout = setTimeout(() => {
                const currentDistance = getTouchDistance(event.touches);
                const delta = currentDistance - initialDistance;
                
                if (Math.abs(delta) > 10) { // Threshold to prevent accidental zooms
                    if (delta > 0) {
                        zoomIn();
                    } else {
                        zoomOut();
                    }
                    initialDistance = currentDistance;
                }
            }, 10);
        } else if (scale > 1 && event.touches.length === 1 && isDragging) {
            // Gestione del trascinamento con un dito quando c'è zoom
            event.preventDefault();
            event.stopPropagation();
            
            const touch = event.touches[0];
            const deltaX = touch.clientX - lastMouseX;
            const deltaY = touch.clientY - lastMouseY;
            
            translateX += deltaX;
            translateY += deltaY;
            
            lastMouseX = touch.clientX;
            lastMouseY = touch.clientY;
        }
    }
    
    function handleTouchEnd(event) {
        // Ripulisci gli stati al termine del tocco
        if (event.touches.length < 2) {
            initialDistance = 0;
        }
        if (event.touches.length === 0) {
            isDragging = false;
        }
        
        // Preveniamo eventuali tap non intenzionali
        event.preventDefault();
        event.stopPropagation();
    }
    
    function getTouchDistance(touches) {
        const dx = touches[0].clientX - touches[1].clientX;
        const dy = touches[0].clientY - touches[1].clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    function handleKeydown(event) {
        // Only handle keys when image viewer is visible
        if (!isVisible) return;
        
        event.preventDefault();
        event.stopPropagation();
        
        switch(event.key) {
            case 'Escape':
                close();
                break;
            case '+':
            case '=':
                zoomIn();
                break;
            case '-':
                zoomOut();
                break;
            case '0':
                resetZoom();
                break;
            case 'f':
            case 'F':
                fitToWindow();
                break;
        }
    }
    
    // Handle clicks on overlay (not on image) to close
    function handleOverlayClick(event) {
        if (event.target === event.currentTarget) {
            close();
        }
        event.stopPropagation();
    }
    
    // Prevent event propagation for buttons
    function handleButtonClick(event, action) {
        event.preventDefault();
        event.stopPropagation();
        action();
    }
    
    // Gestione eventi globali
    let eventListeners = [];
    
    onMount(() => {
        // Quando il componente è montato, impostiamo gli eventi globali
        if (typeof document !== 'undefined') {
            window.addEventListener('resize', fitToWindow);
            document.addEventListener('keydown', captureKeyDown);
            document.addEventListener('mousemove', captureMouseMove);
            document.addEventListener('mouseup', captureMouseUp);
            document.addEventListener('touchmove', captureTouchMove, { passive: false });
            
            // Preveniamo lo scorrimento durante il pinch
            document.addEventListener('touchstart', preventDefaultOnPin, { passive: false });
            
            eventListeners = [
                { target: window, event: 'resize', handler: fitToWindow },
                { target: document, event: 'keydown', handler: captureKeyDown },
                { target: document, event: 'mousemove', handler: captureMouseMove },
                { target: document, event: 'mouseup', handler: captureMouseUp },
                { target: document, event: 'touchmove', handler: captureTouchMove },
                { target: document, event: 'touchstart', handler: preventDefaultOnPin }
            ];
        }
    });
    
    onDestroy(() => {
        // Pulisci tutti i timeouts
        if (wheelTimeout) clearTimeout(wheelTimeout);
        if (touchTimeout) clearTimeout(touchTimeout);
        if (keyTimeout) clearTimeout(keyTimeout);
        
        // Rimuovi tutti gli event listeners
        eventListeners.forEach(({ target, event, handler }) => {
            target.removeEventListener(event, handler);
        });
    });
    
    function preventDefaultOnPin(e) {
        // Previene il default solo per i gesti pinch quando il visualizzatore è aperto
        if (isVisible && e.touches && e.touches.length === 2) {
            e.preventDefault();
        }
    }
    
    // Intercept all keyboard events at the document level
    function captureKeyDown(e) {
        if (isVisible) {
            handleKeydown(e);
        }
    }
    
    // Intercept mouse events at the document level when dragging
    function captureMouseMove(e) {
        if (isVisible && isDragging) {
            handleMouseMove(e);
        }
    }
    
    function captureMouseUp(e) {
        if (isVisible && isDragging) {
            handleMouseUp(e);
        }
    }
    
    function captureTouchMove(e) {
        if (isVisible) {
            // Blocca sempre lo scrolling del documento quando il visualizzatore è aperto
            // anche se non si sta facendo pinch o drag
            if (isDragging || (e.touches && e.touches.length === 2)) {
                e.preventDefault();
                e.stopPropagation();
            }
        }
    }
    
    $: {
        if (typeof document !== 'undefined' && isVisible) {
            // Quando il visualizzatore è visibile, impostiamo il fitToWindow con un piccolo ritardo
            setTimeout(fitToWindow, 100);
        }
    }
</script>

{#if isVisible}
    <div class="image-viewer-overlay" on:click={handleOverlayClick} role="dialog" aria-modal="true" aria-label="Visualizzatore immagine: {imageName}">
        <div class="image-viewer-container">
            <!-- Header with title and close button -->
            <div class="image-viewer-header">
                <h3 class="image-title">{imageName}</h3>
                <button class="close-btn" on:click={(e) => handleButtonClick(e, close)} title="Chiudi (Esc)" aria-label="Chiudi visualizzatore immagine">×</button>
            </div>
            
            <!-- Controls -->
            <div class="image-viewer-controls">
                <button class="control-btn" on:click={(e) => handleButtonClick(e, zoomOut)} title="Zoom Out (-)" aria-label="Riduci zoom">−</button>
                <span class="zoom-level" aria-live="polite" role="status">{Math.round(scale * 100)}%</span>
                <button class="control-btn" on:click={(e) => handleButtonClick(e, zoomIn)} title="Zoom In (+)" aria-label="Aumenta zoom">+</button>
                <button class="control-btn" on:click={(e) => handleButtonClick(e, resetZoom)} title="Reset Zoom (0)" aria-label="Ripristina zoom">1:1</button>
                <button class="control-btn" on:click={(e) => handleButtonClick(e, fitToWindow)} title="Fit to Window (F)" aria-label="Adatta alla finestra">Adatta</button>
            </div>
              <!-- Image container -->
            <div 
                class="image-container" 
                bind:this={imageContainer}
                on:mousedown={handleMouseDown}
                on:wheel={handleWheel}
                on:touchstart={handleTouchStart}
                on:touchmove={handleTouchMove}
                on:touchend={handleTouchEnd}
                style="cursor: {scale > 1 ? (isDragging ? 'grabbing' : 'grab') : 'default'}"
                tabindex="0"
                role="img"
                aria-label="Immagine zoomabile: {imageName}"
            >
                <img 
                    src={imageUrl} 
                    alt={imageName}
                    style="transform: scale({scale}) translate({translateX / scale}px, {translateY / scale}px);"
                    draggable="false"
                    aria-hidden="true"
                />
            </div>
              <!-- Help text -->
            <div class="help-text">
                <span class="desktop-help">Usa la rotella del mouse per zoom • Trascina per spostare • ESC per chiudere</span>
                <span class="mobile-help">Pizzica per zoom • Trascina per spostare • Tocca lo sfondo per chiudere</span>
            </div>
        </div>
    </div>
{/if}

<style>
    .image-viewer-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 2147483647 !important; /* Valore massimo possibile per z-index */
        backdrop-filter: blur(3px);
        -webkit-backdrop-filter: blur(3px);
        /* Ensure it captures all events */
        pointer-events: auto;
        /* Prevent any text selection */
        user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        /* Ensure touch devices respect this layer */
        touch-action: none;
        /* Hide scrollbars when visible */
        overflow: hidden;
        /* Lock the viewport to prevent zooming on mobile */
        max-height: 100%;
        max-width: 100%;
        /* Aggiunti per maggiore sicurezza che sia sopra tutto */
        isolation: isolate;
        contain: strict;
        /* Assicuriamoci che questa sia la "vera" fissata in alto */
        position: fixed !important;
    }
    
    .image-viewer-container {
        width: 90vw;
        height: 90vh;
        background: rgba(20, 25, 40, 0.95);
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        border: 1px solid rgba(127, 223, 255, 0.3);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    }
    
    .image-viewer-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.5rem;
        border-bottom: 1px solid rgba(127, 223, 255, 0.2);
        background: rgba(30, 35, 50, 0.8);
        border-radius: 12px 12px 0 0;
    }
    
    .image-title {
        margin: 0;
        color: #7fdfff;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .close-btn {
        background: none;
        border: none;
        color: #ffb86b;
        font-size: 2rem;
        cursor: pointer;
        padding: 0;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: all 0.2s ease;
    }
    
    .close-btn:hover {
        background: rgba(255, 184, 107, 0.2);
        transform: scale(1.1);
    }
    
    .image-viewer-controls {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.5rem;
        background: rgba(25, 30, 45, 0.8);
        border-bottom: 1px solid rgba(127, 223, 255, 0.1);
    }
    
    .control-btn {
        background: rgba(127, 223, 255, 0.1);
        border: 1px solid rgba(127, 223, 255, 0.3);
        color: #7fdfff;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        min-width: 40px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .control-btn:hover {
        background: rgba(127, 223, 255, 0.2);
        border-color: rgba(127, 223, 255, 0.5);
        transform: translateY(-1px);
    }
    
    .zoom-level {
        color: #ffb86b;
        font-weight: 600;
        min-width: 60px;
        text-align: center;
        font-size: 0.9rem;
    }
    
    .image-container {
        flex: 1;
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        background: rgba(0, 0, 0, 0.3);
    }
    
    .image-container img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        transition: transform 0.1s ease-out;
        user-select: none;
    }
    
    .help-text {
        padding: 0.8rem 1.5rem;
        background: rgba(20, 25, 40, 0.9);
        border-top: 1px solid rgba(127, 223, 255, 0.1);
        text-align: center;
        border-radius: 0 0 12px 12px;
    }
    
    .help-text span {
        color: #aaa;
        font-size: 0.85rem;
    }
    
    .mobile-help {
        display: none;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .desktop-help {
            display: none;
        }
        
        .mobile-help {
            display: inline;
        }
        
        .image-viewer-container {
            width: 95vw;
            height: 95vh;
        }
        
        .image-viewer-header {
            padding: 0.8rem 1rem;
        }
        
        .image-title {
            font-size: 1rem;
        }
        
        .image-viewer-controls {
            padding: 0.8rem 1rem;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        
        .control-btn {
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
            min-width: 35px;
            height: 32px;
        }
        
        .help-text {
            padding: 0.6rem 1rem;
        }
        
        .help-text span {
            font-size: 0.75rem;
        }
    }
</style>
