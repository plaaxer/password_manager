import { useEffect, useState } from "react";
import { listPasswords, logout, storePassword, PasswordMeta } from "../lib/api";

interface Props {
  masterPassword: string;
  onLogout: () => void;
}

const emptyForm = { service_name: "", username: "", password: "", notes: "" };

export default function VaultPage({ masterPassword, onLogout }: Props) {
  const [entries, setEntries] = useState<PasswordMeta[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

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

  async function handleAddPassword(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setFormError(null);
    try {
      await storePassword(form, masterPassword);
      setEntries((prev) => [...prev, { service_name: form.service_name }]);
      setForm(emptyForm);
      setShowAdd(false);
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
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
        <div className="flex gap-3">
          <input
            className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-1 focus:ring-zinc-600 placeholder-zinc-500"
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button
            onClick={() => { setShowAdd(true); setFormError(null); }}
            className="bg-white text-zinc-950 rounded-lg px-4 py-2.5 text-sm font-medium hover:bg-zinc-200 transition-colors whitespace-nowrap"
          >
            + Add
          </button>
        </div>

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

      {/* Add password modal */}
      {showAdd && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <form
            onSubmit={handleAddPassword}
            className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 w-full max-w-sm flex flex-col gap-4"
          >
            <h2 className="text-base font-semibold">Add password</h2>

            {formError && <p className="text-red-400 text-sm">{formError}</p>}

            <input
              required
              className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-zinc-500 placeholder-zinc-500"
              placeholder="Service name *"
              value={form.service_name}
              onChange={(e) => setForm({ ...form, service_name: e.target.value })}
            />
            <input
              className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-zinc-500 placeholder-zinc-500"
              placeholder="Username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
            />
            <input
              required
              type="password"
              className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-zinc-500 placeholder-zinc-500"
              placeholder="Password *"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
            <textarea
              className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-zinc-500 placeholder-zinc-500 resize-none"
              placeholder="Notes"
              rows={2}
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
            />

            <div className="flex gap-2 justify-end">
              <button
                type="button"
                onClick={() => { setShowAdd(false); setForm(emptyForm); }}
                className="text-sm text-zinc-400 hover:text-white transition-colors px-3 py-2"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="bg-white text-zinc-950 rounded-lg px-4 py-2 text-sm font-medium hover:bg-zinc-200 transition-colors disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}