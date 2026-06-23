import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Eco2mix Dashboard - Analyses Avancées", page_icon="🔬", layout="wide")

# 1. Chargement et préparation des données
df = pd.read_csv('eco2mix_regional_journalier.csv', sep=';', decimal='.', encoding='utf-8-sig')
df['Date'] = pd.to_datetime(df['Date'])
df['Annee'] = df['Date'].dt.year
df['Mois'] = df['Date'].dt.month

# --- BARRE LATÉRALE TRANSVERSE (SYNCHRONISÉE) ---
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

# Synchronisation de la mémoire globale
st.session_state['annee'] = annee
st.session_state['mois_num'] = mois_num
st.session_state['mois_nom'] = dict_mois[mois_num]
st.session_state['region'] = region_choisie

# --- SÉLECTION ET FILTRAGE DU DATAFRAME ---
df_filtre = df[df['Annee'] == annee]
if mois_num != 0:
    df_filtre = df_filtre[df_filtre['Mois'] == mois_num]

st.title("🔬 Analyses Avancées de la Performance Énergétique")
st.subheader(f"Période : {dict_mois[mois_num]} {annee}")

# --- CRÉATION DES ONGLETS ---
tab_tco, tab_tch, tab_echanges = st.tabs([
    "📊 TCO (Couverture / Autosuffisance)", 
    "⚡ TCH (Facteur de Charge & Climat)", 
    "🔌 Échanges Physiques Inter-Régionaux"
])

# ==========================================
# ONGLET 1 : TCO (TAUX DE COUVERTURE)
# ==========================================
with tab_tco:
    st.markdown("### Analyse de l'Autosuffisance et des Taux de Couverture (TCO)")
    
    option_tco = st.selectbox(
        "Sélectionnez la maille d'analyse pour le TCO :",
        ["Indice d'Autosuffisance Global", "TCO Thermique (%)", "TCO Nucleaire (%)", "TCO Eolien (%)", "TCO Solaire (%)", "TCO Hydraulique (%)", "TCO Bioenergies (%)"]
    )
    
    if option_tco == "Indice d'Autosuffisance Global":
        df_tco_calc = df_filtre.groupby('Region').agg({
            'Consommation (MW)': 'sum',
            'Thermique (MW)': 'sum', 'Nucleaire (MW)': 'sum', 'Eolien (MW)': 'sum',
            'Solaire (MW)': 'sum', 'Hydraulique (MW)': 'sum', 'Bioenergies (MW)': 'sum'
        }).reset_index()
        
        df_tco_calc['Prod_Totale'] = df_tco_calc[['Thermique (MW)', 'Nucleaire (MW)', 'Eolien (MW)', 'Solaire (MW)', 'Hydraulique (MW)', 'Bioenergies (MW)']].sum(axis=1)
        df_tco_calc['Indice (%)'] = (df_tco_calc['Prod_Totale'] / df_tco_calc['Consommation (MW)']) * 100
        df_tco_calc = df_tco_calc.sort_values(by='Indice (%)', ascending=False)
        
        fig_tco = px.bar(
            df_tco_calc, x='Indice (%)', y='Region', orientation='h',
            title="Indice d'Autosuffisance Global par Région (Production Totale / Consommation)",
            labels={'Indice (%)': "Taux d'Autosuffisance (%)", 'Region': 'Région'},
            color='Indice (%)', color_continuous_scale="RdYlGn"
        )
        fig_tco.add_vline(x=100, line_dash="dash", line_color="black", annotation_text="Équilibre (100%)")
    else:
        df_tco_filiere = df_filtre.groupby('Region')[option_tco].mean().reset_index().sort_values(by=option_tco, ascending=False)
        fig_tco = px.bar(
            df_tco_filiere, x=option_tco, y='Region', orientation='h',
            title=f"Moyenne du {option_tco} par Région",
            labels={option_tco: f"{option_tco} Moyen", 'Region': 'Région'},
            color=option_tco, color_continuous_scale="Blues"
        )
        
    st.plotly_chart(fig_tco, use_container_width=True)
    
    st.markdown("""
    **💡 Note d'analyse BA :** * Un **Indice supérieur à 100%** indique une région structurellement **excédentaire** (ex: Centre-Val de Loire grâce au nucléaire, Auvergne-Rhône-Alpes grâce au mix Nucléaire/Hydraulique). Elle produit plus qu'elle ne consomme et alimente le réseau national.
    * Un **Indice inférieur à 100%** indique une région **déficitaire/dépendante** (ex: Île-de-France, Provence-Alpes-Côte d'Azur).
    """)

# ==========================================
# ONGLET 2 : TCH (TAUX DE CHARGE ET CLIMAT)
# ==========================================
with tab_tch:
    st.markdown("### Analyse du Taux de Charge (TCH) : Performance face aux aléas climatiques")
    st.write(f"Périmètre temporel : {dict_mois[mois_num]} {annee} — Région sélectionnée : {region_choisie}")
    
    df_tch_chrono = df_filtre if region_choisie == 'Toute la France' else df_filtre[df_filtre['Region'] == region_choisie]
    colonnes_tch = ['TCH Thermique (%)', 'TCH Nucleaire (%)', 'TCH Eolien (%)', 'TCH Solaire (%)', 'TCH Hydraulique (%)', 'TCH Bioenergies (%)']
    
    df_tch_jours = df_tch_chrono.groupby('Date')[colonnes_tch].mean().reset_index()
    df_tch_melted = df_tch_jours.melt(id_vars=['Date'], value_vars=colonnes_tch, var_name='Filière', value_name='Taux de Charge (%)')
    
    fig_tch = px.line(
        df_tch_melted, x='Date', y='Taux de Charge (%)', color='Filière',
        title=f"Évolution quotidienne du Taux de Charge par Filière ({region_choisie})",
        labels={'Taux de Charge (%)': 'TCH (%)', 'Date': 'Date'}
    )
    st.plotly_chart(fig_tch, use_container_width=True)
    
    st.markdown("""
    **📈 Décryptage du Taux de Charge (Métier BA) :**
    Le TCH mesure le ratio entre l'énergie réellement produite et la capacité maximale installée. C'est l'indicateur clé de la **météo-dépendance** :
    * **Le Solaire & l'Éolien :** Ils affichent de fortes variations. En été, le TCH solaire culmine mais l'éolien est souvent au plus bas (anticyclones sans vent). En hiver, c'est l'inverse : le TCH éolien grimpe fortement avec les perturbations de saison, compensant l'absence de soleil.
    * **Le Nucléaire :** Il maintient généralement un TCH élevé et stable (facteur de charge de base), sauf lors des périodes de maintenance programmées ou de canicules (contraintes de refroidissement des fleuves).
    * **Le Thermique :** Son TCH n'est pas lié au climat directement mais sert de **variable d'ajustement**. Il n'augmente que lors des pics de consommation nocturnes ou hivernaux lorsque le renouvelable et le nucléaire ne suffisent plus.
    """)

# ==========================================
# ONGLET 3 : ÉCHANGES PHYSIQUES (MW)
# ==========================================
with tab_echanges:
    st.markdown("### Analyse des Flux et Échanges Physiques d'Électricité (MW)")
    
    df_echanges = df_filtre.groupby('Region')['Ech. physiques (MW)'].mean().reset_index()
    df_echanges = df_echanges.sort_values(by='Ech. physiques (MW)', ascending=True)
    
    df_echanges['Statut Réseau'] = df_echanges['Ech. physiques (MW)'].apply(lambda x: "Exportateur (Injection)" if x < 0 else "Importateur (Soutirage)")
    
    fig_echanges = px.bar(
        df_echanges, x='Ech. physiques (MW)', y='Region', orientation='h',
        color='Statut Réseau',
        color_discrete_map={"Exportateur (Injection)": "#2ecc71", "Importateur (Soutirage)": "#e74c3c"},
        title="Balance Commerciale Électrique : Moyenne des Échanges Physiques par Région",
        labels={'Ech. physiques (MW)': 'Flux Moyen (MW) - Négatif = Donne / Positif = Reçoit', 'Region': 'Région'}
    )
    
    st.plotly_chart(fig_echanges, use_container_width=True)
    
    st.markdown("""
    **🔌 Interprétation des Échanges Physiques :**
    Le réseau électrique fonctionne en flux tendu : la production doit égaler la consommation à chaque seconde.
    * **Valeurs NÉGATIVES (Barres Vertes) :** La région injecte de l'énergie sur le réseau. Elle soutient les autres territoires (ex: Hauts-de-France, Grand Est ou Centre-Val de Loire).
    * **Valeurs POSITIVES (Barres Rouges) :** La région consomme plus qu'elle ne produit localement, elle importe de l'électricité depuis les régions voisines (l'exemple type est l'Île-de-France).
    """)
