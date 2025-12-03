import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import AgentProtectedRoute from "@/components/AgentProtectedRoute";
import AgentResetPassword from "./AgentResetPassword";
import AgentDashboard from "./AgentDashboard";

const AgentRoutes = () => {
  return (
    <Routes>
      {/* Protection Globale pour toutes les sous-routes "/agent/*" 
          Si l'utilisateur n'est pas connecté ou n'est pas un Agent, 
          AgentProtectedRoute le redirigera vers /auth ou / (accueil).
      */}
      <Route element={<AgentProtectedRoute />}>
        
        {/* Redirection par défaut : /agent -> /agent/dashboard */}
        <Route path="/" element={<Navigate to="dashboard" replace />} />
        
        {/* Le Dashboard Principal */}
        <Route path="dashboard" element={<AgentDashboard />} />

        {/* Page de changement de mot de passe (obligatoire au premier login) */}
        <Route path="reset-password" element={<AgentResetPassword />} />
        
      </Route>
    </Routes>
  );
};

export default AgentRoutes;