const supabaseUrl =
  "https://vkobxpkysltnycafezen.supabase.co"

const supabaseKey =
  "TA_CLE_ANON"

const supabase =
  window.supabase.createClient(
    supabaseUrl,
    supabaseKey
  )

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

loadCards()
