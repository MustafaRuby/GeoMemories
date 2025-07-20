<script>
  import { createEventDispatcher } from 'svelte';
  export let open = false;
  export let ariaLabel = 'Apri menu ricordi';
  const dispatch = createEventDispatcher();
</script>

<button class="book-btn-modern" aria-label={ariaLabel} on:click={() => dispatch('click')} title="Gestisci ricordi e memorie">
  <div class="book-modern {open ? 'open' : ''}">
    <div class="cover front"></div>
    <div class="pages">
      <div class="page"></div>
      <div class="page"></div>
      <div class="page"></div>
    </div>
    <div class="cover back"></div>
    <div class="bookmark" aria-hidden="true"></div>
  </div>
</button>

<style>
.book-btn-modern {
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
  z-index: 520; /* Bottone sopra il menu ma sotto i modali */
  pointer-events: auto; /* Garantisce che il bottone sia sempre cliccabile */
  animation: initialHint 3s ease-in-out 1s 1;  position: fixed; /* Cambiamo da relative a fixed per impedire lo shift */
  left: 0; /* Aggiungiamo left: 0 per posizionare correttamente con position: fixed */
  top: 24px; /* Specifichiamo esplicitamente la posizione dall'alto */
}

@keyframes initialHint {
  0%, 90%, 100% { transform: scale(1); }
  45% { transform: scale(1.1); }
}
.book-btn-modern:active {
  filter: brightness(0.95);
}
/* Aggiungi uno pseudo-elemento per aumentare l'area cliccabile */
.book-btn-modern::before {
  content: '';
  position: absolute;
  top: -15px;
  left: -15px;
  right: -15px;
  bottom: -15px;
}
.book-modern {
  width: 44px;
  height: 44px;
  perspective: 300px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: filter 0.2s;
}
.cover {
  position: absolute;
  width: 44px;
  height: 44px;
  border-radius: 8px;
  box-shadow: 0 4px 16px #0004, 0 0 0 2px #ffb86b55;
  background: linear-gradient(120deg, #ffb86b 60%, #ff7eb3 100%);
  border: 3px solid #c18949;
  z-index: 3;
  transition: transform 0.5s cubic-bezier(0.4,0.2,0.2,1);
}
.cover.front {
  left: 0;
  top: 0;
  transform-origin: left;
  transform: rotateY(0deg);
}
.book-modern.open .cover.front {
  transform: rotateY(-120deg);
  box-shadow: 0 8px 32px #ffb86b55, 0 0 0 2px #ffb86b99;
}
.cover.back {
  left: 0;
  top: 0;
  background: linear-gradient(120deg, #23272f 60%, #ffb86b 100%);
  border: 3px solid #c18949;
  z-index: 1;
}
.pages {
  position: absolute;
  left: 0;
  top: 0;
  width: 44px;
  height: 44px;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.page {
  width: 38px;
  height: 40px;
  background: linear-gradient(90deg, #fff 80%, #ffe0b2 100%);
  border-radius: 6px;
  margin: 1.5px 0;
  box-shadow: 0 1px 2px #ffb86b33;
  opacity: 0.95;
  transition: box-shadow 0.2s;
}
.book-modern.open .page {
  box-shadow: 0 2px 8px #ffb86b77;
}
.bookmark {
  position: absolute;
  right: 7px;
  top: 7px;
  width: 10px;
  height: 18px;
  background: linear-gradient(180deg, #ff7eb3 60%, #ffb86b 100%);
  border-radius: 3px 3px 8px 8px;
  box-shadow: 0 2px 8px #ff7eb355;
  opacity: 0;
  transform: translateY(-10px) scale(0.7);
  transition: opacity 0.3s, transform 0.3s;
  z-index: 5;
}
.book-modern.open .bookmark {
  opacity: 1;
  transform: translateY(0) scale(1);
}
.book-btn-modern:hover .book-modern {
  filter: drop-shadow(0 0 8px #ffb86b88);
}
</style>
