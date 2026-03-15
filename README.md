
# 🌉 Analisi Sismica Pila da Ponte (OpenSeesPy + Streamlit)

Questa repository contiene un'applicazione web interattiva per l'analisi strutturale e sismica di una pila da ponte. L'app unisce un'interfaccia utente intuitiva e dinamica basata su **Streamlit** con la rigorosa potenza di calcolo del motore agli elementi finiti **OpenSeesPy**.

## 📖 Descrizione Teorica

L'applicazione modella il comportamento trasversale di una pila da ponte schematizzandola come una **mensola incastrata alla base con una massa concentrata in sommità** (modello a un grado di libertà o *Lollipop model*, in linea con i concetti classici della dinamica delle strutture trattati da autori come il Prof. Petrangeli).

La pila viene discretizzata in 30 elementi finiti lungo la sua altezza. A differenza di modelli più elementari, il solutore assegna rigorosamente la massa distribuita lungo il fusto della pila (tramite il peso specifico del materiale) e risolve le equazioni del moto estraendo 6 componenti fondamentali: **Sforzo Normale, Taglio, Momento Flettente, Spostamento, Rotazione e Accelerazione**.

## ✨ Funzionalità

L'applicazione è stata notevolmente espansa per offrire un'esperienza da software commerciale avanzato:

* **Interfaccia e UX Avanzata:** Layout a doppia colonna con visualizzazione grafica *parametrica e dinamica* del modello Lollipop (le proporzioni cambiano in base agli input) e preview immediata dei segnali sismici caricati (Spettro e Accelerogrammi).
* **Gestione Sezioni:** Supporto per pile a sezione costante, a tratti (sezioni multiple lungo l'altezza gestibili tramite tabella interattiva) o a sezione variabile (rastremata con interpolazione lineare).
* **Analisi Statica Lineare Equivalente (NTC):** Non una semplice spinta, ma un calcolo automatizzato che estrae il periodo $T_1$, legge l'accelerazione $S_e(T_1)$ dallo spettro di risposta caricato e applica la spinta statica equivalente.
* **Analisi Modale (Response Spectrum Analysis):**
* Utilizzo del comando nativo di OpenSees per l'analisi a spettro di risposta.
* Possibilità di scegliere il numero di modi di vibrare da estrarre.
* **Filtro modale intelligente**: il codice isola e normalizza correttamente solo i modi a prevalente partecipazione flessionale, nascondendo il "rumore" dei modi puramente assiali.
* Combinazione automatica dei massimi tramite **Regola SRSS**.
* Visualizzazione grafica delle **Forme Modali** e dei punti di lavoro (periodi estratti) direttamente sulla curva dello Spettro NTC.


* **Analisi Dinamica (Time-History):**
* Risoluzione al passo con integrazione di Newmark e smorzamento di Rayleigh al 5%.
* Plottaggio delle **Storie Temporali** per i punti critici (Spostamento, Rotazione e Accelerazione in testa; Sforzo Normale, Taglio e Momento alla base).
* Estrazione degli **Inviluppi Max/Min** lungo tutta l'altezza (ombreggiati graficamente) per tutte e 6 le caratteristiche della sollecitazione/deformazione.
* Calcolo automatico della **media NTC** se vengono caricati almeno 7 segnali sismici.


* 🎬 **Animazione Video Sincrona:** Motore di animazione integrato per guardare il modello della pila che oscilla (con spostamenti scalati visivamente) in perfetta sincronia con lo scorrere dell'accelerogramma al suolo.

## 📂 Struttura del Repository

* `app.py`: File principale che gestisce l'interfaccia grafica (GUI) in Streamlit, il layout responsivo e il tracciamento dei grafici avanzati Plotly.
* `src_core.py`: Modulo contenente il cuore FEM. Definisce la costruzione del modello OpenSees, l'assegnazione delle proprietà geometriche/inerziali, i filtri vettoriali e le routine di analisi.
* `requirements.txt`: Elenco delle librerie Python necessarie per eseguire il progetto.

## 🚀 Installazione e Utilizzo

1. **Clona il repository:**
```bash
git clone https://github.com/tuo-username/nome-repo.git
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
Il tuo browser predefinito si aprirà automaticamente (solitamente all'indirizzo `http://localhost:8501`). Usa la barra laterale sinistra per impostare geometria, masse e caricare i file di testo dei segnali sismici.

## ⚠️ Formato dei File di Input (Testo)

* **Spettro di Risposta:** Un file `.txt` o `.csv` contenente due colonne separate da spazio o tabulazione. La prima colonna è il Periodo $T$ (in secondi), la seconda colonna è l'Accelerazione spettrale $S_e$ (espressa in $g$).
* **Accelerogrammi:** I file `.txt` devono contenere una singola colonna di valori numerici rappresentanti la storia temporale dell'accelerazione (in m/s²). Il passo di integrazione temporale ($dt$) deve essere specificato nell'apposito campo dell'interfaccia.

## 🛠️ Tecnologie Utilizzate

* [Streamlit](https://streamlit.io/) - Framework per la GUI web.
* [OpenSeesPy](https://openseespydoc.readthedocs.io/) - Motore di calcolo non lineare FEM.
* [Plotly](https://plotly.com/python/) - Libreria per la visualizzazione interattiva e le animazioni.
* [NumPy & Pandas](https://numpy.org/) - Gestione array, interpolazioni e tabelle dati.
