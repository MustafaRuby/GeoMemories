<script>
  import { createEventDispatcher } from 'svelte';
  export let open = false;
  export let ariaLabel = 'Apri menu posizioni';
  export let count = 0; // Manteniamo il parametro per retrocompatibilità, ma non lo utilizziamo più
  const dispatch = createEventDispatcher();
</script>

<button class="map-btn-modern" aria-label={ariaLabel} on:click={() => dispatch('click')} title="Gestisci posizioni salvate">
  <div class="map-modern {open ? 'open' : ''}">
    <div class="location-dot" class:hidden={open}></div>    <div class="map-container" class:visible={open}>
      <div class="map-grid"></div>
      <div class="location-pin"></div>
    </div>
    <!-- Badge rimosso per evitare confusione con il numero di posizioni -->
    
  </div>
</button>

<style>
.map-btn-modern {
  background: none;
  border: none;
  padding: 0;
  margin: 0 0 0 30px; /* Manteniamo solo il margine sinistro, poiché top viene gestito da position: fixed */
  cursor: pointer;
  outline: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: filter 0.2s;
  width: 54px;
  height: 54px;
  z-index: 530; /* Bottone sopra il menu ma sotto i modali */
  pointer-events: auto; /* Garantisce che il bottone sia sempre cliccabile */
  animation: initialHint 3s ease-in-out 2s 1;  position: fixed; /* Cambiamo da relative a fixed per impedire lo shift */
  left: 0; /* Aggiungiamo left: 0 per posizionare correttamente con position: fixed */
  top: 95px; /* Posizionato a 95px dall'alto per lasciare spazio al bottone dei ricordi */
}

/* Aggiungiamo uno pseudo-elemento per aumentare l'area cliccabile */
.map-btn-modern::before {
  content: '';
  position: absolute;
  top: -15px;
  left: -15px;
  right: -15px;
  bottom: -15px;
}

@keyframes initialHint {
  0%, 90%, 100% { transform: scale(1); }
  45% { transform: scale(1.1); }
}

.map-btn-modern:active {
  filter: brightness(0.95);
}

.map-modern {
  width: 44px;
  height: 44px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(120deg, #7ddaff 60%, #a259ff 100%);
  border: 3px solid #4ea8d4;
  box-shadow: 0 4px 16px #0004, 0 0 0 2px #7ddaff55;
  transition: all 0.5s cubic-bezier(0.4,0.2,0.2,1);
  overflow: hidden;
}

.map-modern.open {
  box-shadow: 0 8px 32px #7ddaff55, 0 0 0 2px #7ddaff99;
}

.location-dot {
  width: 16px;
  height: 16px;
  background: #fff;
  border-radius: 50%;
  border: 3px solid #4ea8d4;
  transition: all 0.5s cubic-bezier(0.4,0.2,0.2,1);
  box-shadow: 0 2px 8px #0003;
  z-index: 2;
}

.location-dot.hidden {
  opacity: 0;
  transform: scale(0.3);
}

.map-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.5s cubic-bezier(0.4,0.2,0.2,1);
  z-index: 1;
}

.map-container.visible {
  opacity: 1;
  transform: scale(1);
}

.map-grid {
  position: absolute;
  top: 8px;
  left: 8px;
  right: 8px;
  bottom: 8px;
  background-image: 
    linear-gradient(rgba(255,255,255,0.3) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.3) 1px, transparent 1px);
  background-size: 8px 8px;
  border-radius: 6px;
}

.location-pin {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
  border: 2px solid #4ea8d4;
  box-shadow: 0 1px 4px #0004;
  animation: pulse 2s infinite;
  transition: all 0.5s cubic-bezier(0.4,0.2,0.2,1);
}

/* Google Maps style red pin when open */
.map-modern.open .location-pin {
  animation: none;
  width: 12px;
  height: 16px;
  background: #ea4335;
  border: 2px solid #fff;
  border-radius: 50% 50% 50% 0;
  transform: translate(-50%, -70%) rotate(-45deg);
  box-shadow: 0 2px 6px rgba(234, 67, 53, 0.4);
}

.map-modern.open .location-pin::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 4px;
  height: 4px;
  background: #fff;
  border-radius: 50%;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(255, 255, 255, 0);
  }  100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
  }
}

.count-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #ea4335;
  color: #fff;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  font-family: 'Fira Mono', 'JetBrains Mono', monospace;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  z-index: 10;
}
</style>
