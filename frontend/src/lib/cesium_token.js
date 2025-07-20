// Cesium Ion access token da configurazione locale
// Questo utilizza prima le variabili d'ambiente (produzione), poi la config locale (sviluppo)
import { CONFIG } from './config.local.js';

export const CESIUM_TOKEN = import.meta.env.VITE_CESIUM_TOKEN || CONFIG.CESIUM_TOKEN;
