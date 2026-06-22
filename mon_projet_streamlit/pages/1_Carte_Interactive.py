import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Eco2mix Dashboard - Carte", page_icon="🗺️", layout="wide")

# Chargement rapide
df = pd.read_csv('eco2mix_regional_journalier.csv', sep=';', decimal='.', encoding='utf-8-sig')
df['Date'] = pd.to_datetime(df['Date'])
df['Annee'] = df['Date'].dt.year
df['Mois'] = df['Date'].dt.month

# --- RECRÉATION DE LA BARRE LATÉRALE TRANSVERSE ---
st.sidebar.header("🎯 Filtres Globaux")

liste_annees = sorted(df['Annee'].unique(), reverse=True)
annee_defaut = st.session_state.get('annee', liste_annees[0])
annee = st.sidebar.selectbox("Sélectionnez l'année", liste_annees, index=liste_annees.index(annee_defaut))

dict_mois = {0: "Année complète", 1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin", 
             7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"}
mois_defaut = st.session_state.get('mois_num', 0)
mois_num = st.sidebar.selectbox("Sélectionnez le mois", list(dict_mois.keys()), index=list(dict_mois.keys()).index(mois_defaut), format_func=lambda x: dict_mois[x])

liste_regions = ['Toute la France'] + sorted(list(df['Region'].unique()))
region_defaut = st.session_state.get('region', 'Toute la France')
region_choisie = st.sidebar.selectbox("Sélectionnez la Région", liste_regions, index=liste_regions.index(region_defaut))

# Mise à jour immédiate de la mémoire globale
st.session_state['annee'] = annee
st.session_state['mois_num'] = mois_num
st.session_state['mois_nom'] = dict_mois[mois_num]
st.session_state['region'] = region_choisie

# --- TRAITEMENT CARTE ---
st.title("🗺️ Répartition Géographique de la Production")
st.subheader(f"Période : {dict_mois[mois_num]} {annee}")

df_filtre = df[df['Annee'] == annee]
if mois_num != 0:
    df_filtre = df_filtre[df_filtre['Mois'] == mois_num]

filiere_carte = st.selectbox(
    "Choisissez la filière énergétique à afficher sur la carte :",
    ['Consommation (MW)', 'Nucleaire (MW)', 'Eolien (MW)', 'Solaire (MW)', 'Hydraulique (MW)', 'Thermique (MW)', 'Bioenergies (MW)']
)

df_carte = df_filtre.groupby(['Region', 'Code INSEE region'])[filiere_carte].mean().reset_index()

# Si une région spécifique est filtrée dans la sidebar, on peut ajouter un effet visuel ou la mettre en avant
if region_choisie != 'Toute la France':
    st.info(f"🔍 Focus actif sur la région : **{region_choisie}** (la carte montre toutes les régions pour comparaison).")

geojson_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions-version-simplifiee.geojson"

fig_carte = px.choropleth(
    df_carte, geojson=geojson_url, locations='Code INSEE region', featureidkey='properties.code',
    color=filiere_carte, color_continuous_scale="Viridis", hover_name='Region',
    labels={filiere_carte: 'Puissance Moyenne (MW)'}
)
fig_carte.update_geos(fitbounds="locations", visible=False)
fig_carte.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=600)

st.plotly_chart(fig_carte, use_container_width=True)