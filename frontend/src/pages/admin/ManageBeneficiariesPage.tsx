import { useEffect, useState } from "react";
import { apiClient } from "@/lib/axios";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Loader2, Ban, CheckCircle, Search, UserCheck } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import Sidebar from "@/components/Sidebar";
import { useNavigate, useLocation } from "react-router-dom";
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
}

const ManageBeneficiariesPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
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
      fetchBeneficiaries(); // Rafraîchir la liste
    } catch (error) {
      toast({ title: "Erreur", description: "Changement de statut échoué.", variant: "destructive" });
    }
  };

  // Filtrage
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
        
        {/* Header */}
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
                    <p className="text-zinc-400 mt-1">Consultez et modérez les comptes clients.</p>
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
                            <TableHead className="text-zinc-400">Email</TableHead>
                            <TableHead className="text-zinc-400">CIN</TableHead>
                            <TableHead className="text-zinc-400">RIB</TableHead>
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
                            filteredList.map((user) => (
                                <TableRow key={user.id} className="border-zinc-800 hover:bg-zinc-800/30 transition-colors">
                                    <TableCell className="font-medium text-white">
                                        <div className="flex items-center gap-2">
                                            <div className="h-8 w-8 rounded-full bg-zinc-800 flex items-center justify-center text-xs font-bold text-cyan-500 border border-zinc-700">
                                                {user.first_name?.[0]}{user.last_name?.[0]}
                                            </div>
                                            {user.first_name} {user.last_name}
                                        </div>
                                    </TableCell>
                                    <TableCell className="text-zinc-400">{user.email}</TableCell>
                                    <TableCell><Badge variant="outline" className="text-zinc-300 border-zinc-700">{user.cin || 'N/A'}</Badge></TableCell>
                                    <TableCell className="font-mono text-xs text-zinc-500">{user.rib || 'N/A'}</TableCell>
                                    <TableCell>
                                        {user.is_active ? (
                                            <Badge className="bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/20">Actif</Badge>
                                        ) : (
                                            <Badge className="bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20">Suspendu</Badge>
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button 
                                            size="sm" 
                                            variant="ghost" 
                                            onClick={() => handleToggleStatus(user)} 
                                            className={`h-8 px-2 text-zinc-400 hover:bg-zinc-800 ${user.is_active ? "hover:text-red-400" : "hover:text-emerald-400"}`}
                                            title={user.is_active ? "Suspendre le compte" : "Réactiver le compte"}
                                        >
                                            {user.is_active ? <Ban className="h-4 w-4 mr-2" /> : <CheckCircle className="h-4 w-4 mr-2" />}
                                            {user.is_active ? "Suspendre" : "Activer"}
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
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