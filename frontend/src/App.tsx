// FraudDetect-feature-auth/frontend/src/App.tsx
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthPage from './pages/auth/AuthPage';
import AuthCallbackPage from './pages/auth-callback/AuthCallbackPage';
import ProfilePage from './pages/profile/ProfilePage';
import { AuthenticateWithRedirectCallback, useUser } from "@clerk/clerk-react";


import SignUpWithEmail from "./components/SignUpWithEmail";
import FloatingShape from "./components/FloatingShape";

function App() {
  return (
    <BrowserRouter>
      <Routes>

              <Route path="/sso-callback" element={<AuthenticateWithRedirectCallback signUpForceRedirectUrl={"/auth-callback"} />} />
              <Route path="/auth-callback" element={<AuthCallbackPage />} />
              <Route path="/auth" element={
                <div className='min-h-screen bg-gradient-to-br from-gray-900 via-green-900 to-emerald-900 flex items-center justify-center relative overflow-hidden'>
                  <FloatingShape color='bg-green-500' size='w-64 h-64' top='-5%' left='10%' delay={0} />
                  <FloatingShape color='bg-emerald-500' size='w-48 h-48' top='70%' left='80%' delay={5} />
                  <FloatingShape color='bg-lime-500' size='w-32 h-32' top='40%' left='-10%' delay={2} />
                  <AuthPage />
                </div>
              } />
              
              <Route path="/sign-up-email" element={<div className="h-screen bg-black flex items-center justify-center"><SignUpWithEmail /></div>} />
              <Route path="profile" element={<ProfilePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;