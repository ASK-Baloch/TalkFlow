"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("dark"); // "dark" | "light"

  useEffect(() => {
    // Reads a browser-only API (localStorage) unavailable during SSR, so the
    // theme can only be resolved post-mount.
    if (typeof window !== "undefined") {
      const savedTheme = localStorage.getItem("talkflow_theme");
      if (savedTheme === "light") {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setTheme("light");
        document.documentElement.classList.remove("dark");
      } else {
        setTheme("dark");
        document.documentElement.classList.add("dark");
      }
    }
  }, []);

  const toggleTheme = () => {
    setTheme((prevTheme) => {
      const nextTheme = prevTheme === "light" ? "dark" : "light";
      if (typeof window !== "undefined") {
        const root = document.documentElement;
        if (nextTheme === "light") {
          root.classList.remove("dark");
          localStorage.setItem("talkflow_theme", "light");
        } else {
          root.classList.add("dark");
          localStorage.setItem("talkflow_theme", "dark");
        }
      }
      return nextTheme;
    });
  };

  const isDark = theme === "dark";

  return (
    <ThemeContext.Provider value={{ theme, isDark, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}
