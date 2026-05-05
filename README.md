# Die glorreichen sieben Werkzeuge — Projekt

Qualitätssicherung Vorlesung | Fertigungsbeispiel: Schraubenproduktion M8 × 25 mm


---

## Streamlit-App starten

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# App starten
streamlit run glorreiche_sieben_app.py
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`.

---

## Features der Streamlit-App

| Tab | Werkzeug | Interaktivität |
|-----|---------|----------------|
| 1 | Check Sheet | Pivot-Tabelle nach Schicht & Maschine |
| 2 | Flussdiagramm | Statische Visualisierung |
| 3 | Histogramm | Klassenanzahl, LSL/USL, Cp/Cpk-Berechnung |
| 4 | Pareto | Vital-Few-Analyse |
| 5 | Ishikawa | Auswahl der Fehlerart, 6M-Ursachen |
| 6 | Streudiagramm | Korrelationsanalyse mit Regression |
| 7 | Kontrollkarte | x̄- & R-Karte, Stichprobengröße wählbar |
| 📊 | Rohdaten | Filter, Download als CSV |

### Sidebar-Parameter (alle live anpassbar)
- Anzahl Schrauben (50–500)
- Zielmaß, USL, LSL
- Prozess-Streuung σ
- Drift-Startpunkt (simuliert Maschinenverschleiß)
- Seed (Reproduzierbarkeit)

---

## Datensatz

Synthetisch generiert — simuliert eine reale Schraubenproduktion:
- **Merkmal:** Schraubenlänge [mm], Ziel 25,0 mm
- **Fehlerarten:** Zu kurz, Zu lang, Grat, Gewinde defekt, Sonstiges
- **Schichten:** Früh, Spät, Nacht
- **Maschinen:** M-01, M-02, M-03
- **Drift:** Ab konfigurierbarer Stichprobe simuliert (→ Kontrollkarte schlägt an)

---

## Verwendung in der Vorlesung

1. **Folien** für die theoretische Einführung jedes Werkzeugs
2. **App** live im Hörsaal zeigen — Parameter anpassen und Effekte direkt sehen
3. **Aufgaben für Studierende:**
   - Cp-Wert interpretieren: Was bedeutet σ = 0,20 vs. 0,08?
   - Pareto: Welche Maßnahme würde 80 % der Fehler reduzieren?
   - Kontrollkarte: Ab wann schlägt die Karte beim Drift an?
   - Ishikawa: Für jede Fehlerart 5-Why-Analyse durchführen
