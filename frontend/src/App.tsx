import {
  useEffect,
  useState,
} from "react";

import Login from "./components/Login";
import Chat from "./pages/Chat";
import InventoryDashboard from "./pages/InventoryDashboard";

import {
  clearAccessToken,
  getAccessToken,
} from "./api/client";

import {
  getMe,
  type UserResponse,
} from "./api/relay";


type AppView =
  | "chat"
  | "inventory";


function App() {
  const [
    user,
    setUser,
  ] = useState<
    UserResponse | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    currentView,
    setCurrentView,
  ] = useState<AppView>(
    "chat"
  );


  async function loadCurrentUser():
    Promise<UserResponse> {

    const currentUser =
      await getMe();

    setUser(
      currentUser
    );

    return currentUser;
  }


  useEffect(() => {
    async function restoreSession() {
      const token =
        getAccessToken();

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        await loadCurrentUser();

      } catch {
        clearAccessToken();
        setUser(null);

      } finally {
        setLoading(false);
      }
    }

    void restoreSession();
  }, []);


  function handleLogout() {
    clearAccessToken();

    setUser(null);

    setCurrentView(
      "chat"
    );
  }


  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <p className="text-sm text-slate-500">
          Loading...
        </p>
      </div>
    );
  }


  if (!user) {
    return (
      <Login
        onLogin={setUser}
        loadCurrentUser={
          loadCurrentUser
        }
      />
    );
  }


  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
          <div className="flex items-center gap-6">
            <button
              type="button"
              onClick={() =>
                setCurrentView(
                  "chat"
                )
              }
              className="text-lg font-bold text-slate-900"
            >
              Relay AI
            </button>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() =>
                  setCurrentView(
                    "chat"
                  )
                }
                className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
                  currentView ===
                  "chat"
                    ? "bg-slate-900 text-white"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                Assistant
              </button>

              <button
                type="button"
                onClick={() =>
                  setCurrentView(
                    "inventory"
                  )
                }
                className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
                  currentView ===
                  "inventory"
                    ? "bg-slate-900 text-white"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                Inventory
              </button>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-500">
              {user.username}
            </span>

            <button
              type="button"
              onClick={
                handleLogout
              }
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {currentView ===
      "inventory" ? (
        <InventoryDashboard />
      ) : (
        <Chat
          user={user}
        />
      )}
    </div>
  );
}


export default App;