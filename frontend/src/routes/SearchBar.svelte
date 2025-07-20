<script lang="ts">
export let searchQuery;
export let onSearch = (e: any) => {};
export let basemap = 'bing';
export let onBasemapChange = (e: any) => {};
</script>

<form on:submit|preventDefault={(e) => onSearch(e)} class="controls">
    <input type="text" bind:value={searchQuery} placeholder="Cerca luogo, città, stato..." autocomplete="off" class="input-beauty dark" />
    <button type="submit" class="btn-dark" style="display: flex; align-items: center; justify-content: center; padding: 0.5rem 1.2rem;">
        <img src="/searching.svg" alt="Cerca" width="22" height="22" style="display: block;" />
    </button>
    <label for="basemapSelect" style="display:none;">Modello mappa:</label>
    <select id="basemapSelect" bind:value={basemap} on:change={(e) => onBasemapChange(e)} style="display:none;"></select>
</form>

<style>
.controls {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.5rem; /* Reduced from 1rem to 0.5rem for better spacing on larger screens */
}
.input-beauty.dark {
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
.input-beauty.dark:focus {
    border: 2px solid #ffb86b;
    outline: none;
    box-shadow: 0 4px 16px rgba(255,184,107,0.13);
    background: #23272f;
}
.btn-dark {
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
.btn-dark:hover {
    background: linear-gradient(90deg, #2d3a4a 0%, #23272f 100%);
    color: #fff;
    transform: translateY(-2px) scale(1.04);
}

/* Stili responsive per dispositivi piccoli */
@media (max-width: 600px) {
    .controls {
        margin-top: 130px; /* Spazio extra sopra la barra di ricerca su dispositivi piccoli */
        margin-bottom: 1rem; /* Ripristina il margine più ampio su dispositivi piccoli */
        flex-direction: column;
    }
    
    .input-beauty.dark {
        width: 100%;
        margin-right: 0;
        margin-bottom: 0.5rem;
    }
    
    .btn-dark {
        width: 100%;
    }
}

/* Stili per tablet */
@media (min-width: 601px) and (max-width: 900px) {
    .controls {
        margin-top: 90px; /* Spazio moderato per tablet */
    }
}
</style>
