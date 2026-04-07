import { useState } from "react";
import LoginPage from "./pages/LoginPage";
import VaultPage from "./pages/VaultPage";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem("token"));
  const [mp, setMp] = useState("");

  function handleLogin(password: string) {
    setMp(password);
    setLoggedIn(true);
  }

  function handleLogout() {
    setMp("");
    setLoggedIn(false);
  }

  if (!loggedIn) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return <VaultPage masterPassword={mp} onLogout={handleLogout} />;
}