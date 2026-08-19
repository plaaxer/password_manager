import { useEffect, useState } from "react";
import LoginPage from "./pages/LoginPage";
import VaultPage from "./pages/VaultPage";
import { logout, UNAUTHORIZED_EVENT } from "./lib/api";
import "./App.css";

export default function App() {
  const [masterPassword, setMasterPassword] = useState("");
  const [notice, setNotice] = useState(() => {
    const wasAuthenticated = Boolean(localStorage.getItem("token"));
    logout();
    return wasAuthenticated ? "The vault was locked when the application restarted." : "";
  });

  const loggedIn = masterPassword.length > 0;

  useEffect(() => {
    function handleUnauthorized() {
      setMasterPassword("");
      setNotice("Your session expired. Sign in again.");
    }
    window.addEventListener(UNAUTHORIZED_EVENT, handleUnauthorized);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, handleUnauthorized);
  }, []);

  function handleLogin(password: string) {
    setMasterPassword(password);
    setNotice("");
  }

  function handleLogout(reason?: string) {
    logout();
    setMasterPassword("");
    setNotice(reason ?? "");
  }

  if (!loggedIn) return <LoginPage onLogin={handleLogin} notice={notice} />;
  return <VaultPage masterPassword={masterPassword} onLogout={handleLogout} />;
}
