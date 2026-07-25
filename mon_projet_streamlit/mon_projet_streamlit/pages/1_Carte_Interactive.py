import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Eco2mix Dashboard - Carte", page_icon="🗺️", layout="wide")

# --- CHARGEMENT DES FICHIERS ---
@st.cache_data
def load_data():
    df = pd.read_csv('mon_projet_streamlit/eco2mix_regional_journalier.csv', sep=';', decimal='.', encoding='utf-8-sig')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Annee'] = df['Date'].dt.year
    df['Mois'] = df['Date'].dt.month
    return df

df = load_data()

# Chargement du nouveau fichier météo journalier nettoyé
try:
    @st.cache_data
    def load_meteo():
        df_m = pd.read_csv('mon_projet_streamlit/rayonnement-solaire-vitesse-vent-regionaux_journalier.csv', sep=';', encoding='utf-8-sig')
        df_m['Date'] = pd.to_datetime(df_m['Date'])
        df_m['Annee'] = df_m['Date'].dt.year
        df_m['Mois'] = df_m['Date'].dt.month
        return df_m
    df_meteo = load_meteo()
    meteo_dispo = True
except Exception:
    meteo_dispo = False

# ==============================================================================
# --- BARRE LATÉRALE SYNCHRONISÉE (SANS BUG DE DÉCALAGE) ---
# ==============================================================================
st.sidebar.header("🎯 Filtres Globaux")

liste_annees = sorted(df['Annee'].unique(), reverse=True)
dict_mois = {0: "Année complète", 1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin", 
             7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"}
liste_regions = ['Toute la France'] + sorted(list(df['Region'].unique()))

# 1. Initialisation par défaut dans session_state si non existant
if 'annee' not in st.session_state:
    st.session_state['annee'] = liste_annees[0]
if 'mois_num' not in st.session_state:
    st.session_state['mois_num'] = 0
if 'region' not in st.session_state:
    st.session_state['region'] = 'Toute la France'

# 2. Calcul des index dynamiques
idx_annee = liste_annees.index(st.session_state['annee']) if st.session_state['annee'] in liste_annees else 0
idx_mois = list(dict_mois.keys()).index(st.session_state['mois_num']) if st.session_state['mois_num'] in dict_mois else 0
idx_region = liste_regions.index(st.session_state['region']) if st.session_state['region'] in liste_regions else 0

# 3. Callbacks de mise à jour instantanée
def update_annee():
    st.session_state['annee'] = st.session_state['temp_annee']

def update_mois():
    st.session_state['mois_num'] = st.session_state['temp_mois']

def update_region():
    st.session_state['region'] = st.session_state['temp_region']

# 4. Affichage des widgets
annee = st.sidebar.selectbox("Sélectionnez l'année", liste_annees, index=idx_annee, key='temp_annee', on_change=update_annee)
mois_num = st.sidebar.selectbox("Sélectionnez le mois", list(dict_mois.keys()), index=idx_mois, format_func=lambda x: dict_mois[x], key='temp_mois', on_change=update_mois)
region_choisie = st.sidebar.selectbox("Sélectionnez la Région", liste_regions, index=idx_region, key='temp_region', on_change=update_region)

# Mise à jour auxiliaire
st.session_state['mois_nom'] = dict_mois[mois_num]

# URL commune pour les GeoJSON des cartes
geojson_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions-version-simplifiee.geojson"

# --- TITRE PRINCIPAL ET CRÉATION DES ONGLETS ---
st.title("🗺️ Répartition Géographique & Potentiel EnR")
st.subheader(f"Période : {dict_mois[mois_num]} {annee}")

tab_global, tab_focus_enr = st.tabs(["📊 Production Globale", "🌱 Focus Énergies Renouvelables"])

# ==========================================
# ONGLET 1 : PRODUCTION GLOBALE
# ==========================================
with tab_global:
    df_filtre = df[df['Annee'] == annee]
    if mois_num != 0:
        df_filtre = df_filtre[df_filtre['Mois'] == mois_num]

    filiere_carte = st.selectbox(
        "Choisissez la filière énergétique à afficher sur la carte :",
        ['Consommation (MW)', 'Nucleaire (MW)', 'Eolien (MW)', 'Solaire (MW)', 'Hydraulique (MW)', 'Thermique (MW)', 'Bioenergies (MW)']
    )

    df_carte = df_filtre.groupby(['Region', 'Code INSEE region'])[filiere_carte].mean().reset_index()

    if region_choisie != 'Toute la France':
        st.info(f"🔍 Focus actif sur la région : **{region_choisie}**")

    # Dégradé personnalisé : du blanc vers le orange foncé
    degrade_orange = ["#ffffff", "#ffe7cb", "#ffa447", "#f27000", "#b30000"]

    fig_carte = px.choropleth(
        df_carte, geojson=geojson_url, locations='Code INSEE region', featureidkey='properties.code',
        color=filiere_carte, color_continuous_scale=degrade_orange, hover_name='Region',
        labels={filiere_carte: 'Puissance Moyenne (MW)'}
    )
    fig_carte.update_geos(fitbounds="locations", visible=False)
    fig_carte.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=500)
    st.plotly_chart(fig_carte, use_container_width=True)


# ==========================================
# ONGLET 2 : FOCUS ÉNERGIES RENOUVELABLES
# ==========================================
with tab_focus_enr:
    if not meteo_dispo:
        st.error("Le fichier météo journalier n'a pas pu être chargé. Vérifiez son nom, son extension ou l'emplacement racine.")
    else:
        # --- IDÉE 1 : FILTRE DE FILIÈRE ET CARTES CÔTE À CÔTE ---
        st.markdown("### 🗺️ Comparaison Potentiel Météo vs Réalité Énergétique")
        
        choix_enr = st.radio(
            "Choisissez la ressource à analyser :",
            ["☀️ Énergie Solaire", "💨 Énergie Éolienne"],
            horizontal=True
        )
        
        # Filtrage des données pour les cartes selon l'année et le mois
        df_meteo_filtre = df_meteo[df_meteo['Annee'] == annee]
        df_eco_filtre = df[df['Annee'] == annee]
        if mois_num != 0:
            df_meteo_filtre = df_meteo_filtre[df_meteo_filtre['Mois'] == mois_num]
            df_eco_filtre = df_eco_filtre[df_eco_filtre['Mois'] == mois_num]
            
        # Définition des variables dynamiques en fonction du choix
        if choix_enr == "☀️ Énergie Solaire":
            var_meteo = "Rayonnement solaire (W/m2)"
            var_eco = "Solaire (MW)"
            titre_meteo = "Rayonnement Solaire Moyen"
            titre_eco = "Production Solaire Réelle Moyenne"
        else:
            var_meteo = "Vitesse du vent a 100m (m/s)"
            var_eco = "Eolien (MW)"
            titre_meteo = "Vitesse Moyenne du Vent (à 100m)"
            titre_eco = "Production Éolienne Réelle Moyenne"

        # Dégradé personnalisé : du blanc vers le orange foncé
        degrade_orange = ["#ffffff", "#ffe7cb", "#ffa447", "#f27000", "#b30000"]

        # Groupements pour les cartes
        carte_meteo_data = df_meteo_filtre.groupby(['Region', 'Code INSEE region'])[var_meteo].mean().reset_index()
        carte_eco_data = df_eco_filtre.groupby(['Region', 'Code INSEE region'])[var_eco].mean().reset_index()

        # Affichage des deux cartes côte à côte
        col_carte1, col_carte2 = st.columns(2)
        
        with col_carte1:
            st.markdown(f"##### 🌤️ {titre_meteo}")
            fig_m = px.choropleth(
                carte_meteo_data, geojson=geojson_url, locations='Code INSEE region', featureidkey='properties.code',
                color=var_meteo, color_continuous_scale=degrade_orange, hover_name='Region'
            )
            fig_m.update_geos(fitbounds="locations", visible=False)
            fig_m.update_layout(
                margin={"r":0,"t":20,"l":0,"b":0}, 
                height=450,
                coloraxis_colorbar=dict(
                    thickness=15,
                    len=0.7,
                    yanchor="middle",
                    y=0.5
                )
            )
            st.plotly_chart(fig_m, use_container_width=True)
            
        with col_carte2:
            st.markdown(f"##### ⚡ {titre_eco}")
            fig_e = px.choropleth(
                carte_eco_data, geojson=geojson_url, locations='Code INSEE region', featureidkey='properties.code',
                color=var_eco, color_continuous_scale=degrade_orange, hover_name='Region'
            )
            fig_e.update_geos(fitbounds="locations", visible=False)
            fig_e.update_layout(
                margin={"r":0,"t":20,"l":0,"b":0}, 
                height=450,
                coloraxis_colorbar=dict(
                    thickness=15,
                    len=0.7,
                    yanchor="middle",
                    y=0.5
                )
            )
            st.plotly_chart(fig_e, use_container_width=True)

        st.markdown("---")

        # --- IDÉE 2 : GRAPHIQUE TEMPOREL MOIS PAR MOIS AVEC DOUBLE AXE ---
        st.markdown("### 📈 Analyse de la saisonnalité des potentiels")
        
        if region_choisie == "Toute la France":
            st.warning("⚠️ Veuillez sélectionner une région spécifique dans la barre latérale pour observer l'évolution de son potentiel météo.")
        else:
            # Filtrage sur la région choisie et sur l'année complète (pour voir tous les mois)
            graph_meteo_data = df_meteo[(df_meteo['Annee'] == annee) & (df_meteo['Region'] == region_choisie)]
            
            # Calcul des moyennes par mois
            graph_mois = graph_meteo_data.groupby('Mois').agg({
                'Vitesse du vent a 100m (m/s)': 'mean',
                'Rayonnement solaire (W/m2)': 'mean'
            }).reset_index()
            
            # Reconstruction du nom des mois pour l'axe X
            graph_mois['Nom_Mois'] = graph_mois['Mois'].map(dict_mois)
            
            # Création du graphique à double axe avec Graph Objects
            fig_double_axe = go.Figure()
            
            # Courbe 1 : Rayonnement Solaire (Axe Y principal)
            fig_double_axe.add_trace(go.Scatter(
                x=graph_mois['Nom_Mois'],
                y=graph_mois['Rayonnement solaire (W/m2)'],
                name="Rayonnement Solaire (W/m2)",
                line=dict(color='#ff7f0e', width=3),
                yaxis="y"
            ))
            
            # Courbe 2 : Vitesse du vent (Axe Y secondaire)
            fig_double_axe.add_trace(go.Scatter(
                x=graph_mois['Nom_Mois'],
                y=graph_mois['Vitesse du vent a 100m (m/s)'],
                name="Vitesse du vent à 100m (m/s)",
                line=dict(color='#1f77b4', width=3),
                yaxis="y2"
            ))
            
            # Configuration générale de la mise en page
            fig_double_axe.update_layout(
                title=f"Évolution des facteurs de production en {region_choisie} ({annee})",
                xaxis=dict(title="Mois"),
                legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.5)"),
                height=450
            )

            # Configuration de l'axe Y principal (Gauche - Solaire)
            fig_double_axe.update_layout(
                yaxis=dict(
                    title=dict(
                        text="☀️ Rayonnement Solaire (W/m2)",
                        font=dict(color="#ff7f0e")
                    ),
                    tickfont=dict(color="#ff7f0e")
                )
            )

            # Configuration de l'axe Y secondaire (Droite - Vent)
            fig_double_axe.update_layout(
                yaxis2=dict(
                    title=dict(
                        text="💨 Vitesse du Vent (m/s)",
                        font=dict(color="#1f77b4")
                    ),
                    tickfont=dict(color="#1f77b4"),
                    overlaying="y",
                    side="right"
                )
            )
            
            st.plotly_chart(fig_double_axe, use_container_width=True)

        st.markdown("---")

        # --- SUGGESTIONS COMPLÉMENTAIRES ---
        st.markdown("### 💡 Enseignements Business Intelligence (Analyse Métier)")
        
        col_inf1, col_inf2 = st.columns(2)
        with col_inf1:
            st.info("""
            **🤝 Complémentarité des ressources :** En observant le graphique mensuel, vous remarquerez généralement une forte complémentarité : 
            le potentiel éolien est maximal durant les mois d'hiver (période de fortes tensions sur le réseau électrique français), 
            tandis que le potentiel solaire prend naturellement le relais durant la période estivale.
            """)
        with col_inf2:
            st.success("""
            **📈 Analyse d'alignement territorial :**
            En comparant les deux cartes choroplèthes du haut, vérifiez si la couleur intense du potentiel météo (à gauche) correspond à un volume de production élevé (à droite). Si une région est très colorée à gauche mais claire à droite, cela met en évidence un **potentiel de développement inexploité**.
            """)