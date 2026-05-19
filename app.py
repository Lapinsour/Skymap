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
# MODAL STYLES + JS
# =========================

st.markdown("""
<style>
/* ---- Card grid uniform sizing ---- */
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

/* ---- Modal overlay ---- */
#card-modal {
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
#card-modal.open {
    display: flex;
}
#card-modal-inner {
    background: #1a1a1a;
    border-radius: 20px;
    max-width: 480px;
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
#modal-img-container {
    width: 100%;
    aspect-ratio: 2 / 3;
    overflow: hidden;
    background: #222;
}
#modal-img-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
#modal-body {
    padding: 20px 24px 28px;
}
#modal-name {
    color: white;
    font-size: 1.3rem;
    font-weight: 700;
    margin: 0 0 4px;
}
#modal-rarity {
    color: #888;
    font-size: 0.85rem;
    margin: 0 0 14px;
}
#modal-description {
    color: #ccc;
    font-size: 0.9rem;
    line-height: 1.6;
    margin: 0;
}
#modal-close {
    position: absolute;
    top: 14px;
    right: 16px;
    background: rgba(0,0,0,0.55);
    border: none;
    color: white;
    font-size: 1.4rem;
    line-height: 1;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.15s;
}
#modal-close:hover {
    background: rgba(255,255,255,0.15);
}
</style>

<!-- Modal HTML -->
<div id="card-modal">
  <div id="card-modal-inner">
    <button id="modal-close" onclick="closeModal()">✕</button>
    <div id="modal-img-container">
      <img id="modal-img" src="" alt=""/>
    </div>
    <div id="modal-body">
      <p id="modal-name"></p>
      <p id="modal-rarity"></p>
      <p id="modal-description"></p>
    </div>
  </div>
</div>

<script>
function openCard(imgUrl, name, rarity, description) {
    document.getElementById("modal-img").src = imgUrl;
    document.getElementById("modal-name").textContent = name;
    document.getElementById("modal-rarity").textContent = "Rareté : " + rarity;
    document.getElementById("modal-description").textContent = description || "";
    document.getElementById("card-modal").classList.add("open");
    document.body.style.overflow = "hidden";
}
function closeModal() {
    document.getElementById("card-modal").classList.remove("open");
    document.body.style.overflow = "";
}
// Close on backdrop click
document.getElementById("card-modal").addEventListener("click", function(e) {
    if (e.target === this) closeModal();
});
// Close on Escape key
document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") closeModal();
});
</script>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

st.sidebar.title("✦ Skymap")

page = st.sidebar.radio(
    "Navigation",
    ["Pioche", "Bibliothèque"]
)

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
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
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
            st.error("Limite quotidienne atteinte.")
        else:
            card = data["card"]

            st.image(card["image"], use_container_width=True)
            st.subheader(card["name"])
            st.write(f"Rareté : {card['rarity']}")

            if data["already_owned"]:
                st.warning("Doublon")
            else:
                st.success("Nouvelle carte !")

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

    # Fetch all owned cards details
    cards_result = (
        supabase.table("cards")
        .select("*")
        .in_("card_id", card_ids)
        .execute()
    )
    all_cards = cards_result.data or []

    # Separate Common cards from the rest
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

    # --- Non-common cards grid ---
    if not non_common_cards:
        st.info("Aucune carte rare ou supérieure pour le moment.")
        st.stop()

    cols = st.columns(4)

    for i, card in enumerate(non_common_cards):

        img_url = (
            supabase.storage
            .from_("Skyline")
            .get_public_url(card["image"])
            .replace("/cards", "")
        )

        name = card["name"]
        rarity = card.get("rarity", "")
        description = card.get("description", "")

        # Escape single quotes for inline JS
        js_img = img_url.replace("'", "\\'")
        js_name = name.replace("'", "\\'")
        js_rarity = rarity.replace("'", "\\'")
        js_desc = description.replace("'", "\\'").replace("\n", "\\n")

        with cols[i % 4]:
            st.markdown(
                f"""
                <div class="card-wrapper" onclick="openCard('{js_img}', '{js_name}', '{js_rarity}', '{js_desc}')">
                    <div class="card-img-container">
                        <img src="{img_url}" alt="{name}" loading="lazy"/>
                    </div>
                    <p class="card-name">{name}</p>
                    <p class="card-rarity">{rarity}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
