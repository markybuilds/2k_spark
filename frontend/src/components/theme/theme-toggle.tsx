"use client";

import * as React from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "./theme-provider";
import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  // After component mounts, set mounted to true
  React.useEffect(() => {
    setMounted(true);
  }, []);

  // Render a placeholder button during server-side rendering
  if (!mounted) {
    return (
      <Button
        variant="ghost"
        size="icon"
        className="rounded-full relative overflow-hidden"
        aria-label="Toggle theme"
      >
        <div className="h-5 w-5"></div>
      </Button>
    );
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "light" ? "dark" : "light")}
      className="rounded-full relative overflow-hidden group"
      aria-label="Toggle theme"
    >
      <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full"></div>
      <div className="relative z-10 transition-all duration-500 ease-in-out">
        {theme === "light" ? (
          <Moon className="h-5 w-5 transition-all duration-300 group-hover:text-primary" />
        ) : (
          <Sun className="h-5 w-5 transition-all duration-300 group-hover:text-primary" />
        )}
      </div>
    </Button>
  );
}
