import json
import random
import openai
import streamlit as st

st.set_page_config(
    page_title="Démo Quiz RGPD - Personnalisation Secteur", page_icon="🎯"
)

st.title("🎯 Démo : Quiz RGPD Personnalisés par Secteur")
st.write(
    "Testez la génération dynamique d'évaluations adaptées au secteur de vos clients."
)

# Récupération de la clé API via les Secrets Streamlit Cloud
api_key = st.secrets.get("OPENAI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Clé API OpenAI :", type="password")

if not api_key:
    st.info("👈 Veuillez configurer la clé API OpenAI.")
    st.stop()

client = openai.OpenAI(api_key=api_key)

PROGRAMME_6_MODULES = [
    {
        "id": 1,
        "titre": "Module 1: Protection de la vie privée",
        "notion": "Contexte global et cadres réglementaires",
    },
    {
        "id": 2,
        "titre": "Module 2: Nature des données",
        "notion": "Données ordinaires vs sensibles, anonymisation",
    },
    {
        "id": 3,
        "titre": "Module 3: Les 6 règles d'or",
        "notion": "Finalité, minimisation, sécurité, conservation",
    },
    {
        "id": 4,
        "titre": "Module 4: Usages sectoriels",
        "notion": "Bonnes pratiques applicables aux opérations",
    },
    {
        "id": 5,
        "titre": "Module 5: Droits & Responsabilités",
        "notion": "Droits des personnes et obligations des organisations",
    },
    {
        "id": 6,
        "titre": "Module 6: Le GDPR au quotidien",
        "notion": "Vigilance, culture de sécurité, minimisation",
    },
]


def generer_parcours_complet(secteur):
    prompt = f"""
    Tu es un expert e-learning RGPD. Génère un parcours de 6 questions à choix multiples adaptées au secteur "{secteur}".
    
    Pour CHAQUE module ci-dessous, crée 1 mise en situation concrète du secteur avec 3 propositions (1 seule vraie) :
    {json.dumps(PROGRAMME_6_MODULES, ensure_ascii=False)}
    
    Format JSON strict attendu :
    {{
      "questions": [
        {{
          "module_id": 1,
          "titre_module": "Titre du module",
          "scenario": "Court scénario métier...",
          "question": "Question posée ?",
          "options": ["Proposition 1", "Proposition 2", "Proposition 3"],
          "reponse_correcte": 0,
          "explication": "Feedback pédagogique..."
        }}
      ]
    }}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    questions = json.loads(response.choices[0].message.content)["questions"]

    # Mélanger de façon stricte et isolée
    for q in questions:
        options_originales = list(q["options"])
        bonne_reponse_texte = options_originales[q["reponse_correcte"]]
        
        # Mélange des options
        options_melangees = list(options_originales)
        random.shuffle(options_melangees)
        
        q["options"] = options_melangees
        q["reponse_correcte"] = options_melangees.index(bonne_reponse_texte)

    return questions


secteur_choisi = st.selectbox(
    "Sélectionnez le secteur d'activité de l'entreprise cliente :",
    [
        "Santé & Établissements médicaux",
        "BTP & Construction",
        "Immobilier & Promotion",
        "Grande Distribution & E-commerce",
        "Banque & Assurance",
        "Transport & Logistique",
    ],
)

if st.button("🚀 Générer le parcours de 6 quiz", type="primary"):
    with st.spinner("Génération des 6 questions sur mesure par l'IA..."):
        st.session_state["quiz_data"] = generer_parcours_complet(secteur_choisi)
        st.session_state["etape"] = 0
        st.session_state["score"] = 0
        st.session_state["repondu"] = False

if "quiz_data" in st.session_state:
    questions = st.session_state["quiz_data"]
    i = st.session_state["etape"]

    if i < len(questions):
        q = questions[i]
        st.divider()
        st.caption(f"Question {i+1}/6 — {q['titre_module']}")
        st.subheader(q["scenario"])
        st.write(f"**{q['question']}**")

        if not st.session_state.get("repondu", False):
            choix = st.radio(
                "Choisissez votre réponse :",
                q["options"],
                index=None,
                key=f"q_{i}"
            )

            if st.button("Valider la réponse"):
                if choix is None:
                    st.warning("⚠️ Veuillez sélectionner une option avant de valider.")
                else:
                    index_choisi = q["options"].index(choix)
                    st.session_state["dernier_choix"] = index_choisi
                    st.session_state["repondu"] = True
                    if index_choisi == q["reponse_correcte"]:
                        st.session_state["score"] += 1
                    st.rerun()

        else:
            index_choisi = st.session_state["dernier_choix"]
            
            # Afficher le choix fait
            for idx, opt in enumerate(q["options"]):
                if idx == q["reponse_correcte"]:
                    st.markdown(f"✅ **{opt}** *(Bonne réponse)*")
                elif idx == index_choisi:
                    st.markdown(f"❌ **{opt}** *(Votre choix)*")
                else:
                    st.markdown(f"⚪ {opt}")

            st.write("")
            if index_choisi == q["reponse_correcte"]:
                st.success("✅ Excellent !")
            else:
                st.error("❌ Incorrect.")

            st.info(f"💡 **Explication :** {q['explication']}")

            if st.button("Question suivante ➡️"):
                st.session_state["etape"] += 1
                st.session_state["repondu"] = False
                st.rerun()

    else:
        st.divider()
        st.balloons()
        st.success(
            f"🎉 **Parcours terminé !** Score final : {st.session_state['score']}/6"
        )
        if st.button("Recommencer une démonstration"):
            del st.session_state["quiz_data"]
            st.rerun()
