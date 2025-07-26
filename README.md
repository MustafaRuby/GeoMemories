# 🌍 GeoMemories

> **Il diario digitale che unisce ricordi, luoghi e mappe 3D**

GeoMemories è un'applicazione web moderna che trasforma il tuo diario personale in un'esperienza immersiva: puoi associare ricordi a luoghi reali, visualizzarli su una mappa 3D interattiva, arricchirli con foto e file, e ritrovare ogni momento importante... dove è davvero accaduto.

---

## 🚀 Caratteristiche principali

- **Registrazione e login sicuri** (JWT, password hash)
- **Gestione ricordi**: crea, modifica, elimina, associa luoghi e file multimediali
- **Gestione posizioni**: aggiungi, modifica, elimina e cerca luoghi personali
- **Mappa 3D interattiva**: esplora, cerca, vola sulle posizioni, visualizza i tuoi ricordi geolocalizzati
- **Esperienza utente avanzata**: UI moderna, responsive, modali globali, aggiornamento automatico delle liste
- **Sicurezza**: autenticazione robusta, protezione dati, gestione sicura dei file

---

## 🗺️ Come funziona

1. **Registrati** e accedi in modo sicuro
2. **Aggiungi posizioni** sulla mappa 3D o tramite ricerca
3. **Crea ricordi** associandoli a uno o più luoghi e allegando file
4. **Rivivi i tuoi momenti** esplorando la mappa e la timeline dei ricordi
5. **Gestisci tutto** da un'unica interfaccia intuitiva, anche da mobile

---

## 📂 Struttura del progetto

```
project_diary/
├── backend/      # API Flask, MongoDB, Cloudinary
├── frontend/     # Svelte, CesiumJS, UI, store, pagine
├── installation.md  # Guida installazione e configurazione
├── README.md     # (questo file)
```

- **backend/**: API REST, autenticazione, gestione dati, upload file
- **frontend/**: UI Svelte, mappa 3D, gestione ricordi/posizioni, modali
- **installation.md**: guida dettagliata a setup, build, variabili ambiente

---

## 🛠️ Tecnologie principali

| Frontend         | Backend         | Database   | Altri servizi         |
|------------------|----------------|------------|-----------------------|
| Svelte + Vite    | Flask (Python) | MongoDB    | CesiumJS (3D Map)     |
| CesiumJS         | PyMongo        | Atlas/Local| Cloudinary (upload)   |
| CSS custom       | JWT            |            | OpenStreetMap/Nominatim|

---

## 📸 Screenshot

![UI Image](https://github.com/user-attachments/assets/860f5368-4fee-4864-a49e-992a71aae392)
![UI Image](https://github.com/user-attachments/assets/e1551976-6ea8-49e5-8a28-af59114fd68a)
![UI Image](https://github.com/user-attachments/assets/324a49e9-a5c9-4068-8a71-fd60b804e6b4)

---

## 📖 Altre informazioni

- Per dettagli su installazione, avvio e build consulta **installation.md**
- Build produzione frontend: `npm run build`
- Build produzione backend: `pip install requirements.txt`
- Variabili sensibili (token Cesium, Cloudinary, MongoDB URI) vanno in `.env` o file dedicati

## Token e requisiti
Ci sono 3 servizi cloud usati in questo progetto che richiedono token personali: MongoDB; CesiumJS; Cloudinary.
- Per la connessione al database di MongoDB è necessario cambiare l'URI di connessione di mongo DB in `backend/db_manager.py`
- Per la connessione allo spazio cloud di Cloudinary è necessario inserire le proprie credenziali in `backend/cloudinary_credentials.py` e in `frontend/src/lib/config.local.js`
- Per la connessione all'API della mappa di CesiumJS è necessario inserire il proprio token in `frontend/src/lib/config.local.js`

---

## 👨‍💻 Autori
- Abou Elkhir Mostafa
- Barsa Dan
- Trysh Alessandro

---

© 2025 GeoMemories — Tutti i diritti riservati
