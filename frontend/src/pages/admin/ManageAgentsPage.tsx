import { useEffect, useState } from "react";
import { apiClient } from "@/lib/axios";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Loader2, Pencil, Ban, CheckCircle, KeyRound, Search, MailCheck, MailWarning, UserPlus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import Sidebar from "@/components/Sidebar";
import AdminHeader from "@/components/AdminHeader"; // Import

interface Agent {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  bank_name: string;
  is_active: boolean;
}

const ManageAgentsPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [editForm, setEditForm] = useState({ first_name: "", last_name: "" });
  const [isSaving, setIsSaving] = useState(false);

  const fetchAgents = async () => {
    try {
      const res = await apiClient.get("/admin/agents");
      setAgents(res.data);
    } catch (error) {
      toast({ title: "Erreur", description: "Impossible de charger les agents.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAgents(); }, []);

  const handleEditClick = (agent: Agent) => {
    setEditingAgent(agent);
    setEditForm({ first_name: agent.first_name, last_name: agent.last_name });
  };

  const handleSaveEdit = async () => {
    if (!editingAgent) return;
    setIsSaving(true);
    try {
      await apiClient.put(`/admin/agents/${editingAgent.id}`, editForm);
      toast({ title: "Succès", description: "Informations mises à jour.", className: "bg-emerald-600 text-white" });
      setEditingAgent(null);
      fetchAgents();
    } catch (error) {
        toast({ title: "Erreur", description: "Mise à jour échouée.", variant: "destructive" });
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleStatus = async (agent: Agent) => {
    const action = agent.is_active ? "désactiver" : "activer";
    if (!confirm(`Voulez-vous vraiment ${action} cet agent ?`)) return;
    try {
      await apiClient.put(`/admin/agents/${agent.id}/status`);
      toast({ title: "Succès", description: `Agent ${action === "activer" ? "activé" : "désactivé"}.`, className: "bg-emerald-600 text-white" });
      fetchAgents();
    } catch (error) {
      toast({ title: "Erreur", description: "Changement de statut échoué.", variant: "destructive" });
    }
  };

  const handleResetPassword = async (agent: Agent) => {
    if (!confirm("Générer un nouveau mot de passe et l'envoyer par email ?")) return;
    toast({ title: "Traitement...", description: "Envoi de l'email en cours..." });
    try {
      const res = await apiClient.post(`/admin/agents/${agent.id}/reset-password`);
      const { temp_password, email_sent, target_email } = res.data;
      if (email_sent) {
        toast({ title: "Email Envoyé !", description: <div className="flex flex-col gap-1"><span>Envoyé à <strong>{target_email}</strong>.</span><span className="text-xs opacity-80">MDP : {temp_password}</span></div>, className: "bg-emerald-600 text-white border-none", action: <MailCheck className="h-6 w-6 text-white" /> });
      } else {
        toast({ title: "Échec Envoi Email", description: <div className="flex flex-col gap-2"><span>Echec envoi à {target_email}.</span><div className="font-bold bg-white/20 p-2 rounded text-center select-all">{temp_password}</div><span className="text-xs">Transmettre manuellement.</span></div>, variant: "destructive", duration: 10000, action: <MailWarning className="h-6 w-6 text-white" /> });
      }
    } catch (error: any) {
      toast({ title: "Erreur", description: "Réinitialisation échouée.", variant: "destructive" });
    }
  };

  const filteredAgents = agents.filter(a => 
    a.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.bank_name.toLowerCase().includes(searchTerm.toLowerCase())
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
                        Gestion des Agents
                    </h2>
                    <p className="text-gray-500 mt-1">Administrez les comptes et les accès.</p>
                </div>
                
                <div className="flex gap-4 w-full md:w-auto">
                    <div className="relative flex-1 md:w-64">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                        <Input 
                            placeholder="Rechercher..." 
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="pl-10 bg-white border-gray-300 text-gray-900 focus:border-cyan-500 rounded-lg shadow-sm"
                        />
                    </div>
                    <Button 
                        onClick={() => navigate("/admin/create-agent")}
                        className="bg-cyan-600 hover:bg-cyan-700 text-white shadow-md shadow-cyan-200"
                    >
                        <UserPlus className="mr-2 h-4 w-4" /> Ajouter
                    </Button>
                </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                <Table>
                    <TableHeader className="bg-gray-50 border-b border-gray-200">
                        <TableRow className="border-gray-200 hover:bg-gray-100">
                            <TableHead className="text-gray-600 font-semibold">Agent</TableHead>
                            <TableHead className="text-gray-600 font-semibold">Email</TableHead>
                            <TableHead className="text-gray-600 font-semibold">Banque</TableHead>
                            <TableHead className="text-gray-600 font-semibold">Statut</TableHead>
                            <TableHead className="text-right text-gray-600 font-semibold">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow><TableCell colSpan={5} className="text-center h-32"><Loader2 className="mx-auto animate-spin text-cyan-600"/></TableCell></TableRow>
                        ) : filteredAgents.length === 0 ? (
                            <TableRow><TableCell colSpan={5} className="text-center h-32 text-gray-500">Aucun agent trouvé.</TableCell></TableRow>
                        ) : (
                            filteredAgents.map((agent) => (
                                <TableRow key={agent.id} className="border-gray-100 hover:bg-gray-50 transition-colors">
                                    <TableCell className="font-medium text-gray-900">{agent.first_name} {agent.last_name}</TableCell>
                                    <TableCell className="text-gray-600">{agent.email}</TableCell>
                                    <TableCell>
                                        <Badge variant="outline" className="border-cyan-200 text-cyan-700 bg-cyan-50">
                                            {agent.bank_name}
                                        </Badge>
                                    </TableCell>
                                    <TableCell>
                                        {agent.is_active ? (
                                            <Badge className="bg-emerald-100 text-emerald-700 border border-emerald-200 shadow-none hover:bg-emerald-100">Actif</Badge>
                                        ) : (
                                            <Badge className="bg-red-100 text-red-700 border border-red-200 shadow-none hover:bg-red-100">Inactif</Badge>
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <div className="flex items-center justify-end gap-1">
                                            <Button size="icon" variant="ghost" title="Modifier" onClick={() => handleEditClick(agent)} className="h-8 w-8 text-gray-500 hover:text-gray-900 hover:bg-gray-100">
                                                <Pencil className="h-4 w-4" />
                                            </Button>
                                            <Button size="icon" variant="ghost" title="Réinitialiser MDP" onClick={() => handleResetPassword(agent)} className="h-8 w-8 text-gray-500 hover:text-yellow-600 hover:bg-yellow-50">
                                                <KeyRound className="h-4 w-4" />
                                            </Button>
                                            <Button size="icon" variant="ghost" title={agent.is_active ? "Désactiver" : "Activer"} onClick={() => handleToggleStatus(agent)} className={`h-8 w-8 text-gray-500 hover:bg-gray-100 ${agent.is_active ? "hover:text-red-600" : "hover:text-emerald-600"}`}>
                                                {agent.is_active ? <Ban className="h-4 w-4" /> : <CheckCircle className="h-4 w-4" />}
                                            </Button>
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            <Dialog open={!!editingAgent} onOpenChange={(open) => !open && setEditingAgent(null)}>
                <DialogContent className="bg-white border-gray-200 text-gray-900 sm:max-w-[425px]">
                    <DialogHeader><DialogTitle>Modifier l'agent</DialogTitle></DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2"><Label className="text-gray-700">Prénom</Label><Input value={editForm.first_name} onChange={(e) => setEditForm({...editForm, first_name: e.target.value})} className="bg-white border-gray-300 text-gray-900" /></div>
                        <div className="grid gap-2"><Label className="text-gray-700">Nom</Label><Input value={editForm.last_name} onChange={(e) => setEditForm({...editForm, last_name: e.target.value})} className="bg-white border-gray-300 text-gray-900" /></div>
                    </div>
                    <DialogFooter>
                        <Button variant="ghost" onClick={() => setEditingAgent(null)} className="text-gray-600 hover:bg-gray-100">Annuler</Button>
                        <Button onClick={handleSaveEdit} disabled={isSaving} className="bg-cyan-600 hover:bg-cyan-700 text-white">{isSaving ? <Loader2 className="animate-spin h-4 w-4" /> : "Enregistrer"}</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </main>
      </div>
    </div>
  );
};

export default ManageAgentsPage;