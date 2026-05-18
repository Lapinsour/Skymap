const supabaseUrl = "TON_URL"
const supabaseKey = "TON_ANON_KEY"

const supabase = window.supabase.createClient(
  supabaseUrl,
  supabaseKey
)

async function loadCards(){

  const res = await fetch(
    "cards_metadata.json"
  )

  const cards = await res.json()

  const grid = document.getElementById(
    "grid"
  )

  cards.forEach(card => {

    const div = document.createElement("div")

    div.className = "card"

    div.innerHTML = `
      <img src="${card.image}">
      <h2>${card.name || "Carte Commune"}</h2>
    `

    grid.appendChild(div)
  })
}

loadCards()
