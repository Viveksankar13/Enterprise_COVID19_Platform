import React from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { Footer } from "./Footer";

export const AppShell: React.FC = () => {
  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground transition-all duration-300 relative">
      {/* Animated aurora background */}
      <div className="aurora-bg" aria-hidden="true" />

      {/* Collapsible Sidebar — occupies full height, never scrolls with page */}
      <Sidebar />

      {/* Main Content Area — fills remaining width, scrolls independently */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopBar />

        {/* Router Viewport — the only scrollable region */}
        <main className="flex-1 overflow-y-auto">
          {/* Centered content wrapper — prevents stretching on wide screens */}
          <div className="w-full max-w-[1600px] mx-auto px-6 md:px-8 py-6 md:py-8">
            <Outlet />
          </div>
        </main>

        <Footer />
      </div>
    </div>
  );
};
