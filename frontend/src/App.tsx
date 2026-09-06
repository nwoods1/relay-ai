import { useEffect, useState } from "react"
import { getHealth } from "./services/api"

function App() {
  const [status, setStatus] = useState("Checking...")

  useEffect(() => {
    getHealth()
      .then((data) => {
        setStatus(data.status)
      })
      .catch(() => {
        setStatus("offline")
      })
  }, [])

  return (
    <main className="p-8">
      <h1 className="text-3xl font-bold">
        Relay AI
      </h1>

      <p>
        Backend: {status}
      </p>
    </main>
  )
}

export default App