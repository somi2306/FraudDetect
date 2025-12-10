import { useEffect, useState } from "react";
import { apiClient } from "@/lib/axios";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Loader2, Ban, CheckCircle, Search, AlertTriangle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import Sidebar from "@/components/Sidebar";
import AdminHeader from "@/components/AdminHeader"; // Import

interface Beneficiary {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  cin: string;
  rib: string;
  is_active: boolean;
  total_cheques: number;
  rejected_cheques: number;
}

const ManageBeneficiariesPage = () => {
  const { toast } = useToast();
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
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <Sidebar />

      <div className="md:ml-64 min-h-screen transition-all duration-300">
        <AdminHeader />

        <main className="p-8 space-y-8 max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-3xl font-bold text-gray-900">
                        Gestion des Bénéficiaires
                    </h2>
                    <p className="text-gray-500 mt-1">Surveillez l'activité et le risque client.</p>
                </div>
                <div className="relative w-full md:w-96">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input 
                        placeholder="Rechercher (Nom, Email, CIN)..." 
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 bg-white border-gray-300 text-gray-900 focus:border-cyan-500 rounded-lg shadow-sm"
                    />
                </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                <Table>
                    <TableHeader className="bg-gray-50 border-b border-gray-200">
                        <TableRow className="border-gray-200 hover:bg-gray-100">
                            <TableHead className="text-gray-600 font-semibold">Bénéficiaire</TableHead>
                            <TableHead className="text-gray-600 font-semibold">Infos Légales</TableHead>
                            <TableHead className="text-gray-600 font-semibold text-center">Activité Chèques</TableHead>
                            <TableHead className="text-gray-600 font-semibold text-center">Risque (Rejets)</TableHead>
                            <TableHead className="text-gray-600 font-semibold">Statut</TableHead>
                            <TableHead className="text-right text-gray-600 font-semibold">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow><TableCell colSpan={6} className="text-center h-32"><Loader2 className="mx-auto animate-spin text-cyan-600"/></TableCell></TableRow>
                        ) : filteredList.length === 0 ? (
                            <TableRow><TableCell colSpan={6} className="text-center h-32 text-gray-500">Aucun bénéficiaire trouvé.</TableCell></TableRow>
                        ) : (
                            filteredList.map((user) => {
                                const rejectionRate = user.total_cheques > 0 
                                    ? Math.round((user.rejected_cheques / user.total_cheques) * 100) 
                                    : 0;
                                const isHighRisk = rejectionRate > 20;

                                return (
                                    <TableRow key={user.id} className="border-gray-100 hover:bg-gray-50 transition-colors">
                                        <TableCell className="font-medium text-gray-900">
                                            <div className="flex flex-col">
                                                <span className="font-bold">{user.first_name} {user.last_name}</span>
                                                <span className="text-xs text-gray-500">{user.email}</span>
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex flex-col gap-1">
                                                <Badge variant="outline" className="w-fit text-gray-600 border-gray-300 text-[10px]">CIN: {user.cin || 'N/A'}</Badge>
                                                <span className="font-mono text-[10px] text-gray-500">{user.rib || 'N/A'}</span>
                                            </div>
                                        </TableCell>
                                        <TableCell className="text-center">
                                            <span className="text-lg font-bold text-gray-900">{user.total_cheques}</span>
                                            <span className="text-xs text-gray-500 block">Total déposés</span>
                                        </TableCell>
                                        <TableCell className="text-center">
                                            <div className="flex flex-col items-center">
                                                {user.rejected_cheques > 0 ? (
                                                    <div className={`flex items-center gap-1 font-bold ${isHighRisk ? 'text-red-600' : 'text-orange-500'}`}>
                                                        {isHighRisk && <AlertTriangle className="h-3 w-3" />}
                                                        {user.rejected_cheques} ({rejectionRate}%)
                                                    </div>
                                                ) : (
                                                    <span className="text-emerald-600 font-medium text-sm">0 (0%)</span>
                                                )}
                                                <span className="text-xs text-gray-500">Rejetés</span>
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            {user.is_active ? (
                                                <Badge className="bg-emerald-100 text-emerald-700 border border-emerald-200 shadow-none">Actif</Badge>
                                            ) : (
                                                <Badge className="bg-red-100 text-red-700 border border-red-200 shadow-none">Suspendu</Badge>
                                            )}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Button 
                                                size="sm" 
                                                variant="ghost" 
                                                onClick={() => handleToggleStatus(user)} 
                                                className={`h-8 px-3 text-gray-500 hover:bg-gray-100 ${user.is_active ? "hover:text-red-600" : "hover:text-emerald-600"}`}
                                            >
                                                {user.is_active ? <Ban className="h-4 w-4 mr-2" /> : <CheckCircle className="h-4 w-4 mr-2" />}
                                                {user.is_active ? "Suspendre" : "Activer"}
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