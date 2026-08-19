import { useMemo, useState } from "react";
import { register } from "../lib/api";

interface Props { onBack: () => void; onRegistered: (username: string, password: string) => Promise<void>; }

function getPasswordStrength(password: string) {
  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
  if (/\d/.test(password) && /[^A-Za-z0-9]/.test(password)) score++;
  return [{ label: "Too short", score: 0 }, { label: "Weak", score: 1 }, { label: "Fair", score: 2 }, { label: "Good", score: 3 }, { label: "Strong", score: 4 }][score];
}

export default function RegisterPage({ onBack, onRegistered }: Props) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const strength = useMemo(() => getPasswordStrength(password), [password]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (username.length < 3 || username.length > 50) { setError("Account name must be between 3 and 50 characters"); return; }
    if (password !== confirm) { setError("Passwords do not match"); return; }
    if (password.length < 8) { setError("Password must be at least 8 characters"); return; }
    setLoading(true);
    try {
      await register(username, password);
      setSuccess("Account created. Signing you in...");
      try { await onRegistered(username, password); }
      catch (err: unknown) { setError(err instanceof Error ? `Account created, but sign-in failed: ${err.message}` : "Account created, but sign-in failed"); }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally { setLoading(false); }
  }

  return (
    <div className="desktop"><div className="app-window">
      <header className="app-header"><h1>Argus</h1></header>
      <main className="auth-workspace"><section className="auth-panel">
        <div className="panel-heading">Create account</div>
        <form onSubmit={handleSubmit}>
          <div className="auth-form">
            <p className="panel-description">Choose an account name and master password.</p>
            <div className="form-row"><label className="form-label" htmlFor="register-username">Account name</label><input id="register-username" required minLength={3} maxLength={50} className="field" value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" autoFocus /></div>
            <div className="form-hint">3–50 characters</div>
            <div className="form-row"><label className="form-label" htmlFor="register-password">Master password</label><div className="field-with-action"><input id="register-password" required minLength={8} type={showPassword ? "text" : "password"} className="field" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="new-password" /><button type="button" className="field-action" onClick={() => setShowPassword((visible) => !visible)}>{showPassword ? "Hide" : "Show"}</button></div></div>
            <div className="strength-row"><span>Password strength: {strength.label}</span><span className="strength-meter" aria-hidden="true">{[1,2,3,4].map((value) => <i key={value} className={value <= strength.score ? "active" : ""} />)}</span></div>
            <div className="form-row"><label className="form-label" htmlFor="register-confirm">Confirm password</label><input id="register-confirm" required minLength={8} type={showPassword ? "text" : "password"} className="field" value={confirm} onChange={(event) => setConfirm(event.target.value)} autoComplete="new-password" /></div>
            {success && <p className="form-success" role="status">{success}</p>}
            {error && <p className="form-message" role="alert">{error}</p>}
          </div>
          <div className="auth-actions"><button type="button" onClick={onBack} className="secondary-action">Cancel</button><button type="submit" disabled={loading} className="primary-action">{loading ? (success ? "Signing in..." : "Creating...") : "Create Account"}</button></div>
        </form>
      </section></main>
    </div></div>
  );
}
