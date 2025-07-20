# Installation Guide

Questa guida ti spiega come installare tutte le dipendenze e avviare il progetto "Diario con mappa" (Flask + MongoDB + Svelte).

---

## 1. Requisiti
- Python 3.8+ (consigliato Python 3.10+)
- Node.js 18+ e npm
- Connessione internet (per Cesium e MongoDB Atlas)

---

## 2. Installazione Backend (Flask)

1. Apri il terminale e vai nella cartella `backend`:
   ```powershell
   cd backend
   ```
2. Installa le dipendenze Python:
   ```powershell
   pip install -r requirements.txt
   ```
3. Avvia il server Flask:
   ```powershell
   python app.py
   ```
   Il backend sarà disponibile su `http://localhost:5000`.

---

## 3. Installazione Frontend (Svelte)

1. Apri un nuovo terminale e vai nella cartella `frontend`:
   ```powershell
   cd frontend
   ```
2. Installa le dipendenze Node.js:
   ```powershell
   npm install
   ```
3. Costruisci il progetto:
   ```powershell
   npm run build
   ```
4. Avvia il server di sviluppo Svelte:
   ```powershell
   npm run dev
   ```
   Il frontend sarà disponibile su `http://localhost:5173`.

---

## 4. Configurazione variabili d'ambiente (IMPORTANTE per la sicurezza)

### Frontend
1. Copia il file `.env.example` in `.env` nella cartella `frontend`:
   ```powershell
   cd frontend
   cp .env.example .env
   ```
2. Modifica il file `.env` con i tuoi token:
   - **VITE_CESIUM_TOKEN**: Ottieni il token da [Cesium Ion Dashboard](https://cesium.com/ion/dashboard/)
   - **VITE_CLOUDINARY_CLOUD_NAME**: Il nome del tuo cloud Cloudinary
   - **VITE_CLOUDINARY_UPLOAD_PRESET**: Il preset di upload configurato su Cloudinary

### Backend
1. Modifica `backend/cloudinary_credentials.py` con le tue credenziali Cloudinary
2. **IMPORTANTE**: Aggiungi sempre i file `.env` e `cloudinary_credentials.py` al `.gitignore`

---

## 5. Configurazione Cesium (aggiornato)
- Il token Cesium è già incluso in `frontend/src/lib/cesium_token.js`.
- Se vuoi usare un tuo token, sostituisci il valore di `CESIUM_TOKEN` in quel file.

---

## 6. Note su MongoDB
- Il backend è già configurato per usare MongoDB Atlas (cloud). Se vuoi usare un database locale, modifica la variabile `MONGO_URI` in `backend/db_manager.py`.

---

## 7. Flusso di avvio rapido
1. Avvia il backend:
   ```powershell
   cd backend
   python app.py
   ```
2. Avvia il frontend in un altro terminale:
   ```powershell
   cd frontend
   npm run dev
   ```

---

## 8. Accesso all'applicazione
- Vai su [http://localhost:5173](http://localhost:5173) per usare l'app.
- Se non sei autenticato, verrai reindirizzato alla pagina di login su `http://localhost:5173/login`.

---

## 9. Risoluzione problemi
- Se hai problemi con Cesium, verifica il token.
- Se il backend non si avvia, controlla che MongoDB sia accessibile e che le dipendenze siano installate.
- Per errori di CORS, assicurati di usare le porte corrette (5000 per backend, 5173 per frontend).

---

## 10. Disinstallazione
Per rimuovere le dipendenze:
- Python: elimina la cartella `venv` (se usata) o disinstalla i pacchetti manualmente.
- Node.js: elimina la cartella `node_modules`, `svelte-kit` e `dist` nella cartella `frontend`.

---

**Buon viaggio con GeoMemories!**
