const supabaseUrl =
  "https://vkobxpkysltnycafezen.supabase.co"

const supabaseKey =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZrb2J4cGt5c2x0bnljYWZlemVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkxMTA0MzksImV4cCI6MjA5NDY4NjQzOX0.SgdwxgdfV-CsdiJeSdvX5OUg_UCMMf2hrz8DpsfJZrE"

const supabase =
  window.supabase.createClient(
    supabaseUrl,
    supabaseKey
  )

// =========================
// LOAD CARDS
// =========================

async function loadCards(){

  try {

    const res = await fetch(
      "cards_metadata.json"
    )

    if(!res.ok){

      throw new Error(
        "Impossible de charger cards_metadata.json"
      )
    }

    const cards = await res.json()

    const grid =
      document.getElementById("grid")

    cards.forEach(card => {

      const div =
        document.createElement("div")

      div.className = "card"

      div.innerHTML = `
        <img src="${card.image}">
        <h2>
          ${card.name || "Carte Commune"}
        </h2>
      `

      grid.appendChild(div)
    })

  } catch(err){

    console.error(err)
  }
}

// =========================
// LOGIN
// =========================

async function login(){

  const { data, error } =
    await supabase.auth.signInAnonymously()

  if(error){

    console.error(error)
    return
  }

  console.log(
    "Connecté :",
    data.user
  )
}

// =========================
// PULL CARD
// =========================

async function pullCard(){

  const { data, error } =
    await supabase.rpc("pull_card")

  if(error){

    console.error(error)
    return
  }

  console.log(data)
}

// =========================
// EVENTS
// =========================

document
  .getElementById("login-btn")
  .addEventListener(
    "click",
    login
  )

document
  .getElementById("pull-btn")
  .addEventListener(
    "click",
    pullCard
  )

// =========================
// INIT
// =========================

loadCards()
