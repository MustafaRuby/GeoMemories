import { writable } from 'svelte/store';

// Store globale per mostrare/nascondere il floating add button
const showFloatingAddBtn = writable(false);
export default showFloatingAddBtn;
