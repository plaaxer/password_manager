import { useState } from "react";
import { login } from "../lib/api";
import RegisterPage from "./RegisterPage";

interface Props { onLogin: (masterPassword: string) => void; notice?: string; }

export default function LoginPage({ onLogin, notice }: Props) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  async function signIn(accountName: string, masterPassword: string) {
    await login(accountName, masterPassword);
    onLogin(masterPassword);
  }

  if (showRegister) {
    return <RegisterPage onBack={() => setShowRegister(false)} onRegistered={signIn} />;
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try { await signIn(username, password); }
    catch (err: unknown) { setError(err instanceof Error ? err.message : "Login failed"); }
    finally { setLoading(false); }
  }

  return (
    <div className="desktop"><div className="app-window">
      <header className="app-header"><h1>Argus</h1></header>
      <main className="auth-workspace"><section className="auth-panel">
        <div className="panel-heading">Sign in</div>
        <form onSubmit={handleSubmit}>
          <div className="auth-form">
            <p className="panel-description">Enter your account name and master password.</p>
            {notice && <p className="form-notice" role="status">{notice}</p>}
            <div className="form-row"><label className="form-label" htmlFor="login-username">Account name</label><input id="login-username" required minLength={3} maxLength={50} className="field" value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" autoFocus /></div>
            <div className="form-row"><label className="form-label" htmlFor="login-password">Master password</label><div className="field-with-action"><input id="login-password" required type={showPassword ? "text" : "password"} className="field" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" /><button type="button" className="field-action" onClick={() => setShowPassword((visible) => !visible)}>{showPassword ? "Hide" : "Show"}</button></div></div>
            {error && <p className="form-message" role="alert">{error}</p>}
          </div>
          <div className="auth-actions"><button type="button" className="secondary-action" onClick={() => setShowRegister(true)}>Create Account</button><button type="submit" disabled={loading} className="primary-action">{loading ? "Signing in..." : "Sign In"}</button></div>
        </form>
      </section></main>
    </div></div>
  );
}
