import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page principale (renommée pour l'expérience utilisateur)
st.set_page_config(page_title="Eco2mix Dashboard - Home", page_icon="🏠", layout="wide")

st.title("🏠 Accueil — Analyse Éco2mix du Mix Énergétique")
st.subheader("Outil de Business Intelligence & d'Aide à la Décision")

# Chargement des données avec le chemin réseau configuré
@st.cache_data
def load_data():
    df = pd.read_csv('mon_projet_streamlit/eco2mix_regional_journalier.csv', sep=';', decimal='.', encoding='utf-8-sig')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Annee'] = df['Date'].dt.year
    df['Mois'] = df['Date'].dt.month
    return df

df = load_data()

# --- BARRE LATÉRALE COMMUNE ---
st.sidebar.header("🎯 Filtres Globaux")

liste_annees = sorted(df['Annee'].unique(), reverse=True)
annee_session = st.session_state.get('annee', liste_annees[0])
idx_annee = liste_annees.index(annee_session) if annee_session in liste_annees else 0
annee_choisie = st.sidebar.selectbox("Sélectionnez l'année", liste_annees, index=idx_annee)

dict_mois = {0: "Année complète", 1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin", 
             7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"}
mois_session = st.session_state.get('mois_num', 0)
idx_mois = list(dict_mois.keys()).index(mois_session) if mois_session in dict_mois else 0
mois_choisi_num = st.sidebar.selectbox("Sélectionnez le mois", list(dict_mois.keys()), index=idx_mois, format_func=lambda x: dict_mois[x])

liste_regions = ['Toute la France'] + sorted(list(df['Region'].unique()))
region_session = st.session_state.get('region', 'Toute la France')
idx_region = liste_regions.index(region_session) if region_session in liste_regions else 0
region_choisie = st.sidebar.selectbox("Sélectionnez la Région", liste_regions, index=idx_region)

# Sauvegarde globale
st.session_state['annee'] = annee_choisie
st.session_state['mois_num'] = mois_choisi_num
st.session_state['mois_nom'] = dict_mois[mois_choisi_num]
st.session_state['region'] = region_choisie

# --- SÉLECTION DES DONNÉES FILTRÉES ---
df_filtre = df[(df['Annee'] == annee_choisie)]
if mois_choisi_num != 0:
    df_filtre = df_filtre[df_filtre['Mois'] == mois_choisi_num]
if region_choisie != 'Toute la France':
    df_filtre = df_filtre[df_filtre['Region'] == region_choisie]

# ==============================================================================
# STRUCTURE DES ONGLETS DE LA PAGE D'ACCUEIL
# ==============================================================================
tab_contexte, tab_kpi, tab_filières = st.tabs(["📊 Contexte Économique", "📈 Chiffres Clés du Territoire", "⚡ Guide des Filières"])

with tab_contexte:
    st.markdown("### 💸 Les Enjeux Économiques de l'Électricité en France")
    
    col_txt, col_stats = st.columns([2, 1])
    
    with col_txt:
        st.write("""
        L'analyse du mix énergétique est au cœur des enjeux stratégiques et industriels de la France. 
        Suivre en temps réel la production et la consommation permet d'anticiper les tensions sur le réseau, 
        d'optimiser l'indépendance énergétique et de piloter les coûts financiers.
        
        **Quelques chiffres clés du marché macroéconomique français :**
        * **Une facture nationale majeure :** Selon les données officielles du Ministère de la Transition Énergétique (SDES), la dépense finale globale liée à la seule consommation d'électricité s'est élevée à **85 milliards d'euros** sur une année (portée par l'ajustement des prix de marché).
        * **Volume annuel :** La consommation brute française s'établit historiquement autour de **440 à 450 TWh** par an (Source : RTE).
        * **Levier à l'exportation (ROI) :** Grâce à un parc de production bas-carbone hautement compétitif (coûts marginaux faibles), la France enregistre régulièrement des records d'échanges extérieurs, dégageant un solde net d'exportations supérieur à **90 TWh** (générant plusieurs milliards d'euros de bénéfices pour la balance commerciale du pays).
        """)
    
    with col_stats:
        st.info("""
        🎯 **Objectif de l'application**
        En tant que Business Analyst, ce tableau de bord vous permet de croiser l'indicateur de consommation avec les rendements régionaux afin d'identifier la rentabilité, l'autosuffisance (TCO) et la flexibilité de notre mix énergétique.
        """)

with tab_kpi:
    st.markdown(f"### 📊 Indicateurs de Performance — **{region_choisie}**")
    
    # --- CALCULS PRÉCIS BI (Variables locales filtrées par la barre latérale) ---
    puissance_conso_moyenne = df_filtre['Consommation (MW)'].sum() / 1000
    prod_nucleaire = df_filtre['Nucleaire (MW)'].sum() / 1000
    prod_renouvelable = (df_filtre['Eolien (MW)'].sum() + df_filtre['Solaire (MW)'].sum() + 
                         df_filtre['Hydraulique (MW)'].sum() + df_filtre['Bioenergies (MW)'].sum()) / 1000
    prod_totale = prod_nucleaire + prod_renouvelable + (df_filtre['Thermique (MW)'].sum() / 1000)
    energie_consommee_gwh = (df_filtre['Consommation (MW)'].sum() * 24) / 1000

    # Affichage des KPIs du filtre courant
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.metric(
            label="🔋 Énergie Totale Consommée (GWh)", 
            value=f"{energie_consommee_gwh:,.0f}".replace(',', ' '),
            help="Volume total d'énergie consommé sur la période choisie (Puissance en MW x 24h)."
        )
    with col_v2:
        st.metric(
            label="🔌 Puissance Appelée Moyenne (GW)", 
            value=f"{puissance_conso_moyenne:,.1f}".replace(',', ' '),
            help="Moyenne de la puissance appelée instantanément sur le réseau."
        )
        
    st.write("---")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric(label="⚛️ Part du Nucléaire dans la Production", value=f"{(prod_nucleaire/prod_totale)*100:.1f} %" if prod_totale > 0 else "0 %")
    with col_m2:
        st.metric(label="🌱 Part des Énergies Renouvelables", value=f"{(prod_renouvelable/prod_totale)*100:.1f} %" if prod_totale > 0 else "0 %")
        
    st.write("---")
    
    # ==============================================================================
    # 📈 ANALYSE MACRO-HISTORIQUE (Ignore les filtres Année/Mois, garde uniquement Région)
    # ==============================================================================
    st.markdown(f"### ⏳ Évolution Historique Annuelle — **{region_choisie}**")
    st.caption("Note : Ces graphiques affichent l'ensemble de l'historique de vos données pour la région sélectionnée.")

    # 1. Préparation du jeu de données historique (Filtré UNIQUEMENT par région)
    if region_choisie != 'Toute la France':
        df_historique = df[df['Region'] == region_choisie]
    else:
        df_historique = df

    # 2. Agrégation annuelle globale
    df_annuel = df_historique.groupby('Annee').agg({
        'Consommation (MW)': lambda x: (x.sum() * 24) / 1000,
        'Nucleaire (MW)': lambda x: (x.sum() * 24) / 1000,
        'Eolien (MW)': lambda x: (x.sum() * 24) / 1000,
        'Solaire (MW)': lambda x: (x.sum() * 24) / 1000,
        'Hydraulique (MW)': lambda x: (x.sum() * 24) / 1000,
        'Bioenergies (MW)': lambda x: (x.sum() * 24) / 1000,
        'Thermique (MW)': lambda x: (x.sum() * 24) / 1000
    }).reset_index()

    # Rénommage propre pour le premier graphique
    df_annuel = df_annuel.rename(columns={'Consommation (MW)': 'Consommation Annuelle (GWh)'})

    # Calcul des parts en % pour le second graphique
    df_annuel['Production_Totale_GWh'] = (
        df_annuel['Nucleaire (MW)'] + df_annuel['Eolien (MW)'] + 
        df_annuel['Solaire (MW)'] + df_annuel['Hydraulique (MW)'] + 
        df_annuel['Bioenergies (MW)'] + df_annuel['Thermique (MW)']
    )
    
    df_annuel['Part Nucléaire (%)'] = (df_annuel['Nucleaire (MW)'] / df_annuel['Production_Totale_GWh']) * 100
    df_annuel['Part Renouvelables (%)'] = (
        (df_annuel['Eolien (MW)'] + df_annuel['Solaire (MW)'] + 
         df_annuel['Hydraulique (MW)'] + df_annuel['Bioenergies (MW)']) / df_annuel['Production_Totale_GWh']
    ) * 100

    # --- GRAPHIQUE 1 : Évolution de la consommation annuelle ---
    fig_hist_conso = px.bar(
        df_annuel, 
        x='Annee', 
        y='Consommation Annuelle (GWh)',
        title="Évolution du Volume de Consommation Annuelle Globale",
        labels={'Annee': 'Année', 'Consommation Annuelle (GWh)': 'Énergie (GWh)'},
        color_discrete_sequence=['#34495e']
    )
    fig_hist_conso.update_layout(xaxis=dict(type='category'))
    st.plotly_chart(fig_hist_conso, use_container_width=True)

    # --- GRAPHIQUE 2 : Évolution de la structure du Mix ---
    df_mix_evolution = df_annuel.melt(
        id_vars=['Annee'], 
        value_vars=['Part Nucléaire (%)', 'Part Renouvelables (%)'],
        var_name='Indicateur', 
        value_name='Proportion (%)'
    )

    fig_hist_mix = px.line(
        df_mix_evolution, 
        x='Annee', 
        y='Proportion (%)', 
        color='Indicateur',
        title="Transition Énergétique : Évolution des Parts de Production",
        labels={'Annee': 'Année', 'Proportion (%)': 'Part dans le mix (%)'},
        color_discrete_map={
            'Part Nucléaire (%)': '#9b59b6',
            'Part Renouvelables (%)': '#2ecc71'
        },
        markers=True
    )
    fig_hist_mix.update_layout(
        xaxis=dict(type='category'),
        yaxis=dict(range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_hist_mix, use_container_width=True)
        
with tab_filières:
    st.markdown("### 🔍 Comprendre les Énergies de notre Mix Énergétique")
    st.write("Découvrez les spécificités techniques, les points forts et les limites opérationnelles de chaque filière :")
    
    # Sous-onglets pour chaque filière
    sub_nuc, sub_eol, sub_sol, sub_hyd, sub_therm, sub_bio = st.tabs([
        "⚛️ Nucléaire", "💨 Éolien", "☀️ Solaire", "💧 Hydraulique", "🔥 Thermique", "🌱 Bioénergies"
    ])
    
    with sub_nuc:
        st.subheader("⚛️ Énergie Nucléaire")
        
        # --- PARTIE SUPÉRIEURE : IMAGE À GAUCHE & TEXTE CENTRÉ VERTICALEMENT ---
        # vertical_alignment="center" permet d'aligner le texte au milieu de la hauteur de l'image
        col_img, col_texte = st.columns([1, 2], vertical_alignment="center") 
        
        with col_img:
            # L'image est maintenant placée dans la première colonne (à gauche)
            st.image("images/nucleaire.jpg", use_container_width=True)
            
        with col_texte:
            # Le texte s'affichera à droite, parfaitement aligné au milieu du bloc
            st.markdown("**🌐 Fonctionnement :** Fission d'atomes d'uranium générant une chaleur intense. Cette chaleur transforme l'eau en vapeur, qui fait tourner une turbine couplée à un alternateur produisant de l'électricité.")
        
        # Espace pour aérer avant les blocs d'avantages/inconvénients
        st.write("") 
        
        # --- PARTIE INFÉRIEURE : AVANTAGES & INCONVÉNIENTS ---
        col_av, col_inc = st.columns(2)
        with col_av:
            st.success("""
            **👍 Avantages :**
            * **Décarboné :** Quasiment aucune émission de CO2 en phase d'exploitation.
            * **Pilotable & Stable :** Production massive en continu (énergie de base), indépendante de la météo.
            * **Compétitif :** Faibles coûts marginaux de production.
            """)
        with col_inc:
            st.error("""
            **👎 Inconvénients / Contraintes :**
            * **Inertie :** Faible flexibilité pour répondre instantanément aux pics de consommation soudains.
            * **Déchets & Risques :** Gestion des déchets radioactifs à long terme et exigences de sûreté maximales.
            * **Dépendance hydrique :** Nécessite un refroidissement constant (fleuves ou mer).
            """)
        
    with sub_eol:
        st.subheader("💨 Énergie Éolienne")
        
        # --- PARTIE SUPÉRIEURE : IMAGE À GAUCHE & TEXTE CENTRÉ VERTICALEMENT ---
        col_img, col_texte = st.columns([1, 2], vertical_alignment="center")
        
        with col_img:
            st.image("images/eolien.jpg", use_container_width=True)
            
        with col_texte:
            st.markdown("**🌐 Fonctionnement :** Utilisation de la force cinétique du vent pour entraîner un rotor et activer un générateur électrique situé dans la nacelle au sommet du mât.")
            
        st.write("") # Espace de respiration visuelle
        
        # --- PARTIE INFÉRIEURE : AVANTAGES & INCONVÉNIENTS ---
        col_av, col_inc = st.columns(2)
        with col_av:
            st.success("""
            **👍 Avantages :**
            * **Renouvelable & Propre :** Énergie verte sans émissions directes de gaz à effet de serre ni déchets.
            * **Empreinte au sol réduite :** Permet la cohabitation avec des activités agricoles ou marines (offshore).
            * **Installation rapide :** Déploiement plus agile que les centrales traditionnelles.
            """)
        with col_inc:
            st.error("""
            **👎 Inconvénients / Contraintes :**
            * **Intermittence :** Production dépendante de la vitesse du vent (besoin de relais).
            * **Plage de marche :** S'arrête si le vent est trop faible (< 15 km/h) ou trop fort (> 90 km/h par sécurité).
            * **Variabilité :** Facteur de charge saisonnier difficile à planifier précisément.
            """)
        
    with sub_sol:
        st.subheader("☀️ Énergie Solaire Photovoltaïque")
        
        # --- PARTIE SUPÉRIEURE : IMAGE À GAUCHE & TEXTE CENTRÉ VERTICALEMENT ---
        col_img, col_texte = st.columns([1, 2], vertical_alignment="center")
        
        with col_img:
            st.image("images/solaire.jpg", use_container_width=True)
            
        with col_texte:
            st.markdown("**🌐 Fonctionnement :** Conversion directe des photons de la lumière en courant électrique via des cellules de silicium.")
            
        st.write("") # Espace de respiration visuelle
        
        # --- PARTIE INFÉRIEURE : AVANTAGES & INCONVÉNIENTS ---
        col_av, col_inc = st.columns(2)
        with col_av:
            st.success("""
            **👍 Avantages :**
            * **Abondant & Accessible :** Ressource disponible partout, idéale pour l'autoconsommation.
            * **Modularité :** S'installe aussi bien sur des toitures résidentielles que dans de grands parcs au sol.
            * **Maintenance faible :** Absence de pièces mobiles, limitant l'usure mécanique.
            """)
        with col_inc:
            st.error("""
            **👎 Inconvénients / Contraintes :**
            * **Intermittence totale :** Production nulle la nuit et fortement réduite en hiver ou par temps couvert.
            * **Densité énergétique :** Nécessite de grandes surfaces pour une production industrielle.
            * **Sensibilité thermique :** Le rendement des panneaux diminue paradoxalement lors des fortes canicules.
            """)
        
    with sub_hyd:
            st.subheader("💧 Énergie Hydraulique")
            
            # --- PARTIE SUPÉRIEURE : IMAGE À GAUCHE & TEXTE CENTRÉ VERTICALEMENT ---
            col_img, col_texte = st.columns([1, 2], vertical_alignment="center")
            with col_img:
                st.image("images/hydraulique.jpg", use_container_width=True)
            with col_texte:
                st.markdown("**🌐 Fonctionnement :** Force de l'eau (barrages ou fil de l'eau) acheminée vers des conduites pour actionner des turbines.")
                
            st.write("") # Espace de respiration visuelle
            
            # --- PARTIE INFÉRIEURE : AVANTAGES & INCONVÉNIENTS ---
            col_av, col_inc = st.columns(2)
            with col_av:
                st.success("""
                **👍 Avantages :**
                * **Stockable & Ultra-flexible :** Seule énergie renouvelable majeure capable de démarrer en quelques minutes (gestion des pics).
                * **Rendement élevé :** Conversion énergétique très efficace.
                * **Stockage de masse :** Les STEP (stations de pompage) permettent de stocker l'excédent des autres énergies.
                """)
            with col_inc:
                st.error("""
                **👎 Inconvénients / Contraintes :**
                * **Dépendance climatique :** Sensible aux sécheresses prolongées et à la baisse du niveau des cours d'eau.
                * **Limites géographiques :** Potentiel de développement maximal quasiment atteint en France.
                * **Impact environnemental :** Modification locale des écosystèmes aquatiques lors de la création de grands barrages.
                """)
                
    with sub_therm:
        st.subheader("🔥 Énergie Thermique Fossile")
        
        # --- PARTIE SUPÉRIEURE : IMAGE À GAUCHE & TEXTE CENTRÉ VERTICALEMENT ---
        col_img, col_texte = st.columns([1, 2], vertical_alignment="center")
        with col_img:
            st.image("images/thermique.jpg", use_container_width=True)
        with col_texte:
            st.markdown("**🌐 Fonctionnement :** Combustion de gaz, charbon ou fioul pour produire une vapeur haute pression entraînant une turbine.")
            
        st.write("") # Espace de respiration visuelle
        
        # --- PARTIE INFÉRIEURE : AVANTAGES & INCONVÉNIENTS ---
        col_av, col_inc = st.columns(2)
        with col_av:
            st.success("""
            **👍 Avantages :**
            * **Extrêmement flexible :** Démarrage rapide, idéal comme variable d'ajustement ultime lors des pointes hivernales.
            * **Indépendant de la météo :** Disponible sur demande 24h/24 et 7j/7 tant que le combustible est disponible.
            """)
        with col_inc:
            st.error("""
            **👎 Inconvénients / Contraintes :**
            * **Émetteur de CO2 :** Très fort impact carbone, à contre-courant des objectifs de transition énergétique.
            * **Coûts volatils :** Dépendance directe vis-à-vis des prix mondiaux des matières premières (marché du gaz).
            * **Ressource finie :** Utilisation de stocks fossiles non renouvelables.
            """)
            
    with sub_bio:
        st.subheader("🌱 Bioénergies")
        
        # --- PARTIE SUPÉRIEURE : IMAGE À GAUCHE & TEXTE CENTRÉ VERTICALEMENT ---
        col_img, col_texte = st.columns([1, 2], vertical_alignment="center")
        with col_img:
            st.image("images/bioenergies.jpg", use_container_width=True)
        with col_texte:
            st.markdown("**🌐 Fonctionnement :** Valorisation de matières organiques (biomasse solide, incinération de déchets ou biogaz) par combustion.")
            
        st.write("") # Espace de respiration visuelle
        
        # --- PARTIE INFÉRIEURE : AVANTAGES & INCONVÉNIENTS ---
        col_av, col_inc = st.columns(2)
        with col_av:
            st.success("""
            **👍 Avantages :**
            * **Pilotable :** Production stable, programmable et non soumise aux aléas de la météo.
            * **Économie circulaire :** Permet de valoriser les déchets ménagers, agricoles et forestiers locaux.
            * **Bilan carbone neutre (théorique) :** Le CO2 émis équivaut à celui absorbé par la plante durant sa croissance.
            """)
        with col_inc:
            st.error("""
            **👎 Inconvénients / Contraintes :**
            * **Logistique complexe :** Dépendance à la régularité et à la saisonnalité des flux d'approvisionnement en intrants.
            * **Rendement modéré :** Efficacité énergétique globale inférieure à celle d'autres filières thermiques.
            * **Conflits d'usage :** Concurrence possible avec les terres agricoles alimentaires pour certaines cultures énergétiques.
            """)
