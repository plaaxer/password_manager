import { useState } from "react";
import { login } from "../lib/api";
import RegisterPage from "./RegisterPage";

interface Props {
  onLogin: (masterPassword: string) => void;
}

export default function LoginPage({ onLogin }: Props) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  if (showRegister) {
    return <RegisterPage onBack={() => setShowRegister(false)} onRegistered={() => setShowRegister(false)} />;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
      onLogin(password);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-center h-screen bg-zinc-950">
      <div className="w-80 bg-zinc-900 rounded-2xl p-8 shadow-xl border border-zinc-800">
        <h1 className="text-white text-2xl font-semibold mb-1">Argus</h1>
        <p className="text-zinc-400 text-sm mb-6">Password Manager</p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            className="bg-zinc-800 text-white rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-1 focus:ring-zinc-500 placeholder-zinc-500"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
          />
          <input
            type="password"
            className="bg-zinc-800 text-white rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-1 focus:ring-zinc-500 placeholder-zinc-500"
            placeholder="Master password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />

          {error && <p className="text-red-400 text-xs">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="bg-white text-zinc-900 rounded-lg py-2.5 text-sm font-medium hover:bg-zinc-100 transition-colors disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="text-zinc-500 text-xs mt-5 text-center">
          No account?{" "}
          <button
            onClick={() => setShowRegister(true)}
            className="text-zinc-300 hover:text-white transition-colors"
          >
            Register
          </button>
        </p>
      </div>
    </div>
  );
}