# ⚡ Dashboard Éco2mix & Météo - Analyse du Mix Énergétique Régional

Ce projet a été développé dans le cadre de mon mémoire de fin d'études de **Business Analyst**. Il s'agit d'une application web interactive construite avec **Streamlit** et **Plotly**, permettant d'explorer, de visualiser et d'analyser les données de consommation, de production d'électricité et de potentiel météorologique des régions françaises.

## 🎯 Objectifs de l'Application
* **Visualisation cartographique (Choroplèthe) :** Analyser la répartition géographique de la production d'énergie à partir d'un fichier GeoJSON officiel des régions.
* **Focus Énergies Renouvelables & Potentiel Météo :** Croiser la réalité de la production solaire et éolienne avec les facteurs climatiques (rayonnement solaire en $\text{W/m}^2$ et vitesse du vent à 100m en $\text{m/s}$) pour identifier les gisements d'énergie inexploités et la saisonnalité des ressources.
* **Analyse temporelle du Mix :** Suivre l'évolution journalière des filières (Nucléaire, Renouvelables, Thermique) sous forme de graphiques en aires empilées et comparer la production cumulée à la consommation globale.
* **Indicateurs Avancés (Business Intelligence) :** 
  * Calcul de l'**Indice d'Autosuffisance (TCO)** pour isoler les régions excédentaires des régions dépendantes.
  * Suivi du **Taux de Charge (TCH)** pour illustrer la météo-dépendance et la complémentarité des énergies (Solaire/Éolien).
  * Analyse de la balance commerciale électrique via les **Échanges Physiques inter-régionaux**.

## 📊 Données utilisées
Les données proviennent de deux sources principales, agrégées à la maille journalière, nettoyées et optimisées en amont avec Python (**Pandas**) :
1. **ODRE (Open Data Réseaux Énergies) :** Données de production, de consommation, d'échanges physiques, de TCO et de TCH par région.
2. **Données Météorologiques Régionales :** Relevés de rayonnement solaire et de vitesse du vent à 100m de hauteur pour l'analyse du potentiel EnR.

## 🚀 Structure du Projet
```text
├── Home.py                                                     # Page d'accueil (KPI nationaux globaux & fiches filières)
├── eco2mix_regional_journalier.csv                             # Base de données nettoyée - Production & Consommation d'énergie
├── rayonnement-solaire-vitesse-vent-regionaux_journalier.csv   # Base de données nettoyée - Vent (100m) & Rayonnement solaire
├── requirements.txt                                            # Dépendances Python nécessaires au déploiement Cloud
└── pages/
    ├── 1_Carte_Interactive.py                                  # Cartographie interactive & Focus Potentiel EnR vs Météo
    ├── 2_Analyse_Mix.py                                        # Évolution temporelle, mix énergétique & focus production/conso
    └── 3_Analyses_Avancees.py                                  # Onglets TCO (Autosuffisance), TCH (Facteur de charge) & Échanges
└── images/
    ├── bioenergies.jpg                                         # Illustration de la filière
    ├── eolien.jpg                                              # Illustration de la filière
    ├── hydraulique.jpg                                         # Illustration de la filière
    ├── nucleaire.jpg                                           # Illustration de la filière
    ├── solaire.jpg                                             # Illustration de la filière
    └── thermique.jpg                                           # Illustration de la filière
