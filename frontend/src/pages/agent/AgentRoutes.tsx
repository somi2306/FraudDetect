import { Routes, Route, Navigate } from "react-router-dom";
import AgentProtectedRoute from "@/components/AgentProtectedRoute";
import AgentResetPassword from "./AgentResetPassword";
import AgentDashboard from "./AgentDashboard"; // <-- Import du nouveau fichier

const AgentRoutes = () => {
  return (
    <Routes>
      <Route element={<AgentProtectedRoute />}>
        
        {/* Redirection par défaut vers le dashboard */}
        <Route path="/" element={<Navigate to="dashboard" replace />} />
        
        {/* Le Vrai Dashboard */}
        <Route path="dashboard" element={<AgentDashboard />} />

        {/* Page de changement de mot de passe */}
        <Route path="reset-password" element={<AgentResetPassword />} />
        
      </Route>
    </Routes>
  );
};

export default AgentRoutes;