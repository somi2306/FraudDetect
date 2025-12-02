import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthenticateWithRedirectCallback } from "@clerk/clerk-react";

// --- PAGES ---
import AuthPage from './pages/auth/AuthPage';
import AuthCallbackPage from './pages/auth-callback/AuthCallbackPage';
import ProfilePage from './pages/profile/ProfilePage';
import AgentRoutes from './pages/agent/AgentRoutes';

// Pages Admin
import AdminPage from './pages/admin/AdminPage';
import AdminTwoFactorSetup from './pages/admin/AdminTwoFactorSetup'; // Assurez-vous que ce fichier est bien créé
import CreateAgentPage from './pages/admin/CreateAgentPage';
// --- COMPOSANTS ---
import SignUpWithEmail from "./components/SignUpWithEmail";
import FloatingShape from "./components/FloatingShape";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* --- CALLBACKS CLERK --- */}
        <Route 
          path="/sso-callback" 
          element={<AuthenticateWithRedirectCallback signUpForceRedirectUrl={"/auth-callback"} />} 
        />
        <Route path="/auth-callback" element={<AuthCallbackPage />} />

        {/* --- AUTHENTIFICATION (Login / Register) --- */}
        <Route path="/auth" element={
          <div className='min-h-screen bg-gradient-to-br from-gray-900 via-green-900 to-emerald-900 flex items-center justify-center relative overflow-hidden'>
            <FloatingShape color='bg-green-500' size='w-64 h-64' top='-5%' left='10%' delay={0} />
            <FloatingShape color='bg-emerald-500' size='w-48 h-48' top='70%' left='80%' delay={5} />
            <FloatingShape color='bg-lime-500' size='w-32 h-32' top='40%' left='-10%' delay={2} />
            <AuthPage />
          </div>
        } />
        
        <Route 
          path="/sign-up-email" 
          element={<div className="h-screen bg-black flex items-center justify-center"><SignUpWithEmail /></div>} 
        />

        {/* --- UTILISATEURS STANDARD --- */}
        <Route path="/profile" element={<ProfilePage />} />

        {/* --- ADMIN --- */}
        {/* Route pour configurer la 2FA (QR Code) si ce n'est pas encore fait */}
        <Route path="/admin/setup-2fa" element={
            <div className="min-h-screen bg-zinc-900">
                <AdminTwoFactorSetup />
            </div>
        } />

        {/* Dashboard Admin (Accessible une fois sécurisé) */}
        <Route path="/admin/dashboard" element={<AdminPage />} />
        <Route path="/admin/create-agent" element={<CreateAgentPage />} />
        {/* --- AGENTS --- */}
        <Route path="/agent/*" element={<AgentRoutes />} />

        {/* --- REDIRECTION PAR DÉFAUT --- */}
        <Route path="/" element={<Navigate to="/auth" replace />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;