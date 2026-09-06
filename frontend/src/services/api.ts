const API_URL = "http://localhost:8000"

export async function getHealth() {
  const response = await fetch(`${API_URL}/health`)

  if (!response.ok) {
    throw new Error("API request failed")
  }

  return response.json()
}