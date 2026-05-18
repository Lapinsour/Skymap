import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://vkobxpkysltnycafezen.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZrb2J4cGt5c2x0bnljYWZlemVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkxMTA0MzksImV4cCI6MjA5NDY4NjQzOX0.SgdwxgdfV-CsdiJeSdvX5OUg_UCMMf2hrz8DpsfJZrE"

import streamlit as st
from supabase import create_client

# =========================
# CONFIG
# =========================

#SUPABASE_URL = st.secrets["SUPABASE_URL"]
#SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# =========================
# RESTORE SESSION
# =========================

if (
    "access_token" in st.session_state
    and
    "refresh_token" in st.session_state
):

    supabase.auth.set_session(

        st.session_state["access_token"],
        st.session_state["refresh_token"]

    )

# =========================
# SIDEBAR
# =========================

st.sidebar.title("✦ Skymap")

page = st.sidebar.radio(

    "Navigation",

    [
        "Pioche",
        "Bibliothèque"
    ]
)

# =========================
# AUTH SIDEBAR
# =========================

st.sidebar.divider()

if "user" not in st.session_state:

    st.sidebar.subheader("Connexion")

    email = st.sidebar.text_input(
        "Email"
    )

    password = st.sidebar.text_input(
        "Mot de passe",
        type="password"
    )

    # LOGIN
    if st.sidebar.button("Connexion"):

        try:

            res = supabase.auth.sign_in_with_password({

                "email": email,
                "password": password

            })

            st.session_state["access_token"] = \
                res.session.access_token

            st.session_state["refresh_token"] = \
                res.session.refresh_token

            st.session_state["user"] = \
                res.user

            st.rerun()

        except Exception as e:

            st.sidebar.error(str(e))

    # SIGNUP
    if st.sidebar.button("Créer un compte"):

        try:

            supabase.auth.sign_up({

                "email": email,
                "password": password

            })

            st.sidebar.success(
                "Compte créé."
            )

        except Exception as e:

            st.sidebar.error(str(e))

else:

    st.sidebar.success(

        f"Connecté :\n\n"
        f"{st.session_state['user'].email}"

    )

    if st.sidebar.button("Déconnexion"):

        supabase.auth.sign_out()

        st.session_state.clear()

        st.rerun()

# =========================
# PAGE : PIOCHE
# =========================

if page == "Pioche":

    st.title("🎴 Pioche")

    if "user" not in st.session_state:

        st.info(
            "Connectez-vous."
        )

        st.stop()

    if st.button("Piocher une carte"):

        result = supabase.rpc(
            "pull_card"
        ).execute()

        data = result.data
        
        if not data["success"]:

            st.error(
                "Limite quotidienne atteinte."
            )

        else:

            card = data["card"]
            
            st.image(
                card["image"],
                use_container_width=True
            )

            st.subheader(
                card["name"]
            )

            st.write(
                f"Rareté : {card['rarity']}"
            )

            if data["already_owned"]:

                st.warning(
                    "Doublon"
                )

            else:

                st.success(
                    "Nouvelle carte !"
                )

# =========================
# PAGE : BIBLIOTHÈQUE
# =========================

elif page == "Bibliothèque":       

    st.title("📚 Bibliothèque")
    
    if "user" not in st.session_state:
        st.info("Connectez-vous.")
        st.stop()
        
    
    
    user_cards = supabase.table("user_cards") \
        .select("*") \
        .eq("user_id", st.session_state["user"].id) \
        .execute()

    card_ids = [uc["card_id"] for uc in (user_cards.data or [])]

    if not card_ids:
        st.info("Aucune carte.")
        st.stop()

    cards = supabase.table("cards") \
        .select("*") \
        .in_("card_id", card_ids) \
        .execute()

    cols = st.columns(4)

    for i, card in enumerate(cards.data or []):
        
        path = card["image"].lstrip("/")  # sécurité

        img_url = supabase.storage.from_("cards").get_public_url(card["image"])

        with cols[i % 4]:

            st.markdown(f"""
            <div style="
                border-radius:16px;
                padding:10px;
                background:#111;
                text-align:center;
            ">
                <img src="{img_url}" style="width:100%; border-radius:12px;"/>
                <h4 style="color:white">{card["name"]}</h4>
                <p style="color:gray">{card.get("rarity","")}</p>
            </div>
            """, unsafe_allow_html=True)
