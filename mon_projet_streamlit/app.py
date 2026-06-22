import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Eco2mix Dashboard - Accueil", page_icon="⚡", layout="wide")

st.title("⚡ Analyse Éco2mix du Mix Énergétique Régional")
st.subheader("Outil d'aide à la décision et d'analyse pour Business Analyst")

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv('eco2mix_regional_journalier.csv', sep=';', decimal='.', encoding='utf-8-sig')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Annee'] = df['Date'].dt.year
    df['Mois'] = df['Date'].dt.month
    return df

df = load_data()

# --- BARRE LATÉRALE COMMUNE (Avec lecture de la mémoire globale) ---
st.sidebar.header("🎯 Filtres Globaux")

# 1. Filtre Année (on cherche s'il y a un choix existant dans la session, sinon index 0)
liste_annees = sorted(df['Annee'].unique(), reverse=True)
annee_session = st.session_state.get('annee', liste_annees[0])
idx_annee = liste_annees.index(annee_session) if annee_session in liste_annees else 0
annee_choisie = st.sidebar.selectbox("Sélectionnez l'année", liste_annees, index=idx_annee)

# 2. Filtre Mois
dict_mois = {0: "Année complète", 1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin", 
             7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"}
mois_session = st.session_state.get('mois_num', 0)
idx_mois = list(dict_mois.keys()).index(mois_session) if mois_session in dict_mois else 0
mois_choisi_num = st.sidebar.selectbox("Sélectionnez le mois", list(dict_mois.keys()), index=idx_mois, format_func=lambda x: dict_mois[x])

# 3. Filtre Région
liste_regions = ['Toute la France'] + sorted(list(df['Region'].unique()))
region_session = st.session_state.get('region', 'Toute la France')
idx_region = liste_regions.index(region_session) if region_session in liste_regions else 0
region_choisie = st.sidebar.selectbox("Sélectionnez la Région", liste_regions, index=idx_region)

# Sauvegarde/Mise à jour immédiate dans la session globale
st.session_state['annee'] = annee_choisie
st.session_state['mois_num'] = mois_choisi_num
st.session_state['mois_nom'] = dict_mois[mois_choisi_num]
st.session_state['region'] = region_choisie

# --- SÉLECTION DES DONNÉES FILTRÉES POUR L'ACCUEIL ---
df_filtre = df[(df['Annee'] == annee_choisie)]
if mois_choisi_num != 0:
    df_filtre = df_filtre[df_filtre['Mois'] == mois_choisi_num]
if region_choisie != 'Toute la France':
    df_filtre = df_filtre[df_filtre['Region'] == region_choisie]

# --- AFFICHAGE ---
st.markdown(f"### 📊 Chiffres clés — **{region_choisie} ({dict_mois[mois_choisi_num]} {annee_choisie})**")

# Calcul KPI
conso_totale = df_filtre['Consommation (MW)'].sum() / 1000
prod_nucleaire = df_filtre['Nucleaire (MW)'].sum() / 1000
prod_renouvelable = (df_filtre['Eolien (MW)'].sum() + df_filtre['Solaire (MW)'].sum() + 
                     df_filtre['Hydraulique (MW)'].sum() + df_filtre['Bioenergies (MW)'].sum()) / 1000
prod_totale = prod_nucleaire + prod_renouvelable + (df_filtre['Thermique (MW)'].sum() / 1000)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Consommation Cumulée (GW)", value=f"{conso_totale:,.1f}".replace(',', ' '))
with col2:
    st.metric(label="Part du Nucléaire", value=f"{(prod_nucleaire/prod_totale)*100:.1f} %" if prod_totale > 0 else "0 %")
with col3:
    st.metric(label="Part des Énergies Renouvelables", value=f"{(prod_renouvelable/prod_totale)*100:.1f} %" if prod_totale > 0 else "0 %")