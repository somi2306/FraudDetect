import React from "react";
import { useClerk, useUser } from "@clerk/clerk-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { LogOut, ShieldCheck, UserPlus, LayoutDashboard } from "lucide-react";

const AdminPage: React.FC = () => {
  const { signOut } = useClerk();
  const { user } = useUser();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut();
    navigate("/auth");
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-zinc-900 text-white p-4 relative overflow-hidden">
        
        {/* Fonds décoratifs flous aux couleurs des banques */}
        <div className="absolute top-0 left-0 w-96 h-96 bg-cyan-600/10 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-orange-600/10 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

        <div className="p-8 bg-zinc-800/80 backdrop-blur-md rounded-2xl border border-zinc-700 shadow-2xl flex flex-col items-center gap-8 max-w-md w-full animate-in fade-in zoom-in duration-300 z-10">
            
            {/* Header / Info User */}
            <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 via-yellow-500 to-orange-500 rounded-full blur opacity-50"></div>
                <div className="relative h-24 w-24 bg-zinc-900 rounded-full flex items-center justify-center border border-zinc-700">
                    <ShieldCheck className="h-12 w-12 text-white" />
                </div>
            </div>
            
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-yellow-400 to-orange-400">
                    Super Admin
                </h1>
                <p className="text-zinc-400">
                    Connecté en tant que <span className="text-white font-semibold">{user?.firstName}</span>
                </p>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-700 text-xs font-medium tracking-wider text-zinc-300">
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                    SYSTÈME SÉCURISÉ
                </div>
            </div>

            <div className="w-full h-px bg-gradient-to-r from-transparent via-zinc-600 to-transparent" />

            {/* Actions */}
            <div className="w-full space-y-4">
                <Button 
                    onClick={() => navigate("/admin/create-agent")}
                    className="w-full h-auto py-4 flex items-center justify-center gap-3 bg-zinc-700 hover:bg-zinc-600 border border-zinc-600 transition-all hover:border-cyan-500 group"
                >
                    <div className="p-2 rounded-full bg-zinc-800 group-hover:bg-cyan-500/20 transition-colors">
                        <UserPlus className="h-5 w-5 text-cyan-400 group-hover:text-cyan-300" />
                    </div>
                    <span className="text-lg font-semibold">Créer un Agent</span>
                </Button>

                <Button 
                    onClick={() => navigate("/admin/dashboard")} // Lien vers un dashboard stats si vous en avez un
                    className="w-full h-auto py-4 flex items-center justify-center gap-3 bg-zinc-700 hover:bg-zinc-600 border border-zinc-600 transition-all hover:border-orange-500 group"
                >
                    <div className="p-2 rounded-full bg-zinc-800 group-hover:bg-orange-500/20 transition-colors">
                        <LayoutDashboard className="h-5 w-5 text-orange-400 group-hover:text-orange-300" />
                    </div>
                    <span className="text-lg font-semibold">Vue d'ensemble</span>
                </Button>
            </div>

            <Button 
                onClick={handleSignOut}
                variant="ghost"
                className="w-full text-red-400 hover:text-red-300 hover:bg-red-900/10 mt-4"
            >
                <LogOut className="h-4 w-4 mr-2" />
                Se déconnecter
            </Button>
        </div>
    </div>
  );
};

export default AdminPage;