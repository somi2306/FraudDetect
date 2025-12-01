// FraudDetect-feature-auth/frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { ClerkProvider } from '@clerk/clerk-react';
import App from './App';
import './index.css';
import AuthProvider from './providers/AuthProvider'; // <-- 1. Importez le provider

// Récupérez la clé depuis les variables d'environnement
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  throw new Error("Missing Publishable Key");
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <AuthProvider> {/* <-- 2. Enveloppez votre App */}
        <App />
      </AuthProvider>
    </ClerkProvider>
  </React.StrictMode>
);