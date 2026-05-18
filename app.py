import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://vkobxpkysltnycafezen.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZrb2J4cGt5c2x0bnljYWZlemVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkxMTA0MzksImV4cCI6MjA5NDY4NjQzOX0.SgdwxgdfV-CsdiJeSdvX5OUg_UCMMf2hrz8DpsfJZrE"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

if "user" in st.session_state:
    st.success(
        f"Connecté : {st.session_state['user'].email}"
    )

# Authentification
email = st.text_input("Email")
password = st.text_input(
    "Mot de passe",
    type="password"
)

if st.button("Connexion"):
    res = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    st.session_state["session"] = res.session
    st.session_state["user"] = res.user
    
    supabase.auth.set_session(
        access_token=res.session.access_token,
        refresh_token=res.session.refresh_token
    )
    st.success("Connecté")


# Première connexion
if st.button("Créer un compte"):
    res = supabase.auth.sign_up({
        "email": email,
        "password": password
    })
    st.write(res)

if "user" not in st.session_state:
    st.stop()

#Log out
if st.button("Déconnexion"):

    st.session_state.clear()

    supabase.auth.sign_out()

    st.rerun()


# Pioche
if st.button("Piocher une carte"):
    st.write(
            supabase.auth.get_user()
        )
    result = supabase.rpc(
        "pull_card"
    ).execute()

    data = result.data
    if not data["success"]:
        st.error(
            "Limite quotidienne atteinte"
        )
    else:
        card = data["card"]
        st.image(card["image"])
        st.subheader(card["name"])
        st.write(card["rarity"])
        if data["already_owned"]:
            st.warning("Doublon")

        else:
            st.success("Nouvelle carte !")


# Bibliothèque
cards = supabase.table(

    "user_cards"
).select(
    "cards(*)"
).eq(
    "user_id",
    st.session_state["user"].id
).execute()

for item in cards.data:
    card = item["cards"]
    st.image(card["image"])
    st.write(card["name"])
