import { useCallback, useEffect, useState } from "react";
import {
  deletePassword,
  getPassword,
  listPasswords,
  PasswordData,
  PasswordMeta,
  storePassword,
  updatePassword,
} from "../lib/api";

interface Props { masterPassword: string; onLogout: (reason?: string) => void; }
type EditorState = { mode: "add" | "edit"; originalService?: string; data: PasswordData };

const LOCK_TIMEOUT_MS = 5 * 60 * 1000;
const emptyPassword: PasswordData = { service_name: "", username: "", password: "", notes: "" };

export default function VaultPage({ masterPassword, onLogout }: Props) {
  const [entries, setEntries] = useState<PasswordMeta[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editor, setEditor] = useState<EditorState | null>(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [showEditorPassword, setShowEditorPassword] = useState(false);
  const [selected, setSelected] = useState<PasswordData | null>(null);
  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [showDetailPassword, setShowDetailPassword] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const refreshEntries = useCallback(async () => {
    const records = await listPasswords(masterPassword);
    setEntries(records);
  }, [masterPassword]);

  useEffect(() => {
    refreshEntries().catch((err) => setError(err.message)).finally(() => setLoading(false));
  }, [refreshEntries]);

  useEffect(() => {
    let timer = window.setTimeout(() => onLogout("Vault locked after 5 minutes of inactivity."), LOCK_TIMEOUT_MS);
    function resetTimer() {
      window.clearTimeout(timer);
      timer = window.setTimeout(() => onLogout("Vault locked after 5 minutes of inactivity."), LOCK_TIMEOUT_MS);
    }
    const events: Array<keyof WindowEventMap> = ["pointerdown", "keydown", "focus"];
    events.forEach((eventName) => window.addEventListener(eventName, resetTimer));
    return () => {
      window.clearTimeout(timer);
      events.forEach((eventName) => window.removeEventListener(eventName, resetTimer));
    };
  }, [onLogout]);

  const filtered = entries.filter((entry) => {
    const query = search.toLowerCase();
    return entry.service_name.toLowerCase().includes(query) || entry.username.toLowerCase().includes(query);
  });

  function closeDetails() {
    setSelected(null);
    setSelectedService(null);
    setDetailError(null);
    setShowDetailPassword(false);
    setConfirmDelete(false);
  }

  async function openDetails(serviceName: string) {
    setSelectedService(serviceName);
    setSelected(null);
    setDetailError(null);
    setShowDetailPassword(false);
    setConfirmDelete(false);
    setDetailLoading(true);
    try { setSelected(await getPassword(serviceName, masterPassword)); }
    catch (err: unknown) { setDetailError(err instanceof Error ? err.message : "Failed to load record"); }
    finally { setDetailLoading(false); }
  }

  function openEditor(mode: "add" | "edit") {
    const data = mode === "edit" && selected ? { ...selected } : { ...emptyPassword };
    setEditor({ mode, originalService: mode === "edit" ? selected?.service_name : undefined, data });
    setFormError(null);
    setShowEditorPassword(false);
  }

  async function handleSave(event: React.FormEvent) {
    event.preventDefault();
    if (!editor) return;
    setSaving(true);
    setFormError(null);
    try {
      if (editor.mode === "edit" && editor.originalService) await updatePassword(editor.originalService, editor.data, masterPassword);
      else await storePassword(editor.data, masterPassword);
      await refreshEntries();
      if (editor.mode === "edit") setSelected({ ...editor.data });
      setEditor(null);
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : "Failed to save record");
    } finally { setSaving(false); }
  }

  async function handleDelete() {
    if (!selected) return;
    setDeleting(true);
    setDetailError(null);
    try {
      await deletePassword(selected.service_name, masterPassword);
      await refreshEntries();
      closeDetails();
    } catch (err: unknown) {
      setDetailError(err instanceof Error ? err.message : "Failed to delete record");
    } finally { setDeleting(false); }
  }

  async function copyValue(value: string, field: string) {
    try {
      await navigator.clipboard.writeText(value);
      setCopiedField(field);
      window.setTimeout(() => setCopiedField((current) => current === field ? null : current), 1800);
    } catch {
      setDetailError("Clipboard access was denied");
    }
  }

  return (
    <div className="desktop">
      <div className="app-window">
        <header className="app-header"><h1>Argus</h1><span>Passwords</span></header>
        <div className="vault-layout">
          <aside className="vault-sidebar">
            <div className="sidebar-heading">Vault</div>
            <nav className="sidebar-tree"><div className="tree-root">▾ Password Vault</div><div className="tree-item selected">All Records</div></nav>
            <div className="sidebar-session"><div className="lock-note">Locks after 5 minutes idle</div><button onClick={() => onLogout()} className="secondary-action">Sign Out</button></div>
          </aside>
          <main className="vault-main">
            <h2 className="content-heading">Password Records</h2>
            <p className="content-subtitle">Stored accounts and passwords.</p>
            <div className="toolbar"><input className="search-field" aria-label="Search password records" placeholder="Search by service or username..." value={search} onChange={(event) => setSearch(event.target.value)} /><button onClick={() => openEditor("add")} className="toolbar-button">New Record...</button></div>
            <section className="entry-frame" aria-label="Password records">
              <div className="entry-header"><span>Service Name</span><span>Username</span><span>Updated</span></div>
              {loading && <p className="content-state">Loading records...</p>}
              {error && <p className="content-state error" role="alert">{error}</p>}
              <ul className="entry-list">{filtered.map((entry) => <li key={entry.service_name}><button type="button" className="entry-row" onClick={() => openDetails(entry.service_name)}><span className="entry-service">{entry.service_name}</span><span>{entry.username || "—"}</span><span className="entry-state">{new Date(entry.updated_at).toLocaleDateString()}</span></button></li>)}</ul>
              {!loading && filtered.length === 0 && <p className="content-state">No records match the current search.</p>}
              <div className="record-count">{filtered.length} record{filtered.length === 1 ? "" : "s"} displayed</div>
            </section>
          </main>
        </div>
      </div>

      {selectedService && <div className="modal-backdrop"><section className="modal-window detail-window" role="dialog" aria-modal="true" aria-labelledby="details-title">
        <div className="modal-title" id="details-title">Password Record</div>
        <div className="modal-body">
          {detailLoading && <p className="content-state">Loading record...</p>}
          {detailError && <p className="form-message" role="alert">{detailError}</p>}
          {selected && <>
            <dl className="detail-list">
              <div><dt>Service</dt><dd>{selected.service_name}</dd></div>
              <div><dt>Username</dt><dd><span className="detail-value">{selected.username || "—"}</span>{selected.username && <button type="button" className="inline-action" onClick={() => copyValue(selected.username ?? "", "username")}>{copiedField === "username" ? "Copied" : "Copy"}</button>}</dd></div>
              <div><dt>Password</dt><dd><span className="detail-value password-value">{showDetailPassword ? selected.password : "••••••••"}</span><button type="button" className="inline-action" onClick={() => setShowDetailPassword((visible) => !visible)}>{showDetailPassword ? "Hide" : "Reveal"}</button><button type="button" className="inline-action" onClick={() => copyValue(selected.password, "password")}>{copiedField === "password" ? "Copied" : "Copy"}</button></dd></div>
              <div><dt>Notes</dt><dd className="notes-value">{selected.notes || "—"}</dd></div>
            </dl>
            {confirmDelete && <div className="delete-confirm"><strong>Delete this record?</strong><span>This cannot be undone.</span><div><button type="button" className="dialog-button" onClick={() => setConfirmDelete(false)}>Cancel</button><button type="button" className="danger-action" disabled={deleting} onClick={handleDelete}>{deleting ? "Deleting..." : "Delete"}</button></div></div>}
          </>}
        </div>
        <div className="modal-actions">
          {selected && !confirmDelete && <><button type="button" className="danger-link" onClick={() => setConfirmDelete(true)}>Delete...</button><span className="action-spacer" /><button type="button" className="dialog-button" onClick={() => openEditor("edit")}>Edit...</button></>}
          <button type="button" className="dialog-button primary" onClick={closeDetails}>Close</button>
        </div>
      </section></div>}

      {editor && <div className="modal-backdrop"><form onSubmit={handleSave} className="modal-window">
        <div className="modal-title">{editor.mode === "add" ? "Create Password Record" : "Edit Password Record"}</div>
        <div className="modal-body">
          {formError && <p className="form-message" role="alert">{formError}</p>}
          <div className="modal-row"><label className="form-label" htmlFor="service-name">Service name <span className="required-mark">*</span></label><input id="service-name" required autoFocus className="modal-field" disabled={editor.mode === "edit"} value={editor.data.service_name} onChange={(event) => setEditor({ ...editor, data: { ...editor.data, service_name: event.target.value } })} /></div>
          <div className="modal-row"><label className="form-label" htmlFor="service-username">Username</label><input id="service-username" className="modal-field" value={editor.data.username ?? ""} onChange={(event) => setEditor({ ...editor, data: { ...editor.data, username: event.target.value } })} /></div>
          <div className="modal-row"><label className="form-label" htmlFor="service-password">Password <span className="required-mark">*</span></label><div className="field-with-action"><input id="service-password" required type={showEditorPassword ? "text" : "password"} className="modal-field" value={editor.data.password} onChange={(event) => setEditor({ ...editor, data: { ...editor.data, password: event.target.value } })} /><button type="button" className="field-action" onClick={() => setShowEditorPassword((visible) => !visible)}>{showEditorPassword ? "Hide" : "Show"}</button></div></div>
          <div className="modal-row"><label className="form-label" htmlFor="service-notes">Notes</label><textarea id="service-notes" className="modal-field" value={editor.data.notes ?? ""} onChange={(event) => setEditor({ ...editor, data: { ...editor.data, notes: event.target.value } })} /></div>
        </div>
        <div className="modal-actions"><button type="button" onClick={() => setEditor(null)} className="dialog-button">Cancel</button><button type="submit" disabled={saving} className="dialog-button primary">{saving ? "Saving..." : "Save"}</button></div>
      </form></div>}
    </div>
  );
}
