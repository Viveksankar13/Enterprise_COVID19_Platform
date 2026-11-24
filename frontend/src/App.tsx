import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppShell } from "./components/layout/AppShell";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";

// Pages
import { Home } from "./pages/Home";
import { GlobalStatistics } from "./pages/dashboard/GlobalStatistics";
import { CountryComparison } from "./pages/dashboard/CountryComparison";
import { VaccinationAnalytics } from "./pages/analytics/VaccinationAnalytics";
import { MortalityAnalytics } from "./pages/analytics/MortalityAnalytics";
import { HospitalDashboard } from "./pages/analytics/HospitalDashboard";
import { SQLExplorer } from "./pages/dashboard/SQLExplorer";
import { APIDocs } from "./pages/admin/APIDocs";
import { ETLStatus } from "./pages/admin/ETLStatus";
import { PipelineHealth } from "./pages/admin/PipelineHealth";
import { UserManagement } from "./pages/admin/UserManagement";
import { Login } from "./pages/auth/Login";
import { Unauthorized } from "./pages/auth/Unauthorized";
import { PowerBIDashboard } from "./pages/dashboard/PowerBIDashboard";

// Initialize Query Client for API Caching
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/unauthorized" element={<Unauthorized />} />

          {/* Secure Layout Portal Shell */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppShell />
              </ProtectedRoute>
            }
          >
            {/* Secured Pages */}
            <Route index element={<Home />} />
            
            <Route path="global" element={<GlobalStatistics />} />
            
            <Route path="comparison" element={<CountryComparison />} />
            
            <Route path="vaccinations" element={<VaccinationAnalytics />} />
            
            <Route path="mortality" element={<MortalityAnalytics />} />
            
            <Route path="hospital" element={<HospitalDashboard />} />
            
            <Route
              path="explorer"
              element={
                <ProtectedRoute allowedRoles={["admin", "analyst"]}>
                  <SQLExplorer />
                </ProtectedRoute>
              }
            />
            
            <Route path="docs" element={<APIDocs />} />
            
            <Route path="powerbi" element={<PowerBIDashboard />} />

            {/* Admin Only Routes */}
            <Route
              path="etl-status"
              element={
                <ProtectedRoute allowedRoles={["admin"]}>
                  <ETLStatus />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="health"
              element={
                <ProtectedRoute allowedRoles={["admin"]}>
                  <PipelineHealth />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="users"
              element={
                <ProtectedRoute allowedRoles={["admin"]}>
                  <UserManagement />
                </ProtectedRoute>
              }
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
