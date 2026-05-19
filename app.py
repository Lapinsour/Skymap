import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://vkobxpkysltnycafezen.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZrb2J4cGt5c2x0bnljYWZlemVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkxMTA0MzksImV4cCI6MjA5NDY4NjQzOX0.SgdwxgdfV-CsdiJeSdvX5OUg_UCMMf2hrz8DpsfJZrE"

# =========================
# CONFIG
# =========================

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# RESTORE SESSION
# =========================

if (
    "access_token" in st.session_state
    and "refresh_token" in st.session_state
):
    supabase.auth.set_session(
        st.session_state["access_token"],
        st.session_state["refresh_token"]
    )

# =========================
# HTML HELPERS
# =========================

CARD_CSS = """
<style>
.card-wrapper {
    border-radius: 16px;
    padding: 10px;
    background: #111;
    text-align: center;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
}
.card-wrapper:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(255,255,255,0.12);
}
.card-img-container {
    width: 100%;
    aspect-ratio: 2 / 3;
    overflow: hidden;
    border-radius: 12px;
    background: #222;
    display: flex;
    align-items: center;
    justify-content: center;
}
.card-img-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.card-name {
    color: white;
    font-size: 0.9rem;
    font-weight: 600;
    margin: 8px 0 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.card-rarity {
    color: gray;
    font-size: 0.75rem;
    margin: 0;
}

/* Modal */
.sky-modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.85);
    z-index: 99999;
    align-items: center;
    justify-content: center;
    padding: 20px;
    backdrop-filter: blur(6px);
}
.sky-modal-overlay.open {
    display: flex;
}
.sky-modal-inner {
    background: #1a1a1a;
    border-radius: 20px;
    max-width: 420px;
    width: 100%;
    overflow: hidden;
    position: relative;
    box-shadow: 0 24px 64px rgba(0,0,0,0.8);
    animation: modalIn 0.25s ease;
}
@keyframes modalIn {
    from { opacity: 0; transform: scale(0.92); }
    to   { opacity: 1; transform: scale(1); }
}
.sky-modal-img-wrap {
    width: 100%;
    aspect-ratio: 2 / 3;
    overflow: hidden;
    background: #222;
}
.sky-modal-img-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.sky-modal-body {
    padding: 20px 24px 28px;
}
.sky-modal-name {
    color: white;
    font-size: 1.3rem;
    font-weight: 700;
    margin: 0 0 4px;
}
.sky-modal-rarity {
    color: #888;
    font-size: 0.85rem;
    margin: 0 0 14px;
}
.sky-modal-desc {
    color: #ccc;
    font-size: 0.9rem;
    line-height: 1.6;
    margin: 0;
}
.sky-modal-close {
    position: absolute;
    top: 14px;
    right: 16px;
    background: rgba(0,0,0,0.55);
    border: none;
    color: white;
    font-size: 1.2rem;
    width: 34px;
    height: 34px;
    border-radius: 50%;
    cursor: pointer;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: center;
}
.sky-modal-close:hover {
    background: rgba(255,255,255,0.15);
}
</style>
"""


def card_with_modal_html(img_url, name, rarity, description, modal_id):
    """
    Returns a self-contained card + modal block.
    The modal lives inside the same st.markdown() iframe as the card,
    so JS can always find it without cross-frame issues.
    """
    safe_name = name.replace("<", "&lt;").replace(">", "&gt;")
    safe_rarity = rarity.replace("<", "&lt;").replace(">", "&gt;")
    safe_desc = description.replace("<", "&lt;").replace(">", "&gt;")

    return f"""
{CARD_CSS}

<!-- Card -->
<div class="card-wrapper" onclick="document.getElementById('{modal_id}').classList.add('open')">
    <div class="card-img-container">
        <img src="{img_url}" alt="{safe_name}" loading="lazy"/>
    </div>
    <p class="card-name">{safe_name}</p>
    <p class="card-rarity">{safe_rarity}</p>
</div>

<!-- Modal (inside the same iframe as the card) -->
<div class="sky-modal-overlay" id="{modal_id}"
     onclick="if(event.target===this)this.classList.remove('open')">
    <div class="sky-modal-inner">
        <button class="sky-modal-close"
                onclick="document.getElementById('{modal_id}').classList.remove('open')">✕</button>
        <div class="sky-modal-img-wrap">
            <img src="{img_url}" alt="{safe_name}"/>
        </div>
        <div class="sky-modal-body">
            <p class="sky-modal-name">{safe_name}</p>
            <p class="sky-modal-rarity">Rareté : {safe_rarity}</p>
            <p class="sky-modal-desc">{safe_desc}</p>
        </div>
    </div>
</div>

<script>
(function() {{
    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape') {{
            var m = document.getElementById('{modal_id}');
            if (m) m.classList.remove('open');
        }}
    }});
}})();
</script>
"""


def get_img_url(card):
    return (
        supabase.storage
        .from_("Skyline")
        .get_public_url(card["image"])
        .replace("/cards", "")
    )


# =========================
# SIDEBAR
# =========================

st.sidebar.title("✦ Skymap")

page = st.sidebar.radio("Navigation", ["Pioche", "Bibliothèque"])

# =========================
# AUTH SIDEBAR
# =========================

st.sidebar.divider()

if "user" not in st.session_state:

    st.sidebar.subheader("Connexion")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Mot de passe", type="password")

    if st.sidebar.button("Connexion"):
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state["access_token"] = res.session.access_token
            st.session_state["refresh_token"] = res.session.refresh_token
            st.session_state["user"] = res.user
            st.rerun()
        except Exception as e:
            st.sidebar.error(str(e))

    if st.sidebar.button("Créer un compte"):
        try:
            supabase.auth.sign_up({"email": email, "password": password})
            st.sidebar.success("Compte créé.")
        except Exception as e:
            st.sidebar.error(str(e))

else:
    st.sidebar.success(f"Connecté :\n\n{st.session_state['user'].email}")
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
        st.info("Connectez-vous.")
        st.stop()

    if st.button("Piocher une carte"):
        result = supabase.rpc("pull_card").execute()
        data = result.data

        if not data["success"]:
            st.session_state.pop("last_pulled_card", None)
            st.error("Limite quotidienne atteinte.")
        else:
            st.session_state["last_pulled_card"] = data

    # Display last pulled card
    if "last_pulled_card" in st.session_state:
        data = st.session_state["last_pulled_card"]
        card = data["card"]

        img_url = get_img_url(card)
        name = card["name"]
        rarity = card.get("rarity", "")
        description = card.get("description", "")

        if data["already_owned"]:
            st.warning("Doublon")
        else:
            st.success("Nouvelle carte !")

        # Center the card in a single column
        col = st.columns([1, 2, 1])[1]
        with col:
            st.components.v1.html(
                card_with_modal_html(img_url, name, rarity, description, "pioche-modal"),
                height=600,
                scrolling=False
            )

# =========================
# PAGE : BIBLIOTHÈQUE
# =========================

elif page == "Bibliothèque":

    st.title("📚 Bibliothèque")

    if "user" not in st.session_state:
        st.info("Connectez-vous.")
        st.stop()

    user_cards = (
        supabase.table("user_cards")
        .select("*")
        .eq("user_id", st.session_state["user"].id)
        .execute()
    )

    card_ids = [uc["card_id"] for uc in (user_cards.data or [])]

    if not card_ids:
        st.info("Aucune carte.")
        st.stop()

    cards_result = (
        supabase.table("cards")
        .select("*")
        .in_("card_id", card_ids)
        .execute()
    )
    all_cards = cards_result.data or []

    common_cards = [c for c in all_cards if c.get("rarity", "").lower() == "common"]
    non_common_cards = [c for c in all_cards if c.get("rarity", "").lower() != "common"]

    # --- Common card counter ---
    if common_cards:
        st.markdown(
            f"""
            <div style="
                display: inline-flex;
                align-items: center;
                gap: 10px;
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 12px;
                padding: 10px 20px;
                margin-bottom: 24px;
            ">
                <span style="font-size: 1.4rem;">🃏</span>
                <div>
                    <div style="color: #888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em;">Cartes Common</div>
                    <div style="color: white; font-size: 1.3rem; font-weight: 700;">{len(common_cards)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if not non_common_cards:
        st.info("Aucune carte rare ou supérieure pour le moment.")
        st.stop()

    # --- Card grid (4 columns) ---
    # Each card needs its own st.components.v1.html() call so the modal
    # and its trigger live inside the same iframe — no cross-frame JS issues.
    cols = st.columns(4)

    for i, card in enumerate(non_common_cards):
        img_url = get_img_url(card)
        name = card["name"]
        rarity = card.get("rarity", "")
        description = card.get("description", "")
        modal_id = f"modal-{card['card_id']}"

        with cols[i % 4]:
            st.components.v1.html(
                card_with_modal_html(img_url, name, rarity, description, modal_id),
                height=450,
                scrolling=False
            )
