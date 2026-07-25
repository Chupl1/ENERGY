import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Eco2mix Dashboard - Analyse Mix", page_icon="📈", layout="wide")

# --- CHARGEMENT DES FICHIERS ---
@st.cache_data
def load_data():
    df = pd.read_csv('mon_projet_streamlit/eco2mix_regional_journalier.csv', sep=';', decimal='.', encoding='utf-8-sig')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Annee'] = df['Date'].dt.year
    df['Mois'] = df['Date'].dt.month
    return df

df = load_data()

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

# --- SÉLECTION & GRAPH_MIX ---
st.title("📈 Analyse Évolution temporelle et Mix Énergétique")
st.subheader(f"Période : {dict_mois[mois_num]} {annee} — Périmètre : {region_choisie}")

df_filtre = df[df['Annee'] == annee]
if mois_num != 0:
    df_filtre = df_filtre[df_filtre['Mois'] == mois_num]

if region_choisie != 'Toute la France':
    df_chrono = df_filtre[df_filtre['Region'] == region_choisie]
else:
    df_chrono = df_filtre

filieres = ['Thermique (MW)', 'Nucleaire (MW)', 'Eolien (MW)', 'Solaire (MW)', 'Hydraulique (MW)', 'Bioenergies (MW)']
df_chrono_jours = df_chrono.groupby('Date')[['Consommation (MW)'] + filieres].mean().reset_index()

st.markdown("### 📊 Évolution quotidienne du Mix Énergétique de Production")
df_melted = df_chrono_jours.melt(id_vars=['Date'], value_vars=filieres, var_name='Filière Énergétique', value_name='Production (MW)')

fig_mix = px.area(
    df_melted, x='Date', y='Production (MW)', color='Filière Énergétique',
    labels={'Production (MW)': 'Puissance (MW)', 'Date': 'Date'},
    color_discrete_sequence=px.colors.qualitative.Safe
)
st.plotly_chart(fig_mix, use_container_width=True)

st.write("---")
st.markdown("### 🎯 Focus sur la Production Cumulée vs Consommation Globale")

# 1. Sélection des filières à cumuler via les cases à cocher
filieres_selectionnees = st.multiselect(
    "Sélectionnez une ou plusieurs filières à additionner pour la courbe de production :",
    options=filieres,
    default=[filieres[0]]  # Pré-sélectionne la première filière par défaut
)

# 2. Calcul de la limite max de l'axe Y pour garder une échelle fixe et stable
max_conso = df_chrono_jours['Consommation (MW)'].max()
Y_limite_max = max_conso * 1.15

# 3. Création d'un dataframe temporaire pour construire notre graphique à 2 courbes
df_double_courbe = pd.DataFrame({'Date': df_chrono_jours['Date']})

# On garde la consommation globale intacte (Courbe 1)
df_double_courbe['Consommation Globale (MW)'] = df_chrono_jours['Consommation (MW)']

# On calcule la somme des productions sélectionnées (Courbe 2)
if filieres_selectionnees:
    # .sum(axis=1) permet d'additionner les colonnes cochées pour chaque ligne (chaque jour)
    df_double_courbe['Production Sélectionnée (MW)'] = df_chrono_jours[filieres_selectionnees].sum(axis=1)
else:
    # Si l'utilisateur décoche tout, la production cumulée est à 0
    df_double_courbe['Production Sélectionnée (MW)'] = 0

# 4. Génération du graphique avec strictement ces 2 colonnes
courbes_a_afficher = ['Consommation Globale (MW)', 'Production Sélectionnée (MW)']

fig_focus = px.line(
    df_double_courbe, 
    x='Date', 
    y=courbes_a_afficher,
    labels={'value': 'Puissance (MW)', 'Date': 'Date', 'variable': 'Indicateur'},
    color_discrete_map={
        'Consommation Globale (MW)': '#FF9900',         # Consommation en orange
        'Production Sélectionnée (MW)': '#2ecc71'       # Production cumulée en vert
    }
)

# 5. Ajustement du style et verrouillage de l'échelle à 0
fig_focus.update_traces(line=dict(width=3))  # Rend les courbes bien visibles
fig_focus.update_layout(
    yaxis=dict(range=[0, Y_limite_max]),  # Échelle bloquée à 0
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_focus, use_container_width=True)

# Petit message d'aide à la décision contextuel pour votre mémoire
if filieres_selectionnees:
    noms_propres = [f.replace(" (MW)", "") for f in filieres_selectionnees]
    st.info(f"💡 **Interprétation :** La courbe verte représente la production cumulée de : **{', '.join(noms_propres)}**.")