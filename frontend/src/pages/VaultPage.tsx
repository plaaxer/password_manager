import { useEffect, useState } from "react";
import { listPasswords, logout, PasswordMeta } from "../lib/api";

interface Props {
  masterPassword: string;
  onLogout: () => void;
}

export default function VaultPage({ masterPassword, onLogout }: Props) {
  const [entries, setEntries] = useState<PasswordMeta[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listPasswords(masterPassword)
      .then(setEntries)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [masterPassword]);

  const filtered = entries.filter((e) =>
    e.service_name.toLowerCase().includes(search.toLowerCase())
  );

  function handleLogout() {
    logout();
    onLogout();
  }

  return (
    <div className="flex h-screen bg-zinc-950 text-white">
      {/* Sidebar */}
      <aside className="w-56 bg-zinc-900 border-r border-zinc-800 flex flex-col p-4">
        <h1 className="text-lg font-semibold mb-6">Argus</h1>
        <nav className="flex-1 text-sm text-zinc-400 space-y-1">
          <div className="bg-zinc-800 text-white rounded-lg px-3 py-2 cursor-pointer">
            All passwords
          </div>
        </nav>
        <button
          onClick={handleLogout}
          className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors text-left"
        >
          Sign out
        </button>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col p-6 gap-4">
        <input
          className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-1 focus:ring-zinc-600 placeholder-zinc-500 w-full"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        {loading && <p className="text-zinc-500 text-sm">Loading...</p>}
        {error && <p className="text-red-400 text-sm">{error}</p>}

        <ul className="flex flex-col gap-2">
          {filtered.map((entry) => (
            <li
              key={entry.service_name}
              className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3 flex items-center justify-between hover:border-zinc-600 cursor-pointer transition-colors"
            >
              <span className="text-sm font-medium">{entry.service_name}</span>
              <span className="text-xs text-zinc-500">••••••••</span>
            </li>
          ))}
          {!loading && filtered.length === 0 && (
            <p className="text-zinc-500 text-sm">No entries found.</p>
          )}
        </ul>
      </main>
    </div>
  );
}