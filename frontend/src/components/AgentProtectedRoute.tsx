// src/components/AgentProtectedRoute.tsx
// Composant de protection basé sur le JWT de l'Agent

import React from 'react';
import type  { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAgentAuthStore } from "@/stores/useAgentAuthStore"; 
import { Loader } from 'lucide-react'; // Pour afficher un loader pendant l'initialisation

// --- Interface des Props ---
interface AgentProtectedRouteProps {
  children: ReactNode; 
  requiredRole?: string; // Rôle est optionnel, mais peut être utilisé pour la vérification
}

const AgentProtectedRoute: React.FC<AgentProtectedRouteProps> = ({ 
    children, 
    requiredRole 
}) => {
    // Récupérer l'état du store Agent (qui est initialisé dans AgentAuthProvider)
    const { isLoggedIn, user, initializeAuth } = useAgentAuthStore();
    
    // Si l'état n'a pas encore été initialisé depuis le localStorage (similaire à isLoaded de Clerk)
    // Nous devons nous assurer que le store a eu le temps de lire le jeton
    // NOTE: Dans notre architecture, l'AgentAuthProvider gère déjà l'initialisation, 
    // mais une vérification de l'état du store est toujours recommandée.
    // Pour simplifier, nous allons supposer que si isLoggedIn est null/false, 
    // l'AgentAuthProvider a fini son travail.

    // 1. Vérification de la Connexion
    if (!isLoggedIn) {
        // Rediriger vers la page de connexion de l'Agent si le jeton est manquant
        // Note: L'URL doit être /agent/login
        return <Navigate to="/agent/login" replace />; 
    }
    
    // 2. Vérification du Rôle (si spécifié)
    if (requiredRole && (!user || user.role !== requiredRole)) {
        // Rediriger vers un endroit sûr ou afficher un message d'accès refusé
        // Ici, on redirige vers le login pour obliger la reconnexion si le rôle est erroné
        console.warn(`Accès refusé. Rôle requis: ${requiredRole}, Rôle actuel: ${user?.role}`);
        return <Navigate to="/agent/login" replace />; 
    }

    // 3. Affichage du Contenu
    return <>{children}</>;
};

export default AgentProtectedRoute;