# 🌉 Analisi Sismica Pila da Ponte (OpenSeesPy + Streamlit)

Questa repository contiene un'applicazione web interattiva per l'analisi strutturale e sismica di una pila da ponte. L'app unisce un'interfaccia utente intuitiva basata su **Streamlit** con la potenza di calcolo del motore agli elementi finiti **OpenSeesPy**.

![Rappresentazione del Modello](inserisci_qui_il_link_alla_tua_immagine.png)

## 📖 Descrizione Teorica

L'applicazione modella il comportamento trasversale di una pila da ponte schematizzandola come una **mensola incastrata alla base con una massa concentrata in sommità** (modello a un grado di libertà o *Lollipop model*, in linea con i concetti classici della dinamica delle strutture trattati da autori come il Prof. Petrangeli).

La pila viene discretizzata in 30 elementi finiti lungo la sua altezza, permettendo di estrarre e plottare in modo accurato l'inviluppo delle sollecitazioni (Taglio e Momento Flettente).

## ✨ Funzionalità

* **Gestione Sezioni Avanzata:** Supporto per pile a sezione costante, a tratti (sezioni multiple lungo l'altezza gestibili tramite tabella interattiva) o a sezione variabile (rastremata con interpolazione lineare).
* **Analisi Modale:** Calcolo immediato del periodo fondamentale (T1) della struttura.
* **Analisi Statica Lineare:** Applicazione di una forza statica in testa ed estrazione dei diagrammi di Taglio e Momento lungo l'altezza.
* **Analisi Time-History (NTC):**
  * Possibilità di caricare fino a 7 (o più) accelerogrammi in formato `.txt`.
  * Risoluzione al passo dinamica con integrazione di Newmark e smorzamento di Rayleigh al 5%.
  * Tracciamento della storia temporale degli spostamenti in testa.
  * Calcolo automatico della **media degli inviluppi massimi** di Taglio e Momento se vengono caricati almeno 7 segnali, come richiesto dalle Norme Tecniche per le Costruzioni (NTC).
* **Grafici Interattivi:** Tutti i risultati sono visualizzati tramite grafici Plotly, che permettono zoom, pan e ispezione puntuale dei valori sui nodi.

## 📂 Struttura del Repository

* `app.py`: File principale che gestisce l'interfaccia grafica (GUI) in Streamlit, i widget di input e il tracciamento dei grafici Plotly.
* `src_core.py`: Modulo contenente il motore numerico. Definisce la costruzione del modello OpenSees, l'assegnazione delle proprietà geometriche e le routine di analisi (modale, statica, time-history).
* `requirements.txt`: Elenco delle librerie Python necessarie per eseguire il progetto.

## 🚀 Installazione e Utilizzo

1. **Clona il repository:**
   ```bash
   git clone [https://github.com/tuo-username/nome-repo.git](https://github.com/tuo-username/nome-repo.git)
   cd nome-repo

```

2. **Crea un ambiente virtuale (consigliato) e installa le dipendenze:**
```bash
pip install -r requirements.txt

```


*(Assicurati che nel file `requirements.txt` siano presenti: `streamlit`, `openseespy`, `numpy`, `pandas`, `plotly`)*
3. **Avvia l'applicazione Streamlit:**
```bash
streamlit run app.py

```


4. **Usa l'app:**
Il tuo browser predefinito si aprirà automaticamente (solitamente all'indirizzo `http://localhost:8501`). Usa la barra laterale sinistra per impostare la geometria, selezionare il tipo di sezione, definire la massa e caricare i file di testo degli accelerogrammi.

## ⚠️ Formato degli Accelerogrammi

I file `.txt` caricati per l'analisi Time-History devono contenere una singola colonna di valori numerici rappresentanti l'accelerazione (espressa coerentemente con le unità di misura scelte, es. m/s2). Il passo di integrazione temporale (dt) viene specificato direttamente dall'interfaccia.

## 🛠️ Tecnologie Utilizzate

* [Streamlit](https://streamlit.io/) - Framework per la GUI.
* [OpenSeesPy](https://openseespydoc.readthedocs.io/) - Motore di analisi FEM.
* [Plotly](https://plotly.com/python/) - Libreria per la visualizzazione dati.
* [NumPy & Pandas](https://numpy.org/) - Gestione array e tabelle dati.
