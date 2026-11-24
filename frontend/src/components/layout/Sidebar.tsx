import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import {
  LayoutDashboard,
  Globe,
  GitCompare,
  Syringe,
  Activity,
  CalendarDays,
  Database,
  Code,
  HardDrive,
  UserCog,
  ChevronLeft,
  ChevronRight,
  Stethoscope,
  Layout,
  Wifi,
} from "lucide-react";
import clsx from "clsx";

interface NavItem {
  name: string;
  path: string;
  icon: React.ComponentType<any>;
  roles?: ("admin" | "analyst" | "viewer" | "api_user")[];
}

interface NavSection {
  label: string;
  items: NavItem[];
}

const NAV_SECTIONS: NavSection[] = [
  {
    label: "Overview",
    items: [
      { name: "Home Dashboard",     path: "/",           icon: LayoutDashboard },
      { name: "Global Statistics",  path: "/global",     icon: Globe },
      { name: "Country Comparison", path: "/comparison", icon: GitCompare },
    ],
  },
  {
    label: "Analytics",
    items: [
      { name: "Vaccination",        path: "/vaccinations", icon: Syringe },
      { name: "Mortality Burden",   path: "/mortality",    icon: Activity },
      { name: "Hospital Capacity",  path: "/hospital",     icon: Stethoscope },
      { name: "Power BI",           path: "/powerbi",      icon: Layout },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { name: "SQL Explorer",       path: "/explorer",    icon: Database,      roles: ["admin", "analyst"] },
      { name: "API Documentation",  path: "/docs",        icon: Code },
    ],
  },
  {
    label: "Administration",
    items: [
      { name: "ETL Pipeline",       path: "/etl-status",  icon: CalendarDays,  roles: ["admin"] },
      { name: "Pipeline Health",    path: "/health",       icon: HardDrive,     roles: ["admin"] },
      { name: "User Management",    path: "/users",        icon: UserCog,       roles: ["admin"] },
    ],
  },
];

export const Sidebar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();
  const user = useAuthStore((state) => state.user);
  const roleName = user?.role?.name || "viewer";

  const canSee = (item: NavItem) =>
    !item.roles || item.roles.includes(roleName as any);

  return (
    <aside
      className={clsx(
        "glass-panel border-r border-white/5 h-full flex flex-col justify-between transition-all duration-300 ease-in-out z-30 sticky top-0 shrink-0 overflow-hidden",
        isCollapsed ? "w-[70px]" : "w-[240px]"
      )}
    >
      {/* ── Brand Header ── */}
      <div>
        <div className="flex items-center justify-between px-4 h-16 border-b border-white/5">
          {!isCollapsed && (
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div
                className="h-7 w-7 rounded-lg shrink-0 flex items-center justify-center"
                style={{ background: "linear-gradient(135deg,#3b82f6,#8b5cf6)" }}
              >
                <Activity size={14} className="text-white" />
              </div>
              <span className="text-[11px] font-bold tracking-[0.14em] text-slate-300 uppercase whitespace-nowrap">
                COVID‑19 Enterprise
              </span>
            </div>
          )}

          {isCollapsed && (
            <div
              className="h-8 w-8 rounded-lg mx-auto flex items-center justify-center"
              style={{ background: "linear-gradient(135deg,#3b82f6,#8b5cf6)" }}
            >
              <Activity size={16} className="text-white" />
            </div>
          )}

          {!isCollapsed && (
            <button
              onClick={() => setIsCollapsed(true)}
              className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors shrink-0 ml-2"
            >
              <ChevronLeft size={16} />
            </button>
          )}
        </div>

        {/* Live status bar */}
        {!isCollapsed && (
          <div className="px-4 py-2.5 border-b border-white/5 flex items-center gap-2">
            <div className="pulse-dot" />
            <span className="text-[10px] font-semibold text-emerald-400 uppercase tracking-wider">
              Data pipeline: Live
            </span>
          </div>
        )}

        {/* ── Navigation ── */}
        <nav className="py-3 overflow-y-auto flex-1">
          {NAV_SECTIONS.map((section) => {
            const visibleItems = section.items.filter(canSee);
            if (visibleItems.length === 0) return null;

            return (
              <div key={section.label} className="mb-1">
                {!isCollapsed && (
                  <p className="nav-section-label">{section.label}</p>
                )}
                {visibleItems.map((item) => {
                  const isActive =
                    item.path === "/"
                      ? location.pathname === "/"
                      : location.pathname.startsWith(item.path);
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      title={isCollapsed ? item.name : undefined}
                      className={clsx(
                        "nav-item flex items-center gap-3 mx-2 my-0.5 px-3 py-2.5 rounded-lg text-[13px] font-medium",
                        isActive
                          ? "nav-active"
                          : "text-slate-400 hover:text-slate-200"
                      )}
                    >
                      <Icon
                        size={17}
                        className={clsx("shrink-0", isActive ? "text-blue-400" : "")}
                      />
                      {!isCollapsed && (
                        <span className="truncate">{item.name}</span>
                      )}
                    </Link>
                  );
                })}
              </div>
            );
          })}
        </nav>
      </div>

      {/* ── User Footer ── */}
      <div className="border-t border-white/5">
        {isCollapsed ? (
          <div className="flex flex-col items-center gap-2 py-3">
            <div
              className="h-8 w-8 rounded-full flex items-center justify-center text-xs font-black text-white"
              style={{ background: "linear-gradient(135deg,#3b82f6,#8b5cf6)" }}
            >
              {user?.username?.charAt(0).toUpperCase() || "U"}
            </div>
            <button
              onClick={() => setIsCollapsed(false)}
              className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        ) : (
          <div className="px-3 py-3 flex items-center gap-3">
            <div
              className="h-9 w-9 rounded-full flex items-center justify-center text-sm font-black text-white shrink-0"
              style={{ background: "linear-gradient(135deg,#3b82f6,#8b5cf6)", boxShadow: "0 0 14px rgba(59,130,246,0.3)" }}
            >
              {user?.username?.charAt(0).toUpperCase() || "U"}
            </div>
            <div className="truncate flex-1 min-w-0">
              <p className="text-xs font-semibold truncate text-slate-200">
                {user?.full_name || user?.username || "Guest User"}
              </p>
              <span className="inline-block px-1.5 py-0.5 text-[9px] font-bold rounded bg-blue-500/15 text-blue-400 uppercase tracking-wider border border-blue-500/20">
                {roleName}
              </span>
            </div>
            <Wifi size={13} className="text-emerald-400 shrink-0" />
          </div>
        )}
      </div>
    </aside>
  );
};
