import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  ShieldCheck, 
  Users, 
  LayoutDashboard, 
  Landmark,
  UserCheck
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/axios";
import Sidebar from "@/components/Sidebar";
import AdminHeader from "@/components/AdminHeader";

// Composant StatCard adapté au thème clair
const StatCard = ({ title, value, icon: Icon, colorClass, bgClass, textClass }: any) => (
    <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-300 relative overflow-hidden group">
        <div className={`absolute top-0 right-0 w-24 h-24 ${bgClass} opacity-10 rounded-full blur-2xl -mr-10 -mt-10 transition-opacity`} />
        <div className="flex justify-between items-start mb-4 relative z-10">
            <div>
                <p className="text-gray-500 text-sm font-medium mb-1">{title}</p>
                <h3 className="text-3xl font-bold text-gray-900">{value}</h3>
            </div>
            <div className={`p-3 rounded-xl ${bgClass} bg-opacity-20 border ${colorClass.replace('text-', 'border-')} border-opacity-20`}>
                <Icon className={`h-6 w-6 ${textClass}`} />
            </div>
        </div>
    </div>
);

const AdminPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
      totalAgents: 0,
      activeAgents: 0,
      totalBanks: 0,
      totalBeneficiaries: 0
  });

  useEffect(() => {
      const fetchData = async () => {
          try {
              const [agentsRes, banksRes, benefRes] = await Promise.all([
                  apiClient.get("/admin/agents"),
                  apiClient.get("/admin/banks"),
                  apiClient.get("/admin/beneficiaries")
              ]);
              const agents = agentsRes.data;
              const banks = banksRes.data;
              const benefs = benefRes.data;

              setStats({
                  totalAgents: agents.length,
                  activeAgents: agents.filter((a: any) => a.is_active).length,
                  totalBanks: banks.length,
                  totalBeneficiaries: benefs.length
              });
          } catch (e) {
              console.error("Erreur chargement données", e);
          }
      };
      fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
        
        {/* Sidebar partagée */}
        <Sidebar />

        <div className="md:ml-64 min-h-screen transition-all duration-300">
            
            {/* Header partagé */}
            <AdminHeader />

            <main className="p-8 space-y-8 max-w-7xl mx-auto">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h2 className="text-3xl font-bold text-gray-900">
                            Tableau de bord
                        </h2>
                        <p className="text-gray-500 mt-1">Vue d'ensemble de la plateforme et des statistiques.</p>
                    </div>
                </div>

                {/* --- STATISTIQUES (3 Couleurs uniquement : Jaune, Cyan, Orange) --- */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {/* 1. Banques -> Jaune */}
                    <StatCard 
                        title="Banques" 
                        value={stats.totalBanks} 
                        icon={Landmark} 
                        bgClass="bg-yellow-100" 
                        textClass="text-yellow-600"
                        colorClass="text-yellow-600"
                    />
                    
                    {/* 2. Total Agents -> Cyan */}
                    <StatCard 
                        title="Agents" 
                        value={stats.totalAgents} 
                        icon={Users} 
                        bgClass="bg-cyan-100" 
                        textClass="text-cyan-600"
                        colorClass="text-cyan-600"
                    />
                    
                    {/* 3. Agents Actifs -> Orange */}
                    <StatCard 
                        title="Agents Actifs" 
                        value={stats.activeAgents} 
                        icon={ShieldCheck} 
                        bgClass="bg-orange-100" 
                        textClass="text-orange-600"
                        colorClass="text-orange-600"
                    />

                    {/* 4. Bénéficiaires -> Cyan (Réutilisation pour cohérence) */}
                    <StatCard 
                        title="Bénéficiaires" 
                        value={stats.totalBeneficiaries} 
                        icon={UserCheck} 
                        bgClass="bg-cyan-100" 
                        textClass="text-cyan-600"
                        colorClass="text-cyan-600"
                    />
                </div>

                {/* Section d'action rapide */}
                <div className="grid grid-cols-1 gap-8">
                    <div className="bg-white border border-gray-200 rounded-2xl p-8 relative overflow-hidden shadow-sm">
                        <div className="relative z-10">
                            <h3 className="text-xl font-bold text-gray-900 mb-2">Gestion des Équipes</h3>
                            <p className="text-gray-500 mb-6 max-w-lg">
                                Accédez à la liste complète des agents pour en ajouter de nouveaux, modifier leurs informations ou gérer leurs accès.
                            </p>
                            <Button 
                                onClick={() => navigate("/admin/manage-agents")} 
                                variant="outline" 
                                className="border-gray-300 text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                            >
                                <LayoutDashboard className="mr-2 h-4 w-4" /> Accéder à la gestion
                            </Button>
                        </div>
                        {/* Décoration de fond (Cyan/Orange) */}
                        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-cyan-50 to-orange-50 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none" />
                    </div>
                </div>
            </main>
        </div>
    </div>
  );
};

export default AdminPage;