"use client";

import { createContext, type ReactNode, useContext, useEffect, useState } from "react";
import type { AgentApi } from "./api";

export type DemoLanguage = "en" | "zh";
type Copy = Readonly<Record<string, string>>;
const LanguageContext = createContext({
  language: "en" as DemoLanguage,
  setLanguage: (_language: DemoLanguage) => {},
  t: (text: string) => text,
});

/** Optional: examples without this provider keep their existing English behavior. */
export function DemoLanguageProvider({ api, chinese, children }: { api: AgentApi; chinese: Copy; children: ReactNode }) {
  const [language, setValue] = useState<DemoLanguage>("en");
  function setLanguage(next: DemoLanguage) {
    api.language = next;
    setValue(next);
    localStorage.setItem("retail-demo-language", next);
    document.documentElement.lang = next === "zh" ? "zh-CN" : "en";
  }
  useEffect(() => {
    const saved = localStorage.getItem("retail-demo-language");
    const next = saved === "zh" ? "zh" : "en";
    api.language = next;
    setValue(next);
    document.documentElement.lang = next === "zh" ? "zh-CN" : "en";
  }, [api]);
  function t(text: string): string {
    if (language !== "zh") return text;
    if (chinese[text]) return chinese[text];
    const analysis = /^analysis: step (\d+) — (.+)$/.exec(text);
    if (analysis) return `分析：第${analysis[1]}步 · ${analysis[2].split(", ").map((verb) => chinese[verb] ?? verb).join("、")}`;
    // Tool activity appends the user's query; translate its fixed label only.
    const query = /^(.*?) · (“.*”)$/.exec(text);
    if (query && chinese[`${query[1]}…`]) return `${chinese[`${query[1]}…`].replace(/…$/, "")} · ${query[2]}`;
    return text;
  }
  return <LanguageContext.Provider value={{ language, setLanguage, t }}>{children}</LanguageContext.Provider>;
}

export function useDemoLanguage() {
  return useContext(LanguageContext);
}

export function LanguageSwitch({ disabled = false }: { disabled?: boolean }) {
  const { language, setLanguage } = useDemoLanguage();
  return (
    <button type="button" disabled={disabled} aria-label={language === "en" ? "Switch to Chinese" : "切换为英文"}
      title={language === "zh" ? "切换界面与后续回复的语言；历史对话保留原语言。" : "Switch the interface and future replies; earlier conversation keeps its original language."}
      onClick={() => setLanguage(language === "en" ? "zh" : "en")}
      className="shrink-0 rounded-lg border border-(--line) px-2 py-1 text-xs font-medium disabled:opacity-50">
      {language === "en" ? "中文" : "English"}
    </button>
  );
}
