import React from "react";
import { useClerk, useUser } from "@clerk/clerk-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { LogOut, ShieldCheck, UserPlus } from "lucide-react"; // Import UserPlus

const AdminPage: React.FC = () => {
  const { signOut } = useClerk();
  const { user } = useUser();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut();
    navigate("/auth");
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-zinc-900 text-white p-4">
        <div className="p-8 bg-zinc-800 rounded-xl border border-zinc-700 shadow-2xl flex flex-col items-center gap-6 max-w-md w-full animate-in fade-in zoom-in duration-300">
            
            {/* Header / Info User comme avant ... */}
            <div className="h-20 w-20 bg-emerald-500/20 rounded-full flex items-center justify-center ring-2 ring-emerald-500/50">
                <ShieldCheck className="h-10 w-10 text-emerald-500" />
            </div>
            
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-bold text-white">Espace Admin</h1>
                <p className="text-zinc-400">
                    <span className="text-emerald-400 font-semibold">{user?.fullName}</span>
                </p>
                <div className="inline-flex items-center px-3 py-1 rounded-full bg-emerald-900/50 border border-emerald-800 text-emerald-400 text-xs font-medium uppercase tracking-wider">
                    ● Accès Sécurisé
                </div>
            </div>

            <div className="w-full h-px bg-zinc-700 my-2" />

            {/* --- NOUVEAU BOUTON : CRÉER UN AGENT --- */}
            <Button 
                onClick={() => navigate("/admin/create-agent")}
                className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-6"
            >
                <UserPlus className="h-5 w-5" />
                Créer un compte Agent
            </Button>

            <Button 
                onClick={handleSignOut}
                variant="outline" // Changé en outline pour donner priorité à l'action principale
                className="w-full flex items-center justify-center gap-2 border-red-900/50 text-red-400 hover:bg-red-900/20 hover:text-red-300 py-4"
            >
                <LogOut className="h-4 w-4" />
                Se déconnecter
            </Button>
        </div>
    </div>
  );
};

export default AdminPage;