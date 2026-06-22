# ⚡ Dashboard Éco2mix - Analyse du Mix Énergétique Régional

Ce projet a été développé dans le cadre de mon mémoire de fin d'études de **Business Analyst**. Il s'agit d'une application web interactive construite avec **Streamlit** et **Plotly**, permettant d'explorer, de visualiser et d'analyser les données de consommation et de production d'électricité des régions françaises.

## 🎯 Objectifs de l'Application
* **Visualisation cartographique (Choroplèthe) :** Analyser la répartition géographique de la production d'énergie à partir d'un fichier GeoJSON officiel des régions.
* **Analyse temporelle du Mix :** Suivre l'évolution journalière des filières (Nucléaire, Renouvelables, Thermique) sous forme de graphiques en aires empilées.
* **Indicateurs Avancés (Business Intelligence) :** * Calcul de l'**Indice d'Autosuffisance (TCO)** pour isoler les régions excédentaires des régions dépendantes.
  * Suivi du **Taux de Charge (TCH)** pour illustrer la météo-dépendance et la complémentarité des énergies (Solaire/Éolien).
  * Analyse de la balance commerciale électrique via les **Échanges Physiques**.

## 📊 Données utilisées
Les données proviennent de l'**ODRE** (Open Data Réseaux Énergies) et couvrent un historique agrégé à la maille journalière, nettoyé et optimisé en amont avec Python (Pandas).

## 🚀 Structure du Projet
```text
├── app.py                           # Page d'accueil (KPI nationaux globaux)
├── eco2mix_regional_journalier.csv  # Base de données nettoyée
├── requirements.txt                 # Dépendances Python nécessaires au Cloud
└── pages/
    ├── 1_Carte_Interactive.py       # Cartographie interactive des filières
    └── 3_Analyses_Avancees.py       # Onglets TCO, TCH et Échanges physiques
