import {
  useEffect,
  useState,
} from "react";

import Login from "./components/Login";
import Chat from "./pages/Chat";

import {
  clearAccessToken,
  getAccessToken,
} from "./api/client";

import {
  getMe,
  type UserResponse,
} from "./api/relay";


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

    restoreSession();
  }, []);


  function handleLogout() {
    clearAccessToken();

    setUser(null);
  }


  if (loading) {
    return (
      <p>
        Loading...
      </p>
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
    <div>
      <button
        onClick={
          handleLogout
        }
      >
        Logout
      </button>

      <hr />

      <Chat
        user={user}
      />
    </div>
  );
}


export default App;