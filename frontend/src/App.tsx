import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { api, User } from "./api";
import { CustomerWorkspace } from "./dashboard/CustomerWorkspace";
import { LandingPage } from "./site/LandingPage";

export type Lang = "en" | "fa";
export type Theme = "light" | "dark";

type AppContextValue = {
  lang: Lang;
  setLang: (lang: Lang) => void;
  theme: Theme;
  toggleTheme: () => void;
  user: User | null;
  loading: boolean;
  refreshUser: () => Promise<void>;
  logout: () => void;
};

const AppContext = createContext<AppContextValue | null>(null);

export function useApp() {
  const value = useContext(AppContext);
  if (!value) throw new Error("useApp must be used within AppContext");
  return value;
}

export const localize = <T,>(lang: Lang, en: T, fa: T) => lang === "en" ? en : fa;

function ProtectedWorkspace() {
  const { user, loading } = useApp();
  if (loading) return <div className="route-loader"><span className="brand-bars"><i/><i/><i/><i/></span><p>InsightFlow</p></div>;
  return user ? <CustomerWorkspace /> : <Navigate to="/" replace />;
}

export default function App() {
  const [lang, setLangState] = useState<Lang>(() => (localStorage.getItem("lang") as Lang) || "en");
  const [theme, setTheme] = useState<Theme>(() => (localStorage.getItem("theme") as Theme) || "light");
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = async () => {
    try { setUser(await api.profile()); }
    catch { setUser(null); }
    finally { setLoading(false); }
  };

  useEffect(() => { refreshUser(); }, []);
  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "fa" ? "rtl" : "ltr";
    localStorage.setItem("lang", lang);
  }, [lang]);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", theme === "dark" ? "#0D1B2A" : "#E0E1DD");
    localStorage.setItem("theme", theme);
  }, [theme]);

  const value = useMemo<AppContextValue>(() => ({
    lang,
    setLang: setLangState,
    theme,
    toggleTheme: () => setTheme(current => current === "light" ? "dark" : "light"),
    user,
    loading,
    refreshUser,
    logout: () => { api.tokens.clear(); setUser(null); }
  }), [lang, theme, user, loading]);

  return <AppContext.Provider value={value}>
    <Routes>
      <Route path="/app/*" element={<ProtectedWorkspace />} />
      <Route path="/*" element={<LandingPage />} />
    </Routes>
  </AppContext.Provider>;
}
