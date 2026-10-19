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
  ] = useState("");

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(false);


  function setSales() {
    setUsername("sales");
    setPassword("");
    setError(null);
  }


  function setManager() {
    setUsername("manager");
    setPassword("");
    setError(null);
  }


  function setAdmin() {
    setUsername("admin");
    setPassword("");
    setError(null);
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
        "Login failed. Check your username and password."
      );

    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="flex min-h-screen items-center justify-center bg-[#eef0eb] px-5 py-10">
      <div className="grid w-full max-w-5xl overflow-hidden rounded-[30px] border border-[#dfe4da] bg-white shadow-[0_24px_70px_rgba(44,63,37,0.10)] lg:grid-cols-[1.05fr_0.95fr]">
        <section className="relative hidden min-h-[640px] overflow-hidden bg-gradient-to-br from-[#8eac73] via-[#719451] to-[#4e6d3a] p-10 text-white lg:block">
          <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-white/10 blur-2xl" />
          <div className="absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-white/10 blur-2xl" />

          <div className="relative flex h-full flex-col justify-between">
            <div>
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/15 text-lg font-bold backdrop-blur">
                  R
                </div>

                <div>
                  <p className="text-lg font-semibold">
                    Relay AI
                  </p>

                  <p className="text-sm text-white/70">
                    Enterprise Operations Assistant
                  </p>
                </div>
              </div>

              <div className="mt-16 max-w-md">
                <p className="text-sm font-medium uppercase tracking-[0.14em] text-white/65">
                  Smarter operations
                </p>

                <h1 className="mt-4 text-4xl font-semibold leading-tight tracking-[-0.04em] text-white">
                  Turn natural language into controlled business workflows.
                </h1>

                <p className="mt-5 text-sm leading-7 text-white/75">
                  Relay connects AI with inventory,
                  pricing, customer data,
                  permissions, approvals, and
                  auditable workflows.
                </p>
              </div>
            </div>

            <div className="grid gap-3">
              <div className="rounded-2xl bg-white/12 p-4 backdrop-blur">
                <p className="text-sm font-medium">
                  Controlled automation
                </p>

                <p className="mt-1 text-sm leading-6 text-white/70">
                  AI understands the request while
                  backend rules and permissions
                  control the action.
                </p>
              </div>

              <div className="rounded-2xl bg-white/12 p-4 backdrop-blur">
                <p className="text-sm font-medium">
                  Human-in-the-loop
                </p>

                <p className="mt-1 text-sm leading-6 text-white/70">
                  Sensitive quotes can pause for
                  manager approval and resume safely.
                </p>
              </div>
            </div>
          </div>
        </section>


        <section className="flex min-h-[640px] items-center p-7 sm:p-10 lg:p-12">
          <div className="mx-auto w-full max-w-md">
            <div className="lg:hidden">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#719451] text-sm font-bold text-white">
                  R
                </div>

                <div>
                  <p className="font-semibold text-[#1d2919]">
                    Relay AI
                  </p>

                  <p className="text-xs text-[#7b8376]">
                    Enterprise Operations Assistant
                  </p>
                </div>
              </div>
            </div>


            <div className="mt-8 lg:mt-0">
              <p className="text-sm font-medium text-[#719451]">
                Welcome back
              </p>

              <h2 className="mt-2 text-3xl font-semibold tracking-[-0.04em] text-[#1b2518]">
                Sign in to Relay
              </h2>

              <p className="mt-3 text-sm leading-6 text-[#747d70]">
                Choose a test account or enter your
                credentials manually.
              </p>
            </div>


            <div className="mt-7 grid grid-cols-3 gap-2 rounded-2xl bg-[#f3f5f0] p-1.5">
              <button
                type="button"
                onClick={setSales}
                className={`rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                  username === "sales"
                    ? "bg-white text-[#314525] shadow-sm"
                    : "text-[#727a6e] hover:text-[#415039]"
                }`}
              >
                Sales
              </button>

              <button
                type="button"
                onClick={setManager}
                className={`rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                  username === "manager"
                    ? "bg-white text-[#314525] shadow-sm"
                    : "text-[#727a6e] hover:text-[#415039]"
                }`}
              >
                Manager
              </button>

              <button
                type="button"
                onClick={setAdmin}
                className={`rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                  username === "admin"
                    ? "bg-white text-[#314525] shadow-sm"
                    : "text-[#727a6e] hover:text-[#415039]"
                }`}
              >
                Admin
              </button>
            </div>


            <form
              onSubmit={handleSubmit}
              className="mt-7 space-y-5"
            >
              <div>
                <label
                  htmlFor="username"
                  className="mb-2 block text-sm font-medium text-[#384334]"
                >
                  Username
                </label>

                <input
                  id="username"
                  value={username}
                  onChange={(event) =>
                    setUsername(
                      event.target.value
                    )
                  }
                  autoComplete="username"
                  className="w-full rounded-xl border border-[#d9dfd3] bg-[#f9faf7] px-4 py-3 text-sm text-[#263022] outline-none transition placeholder:text-[#9ba297] focus:border-[#8aac69] focus:bg-white focus:ring-4 focus:ring-[#8aac69]/10"
                />
              </div>


              <div>
                <label
                  htmlFor="password"
                  className="mb-2 block text-sm font-medium text-[#384334]"
                >
                  Password
                </label>

                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(event) =>
                    setPassword(
                      event.target.value
                    )
                  }
                  autoComplete="current-password"
                  placeholder="Enter your password"
                  className="w-full rounded-xl border border-[#d9dfd3] bg-[#f9faf7] px-4 py-3 text-sm text-[#263022] outline-none transition placeholder:text-[#9ba297] focus:border-[#8aac69] focus:bg-white focus:ring-4 focus:ring-[#8aac69]/10"
                />
              </div>


              {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}


              <button
                type="submit"
                disabled={
                  loading ||
                  !username.trim() ||
                  !password
                }
                className="flex w-full items-center justify-center rounded-xl bg-[#1d2f18] px-4 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-[#314525] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading
                  ? "Signing in..."
                  : "Sign in"}
              </button>
            </form>


            <div className="mt-7 rounded-2xl border border-[#e0e5db] bg-[#f7f8f5] p-4">
              <p className="text-xs font-medium uppercase tracking-[0.12em] text-[#8a9286]">
                Test accounts
              </p>

              <div className="mt-3 space-y-2 text-xs text-[#6f786a]">
                <div className="flex items-center justify-between">
                  <span>
                    Sales
                  </span>

                  <span className="font-mono text-[#475441]">
                    sales
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span>
                    Manager
                  </span>

                  <span className="font-mono text-[#475441]">
                    manager
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span>
                    Admin
                  </span>

                  <span className="font-mono text-[#475441]">
                    admin
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}