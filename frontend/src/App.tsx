import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthenticateWithRedirectCallback } from "@clerk/clerk-react";

// --- IMPORT DU TOASTER ---
import { Toaster } from "@/components/ui/toaster"; 

// Pages
import AuthPage from './pages/auth/AuthPage';
import AuthCallbackPage from './pages/auth-callback/AuthCallbackPage';
import ProfilePage from './pages/profile/ProfilePage';
import AgentRoutes from './pages/agent/AgentRoutes'; 
import AdminPage from './pages/admin/AdminPage';
import CreateAgentPage from './pages/admin/CreateAgentPage';
import AdminTwoFactorSetup from './pages/admin/AdminTwoFactorSetup';
import ManageAgentsPage from './pages/admin/ManageAgentsPage'; // Assurez-vous que cette route est bien là

// Composants
import SignUpWithEmail from "./components/SignUpWithEmail";
import FloatingShape from "./components/FloatingShape";
import AuthProvider from "./providers/AuthProvider";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/sso-callback" element={<AuthenticateWithRedirectCallback signUpForceRedirectUrl={"/auth-callback"} />} />
          <Route path="/auth-callback" element={<AuthCallbackPage />} />
          
          <Route path="/auth" element={
            <div className='min-h-screen bg-gradient-to-br from-cyan-950 via-gray-900 to-orange-950 flex items-center justify-center relative overflow-hidden'>
              <FloatingShape color='bg-cyan-500' size='w-64 h-64' top='-5%' left='10%' delay={0} />
              <FloatingShape color='bg-yellow-500' size='w-48 h-48' top='70%' left='80%' delay={5} />
              <FloatingShape color='bg-orange-500' size='w-32 h-32' top='40%' left='-10%' delay={2} />
              <AuthPage />
            </div>
          } />

          <Route path="/sign-up-email" element={<div className="h-screen bg-black flex items-center justify-center"><SignUpWithEmail /></div>} />
          <Route path="/profile" element={<ProfilePage />} />

          {/* Routes Admin */}
          <Route path="/admin/setup-2fa" element={<div className="min-h-screen bg-zinc-900"><AdminTwoFactorSetup /></div>} />
          <Route path="/admin/dashboard" element={<AdminPage />} />
          <Route path="/admin/create-agent" element={<CreateAgentPage />} />
          <Route path="/admin/manage-agents" element={<ManageAgentsPage />} />

          {/* Routes Agent */}
          <Route path="/agent/*" element={<AgentRoutes />} />

          <Route path="/" element={<Navigate to="/auth" replace />} />
        </Routes>

        {/* --- AJOUTER LE COMPOSANT TOASTER ICI --- */}
        <Toaster />
        
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;