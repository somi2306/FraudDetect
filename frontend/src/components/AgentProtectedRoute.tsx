import { useAuthStore } from "@/stores/useAuthStore";
import { useUser } from "@clerk/clerk-react";
import { Navigate, Outlet } from "react-router-dom";
import { Loader } from "lucide-react";

const AgentProtectedRoute = () => {
  const { isLoaded, isSignedIn } = useUser();
  const { role, isLoading } = useAuthStore();

  // 1. Chargement initial de Clerk ou du Store
  if (!isLoaded || isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-zinc-900">
        <Loader className="animate-spin text-emerald-500 h-8 w-8" />
      </div>
    );
  }

  // 2. Vérification Authentification de base
  if (!isSignedIn) {
    return <Navigate to="/auth" replace />;
  }

  // 3. Vérification du Rôle "Agent"
  if (role !== "Agent") {
    // Si l'utilisateur est connecté mais n'est pas Agent (ex: Admin ou Bénéficiaire)
    // On le redirige vers une page non autorisée ou son propre espace
    console.warn("Accès refusé : Rôle actuel =", role);
    return <Navigate to="/" replace />; 
  }

  // 4. Tout est bon, on affiche la route enfant (Dashboard Agent)
  return <Outlet />;
};

export default AgentProtectedRoute;