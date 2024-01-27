# ANALISI STATICA DI GROOVY CON SPOTBUGS

## Descrizione
Questo script Python è progettato per analizzare Groovy utilizzando SpotBugs, uno strumento di analisi statica del codice per trovare potenziali bug in progetti Java.

# **Il progetto funziona solo su sistema Linux**

## Requisiti
- Stema operativo GNU/Linux (necessario per eseguire le build di Groovy)
- Python 3.x installato sul tuo sistema
- Librerie Python necessarie: `gitpython` (per gestire il repository Git)

Puoi installare le librerie necessarie eseguendo il seguente comando:
```bash
pip install GitPython
```
Se si vuole analizzare dei commit vecchi potrebbe essere necessario Spotbugs Standalone, se è questo il caso eseguire lo script di seguito:
```bash
python3 install_spotbugs.py
```
Per rendere eseguibile spotbugs standalone eseguire:
```bash
chmod +x "spotbugs-4.8.3/bin/spotbugs"
```


## Utilizzo
1. Esegui lo script:
```bash
python main.py
```
2. Segui le istruzioni nel menu per iniziare l'analisi o visualizzare i risultati.

## Opzioni
- **START ANALIZING GROOVY**: Questa opzione avvia l'analisi del repository Git specificato. Puoi scegliere di analizzare un intervallo personalizzato di commit.
- **EXTRACT FINAL RESULTS**: Estrae e aggrega i risultati finali dell'analisi SpotBugs.
- **SEE FINAL RESULTS**: Visualizza i risultati finali dell'analisi SpotBugs, inclusi il numero totale di bug per categoria e per file.
- **EXIT**: Chiude lo script.

## Note
- I primi 1500 commit vengono considerati vuoti.
- I commit che non utilizzano groovy verranno saltati
