import { useEffect, useState } from "react";
import { apiClient } from "@/lib/axios";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Loader2, Ban, CheckCircle, Search, AlertTriangle } from "lucide-react"; // Import AlertTriangle
import { useToast } from "@/hooks/use-toast";
import Sidebar from "@/components/Sidebar";
import { useUser } from "@clerk/clerk-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface Beneficiary {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  cin: string;
  rib: string;
  is_active: boolean;
  total_cheques: number;    // Nouveau
  rejected_cheques: number; // Nouveau
}

const ManageBeneficiariesPage = () => {
  const { toast } = useToast();
  const { user } = useUser();

  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  const fetchBeneficiaries = async () => {
    try {
      const res = await apiClient.get("/admin/beneficiaries");
      setBeneficiaries(res.data);
    } catch (error) {
      toast({ title: "Erreur", description: "Impossible de charger les bénéficiaires.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchBeneficiaries(); }, []);

  const handleToggleStatus = async (beneficiary: Beneficiary) => {
    const action = beneficiary.is_active ? "désactiver" : "activer";
    if (!confirm(`Voulez-vous vraiment ${action} ce bénéficiaire ?`)) return;
    try {
      await apiClient.put(`/admin/beneficiaries/${beneficiary.id}/status`);
      toast({ title: "Succès", description: `Compte ${action === "activer" ? "activé" : "désactivé"}.`, className: "bg-emerald-600 text-white" });
      fetchBeneficiaries();
    } catch (error) {
      toast({ title: "Erreur", description: "Changement de statut échoué.", variant: "destructive" });
    }
  };

  const filteredList = beneficiaries.filter(b => 
    (b.first_name?.toLowerCase() || "").includes(searchTerm.toLowerCase()) ||
    (b.last_name?.toLowerCase() || "").includes(searchTerm.toLowerCase()) ||
    (b.email?.toLowerCase() || "").includes(searchTerm.toLowerCase()) ||
    (b.cin?.toLowerCase() || "").includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-zinc-950 text-white font-sans selection:bg-cyan-500/30">
      <Sidebar activePath={location.pathname} />

      <div className="md:ml-64 min-h-screen transition-all duration-300">
        <header className="sticky top-0 z-40 bg-zinc-950/80 backdrop-blur-md border-b border-zinc-800 px-8 py-4 flex items-center justify-between">
            <div className="flex-1"></div>
            <div className="flex items-center gap-3 pl-4 border-l border-zinc-800">
                <div className="text-right hidden sm:block">
                    <p className="text-sm font-medium text-white">{user?.fullName}</p>
                    <p className="text-xs text-zinc-500">Super Admin</p>
                </div>
                <Avatar className="h-10 w-10 border-2 border-zinc-800">
                    <AvatarImage src={user?.imageUrl} />
                    <AvatarFallback className="bg-cyan-600 text-white">AD</AvatarFallback>
                </Avatar>
            </div>
        </header>

        <main className="p-8 space-y-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600">
                        Gestion des Bénéficiaires
                    </h2>
                    <p className="text-zinc-400 mt-1">Surveillez l'activité et le risque client.</p>
                </div>
                <div className="relative w-full md:w-96">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                    <Input 
                        placeholder="Rechercher (Nom, Email, CIN)..." 
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 bg-zinc-900 border-zinc-700 text-white focus:border-cyan-500"
                    />
                </div>
            </div>

            <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl">
                <Table>
                    <TableHeader className="bg-zinc-900 border-b border-zinc-800">
                        <TableRow className="border-zinc-800 hover:bg-zinc-900">
                            <TableHead className="text-zinc-400">Bénéficiaire</TableHead>
                            <TableHead className="text-zinc-400">Infos Légales</TableHead>
                            <TableHead className="text-zinc-400 text-center">Activité Chèques</TableHead>
                            <TableHead className="text-zinc-400 text-center">Risque (Rejets)</TableHead>
                            <TableHead className="text-zinc-400">Statut</TableHead>
                            <TableHead className="text-right text-zinc-400">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow><TableCell colSpan={6} className="text-center h-32"><Loader2 className="mx-auto animate-spin text-cyan-500"/></TableCell></TableRow>
                        ) : filteredList.length === 0 ? (
                            <TableRow><TableCell colSpan={6} className="text-center h-32 text-zinc-500">Aucun bénéficiaire trouvé.</TableCell></TableRow>
                        ) : (
                            filteredList.map((user) => {
                                // Calcul du pourcentage de rejet pour l'affichage visuel
                                const rejectionRate = user.total_cheques > 0 
                                    ? Math.round((user.rejected_cheques / user.total_cheques) * 100) 
                                    : 0;
                                const isHighRisk = rejectionRate > 20; // Seuil d'alerte arbitraire à 20%

                                return (
                                    <TableRow key={user.id} className="border-zinc-800 hover:bg-zinc-800/30 transition-colors">
                                        <TableCell className="font-medium text-white">
                                            <div className="flex flex-col">
                                                <span className="font-bold">{user.first_name} {user.last_name}</span>
                                                <span className="text-xs text-zinc-500">{user.email}</span>
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex flex-col gap-1">
                                                <Badge variant="outline" className="w-fit text-zinc-300 border-zinc-700 text-[10px]">CIN: {user.cin || 'N/A'}</Badge>
                                                <span className="font-mono text-[10px] text-zinc-500">{user.rib || 'N/A'}</span>
                                            </div>
                                        </TableCell>
                                        
                                        {/* COLONNE ACTIVITÉ */}
                                        <TableCell className="text-center">
                                            <span className="text-lg font-bold text-white">{user.total_cheques}</span>
                                            <span className="text-xs text-zinc-500 block">Total déposés</span>
                                        </TableCell>

                                        {/* COLONNE RISQUE */}
                                        <TableCell className="text-center">
                                            <div className="flex flex-col items-center">
                                                {user.rejected_cheques > 0 ? (
                                                    <div className={`flex items-center gap-1 font-bold ${isHighRisk ? 'text-red-500' : 'text-orange-400'}`}>
                                                        {isHighRisk && <AlertTriangle className="h-3 w-3" />}
                                                        {user.rejected_cheques} ({rejectionRate}%)
                                                    </div>
                                                ) : (
                                                    <span className="text-emerald-500 font-medium text-sm">0 (0%)</span>
                                                )}
                                                <span className="text-xs text-zinc-500">Rejetés</span>
                                            </div>
                                        </TableCell>

                                        <TableCell>
                                            {user.is_active ? (
                                                <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">Actif</Badge>
                                            ) : (
                                                <Badge className="bg-red-500/10 text-red-400 border-red-500/20">Suspendu</Badge>
                                            )}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Button 
                                                size="sm" 
                                                variant="ghost" 
                                                onClick={() => handleToggleStatus(user)} 
                                                className={`h-8 px-3 text-zinc-400 hover:bg-zinc-800 ${user.is_active ? "hover:text-red-400" : "hover:text-emerald-400"}`}
                                            >
                                                {user.is_active ? <Ban className="h-4 w-4 mr-2" /> : <CheckCircle className="h-4 w-4 mr-2" />}
                                                {user.is_active ? "Bannir" : "Activer"}
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                );
                            })
                        )}
                    </TableBody>
                </Table>
            </div>
        </main>
      </div>
    </div>
  );
};

export default ManageBeneficiariesPage;