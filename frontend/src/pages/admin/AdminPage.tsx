import React, { useEffect, useState } from "react";
import { useUser } from "@clerk/clerk-react";
import { useNavigate, useLocation } from "react-router-dom";
import { 
  ShieldCheck, 
  UserPlus, 
  Users, 
  LayoutDashboard, 
  Bell,
  Search,
  Menu,
  Landmark
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/axios";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import Sidebar from "@/components/Sidebar";

const StatCard = ({ title, value, icon: Icon, colorClass }: any) => (
    <div className="bg-zinc-800/50 backdrop-blur-sm border border-zinc-700/50 rounded-2xl p-6 relative overflow-hidden group hover:border-zinc-600 transition-all duration-300">
        <div className={`absolute top-0 right-0 w-24 h-24 ${colorClass} opacity-5 rounded-full blur-2xl -mr-10 -mt-10 group-hover:opacity-10 transition-opacity`} />
        <div className="flex justify-between items-start mb-4">
            <div>
                <p className="text-zinc-400 text-sm font-medium mb-1">{title}</p>
                <h3 className="text-3xl font-bold text-white">{value}</h3>
            </div>
            <div className={`p-3 rounded-xl ${colorClass} bg-opacity-10 border border-white/5`}>
                <Icon className={`h-6 w-6 ${colorClass.replace('bg-', 'text-')}`} />
            </div>
        </div>
    </div>
);

const AdminPage: React.FC = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const location = useLocation();

  const [stats, setStats] = useState({
      totalAgents: 0,
      activeAgents: 0,
      totalBanks: 0
  });

  useEffect(() => {
      const fetchData = async () => {
          try {
              const [agentsRes, banksRes] = await Promise.all([
                  apiClient.get("/admin/agents"),
                  apiClient.get("/admin/banks")
              ]);
              const agents = agentsRes.data;
              const banks = banksRes.data;

              setStats({
                  totalAgents: agents.length,
                  activeAgents: agents.filter((a: any) => a.is_active).length,
                  totalBanks: banks.length
              });
          } catch (e) {
              console.error("Erreur chargement données", e);
          }
      };
      fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-zinc-950 text-white font-sans selection:bg-cyan-500/30">
        
        {/* SIDEBAR PARTAGÉE */}
        <Sidebar activePath={location.pathname} />

        <div className="md:ml-64 min-h-screen transition-all duration-300">
            <header className="sticky top-0 z-40 bg-zinc-950/80 backdrop-blur-md border-b border-zinc-800 px-8 py-4 flex items-center justify-between">
                <div className="md:hidden"><Button variant="ghost" size="icon"><Menu className="h-6 w-6 text-zinc-400" /></Button></div>
                <div className="flex-1"></div>
                <div className="flex items-center gap-4 ml-auto">
                    <div className="flex items-center gap-3 pl-4 border-l border-zinc-800">
                        <div className="text-right hidden sm:block">
                            <p className="text-sm font-medium text-white">{user?.fullName}</p>
                            
                        </div>
                        <Avatar className="h-10 w-10 border-2 border-zinc-800">
                            <AvatarImage src={user?.imageUrl} />
                            <AvatarFallback className="bg-cyan-600 text-white">AD</AvatarFallback>
                        </Avatar>
                    </div>
                </div>
            </header>

            <main className="p-8 space-y-8">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-yellow-500 to-orange-500">
                            Tableau de bord
                        </h2>
                        <p className="text-zinc-400 mt-1">Vue d'ensemble de la plateforme.</p>
                    </div>
                </div>

                {/* --- STATISTIQUES AUX COULEURS DES BANQUES --- */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* 1. Banques -> Jaune (Attijari) */}
                    <StatCard 
                        title="Banques Partenaires" 
                        value={stats.totalBanks} 
                        icon={Landmark} 
                        colorClass="bg-yellow-500" 
                    />
                    
                    {/* 2. Total Agents -> Cyan (CIH) */}
                    <StatCard 
                        title="Total Agents" 
                        value={stats.totalAgents} 
                        icon={Users} 
                        colorClass="bg-cyan-500" 
                    />
                    
                    {/* 3. Agents Actifs -> Orange (BCP) */}
                    <StatCard 
                        title="Agents Actifs" 
                        value={stats.activeAgents} 
                        icon={ShieldCheck} 
                        colorClass="bg-orange-500" 
                    />
                </div>

                <div className="grid grid-cols-1 gap-8">
                    <div className="bg-gradient-to-br from-zinc-800 to-zinc-900 border border-zinc-700/50 rounded-2xl p-8 relative overflow-hidden">
                        <div className="relative z-10">
                            <h3 className="text-xl font-bold text-white mb-2">Gestion des Équipes</h3>
                            <p className="text-zinc-400 mb-6 max-w-lg">
                                Gérez les accès des agents bancaires, réinitialisez les mots de passe et surveillez l'activité.
                            </p>
                            <Button onClick={() => navigate("/admin/manage-agents")} variant="outline" className="border-zinc-600 text-zinc-300 hover:text-white hover:bg-zinc-700 hover:border-zinc-500 bg-transparent">
                                <LayoutDashboard className="mr-2 h-4 w-4" /> Accéder à la gestion
                            </Button>
                        </div>
                        {/* Décoration d'arrière-plan avec les couleurs CIH/BCP */}
                        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-cyan-500/10 to-orange-500/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none" />
                    </div>
                </div>
            </main>
        </div>
    </div>
  );
};

export default AdminPage;