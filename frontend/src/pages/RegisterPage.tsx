import { useState } from "react";
import { register } from "../lib/api";

interface Props {
  onBack: () => void;
  onRegistered: () => void;
}

export default function RegisterPage({ onBack, onRegistered }: Props) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);
    try {
      await register(username, password);
      onRegistered();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-center h-screen bg-zinc-950">
      <div className="w-80 bg-zinc-900 rounded-2xl p-8 shadow-xl border border-zinc-800">
        <h1 className="text-white text-2xl font-semibold mb-1">Argus</h1>
        <p className="text-zinc-400 text-sm mb-6">Create an account</p>

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
            autoComplete="new-password"
          />
          <input
            type="password"
            className="bg-zinc-800 text-white rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-1 focus:ring-zinc-500 placeholder-zinc-500"
            placeholder="Confirm password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            autoComplete="new-password"
          />

          {error && <p className="text-red-400 text-xs">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="bg-white text-zinc-900 rounded-lg py-2.5 text-sm font-medium hover:bg-zinc-100 transition-colors disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="text-zinc-500 text-xs mt-5 text-center">
          Already have an account?{" "}
          <button
            onClick={onBack}
            className="text-zinc-300 hover:text-white transition-colors"
          >
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
}