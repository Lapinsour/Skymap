import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://vkobxpkysltnycafezen.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZrb2J4cGt5c2x0bnljYWZlemVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkxMTA0MzksImV4cCI6MjA5NDY4NjQzOX0.SgdwxgdfV-CsdiJeSdvX5OUg_UCMMf2hrz8DpsfJZrE"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# RESTORE SESSION
# =========================

if "access_token" in st.session_state and "refresh_token" in st.session_state:
    supabase.auth.set_session(
        st.session_state["access_token"],
        st.session_state["refresh_token"]
    )

# =========================
# HELPERS
# =========================

def get_img_url(card):
    return (
        supabase.storage
        .from_("Skyline")
        .get_public_url(card["image"])
        .replace("/cards", "")
    )

def build_library_html(cards):
    """
    Single self-contained HTML block:
    - 4-column card grid (uniform 2/3 ratio)
    - One fullscreen overlay shared by all cards
    - Click card → overlay opens (shows image + title)
    - Click again → flips to description
    - Click again → flips back to image
    - Click outside card → overlay closes
    """

    cards_json_items = []
    for card in cards:
        img_url = get_img_url(card)
        name = card["name"].replace('"', '&quot;').replace("'", r"\'")
        rarity = card.get("rarity", "").replace('"', '&quot;').replace("'", r"\'")
        desc = card.get("description", "").replace('"', '&quot;').replace("'", r"\'").replace("\n", r"\n")
        cid = card["card_id"]
        cards_json_items.append(
            f'{{"id":"{cid}","img":"{img_url}","name":"{name}","rarity":"{rarity}","desc":"{desc}"}}'
        )

    cards_json = "[" + ",".join(cards_json_items) + "]"

    # Build thumbnail grid HTML
    thumbs_html = ""
    for card in cards:
        img_url = get_img_url(card)
        safe_name = card["name"].replace('"', '&quot;')
        cid = card["card_id"]
        thumbs_html += f"""
        <div class="card-thumb" onclick="openCard('{cid}')" title="{safe_name}">
            <div class="card-img-wrap">
                <img src="{img_url}" alt="{safe_name}" loading="lazy"/>
            </div>
            <p class="card-name">{safe_name}</p>
            <p class="card-rarity">{card.get("rarity","")}</p>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; font-family: sans-serif; }}

  /* Grid */
  .grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    padding: 4px;
  }}

  /* Thumbnail card */
  .card-thumb {{
    background: #111;
    border-radius: 14px;
    padding: 8px;
    cursor: pointer;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
  }}
  .card-thumb:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(255,255,255,0.1);
  }}
  .card-img-wrap {{
    width: 100%;
    aspect-ratio: 2 / 3;
    overflow: hidden;
    border-radius: 10px;
    background: #222;
  }}
  .card-img-wrap img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}
  .card-name {{
    color: #fff;
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .card-rarity {{
    color: #666;
    font-size: 0.68rem;
    margin-top: 2px;
  }}

  /* Overlay */
  #overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.82);
    backdrop-filter: blur(8px);
    z-index: 1000;
    align-items: center;
    justify-content: center;
  }}
  #overlay.active {{
    display: flex;
  }}

  /* Modal card */
  #modal-card {{
    width: min(340px, 80vw);
    background: #1a1a1a;
    border-radius: 20px;
    overflow: hidden;
    position: relative;
    cursor: pointer;
    box-shadow: 0 32px 80px rgba(0,0,0,0.9);
    animation: popIn 0.22s ease;
    user-select: none;
  }}
  @keyframes popIn {{
    from {{ opacity: 0; transform: scale(0.88); }}
    to   {{ opacity: 1; transform: scale(1); }}
  }}

  /* Face: image */
  #face-image {{
    display: block;
  }}
  #face-image .modal-img-wrap {{
    width: 100%;
    aspect-ratio: 2 / 3;
    overflow: hidden;
    background: #222;
  }}
  #face-image .modal-img-wrap img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}
  #face-image .modal-info {{
    padding: 16px 20px 20px;
  }}
  #face-image .modal-name {{
    color: #fff;
    font-size: 1.1rem;
    font-weight: 700;
  }}
  #face-image .modal-rarity {{
    color: #888;
    font-size: 0.8rem;
    margin-top: 4px;
  }}
  #face-image .modal-hint {{
    color: #555;
    font-size: 0.72rem;
    margin-top: 10px;
    font-style: italic;
  }}

  /* Face: description */
  #face-desc {{
    display: none;
    padding: 36px 28px 40px;
    min-height: 280px;
    flex-direction: column;
    justify-content: center;
  }}
  #face-desc.active {{
    display: flex;
  }}
  #face-image.hidden {{
    display: none;
  }}
  #face-desc .desc-name {{
    color: #fff;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 16px;
  }}
  #face-desc .desc-text {{
    color: #ccc;
    font-size: 0.9rem;
    line-height: 1.65;
  }}
  #face-desc .modal-hint {{
    color: #555;
    font-size: 0.72rem;
    margin-top: 20px;
    font-style: italic;
  }}

  /* Close button */
  #modal-close {{
    position: absolute;
    top: 12px;
    right: 14px;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: rgba(0,0,0,0.5);
    border: none;
    color: #fff;
    font-size: 1rem;
    cursor: pointer;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  #modal-close:hover {{ background: rgba(255,255,255,0.15); }}
</style>
</head>
<body>

<!-- Thumbnail grid -->
<div class="grid">
  {thumbs_html}
</div>

<!-- Shared overlay -->
<div id="overlay" onclick="handleOverlayClick(event)">
  <div id="modal-card" onclick="handleCardClick(event)">
    <button id="modal-close" onclick="closeOverlay(event)">✕</button>

    <!-- Face 1: image + title -->
    <div id="face-image">
      <div class="modal-img-wrap">
        <img id="modal-img" src="" alt=""/>
      </div>
      <div class="modal-info">
        <p class="modal-name" id="modal-name"></p>
        <p class="modal-rarity" id="modal-rarity"></p>
        <p class="modal-hint">Cliquer pour voir la description →</p>
      </div>
    </div>

    <!-- Face 2: description -->
    <div id="face-desc">
      <p class="desc-name" id="modal-desc-name"></p>
      <p class="desc-text" id="modal-desc-text"></p>
      <p class="modal-hint">← Cliquer pour revenir à la carte</p>
    </div>
  </div>
</div>

<script>
  var CARDS = {cards_json};
  var cardMap = {{}};
  CARDS.forEach(function(c) {{ cardMap[c.id] = c; }});

  var showingDesc = false;

  function openCard(id) {{
    var c = cardMap[id];
    if (!c) return;
    showingDesc = false;

    document.getElementById('modal-img').src = c.img;
    document.getElementById('modal-name').textContent = c.name;
    document.getElementById('modal-rarity').textContent = 'Rareté : ' + c.rarity;
    document.getElementById('modal-desc-name').textContent = c.name;
    document.getElementById('modal-desc-text').textContent = c.desc;

    // Show image face
    document.getElementById('face-image').classList.remove('hidden');
    document.getElementById('face-desc').classList.remove('active');

    document.getElementById('overlay').classList.add('active');
  }}

  function handleCardClick(e) {{
    e.stopPropagation();
    // Don't toggle if close button was clicked
    if (e.target.id === 'modal-close') return;

    showingDesc = !showingDesc;
    if (showingDesc) {{
      document.getElementById('face-image').classList.add('hidden');
      document.getElementById('face-desc').classList.add('active');
    }} else {{
      document.getElementById('face-image').classList.remove('hidden');
      document.getElementById('face-desc').classList.remove('active');
    }}
  }}

  function handleOverlayClick(e) {{
    // Click outside the modal card closes the overlay
    if (e.target === document.getElementById('overlay')) {{
      closeOverlay(e);
    }}
  }}

  function closeOverlay(e) {{
    if (e) e.stopPropagation();
    document.getElementById('overlay').classList.remove('active');
  }}

  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closeOverlay(null);
  }});
</script>
</body>
</html>
"""

def build_pioche_html(card):
    img_url = get_img_url(card)
    name = card["name"].replace('"', '&quot;')
    rarity = card.get("rarity", "").replace('"', '&quot;')
    desc = card.get("description", "").replace('"', '&quot;').replace("\n", "&#10;")

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; font-family: sans-serif; display: flex; justify-content: center; }}

  #modal-card {{
    width: min(300px, 90vw);
    background: #1a1a1a;
    border-radius: 20px;
    overflow: hidden;
    cursor: pointer;
    box-shadow: 0 16px 48px rgba(0,0,0,0.7);
    user-select: none;
  }}

  #face-image {{ display: block; }}
  .modal-img-wrap {{
    width: 100%;
    aspect-ratio: 2 / 3;
    overflow: hidden;
    background: #222;
  }}
  .modal-img-wrap img {{
    width: 100%; height: 100%; object-fit: cover; display: block;
  }}
  .modal-info {{ padding: 16px 20px 20px; }}
  .modal-name {{ color: #fff; font-size: 1.1rem; font-weight: 700; }}
  .modal-rarity {{ color: #888; font-size: 0.8rem; margin-top: 4px; }}
  .modal-hint {{ color: #555; font-size: 0.72rem; margin-top: 10px; font-style: italic; }}

  #face-desc {{
    display: none;
    padding: 36px 28px 40px;
    min-height: 280px;
    flex-direction: column;
    justify-content: center;
  }}
  #face-desc.active {{ display: flex; }}
  #face-image.hidden {{ display: none; }}
  .desc-name {{ color: #fff; font-size: 1.1rem; font-weight: 700; margin-bottom: 16px; }}
  .desc-text {{ color: #ccc; font-size: 0.9rem; line-height: 1.65; }}
</style>
</head>
<body>
  <div id="modal-card" onclick="toggle()">
    <div id="face-image">
      <div class="modal-img-wrap">
        <img src="{img_url}" alt="{name}"/>
      </div>
      <div class="modal-info">
        <p class="modal-name">{name}</p>
        <p class="modal-rarity">Rareté : {rarity}</p>
        <p class="modal-hint">Cliquer pour voir la description →</p>
      </div>
    </div>
    <div id="face-desc">
      <p class="desc-name">{name}</p>
      <p class="desc-text">{desc}</p>
      <p class="modal-hint" style="margin-top:20px; color:#555; font-size:0.72rem; font-style:italic;">← Cliquer pour revenir à la carte</p>
    </div>
  </div>
<script>
  var showingDesc = false;
  function toggle() {{
    showingDesc = !showingDesc;
    document.getElementById('face-image').classList.toggle('hidden', showingDesc);
    document.getElementById('face-desc').classList.toggle('active', showingDesc);
  }}
</script>
</body>
</html>
"""

# =========================
# SIDEBAR
# =========================

st.sidebar.title("✦ Skymap")
page = st.sidebar.radio("Navigation", ["Pioche", "Bibliothèque"])
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

    if "last_pulled_card" in st.session_state:
        data = st.session_state["last_pulled_card"]
        card = data["card"]

        if data["already_owned"]:
            st.warning("Doublon")
        else:
            st.success("Nouvelle carte !")

        # Estimate height: image (300 * 3/2 = 450) + info block (~110)
        st.components.v1.html(
            build_pioche_html(card),
            height=580,
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

    common_cards    = [c for c in all_cards if c.get("rarity", "").lower() == "common"]
    non_common_cards = [c for c in all_cards if c.get("rarity", "").lower() != "common"]

    # Common counter
    if common_cards:
        st.markdown(f"""
        <div style="display:inline-flex;align-items:center;gap:10px;
                    background:#1a1a1a;border:1px solid #333;border-radius:12px;
                    padding:10px 20px;margin-bottom:24px;">
            <span style="font-size:1.4rem;">🃏</span>
            <div>
                <div style="color:#888;font-size:0.75rem;text-transform:uppercase;
                            letter-spacing:0.08em;">Cartes Common</div>
                <div style="color:white;font-size:1.3rem;font-weight:700;">{len(common_cards)}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    if not non_common_cards:
        st.info("Aucune carte rare ou supérieure pour le moment.")
        st.stop()

    # Estimate grid height: each row is roughly (column_width * 3/2) tall
    # With 4 cols and ~200px thumb width → ~300px/row + label ~50px = ~350px/row
    n_rows = (len(non_common_cards) + 3) // 4
    grid_height = n_rows * 360 + 40  # 360px per row + padding

    st.components.v1.html(
        build_library_html(non_common_cards),
        height=grid_height,
        scrolling=False
    )
