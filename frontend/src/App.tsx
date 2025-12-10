/*import React from "react";*/
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthenticateWithRedirectCallback, useUser } from "@clerk/clerk-react";

// --- UI IMPORTS ---
import { Toaster } from "@/components/ui/toaster"; 
import FloatingShape from "./components/FloatingShape";

// --- PROVIDERS ---
import AuthProvider from "./providers/AuthProvider";
import { BeneficiaryProvider } from './pages/beneficiary/BeneficiaryContext';

// --- AUTH PAGES ---
import AuthPage from './pages/auth/AuthPage';
import AuthCallbackPage from './pages/auth-callback/AuthCallbackPage';
import SignUpWithEmail from "./components/SignUpWithEmail";

// --- PROFILE PAGES ---
import ProfilePage from './pages/profile/ProfilePage';
import AdminProfilePage from './pages/admin/AdminProfilePage';

// --- ADMIN PAGES ---
import AdminPage from './pages/admin/AdminPage';
import CreateAgentPage from './pages/admin/CreateAgentPage';
import AdminTwoFactorSetup from './pages/admin/AdminTwoFactorSetup';
import ManageAgentsPage from './pages/admin/ManageAgentsPage';
import ManageBeneficiariesPage from './pages/admin/ManageBeneficiariesPage'; // Import
// --- AGENT ROUTES ---
import AgentRoutes from './pages/agent/AgentRoutes';

// --- BENEFICIARY IMPORTS ---
import BeneficiaryLayout from './pages/beneficiary/layouts/BeneficiaryLayout';
import Dashboard from './pages/beneficiary/Dashboard';
import CheckList from './pages/beneficiary/components/CheckList';
import CheckHistory from './pages/beneficiary/components/CheckHistory';
import Notifications from './pages/beneficiary/components/Notifications';

// --- ROUTE GUARD (POUR BENEFICIAIRE) ---
// Note : Pour Admin et Agent, la protection est gérée dans leurs composants respectifs (AgentRoutes / AdminPage)
const BeneficiaryProtectedRoute = () => {
  const { isLoaded, isSignedIn } = useUser();

  if (!isLoaded) {
    return <div className="flex h-screen items-center justify-center">Chargement...</div>; 
  }

  if (isSignedIn) {
    return <Outlet />;
  }

  return <Navigate to="/auth" replace />;
};

function App() {
  return (
    <BrowserRouter>
      {/* AuthProvider gère Clerk globalement */}
      <AuthProvider>
        {/* BeneficiaryProvider gère le contexte spécifique aux bénéficiaires */}
        <BeneficiaryProvider>
          
          <Routes>
            {/* --- 1. AUTHENTICATION --- */}
            <Route path="/sso-callback" element={<AuthenticateWithRedirectCallback signUpForceRedirectUrl={"/auth-callback"} />} />
            <Route path="/auth-callback" element={<AuthCallbackPage />} />
            <Route path="/sign-up-email" element={<div className="h-screen bg-black flex items-center justify-center"><SignUpWithEmail /></div>} />
            
            {/* Page de Connexion Unifiée (Design Cyan/Jaune/Orange) */}
            <Route path="/auth" element={
              <div className='min-h-screen bg-gradient-to-br from-cyan-950 via-gray-900 to-orange-950 flex items-center justify-center relative overflow-hidden'>
                <FloatingShape color='bg-cyan-500' size='w-64 h-64' top='-5%' left='10%' delay={0} />
                <FloatingShape color='bg-yellow-500' size='w-48 h-48' top='70%' left='80%' delay={5} />
                <FloatingShape color='bg-orange-500' size='w-32 h-32' top='40%' left='-10%' delay={2} />
                <AuthPage />
              </div>
            } />

            {/* --- 2. PROFILE --- */}
            <Route path="/profile" element={<ProfilePage />} />

            {/* --- 3. ESPACE ADMIN --- */}
            <Route path="/admin/setup-2fa" element={<div className="min-h-screen bg-zinc-900"><AdminTwoFactorSetup /></div>} />
            <Route path="/admin/dashboard" element={<AdminPage />} />
            <Route path="/admin/create-agent" element={<CreateAgentPage />} />
            <Route path="/admin/manage-agents" element={<ManageAgentsPage />} />
            <Route path="/admin/manage-beneficiaries" element={<ManageBeneficiariesPage />} />
            <Route path="/admin/profile" element={<AdminProfilePage />} />
            {/* --- 4. ESPACE AGENT --- */}
            <Route path="/agent/*" element={<AgentRoutes />} />

            {/* --- 5. ESPACE BENEFICIAIRE (PROTECTED) --- */}
            <Route element={<BeneficiaryProtectedRoute />}>
               <Route path="/beneficiary" element={<BeneficiaryLayout />}>
                   <Route index element={<Dashboard />} />
                   <Route path="checks" element={<CheckList />} />
                   <Route path="history" element={<CheckHistory />} />
                   <Route path="notifications" element={<Notifications />} />
               </Route>
            </Route>

            {/* --- 6. REDIRECTION PAR DÉFAUT --- */}
            <Route path="/" element={<Navigate to="/auth" replace />} />
          </Routes>

          {/* Toast Notification System */}
          <Toaster />

        </BeneficiaryProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;