# 🌉 Analisi Sismica Pila da Ponte (OpenSeesPy + Streamlit)

Questa repository contiene un'applicazione web interattiva per l'analisi strutturale e sismica di una pila da ponte. L'app unisce un'interfaccia utente intuitiva basata su **Streamlit** con la potenza di calcolo del motore agli elementi finiti **OpenSeesPy**.

![Rappresentazione del Modello](Gemini_Generated_Image_ugw81augw81augw8.png)

## 📖 Descrizione Teorica

L'applicazione modella il comportamento trasversale di una pila da ponte schematizzandola come una **mensola incastrata alla base con una massa concentrata in sommità** (modello a un grado di libertà o *Lollipop model*, in linea con i concetti classici della dinamica delle strutture trattati da autori come il Prof. Petrangeli).

La pila viene discretizzata in 30 elementi finiti lungo la sua altezza, permettendo di estrarre e plottare in modo accurato l'inviluppo delle sollecitazioni (Taglio e Momento Flettente). A differenza di modelli base, il solutore assegna rigorosamente la massa distribuita lungo il fusto e calcola 6 componenti fondamentali: Sforzo Normale, Taglio, Momento, Spostamento, Rotazione e Accelerazione.

![Rappresentazione del Modello](Gemini_Generated_Image_o757zo757zo757zo.png)

## ✨ Funzionalità

* **Interfaccia Dinamica:** Layout a doppia colonna con visualizzazione grafica parametrica del modello e preview immediata dei segnali sismici caricati (Spettro e Accelerogrammi).
* **Gestione Sezioni Avanzata:** Supporto per pile a sezione costante, a tratti (sezioni multiple gestibili tramite tabella interattiva) o a sezione variabile (rastremata con interpolazione lineare).
* **Analisi Statica Lineare Equivalente (NTC):** Estrazione del periodo fondamentale, calcolo automatico dell'accelerazione spettrale e applicazione della spinta statica equivalente.
* **Analisi Modale (Response Spectrum Analysis):**
  * Utilizzo del comando nativo OpenSeesPy.
  * Possibilità di scegliere il numero di modi da estrarre con filtro modale integrato (isola i modi flessionali da quelli assiali).
  * Combinazione automatica dei massimi tramite **Regola SRSS**.
  * Visualizzazione delle deformate modali e dei punti di lavoro direttamente sulla curva dello Spettro NTC.
* **Analisi Dinamica (Time-History NTC):**
  * Integrazione al passo di Newmark con smorzamento di Rayleigh al 5%.
  * Plottaggio delle storie temporali per i punti critici (Top e Base).
  * Estrazione degli inviluppi Max/Min lungo l'altezza.
  * Calcolo automatico della **media degli inviluppi massimi** caricando 7 o più accelerogrammi.
* 🎬 **Animazione Video:** Motore integrato per visualizzare la deformata della pila che oscilla in perfetta sincronia con l'accelerogramma al suolo.

## 📂 Struttura del Repository

* `app.py`: File principale che gestisce l'interfaccia grafica (GUI) in Streamlit e il tracciamento dei grafici Plotly.
* `src_core.py`: Modulo contenente il motore numerico FEM in OpenSeesPy (costruzione modello, carichi, analisi statica, modale e time-history).
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
Il tuo browser predefinito si aprirà automaticamente all'indirizzo `http://localhost:8501`. Usa la barra laterale per impostare la geometria e caricare i file dei segnali.

## ⚠️ Formato dei File di Input (Testo)

* **Spettro di Risposta:** File `.txt` o `.csv` con due colonne separate da spazio/tab (Periodo in secondi, Accelerazione in g).
* **Accelerogrammi:** File `.txt` con una singola colonna di valori rappresentanti l'accelerazione (es. in m/s²). Il passo $dt$ si specifica nell'interfaccia.

## 🛠️ Tecnologie Utilizzate

* [Streamlit](https://streamlit.io/) - Framework per la GUI.
* [OpenSeesPy](https://openseespydoc.readthedocs.io/) - Motore di analisi FEM.
* [Plotly](https://plotly.com/python/) - Libreria per la visualizzazione dati e animazioni.
* [NumPy & Pandas](https://numpy.org/) - Gestione array e tabelle dati.
