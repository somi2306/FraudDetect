import React from "react";
import { useClerk, useUser } from "@clerk/clerk-react";
import { useAuthStore } from "@/stores/useAuthStore";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { LogOut, Building2, Wallet } from "lucide-react";

const AgentDashboard = () => {
  const { signOut } = useClerk();
  const { user } = useUser();
  const { bankId } = useAuthStore();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    // Déconnexion Clerk -> Redirection vers la page de login unique
    await signOut();
    navigate("/auth");
  };

  return (
    <div className="min-h-screen bg-zinc-900 text-white p-6">
      {/* --- Header / Barre de navigation --- */}
      <header className="flex flex-col md:flex-row justify-between items-center mb-8 bg-zinc-800 p-4 rounded-xl border border-zinc-700 shadow-lg gap-4">
        
        <div className="flex items-center gap-4">
            <div className="h-12 w-12 bg-emerald-500/20 rounded-full flex items-center justify-center ring-1 ring-emerald-500/50">
                <Building2 className="h-6 w-6 text-emerald-500" />
            </div>
            <div>
                <h1 className="text-xl font-bold text-white">Espace Bancaire</h1>
                <div className="flex items-center gap-2 text-sm text-zinc-400">
                    <span className="bg-zinc-700 px-2 py-0.5 rounded text-xs font-mono text-emerald-400">
                        BANK-ID: {bankId || "Chargement..."}
                    </span>
                    <span>• {user?.firstName} {user?.lastName}</span>
                </div>
            </div>
        </div>

        <div className="flex items-center gap-4 w-full md:w-auto">
            <Button 
                onClick={handleSignOut} 
                variant="destructive"
                className="w-full md:w-auto bg-red-600 hover:bg-red-700 text-white font-semibold shadow-md transition-all hover:scale-105"
            >
                <LogOut className="h-4 w-4 mr-2" />
                Se déconnecter
            </Button>
        </div>
      </header>

      {/* --- Contenu Principal (Exemple) --- */}
      <main className="grid gap-6 md:grid-cols-3">
        {/* Carte Statistique 1 */}
        <div className="p-6 bg-zinc-800 rounded-xl border border-zinc-700 hover:border-emerald-500/50 transition-colors cursor-pointer">
            <div className="flex justify-between items-start mb-4">
                <div className="p-2 bg-emerald-900/30 rounded-lg">
                    <Wallet className="h-6 w-6 text-emerald-400" />
                </div>
                <span className="text-xs font-medium bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded-full">+12%</span>
            </div>
            <h3 className="text-zinc-400 text-sm font-medium">Chèques traités</h3>
            <p className="text-3xl font-bold text-white mt-2">0</p>
        </div>

        {/* Vous pourrez ajouter d'autres widgets ici */}
      </main>
    </div>
  );
};

export default AgentDashboard;