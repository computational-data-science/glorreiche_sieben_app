"""
Die glorreichen sieben Werkzeuge -- Interaktive Streamlit-App
Qualitätssicherung Vorlesung | Fertigungsbeispiel: Schraubenproduktion
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import scipy.stats as stats

# ─── Seitenkonfiguration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Die glorreichen sieben Werkzeuge",
    page_icon="🔩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono&display=swap');

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #0057A8 0%, #003d7a 100%);
        color: white;
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { margin: 0; font-size: 2rem; font-weight: 700; }
    .main-header p  { margin: 0.4rem 0 0 0; opacity: 0.85; font-size: 1rem; }

    .tool-card {
        border: 2px solid #e0e8f4;
        border-left: 5px solid #0057A8;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        background: #f7faff;
    }
    .tool-card h4 { margin: 0 0 0.2rem 0; color: #0057A8; }
    .tool-card p  { margin: 0; font-size: 0.9rem; color: #444; }

    .metric-box {
        background: white;
        border: 1.5px solid #d0ddef;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        text-align: center;
    }
    .metric-box .val { font-size: 1.6rem; font-weight: 700; color: #0057A8; }
    .metric-box .lbl { font-size: 0.78rem; color: #666; }

    .alert-ok  { background:#e6f9ee; border-left:4px solid #2ECC71; padding:0.6rem 1rem; border-radius:6px; }
    .alert-warn{ background:#fff4e0; border-left:4px solid #F39C12; padding:0.6rem 1rem; border-radius:6px; }
    .alert-bad { background:#fde8e8; border-left:4px solid #E84C4C; padding:0.6rem 1rem; border-radius:6px; }
</style>
""", unsafe_allow_html=True)

# ─── Farben ──────────────────────────────────────────────────────────────────
BLUE   = "#0057A8"
LBLUE  = "#D6E8FF"
RED    = "#E84C4C"
ORANGE = "#F39C12"
GREEN  = "#2ECC71"
GRAY   = "#F4F6F8"

# ─── Datengenerator ──────────────────────────────────────────────────────────
@st.cache_data
def generate_screw_data(n: int = 200, seed: int = 42,
                        mu: float = 25.0, sigma: float = 0.12,
                        drift_from: int = 120) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    lengths = rng.normal(mu, sigma, n)
    # leichter Drift ab index drift_from
    lengths[drift_from:] += np.linspace(0, 0.15, n - drift_from)
    fehlerarten = rng.choice(
        ["Zu kurz", "Zu lang", "Grat", "Gewinde defekt", "Sonstiges"],
        p=[0.45, 0.25, 0.15, 0.10, 0.05], size=n
    )
    schicht = rng.choice(["Früh", "Spät", "Nacht"], p=[0.4, 0.35, 0.25], size=n)
    maschine = rng.choice(["M-01", "M-02", "M-03"], size=n)
    geschw   = rng.uniform(90, 150, n)
    abw      = (lengths - 25.0) + rng.normal(0, 0.01, n)

    return pd.DataFrame({
        "Nr":         range(1, n + 1),
        "Länge_mm":   np.round(lengths, 4),
        "Fehlerart":  fehlerarten,
        "Schicht":    schicht,
        "Maschine":   maschine,
        "Geschw_m_min": np.round(geschw, 1),
        "Abweichung": np.round(abw, 4),
    })


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Datensatz-Parameter")
    n_samples = st.slider("Anzahl Schrauben", 50, 500, 200, 10)
    ziel_laenge = st.number_input("Zielmaß (mm)", value=25.0, step=0.05)
    usl = st.number_input("USL (mm)", value=25.30, step=0.01)
    lsl = st.number_input("LSL (mm)", value=24.70, step=0.01)
    sigma_input = st.slider("Prozess-Streuung σ", 0.05, 0.30, 0.12, 0.01)
    drift_start = st.slider("Drift ab Stichprobe #", 50, n_samples - 10, 120, 5)
    seed_val = st.number_input("Seed (Reproduzierbarkeit)", value=42, step=1)

    st.markdown("---")
    st.markdown("**🔩 Glorreiche Sieben**")
    for i, tool in enumerate(["Check Sheet", "Flussdiagramm", "Histogramm",
                               "Pareto", "Ishikawa", "Streudiagramm", "Kontrollkarte"], 1):
        st.markdown(f"**{i}.** {tool}")

df = generate_screw_data(n_samples, int(seed_val), ziel_laenge, sigma_input, drift_start)
lsl_val, usl_val = lsl, usl


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
  <h1>🔩 Die glorreichen sieben Werkzeuge</h1>
  <p>Qualitätssicherung · Fertigungsbeispiel: Schraubenproduktion (M8, {ziel_laenge} mm Länge)</p>
</div>
""", unsafe_allow_html=True)

# KPI-Zeile
n_ok  = ((df["Länge_mm"] >= lsl_val) & (df["Länge_mm"] <= usl_val)).sum()
n_nok = n_samples - n_ok
s     = df["Länge_mm"].std()
cp    = (usl_val - lsl_val) / (6 * s) if s > 0 else 0
xbar  = df["Länge_mm"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f'<div class="metric-box"><div class="val">{n_samples}</div><div class="lbl">Stichproben</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box"><div class="val" style="color:#2ECC71">{n_ok}</div><div class="lbl">i.O.</div></div>', unsafe_allow_html=True)
with c3:
    col = RED if n_nok > 0 else GREEN
    st.markdown(f'<div class="metric-box"><div class="val" style="color:{col}">{n_nok}</div><div class="lbl">n.i.O.</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-box"><div class="val">{xbar:.4f}</div><div class="lbl">x̄ (mm)</div></div>', unsafe_allow_html=True)
with c5:
    col = GREEN if cp >= 1.33 else (ORANGE if cp >= 1.0 else RED)
    st.markdown(f'<div class="metric-box"><div class="val" style="color:{col}">{cp:.2f}</div><div class="lbl">Cp</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "1 · Check Sheet",
    "2 · Flussdiagramm",
    "3 · Histogramm",
    "4 · Pareto",
    "5 · Ishikawa",
    "6 · Streudiagramm",
    "7 · Kontrollkarte",
    "📊 Rohdaten",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 · CHECK SHEET
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.subheader("1 · Check Sheet — Daten strukturiert erfassen")
    st.caption("**Zweck:** Was passiert überhaupt? Strukturierte Strichliste der Fehlerarten.")

    col_a, col_b = st.columns([1.1, 1])

    with col_a:
        st.markdown("**Strichliste nach Fehlerart & Schicht**")
        pivot = df.groupby(["Fehlerart", "Schicht"]).size().unstack(fill_value=0)
        pivot["Gesamt"] = pivot.sum(axis=1)
        pivot = pivot.sort_values("Gesamt", ascending=False)
        pivot.loc["**Gesamt**"] = pivot.sum()
        st.dataframe(pivot, use_container_width=True)

    with col_b:
        st.markdown("**Fehler nach Maschine**")
        mach_tbl = df.groupby(["Maschine", "Fehlerart"]).size().unstack(fill_value=0)
        mach_tbl["Gesamt"] = mach_tbl.sum(axis=1)
        st.dataframe(mach_tbl, use_container_width=True)

    st.info("💡 **Praxistipp:** Immer Datum, Schicht, Maschine und Operator festhalten – erst dann sind die Daten auswertbar!")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 · FLUSSDIAGRAMM
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.subheader("2 · Flussdiagramm — Prozess verstehen")
    st.caption("**Zweck:** Wo im Ablauf könnte das Problem entstehen?")

    fig, ax = plt.subplots(figsize=(10, 7), facecolor="white")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis("off")

    def box(ax, x, y, txt, w=3.0, h=0.8, color=BLUE, shape="rect"):
        if shape == "diamond":
            dx, dy = w/2, h/2*1.4
            diamond = plt.Polygon(
                [[x, y+dy], [x+dx, y], [x, y-dy], [x-dx, y]],
                closed=True, facecolor=ORANGE+"30", edgecolor=ORANGE, lw=2
            )
            ax.add_patch(diamond)
            ax.text(x, y, txt, ha="center", va="center", fontsize=8, fontweight="bold", color="#7a4f00")
        elif shape == "round":
            fancy = mpatches.FancyBboxPatch((x-w/2, y-h/2), w, h,
                boxstyle="round,pad=0.1", facecolor=color, edgecolor=color, lw=2)
            ax.add_patch(fancy)
            ax.text(x, y, txt, ha="center", va="center", fontsize=9, fontweight="bold", color="white")
        else:
            rect = plt.Rectangle((x-w/2, y-h/2), w, h,
                facecolor=LBLUE, edgecolor=BLUE, lw=2, zorder=3)
            ax.add_patch(rect)
            ax.text(x, y, txt, ha="center", va="center", fontsize=9, color="#003060", zorder=4)

    def arrow(ax, x1, y1, x2, y2, label="", color=BLUE):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color=color, lw=2))
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx+0.15, my, label, fontsize=8, color=color)

    # Prozessschritte (Hauptpfad x=5)
    steps = [
        (5, 13,   "Rohmaterial",           "round"),
        (5, 11.5, "Drehen / Fräsen",       "rect"),
        (5, 10,   "Maß-Prüfung",           "diamond"),
        (5, 8.3,  "Gewindeschneiden",      "rect"),
        (5, 6.8,  "Gewinde-Prüfung",       "diamond"),
        (5, 5.3,  "Oberflächenbehandlung", "rect"),
        (5, 3.8,  "Endkontrolle",          "diamond"),
        (5, 2.5,  "Versand / Lager",       "round"),
    ]
    for x, y, txt, shp in steps:
        box(ax, x, y, txt, shape=shp)

    # Hauptpfeil-Verbindungen
    connections = [(5,12.6,5,11.9), (5,11.1,5,10.7), (5,9.3,5,8.7),
                   (5,7.9,5,7.5), (5,6.1,5,5.7), (5,4.9,5,4.5),
                   (5,3.1,5,2.9)]
    for x1,y1,x2,y2 in connections:
        arrow(ax, x1, y1, x2, y2)

    # Ja/Nein-Pfeile
    ax.text(5.15, 9.65, "Ja", fontsize=8, color="green")
    ax.text(5.15, 7.15, "Ja", fontsize=8, color="green")
    ax.text(5.15, 3.45, "Ja", fontsize=8, color="green")

    # Nein-Zweige (Nacharbeit / Ausschuss)
    box(ax, 8.2, 10, "Nacharbeit", w=2.4, color=RED)
    ax.annotate("", xy=(6.5, 10), xytext=(7.0, 10),
        arrowprops=dict(arrowstyle="->", color=RED, lw=1.5))
    ax.text(6.6, 10.15, "Nein", fontsize=8, color=RED)
    ax.annotate("", xy=(6.5, 10), xytext=(6.5, 10),)
    # draw arrow from diamond right to Nacharbeit
    ax.annotate("", xy=(6.98, 10), xytext=(5.75, 10),
        arrowprops=dict(arrowstyle="->", color=RED, lw=1.5))

    box(ax, 8.2, 6.8, "Ausschuss", w=2.4, color=RED)
    ax.annotate("", xy=(6.98, 6.8), xytext=(5.75, 6.8),
        arrowprops=dict(arrowstyle="->", color=RED, lw=1.5))
    ax.text(6.2, 6.95, "Nein", fontsize=8, color=RED)

    box(ax, 8.2, 3.8, "Sonderfreigabe", w=2.8, color=ORANGE)
    ax.annotate("", xy=(6.98, 3.8), xytext=(5.75, 3.8),
        arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.5))
    ax.text(6.2, 3.95, "Nein", fontsize=8, color=ORANGE)

    ax.set_title("Fertigungsprozess: Schraube M8 × 25 mm", fontsize=12,
                 fontweight="bold", color=BLUE, pad=10)
    st.pyplot(fig, use_container_width=True)
    plt.close()

    st.info("💡 **ISO 5807:** Rechteck = Prozessschritt · Raute = Entscheidung · Abgerundet = Start/Ende")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 · HISTOGRAMM
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.subheader("3 · Histogramm — Datenverteilung analysieren")
    st.caption("**Zweck:** Wie sieht die Streuung aus? Ist der Prozess fähig?")

    col_h, col_info = st.columns([2, 1])

    with col_h:
        fig, ax = plt.subplots(figsize=(8, 5), facecolor="white")
        n_bins = st.slider("Anzahl Klassen", 5, 30, 15)
        counts, bins, patches = ax.hist(df["Länge_mm"], bins=n_bins,
                                        color=BLUE, edgecolor="white", alpha=0.85)
        # Farbe für Ausreißer
        for patch, left, right in zip(patches, bins[:-1], bins[1:]):
            if right <= lsl_val or left >= usl_val:
                patch.set_facecolor(RED)
                patch.set_alpha(0.9)

        ax.axvline(lsl_val, color=RED, lw=2, ls="--", label=f"LSL = {lsl_val}")
        ax.axvline(usl_val, color=RED, lw=2, ls="--", label=f"USL = {usl_val}")
        ax.axvline(xbar, color=ORANGE, lw=2, ls="-", label=f"x̄ = {xbar:.4f}")
        ax.axvline(ziel_laenge, color=GREEN, lw=2, ls=":", label=f"Ziel = {ziel_laenge}")

        # Normalverteilungskurve
        x_curve = np.linspace(df["Länge_mm"].min(), df["Länge_mm"].max(), 300)
        y_curve = stats.norm.pdf(x_curve, xbar, s)
        bin_width = (bins[-1] - bins[0]) / n_bins
        ax.plot(x_curve, y_curve * len(df) * bin_width, color=ORANGE,
                lw=2.5, ls="-", label="Normalverteilung")

        ax.set_xlabel("Schraubenlänge (mm)", fontsize=11)
        ax.set_ylabel("Häufigkeit", fontsize=11)
        ax.set_title("Histogramm der Schraubenlängen", fontsize=13,
                     fontweight="bold", color=BLUE)
        ax.legend(fontsize=9)
        ax.grid(axis="y", ls="--", alpha=0.4)
        ax.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with col_info:
        st.markdown("**Kenngrößen:**")
        st.markdown(f"- Mittelwert x̄ = **{xbar:.4f} mm**")
        st.markdown(f"- Std.-Abw. s = **{s:.4f} mm**")
        st.markdown(f"- Min = {df['Länge_mm'].min():.4f} mm")
        st.markdown(f"- Max = {df['Länge_mm'].max():.4f} mm")

        st.markdown("---")
        st.markdown("**Prozessfähigkeit:**")
        cpu = (usl_val - xbar) / (3 * s)
        cpl = (xbar - lsl_val) / (3 * s)
        cpk = min(cpu, cpl)
        st.markdown(f"- Cp = **{cp:.3f}**")
        st.markdown(f"- Cpk = **{cpk:.3f}**")

        if cp >= 1.67:
            st.markdown('<div class="alert-ok">✅ Sehr guter Prozess (Cp ≥ 1.67)</div>', unsafe_allow_html=True)
        elif cp >= 1.33:
            st.markdown('<div class="alert-ok">✅ Fähiger Prozess (Cp ≥ 1.33)</div>', unsafe_allow_html=True)
        elif cp >= 1.0:
            st.markdown('<div class="alert-warn">⚠️ Grenzwertig (1.0 ≤ Cp < 1.33)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-bad">❌ Nicht fähig (Cp < 1.0)</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.latex(r"C_p = \frac{USL - LSL}{6s}")
        st.latex(r"C_{pk} = \min(C_{pu}, C_{pl})")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 · PARETO
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.subheader("4 · Pareto-Diagramm — Prioritäten setzen")
    st.caption("**Zweck:** 80 % der Probleme haben 20 % der Ursachen — diese zuerst angehen!")

    col_p, col_pi = st.columns([2, 1])

    with col_p:
        fehler_cnt = df["Fehlerart"].value_counts().sort_values(ascending=False)
        kum = fehler_cnt.cumsum() / fehler_cnt.sum() * 100

        fig, ax1 = plt.subplots(figsize=(8, 5), facecolor="white")
        ax2 = ax1.twinx()

        bars = ax1.bar(fehler_cnt.index, fehler_cnt.values,
                       color=BLUE, edgecolor="white", alpha=0.85, zorder=3)
        # Farbe vital few
        vital = kum[kum <= 80].index.tolist()
        for bar, label in zip(bars, fehler_cnt.index):
            if label in vital:
                bar.set_facecolor(BLUE)
            else:
                bar.set_facecolor("#90b8d8")

        ax2.plot(range(len(fehler_cnt)), kum.values,
                 color=ORANGE, lw=2.5, marker="o", markersize=7, zorder=4)
        ax2.axhline(80, color=RED, ls="--", lw=1.5, label="80%-Linie")

        ax1.set_xlabel("Fehlerart", fontsize=11)
        ax1.set_ylabel("Anzahl", fontsize=11)
        ax2.set_ylabel("Kumuliert (%)", fontsize=11, color=ORANGE)
        ax2.set_ylim(0, 105)
        ax2.tick_params(axis="y", colors=ORANGE)
        ax1.set_title("Pareto-Diagramm der Fehlerarten", fontsize=13,
                      fontweight="bold", color=BLUE)
        ax1.grid(axis="y", ls="--", alpha=0.4, zorder=0)
        ax1.spines[["top", "right"]].set_visible(False)

        for i, (val, cum) in enumerate(zip(fehler_cnt.values, kum.values)):
            ax1.text(i, val + 0.5, str(val), ha="center", fontsize=9, fontweight="bold")
            ax2.text(i + 0.15, cum + 1.5, f"{cum:.0f}%", fontsize=8, color=ORANGE)

        st.pyplot(fig, use_container_width=True)
        plt.close()

    with col_pi:
        st.markdown("**Rangfolge der Fehlerarten:**")
        pareto_df = pd.DataFrame({
            "Fehlerart": fehler_cnt.index,
            "Anzahl": fehler_cnt.values,
            "Kumuliert %": kum.values.round(1),
        })
        st.dataframe(pareto_df, hide_index=True, use_container_width=True)

        vital_few = pareto_df[pareto_df["Kumuliert %"] <= 80.1]["Fehlerart"].tolist()
        st.markdown(f"**Vital Few (≤80%):** {', '.join(vital_few)}")
        pct = len(vital_few) / len(fehler_cnt) * 100
        st.markdown(f"→ **{pct:.0f}%** der Fehlerarten verursachen **80%** der Probleme")
        st.info("💡 Konzentriere Verbesserungsmaßnahmen auf die **Vital Few**!")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 · ISHIKAWA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.subheader("5 · Ishikawa-Diagramm — Ursachen finden")
    st.caption("**Zweck:** Warum passiert das Problem systematisch? (6M-Methode)")

    # Interaktiv: Fehlerart wählen
    fehlerart = st.selectbox("Fehlerart analysieren:", df["Fehlerart"].unique())

    # Ursachen-Bibliothek
    ursachen_db = {
        "Zu kurz": {
            "Mensch": ["Falsches Nullpunkt-Setzen", "Unerfahrener Bediener", "Ablenkung"],
            "Maschine": ["Anschlag verschoben", "Spindelverschleiß", "Klemmen defekt"],
            "Material": ["Rohling zu kurz geliefert", "Falsche Charge", "Maßschwankung Lieferant"],
            "Methode": ["Kein SOP vorhanden", "Falsche Zeichnungsrevision", "Fehlende Prüfanweisung"],
            "Milieu": ["Temperatur-Ausdehnung", "Vibration der Maschine", "Span-Ansammlung"],
            "Messung": ["Messschieber nicht kalibriert", "Parallaxefehler", "Falscher Messpunkt"],
        },
        "Zu lang": {
            "Mensch": ["Maß falsch eingegeben", "Kontrollschritt übersprungen"],
            "Maschine": ["Anschlag zu früh", "Stopper defekt"],
            "Material": ["Rohling zu lang", "Härteverzug"],
            "Methode": ["Programm falsch", "Kein Probelauf"],
            "Milieu": ["Thermische Ausdehnung (Anlauf)", "Kühlmittelmangel"],
            "Messung": ["Messung nach Erwärmung", "Falsches Bezugsmaß"],
        },
        "Grat": {
            "Mensch": ["Abnutzung nicht gemeldet", "Falsche Schnittparameter"],
            "Maschine": ["Werkzeug stumpf", "Zu hoher Vorschub"],
            "Material": ["Zähes Material", "Falsche Legierung"],
            "Methode": ["Kein Entgraten im Prozess", "Falsche Schnittgeschwindigkeit"],
            "Milieu": ["Kühlmittel zu wenig", "Späne nicht entfernt"],
            "Messung": ["Grat nicht als Fehler klassifiziert", "Sichtprüfung fehlt"],
        },
        "Gewinde defekt": {
            "Mensch": ["Gewindebohrer falsch gespannt", "Schmierung vergessen"],
            "Maschine": ["Gewindeschneidkopf verschlissen", "Zentrierung falsch"],
            "Material": ["Kernloch zu klein", "Materialspannung"],
            "Methode": ["Falsches Schneidöl", "Kein Bruchkontrolle"],
            "Milieu": ["Span im Gewinde", "Vibration beim Schneiden"],
            "Messung": ["Gewindelehre fehlt", "Nur Sichtprüfung"],
        },
        "Sonstiges": {
            "Mensch": ["Unklare Zuständigkeit", "Fehlende Schulung"],
            "Maschine": ["Unbekannte Ursache", "Intermittierender Fehler"],
            "Material": ["Unbekannte Charge", "Falsch eingelagert"],
            "Methode": ["Prozess nicht dokumentiert", "Kein Standard"],
            "Milieu": ["Unbekannter Umwelteinfluss"],
            "Messung": ["Fehler nicht messbar"],
        },
    }

    ursachen = ursachen_db.get(fehlerart, ursachen_db["Sonstiges"])

    fig, ax = plt.subplots(figsize=(14, 8), facecolor="white")
    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 9)
    ax.axis("off")

    # Hauptgräte
    ax.annotate("", xy=(9.5, 4), xytext=(1, 4),
        arrowprops=dict(arrowstyle="->", color=BLUE, lw=3))

    # Problem-Box
    problem_box = mpatches.FancyBboxPatch((9.5, 3.2), 1.4, 1.6,
        boxstyle="round,pad=0.1", facecolor=RED+"20", edgecolor=RED, lw=2)
    ax.add_patch(problem_box)
    ax.text(10.2, 4.0, fehlerart, ha="center", va="center",
            fontsize=10, fontweight="bold", color=RED, wrap=True)

    # 6 Äste
    m6_colors = [BLUE, "#1a7a5e", "#8b4513", "#6a0dad", ORANGE, "#c0392b"]
    positions = [
        (2.5, 4, 2.0, 6.5, "Mensch",   "top"),
        (4.5, 4, 4.0, 6.5, "Maschine", "top"),
        (6.5, 4, 6.0, 6.5, "Methode",  "top"),
        (2.5, 4, 2.0, 1.5, "Material", "bottom"),
        (4.5, 4, 4.0, 1.5, "Milieu",   "bottom"),
        (6.5, 4, 6.0, 1.5, "Messung",  "bottom"),
    ]

    for (xm, ym, xh, yh, name, side), col in zip(positions, m6_colors):
        ax.annotate("", xy=(xm, ym), xytext=(xh, yh),
            arrowprops=dict(arrowstyle="->", color=col, lw=2.5))
        ax.text(xh, yh + (0.35 if side=="top" else -0.35), name,
                ha="center", va="center", fontsize=11,
                fontweight="bold", color=col,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor=col, lw=1.5))
        # Unterursachen
        causes = ursachen.get(name, [])[:3]
        for i, cause in enumerate(causes):
            if side == "top":
                xc = xh + (i - 1) * 1.0
                yc = yh - 0.9 - i * 0.4
            else:
                xc = xh + (i - 1) * 1.0
                yc = yh + 0.9 + i * 0.4
            ax.text(xc, yc, f"• {cause}", ha="center", va="center",
                    fontsize=7.5, color="#333",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="#f5f5f5",
                              edgecolor=col+"80", lw=1))

    ax.set_title(f"Ishikawa-Diagramm: Ursachen für '{fehlerart}'",
                 fontsize=14, fontweight="bold", color=BLUE, pad=15)
    st.pyplot(fig, use_container_width=True)
    plt.close()

    st.info("💡 **5-Why-Methode:** Für jede Hauptursache fünfmal 'Warum?' fragen, bis die Wurzelursache gefunden ist.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 · STREUDIAGRAMM
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.subheader("6 · Streudiagramm — Zusammenhänge prüfen")
    st.caption("**Zweck:** Gibt es Korrelationen zwischen Prozessparametern?")

    col_s, col_si = st.columns([2, 1])

    with col_s:
        fig, ax = plt.subplots(figsize=(8, 5), facecolor="white")

        # Farbe nach Maschine
        machine_colors = {"M-01": BLUE, "M-02": GREEN, "M-03": ORANGE}
        for mach, grp in df.groupby("Maschine"):
            ax.scatter(grp["Geschw_m_min"], grp["Abweichung"],
                       color=machine_colors[mach], alpha=0.65, s=40,
                       label=mach, zorder=3)

        # Regressionsgerade
        x = df["Geschw_m_min"].values
        y = df["Abweichung"].values
        m, b, r, p, se = stats.linregress(x, y)
        x_line = np.linspace(x.min(), x.max(), 200)
        ax.plot(x_line, m * x_line + b, color=RED, lw=2, ls="--",
                label=f"Regression (r={r:.3f})")

        ax.axhline(0, color=GRAY, lw=1, ls="-")
        ax.set_xlabel("Schnittgeschwindigkeit (m/min)", fontsize=11)
        ax.set_ylabel("Längenabweichung (mm)", fontsize=11)
        ax.set_title("Streudiagramm: Schnittgeschwindigkeit vs. Maßabweichung",
                     fontsize=12, fontweight="bold", color=BLUE)
        ax.legend(fontsize=9)
        ax.grid(ls="--", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with col_si:
        st.markdown("**Korrelationsanalyse:**")
        r_val = r
        r2 = r_val**2
        st.markdown(f"- Korrelationskoeffizient r = **{r_val:.4f}**")
        st.markdown(f"- Bestimmtheitsmaß R² = **{r2:.4f}**")
        st.markdown(f"- p-Wert = **{p:.4f}**")
        st.markdown(f"- Steigung m = **{m:.5f}**")

        if abs(r_val) > 0.9:
            st.markdown('<div class="alert-bad">⚠️ Starke Korrelation – Einfluss prüfen!</div>', unsafe_allow_html=True)
        elif abs(r_val) > 0.6:
            st.markdown('<div class="alert-warn">⚠️ Moderate Korrelation</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-ok">✅ Schwache / keine Korrelation</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Interpretation:**")
        st.markdown(f"Mit steigender Schnittgeschwindigkeit {'steigt' if m > 0 else 'sinkt'} die Längenabweichung um **{abs(m)*10:.4f} mm** pro 10 m/min.")
        st.warning("⚠️ Korrelation ≠ Kausalität! Immer Prozesswissen hinzuziehen.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 · KONTROLLKARTE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.subheader("7 · Kontrollkarte (SPC) — Prozess überwachen")
    st.caption("**Zweck:** Ist der Prozess stabil? Eingreifen bevor Ausschuss entsteht!")

    col_k, col_ki = st.columns([2, 1])

    with col_k:
        subgroup_size = st.slider("Stichprobengröße n", 3, 10, 5)
        n_groups = len(df) // subgroup_size
        groups = [df["Länge_mm"].iloc[i*subgroup_size:(i+1)*subgroup_size]
                  for i in range(n_groups)]

        xbar_vals = np.array([g.mean() for g in groups])
        r_vals    = np.array([g.max() - g.min() for g in groups])

        # Kontrollgrenzen (x-bar Karte)
        A2 = {2:1.880, 3:1.023, 4:0.729, 5:0.577, 6:0.483,
              7:0.419, 8:0.373, 9:0.337, 10:0.308}
        a2 = A2.get(subgroup_size, 0.577)

        cl  = xbar_vals.mean()
        r_bar = r_vals.mean()
        ucl = cl + a2 * r_bar
        lcl = cl - a2 * r_bar

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), facecolor="white",
                                        sharex=True)
        x_idx = np.arange(1, n_groups + 1)

        # ── x-bar Karte ──
        ax1.plot(x_idx, xbar_vals, color=BLUE, lw=1.8, marker="o",
                 markersize=5, zorder=3)
        ax1.axhline(cl,  color=BLUE,   lw=1.5, ls="-",  label=f"CL={cl:.4f}")
        ax1.axhline(ucl, color=RED,    lw=1.5, ls="--", label=f"UCL={ucl:.4f}")
        ax1.axhline(lcl, color=RED,    lw=1.5, ls="--", label=f"LCL={lcl:.4f}")

        # Violations
        violations = np.where((xbar_vals > ucl) | (xbar_vals < lcl))[0]
        if len(violations):
            ax1.scatter(x_idx[violations], xbar_vals[violations],
                        color=RED, s=80, zorder=5, label="Eingriff!")

        ax1.set_ylabel("x̄ (mm)", fontsize=10)
        ax1.set_title("x̄-Karte (Mittelwertkarte)", fontsize=12,
                      fontweight="bold", color=BLUE)
        ax1.legend(fontsize=8, loc="upper left")
        ax1.grid(ls="--", alpha=0.3)
        ax1.spines[["top", "right"]].set_visible(False)

        # ── R-Karte ──
        D3 = {2:0, 3:0, 4:0, 5:0, 6:0, 7:0.076, 8:0.136, 9:0.184, 10:0.223}
        D4 = {2:3.267, 3:2.574, 4:2.282, 5:2.114, 6:2.004,
              7:1.924, 8:1.864, 9:1.816, 10:1.777}
        r_ucl = D4.get(subgroup_size, 2.114) * r_bar
        r_lcl = D3.get(subgroup_size, 0) * r_bar

        ax2.plot(x_idx, r_vals, color="#1a7a5e", lw=1.8, marker="s",
                 markersize=5, zorder=3)
        ax2.axhline(r_bar, color="#1a7a5e", lw=1.5, ls="-",  label=f"R̄={r_bar:.4f}")
        ax2.axhline(r_ucl, color=RED,      lw=1.5, ls="--", label=f"UCL={r_ucl:.4f}")
        if r_lcl > 0:
            ax2.axhline(r_lcl, color=RED, lw=1.5, ls="--", label=f"LCL={r_lcl:.4f}")

        r_viol = np.where(r_vals > r_ucl)[0]
        if len(r_viol):
            ax2.scatter(x_idx[r_viol], r_vals[r_viol], color=RED, s=80, zorder=5)

        ax2.set_xlabel("Stichprobengruppe", fontsize=10)
        ax2.set_ylabel("R (mm)", fontsize=10)
        ax2.set_title("R-Karte (Spannweitenkarte)", fontsize=12,
                      fontweight="bold", color="#1a7a5e")
        ax2.legend(fontsize=8, loc="upper left")
        ax2.grid(ls="--", alpha=0.3)
        ax2.spines[["top", "right"]].set_visible(False)

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with col_ki:
        st.markdown("**Kontrollgrenzen:**")
        st.markdown(f"- CL = **{cl:.4f} mm**")
        st.markdown(f"- UCL = **{ucl:.4f} mm**")
        st.markdown(f"- LCL = **{lcl:.4f} mm**")
        st.markdown(f"- A₂ = **{a2}** (n={subgroup_size})")

        st.markdown("---")
        if len(violations) == 0:
            st.markdown('<div class="alert-ok">✅ Prozess unter statistischer Kontrolle</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-bad">❌ {len(violations)} Eingriffspunkt(e) erkannt!</div>', unsafe_allow_html=True)
            st.markdown(f"Stichprobengruppen: {list(x_idx[violations])}")

        st.markdown("---")
        st.markdown("**Nelson-Regeln (Auszug):**")
        st.markdown("1. 1 Punkt außerhalb UCL/LCL")
        st.markdown("2. 9 Punkte auf einer Seite der CL")
        st.markdown("3. 6 Punkte stetig steigend/fallend")
        st.markdown("4. 14 Punkte abwechselnd auf/ab")

        st.latex(r"UCL/LCL = \bar{\bar{x}} \pm A_2 \cdot \bar{R}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB · ROHDATEN
# ══════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.subheader("📊 Rohdaten")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        schicht_filter = st.multiselect("Schicht:", df["Schicht"].unique(),
                                         default=list(df["Schicht"].unique()))
    with col_f2:
        masch_filter = st.multiselect("Maschine:", df["Maschine"].unique(),
                                       default=list(df["Maschine"].unique()))

    df_filtered = df[df["Schicht"].isin(schicht_filter) & df["Maschine"].isin(masch_filter)]

    def highlight_oor(row):
        if row["Länge_mm"] < lsl_val or row["Länge_mm"] > usl_val:
            return ["background-color: #fde8e8"] * len(row)
        return [""] * len(row)

    st.dataframe(df_filtered.style.apply(highlight_oor, axis=1),
                 use_container_width=True, height=400)

    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("📥 CSV herunterladen", csv,
                       "schrauben_daten.csv", "text/csv")
