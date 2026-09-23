import {
  type FormEvent,
  useState,
} from "react";

import {
  login,
  type UserResponse,
} from "../api/relay";

import {
  setAccessToken,
} from "../api/client";


type LoginProps = {
  onLogin: (
    user: UserResponse
  ) => void;

  loadCurrentUser: () =>
    Promise<UserResponse>;
};


export default function Login(
  {
    onLogin,
    loadCurrentUser,
  }: LoginProps
) {
  const [
    username,
    setUsername,
  ] = useState("sales");

  const [
    password,
    setPassword,
  ] = useState("Sales123!");

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  );

  const [
    loading,
    setLoading,
  ] = useState(false);


  function setSales() {
    setUsername("sales");
    setPassword("Sales123!");
  }


  function setManager() {
    setUsername("manager");
    setPassword("Manager123!");
  }


  function setAdmin() {
    setUsername("admin");
    setPassword("Admin123!");
  }


  async function handleSubmit(
    event: FormEvent
  ) {
    event.preventDefault();

    try {
      setLoading(true);
      setError(null);

      const authResponse =
        await login(
          username,
          password
        );

      setAccessToken(
        authResponse.access_token
      );

      const user =
        await loadCurrentUser();

      onLogin(user);

    } catch (err) {
      console.error(err);

      setError(
        "Login failed"
      );

    } finally {
      setLoading(false);
    }
  }


  return (
    <div>
      <h1>Relay AI Login</h1>

      <p>
        Choose a test account or
        enter credentials manually.
      </p>

      <button
        onClick={setSales}
      >
        Sales
      </button>

      <button
        onClick={setManager}
      >
        Manager
      </button>

      <button
        onClick={setAdmin}
      >
        Admin
      </button>

      <br />
      <br />

      <form
        onSubmit={
          handleSubmit
        }
      >
        <label>
          Username
        </label>

        <br />

        <input
          value={username}
          onChange={(event) =>
            setUsername(
              event.target.value
            )
          }
        />

        <br />
        <br />

        <label>
          Password
        </label>

        <br />

        <input
          type="password"
          value={password}
          onChange={(event) =>
            setPassword(
              event.target.value
            )
          }
        />

        <br />
        <br />

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Logging in..."
            : "Login"}
        </button>
      </form>

      {error && (
        <p>{error}</p>
      )}
    </div>
  );
}