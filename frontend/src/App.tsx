import {
  useEffect,
  useState,
} from "react";

import Login from "./components/Login";
import Chat from "./pages/Chat";
import InventoryDashboard from "./pages/InventoryDashboard";
import OperationsDashboard from "./pages/OperationsDashboard";

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
  | "inventory"
  | "operations";


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
      <div className="flex min-h-screen items-center justify-center bg-[#eef0eb]">
        <div className="flex items-center gap-2 text-sm text-[#6f776b]">
          <span className="h-2 w-2 animate-pulse rounded-full bg-[#719451]" />

          Loading Relay...
        </div>
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


  const navigation: {
    label: string;
    view: AppView;
  }[] = [
    {
      label: "Assistant",
      view: "chat",
    },
    {
      label: "Inventory",
      view: "inventory",
    },
    ...(user.role === "manager" ||
    user.role === "admin"
      ? [
          {
            label: "Operations",
            view: "operations" as AppView,
          },
        ]
      : []),
  ];


  return (
    <div className="min-h-screen bg-[#eef0eb]">
      <header className="sticky top-0 z-40 border-b border-[#dde2d8]/80 bg-[#eef0eb]/95 backdrop-blur">
        <div className="mx-auto flex max-w-[1480px] items-center justify-between gap-4 px-5 py-3 sm:px-7 lg:px-9">
          <button
            type="button"
            onClick={() =>
              setCurrentView(
                "chat"
              )
            }
            className="flex items-center gap-2"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#719451] text-sm font-bold text-white">
              R
            </div>

            <span className="hidden text-sm font-semibold text-[#1d2919] sm:inline">
              Relay AI
            </span>
          </button>


          <nav className="flex items-center gap-1 rounded-2xl border border-[#dce1d7] bg-white p-1 shadow-sm">
            {navigation.map(
              (item) => (
                <button
                  key={
                    item.view
                  }
                  type="button"
                  onClick={() =>
                    setCurrentView(
                      item.view
                    )
                  }
                  className={`rounded-xl px-3 py-1.5 text-xs font-medium transition sm:px-4 ${
                    currentView ===
                    item.view
                      ? "bg-[#8aac69] text-white shadow-sm"
                      : "text-[#71796d] hover:bg-[#f3f5f0] hover:text-[#33402e]"
                  }`}
                >
                  {item.label}
                </button>
              )
            )}
          </nav>


          <div className="flex items-center gap-2">
            <div className="hidden rounded-xl border border-[#dce1d7] bg-white px-3 py-1.5 sm:block">
              <p className="text-[10px] uppercase tracking-wide text-[#969d92]">
                Signed in
              </p>

              <p className="text-xs font-medium text-[#35422f]">
                {user.username}
              </p>
            </div>

            <button
              type="button"
              onClick={
                handleLogout
              }
              className="flex h-9 w-9 items-center justify-center rounded-xl border border-[#dce1d7] bg-white text-[#667061] transition hover:bg-[#f6f7f3]"
              title="Logout"
              aria-label="Logout"
            >
              <svg
                viewBox="0 0 24 24"
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <path
                  d="M10 17l5-5-5-5"
                />

                <path
                  d="M15 12H3"
                />

                <path
                  d="M21 19V5a2 2 0 0 0-2-2h-6"
                />
              </svg>
            </button>
          </div>
        </div>
      </header>


      {currentView ===
      "inventory" ? (
        <InventoryDashboard />

      ) : currentView ===
        "operations" ? (
        <OperationsDashboard />

      ) : (
        <Chat
          user={user}
        />
      )}
    </div>
  );
}


export default App;