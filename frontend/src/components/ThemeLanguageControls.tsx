import { Moon, Sun } from "lucide-react";
import { localize, useApp } from "../App";

export function ThemeLanguageControls({ compact = false }: { compact?: boolean }) {
  const { lang, setLang, theme, toggleTheme } = useApp();
  return <div className="preference-controls">
    <button aria-label={localize(lang, "Switch language", "تغییر زبان")} onClick={() => setLang(lang === "en" ? "fa" : "en")}>
      {compact ? (lang === "en" ? "FA" : "EN") : <><span className={lang === "en" ? "active" : ""}>EN</span><i>/</i><span className={lang === "fa" ? "active" : ""}>FA</span></>}
    </button>
    <button className="theme-control" aria-label={localize(lang, "Toggle color theme", "تغییر پوسته رنگی")} onClick={toggleTheme}>
      {theme === "light" ? <Moon size={17}/> : <Sun size={17}/>}
    </button>
  </div>;
}
