import { useEffect, useState } from "react";
import { apiClient } from "@/lib/axios";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { 
  Loader2, 
  Pencil, 
  Ban, 
  CheckCircle, 
  KeyRound, 
  Search, 
  MailCheck, 
  MailWarning, 
  UserPlus, 
  Menu,
  Filter,
  RefreshCw,
  Users,
  Building,
  Mail
} from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { useUser } from "@clerk/clerk-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import Sidebar from "@/components/Sidebar";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

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
  const location = useLocation();
  const { toast } = useToast();
  const { user } = useUser();

  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [bankFilter, setBankFilter] = useState<string>("all");

  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [editForm, setEditForm] = useState({ first_name: "", last_name: "" });
  const [isSaving, setIsSaving] = useState(false);
  const [resetDialog, setResetDialog] = useState<{show: boolean, agent: Agent | null}>({ show: false, agent: null });

  const fetchAgents = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get("/admin/agents");
      setAgents(res.data);
    } catch (error) {
      toast({ 
        title: "Erreur", 
        description: "Impossible de charger les agents.", 
        variant: "destructive" 
      });
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
      toast({ 
        title: "Succès", 
        description: "Informations mises à jour.", 
        className: "bg-emerald-900 border-emerald-700 text-white" 
      });
      setEditingAgent(null);
      fetchAgents();
    } catch (error) {
      toast({ 
        title: "Erreur", 
        description: "Mise à jour échouée.", 
        variant: "destructive" 
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleStatus = async (agent: Agent) => {
    const action = agent.is_active ? "désactiver" : "activer";
    if (!confirm(`Voulez-vous vraiment ${action} l'agent ${agent.first_name} ${agent.last_name} ?`)) return;
    try {
      await apiClient.put(`/admin/agents/${agent.id}/status`);
      toast({ 
        title: "Succès", 
        description: `Agent ${action === "activer" ? "activé" : "désactivé"} avec succès.`, 
        className: "bg-emerald-900 border-emerald-700 text-white" 
      });
      fetchAgents();
    } catch (error) {
      toast({ 
        title: "Erreur", 
        description: "Changement de statut échoué.", 
        variant: "destructive" 
      });
    }
  };

  const handleResetPassword = async () => {
    if (!resetDialog.agent) return;
    const agent = resetDialog.agent;
    
    toast({ 
      title: "Traitement...", 
      description: "Envoi de l'email en cours...",
      className: "bg-blue-900 border-blue-700 text-white"
    });
    
    try {
      const res = await apiClient.post(`/admin/agents/${agent.id}/reset-password`);
      const { temp_password, email_sent, target_email } = res.data;
      
      if (email_sent) {
        toast({ 
          title: "Email Envoyé", 
          description: (
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <MailCheck className="h-5 w-5 text-emerald-400" />
                <span className="font-medium">L'agent a été notifié</span>
              </div>
              <div className="text-sm">
                Email envoyé à <span className="font-semibold text-white">{target_email}</span>
              </div>
            </div>
          ), 
          className: "bg-emerald-900 border-emerald-700 text-white",
          duration: 5000
        });
      } else {
        toast({ 
          title: "⚠️ Attention", 
          description: (
            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-2">
                <MailWarning className="h-5 w-5 text-amber-400" />
                <span className="font-medium">Échec de l'envoi</span>
              </div>
              <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-3">
                <div className="text-xs text-amber-300 mb-2">Mot de passe temporaire :</div>
                <div className="font-mono text-center text-white bg-black/40 p-2 rounded select-all">
                  {temp_password}
                </div>
              </div>
            </div>
          ), 
          className: "bg-amber-900 border-amber-700 text-white",
          duration: 10000
        });
      }
    } catch (error: any) {
      toast({ 
        title: "Erreur", 
        description: error.response?.data?.detail || "Réinitialisation échouée.", 
        variant: "destructive" 
      });
    } finally {
      setResetDialog({ show: false, agent: null });
    }
  };

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = 
      agent.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agent.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agent.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agent.bank_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = 
      statusFilter === "all" || 
      (statusFilter === "active" && agent.is_active) ||
      (statusFilter === "inactive" && !agent.is_active);
    
    const matchesBank = 
      bankFilter === "all" || 
      agent.bank_name === bankFilter;
    
    return matchesSearch && matchesStatus && matchesBank;
  });

  const activeAgents = agents.filter(a => a.is_active).length;
  const inactiveAgents = agents.filter(a => !a.is_active).length;
  const uniqueBanks = [...new Set(agents.map(a => a.bank_name))];

  return (
    <div className="min-h-screen bg-zinc-950 text-white font-sans selection:bg-cyan-500/30">
      <Sidebar activePath={location.pathname} />

      <div className="md:ml-64 min-h-screen transition-all duration-300">
        <header className="sticky top-0 z-40 bg-zinc-950/90 backdrop-blur-lg border-b border-zinc-800/50 px-8 py-4 flex items-center justify-between">
          <div className="md:hidden">
            <Button variant="ghost" size="icon" className="hover:bg-zinc-800">
              <Menu className="h-6 w-6 text-zinc-400" />
            </Button>
          </div>
          <div className="flex-1"></div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-3 pl-3 border-l border-zinc-800">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-white">{user?.fullName}</p>
                
              </div>
              <Avatar className="h-10 w-10 border-2 border-zinc-800">
                <AvatarImage src={user?.imageUrl} />
                <AvatarFallback className="bg-cyan-600 text-white">
                  {user?.firstName?.[0]}
                  {user?.lastName?.[0]}
                </AvatarFallback>
              </Avatar>
            </div>
          </div>
        </header>

        <main className="p-8 space-y-8">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div>
              <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-yellow-500 to-orange-500">
                Gestion des Agents
              </h2>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto">
              <div className="relative flex-1 md:w-72">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                <Input 
                  placeholder="Rechercher un agent..." 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-zinc-900 border-zinc-800 text-white focus:border-cyan-500 focus:ring-cyan-500/20"
                />
              </div>
              <div className="flex gap-2">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" className="border-zinc-800 text-zinc-400 hover:text-white">
                      <Filter className="h-4 w-4 mr-2" />
                      Filtres
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-zinc-900 border-zinc-800 text-white min-w-[200px]">
                    <DropdownMenuLabel>Filtrer par statut</DropdownMenuLabel>
                    <DropdownMenuSeparator className="bg-zinc-800" />
                    <DropdownMenuItem onClick={() => setStatusFilter("all")} className="cursor-pointer">
                      Tous les agents ({agents.length})
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setStatusFilter("active")} className="cursor-pointer">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full bg-emerald-500" />
                        Actifs ({activeAgents})
                      </div>
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setStatusFilter("inactive")} className="cursor-pointer">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full bg-red-500" />
                        Inactifs ({inactiveAgents})
                      </div>
                    </DropdownMenuItem>
                    
                    <DropdownMenuSeparator className="bg-zinc-800" />
                    <DropdownMenuLabel>Filtrer par banque</DropdownMenuLabel>
                    <DropdownMenuSeparator className="bg-zinc-800" />
                    <DropdownMenuItem onClick={() => setBankFilter("all")} className="cursor-pointer">
                      Toutes les banques
                    </DropdownMenuItem>
                    {uniqueBanks.map((bank) => (
                      <DropdownMenuItem 
                        key={bank} 
                        onClick={() => setBankFilter(bank)} 
                        className="cursor-pointer"
                      >
                        <div className="flex items-center gap-2">
                          <Building className="h-3 w-3 text-cyan-400" />
                          {bank}
                        </div>
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
                
                <Button 
                  onClick={() => navigate("/admin/create-agent")}
                  className="bg-gradient-to-r from-cyan-500 to-yellow-500 hover:from-cyan-600 hover:to-yellow-600 text-white shadow-lg shadow-cyan-500/30"
                >
                  <UserPlus className="h-4 w-4 mr-2" />
                  Ajouter
                </Button>
              </div>
            </div>
          </div>

          {/* Indicateurs de filtres actifs */}
          {(statusFilter !== "all" || bankFilter !== "all") && (
            <div className="flex flex-wrap gap-2">
              {statusFilter !== "all" && (
                <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 bg-emerald-500/10">
                  {statusFilter === "active" ? "Actifs uniquement" : "Inactifs uniquement"}
                  <button 
                    onClick={() => setStatusFilter("all")}
                    className="ml-2 text-xs hover:text-white"
                  >
                    ×
                  </button>
                </Badge>
              )}
              {bankFilter !== "all" && (
                <Badge variant="outline" className="border-cyan-500/30 text-cyan-400 bg-cyan-500/10">
                  Banque: {bankFilter}
                  <button 
                    onClick={() => setBankFilter("all")}
                    className="ml-2 text-xs hover:text-white"
                  >
                    ×
                  </button>
                </Badge>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-zinc-400 text-sm">Total agents</p>
                    <h3 className="text-2xl font-bold text-white mt-1">{agents.length}</h3>
                  </div>
                  <div className="p-3 rounded-lg bg-blue-500/10">
                    <Users className="h-6 w-6 text-blue-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-zinc-400 text-sm">Actifs</p>
                    <h3 className="text-2xl font-bold text-emerald-400 mt-1">{activeAgents}</h3>
                  </div>
                  <div className="p-3 rounded-lg bg-emerald-500/10">
                    <CheckCircle className="h-6 w-6 text-emerald-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-zinc-400 text-sm">Inactifs</p>
                    <h3 className="text-2xl font-bold text-red-400 mt-1">{inactiveAgents}</h3>
                  </div>
                  <div className="p-3 rounded-lg bg-red-500/10">
                    <Ban className="h-6 w-6 text-red-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-zinc-400 text-sm">Banques</p>
                    <h3 className="text-2xl font-bold text-yellow-400 mt-1">
                      {uniqueBanks.length}
                    </h3>
                  </div>
                  <div className="p-3 rounded-lg bg-yellow-500/10">
                    <Building className="h-6 w-6 text-yellow-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl overflow-hidden">
            <div className="p-6 border-b border-zinc-800 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">Liste des agents</h3>
                <p className="text-sm text-zinc-400 mt-1">
                  {filteredAgents.length} agent{filteredAgents.length > 1 ? 's' : ''} trouvé{filteredAgents.length > 1 ? 's' : ''}
                  {statusFilter !== "all" && ` • Statut: ${statusFilter === "active" ? "Actifs" : "Inactifs"}`}
                  {bankFilter !== "all" && ` • Banque: ${bankFilter}`}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={fetchAgents}
                  className="text-zinc-400 hover:text-white"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Actualiser
                </Button>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <Table>
                <TableHeader className="bg-zinc-900 border-b border-zinc-800">
                  <TableRow className="border-zinc-800 hover:bg-zinc-900">
                    <TableHead className="text-zinc-400">Agent</TableHead>
                    <TableHead className="text-zinc-400">Contact</TableHead>
                    <TableHead className="text-zinc-400">Banque</TableHead>
                    <TableHead className="text-zinc-400">Statut</TableHead>
                    <TableHead className="text-right text-zinc-400">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    Array.from({ length: 5 }).map((_, index) => (
                      <TableRow key={index} className="border-zinc-800">
                        <TableCell colSpan={5} className="h-20">
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-full bg-zinc-800 animate-pulse" />
                            <div className="space-y-2">
                              <div className="h-4 w-32 bg-zinc-800 rounded animate-pulse" />
                              <div className="h-3 w-24 bg-zinc-800 rounded animate-pulse" />
                            </div>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : filteredAgents.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center h-64">
                        <div className="flex flex-col items-center justify-center py-12">
                          <Users className="h-12 w-12 text-zinc-700 mb-4" />
                          <h3 className="text-lg font-semibold text-zinc-400">Aucun agent trouvé</h3>
                          <p className="text-zinc-500 mt-2 max-w-md">
                            {searchTerm ? `Aucun résultat pour "${searchTerm}"` : "Aucun agent dans le système"}
                            {(statusFilter !== "all" || bankFilter !== "all") && " avec les filtres actuels"}
                          </p>
                          {(searchTerm || statusFilter !== "all" || bankFilter !== "all") && (
                            <Button 
                              variant="outline" 
                              className="mt-4 border-zinc-700"
                              onClick={() => {
                                setSearchTerm("");
                                setStatusFilter("all");
                                setBankFilter("all");
                              }}
                            >
                              Réinitialiser les filtres
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredAgents.map((agent) => (
                      <TableRow key={agent.id} className="border-zinc-800 hover:bg-zinc-800/30 transition-colors">
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <Avatar className="h-10 w-10 border-2 border-zinc-800">
                              <AvatarFallback className="bg-gradient-to-br from-cyan-500 to-yellow-500 text-white">
                                {agent.first_name?.[0]}
                                {agent.last_name?.[0]}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <div className="font-medium text-white">
                                {agent.first_name} {agent.last_name}
                              </div>
                              
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            <div className="flex items-center gap-2 text-sm">
                              <Mail className="h-3 w-3 text-zinc-500" />
                              <span className="text-zinc-400">{agent.email}</span>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Building className="h-4 w-4 text-cyan-400" />
                            <Badge variant="outline" className="border-cyan-500/30 text-cyan-300 bg-cyan-500/5">
                              {agent.bank_name}
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell>
                          {agent.is_active ? (
                            <Badge className="bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/20 px-3 py-1">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Actif
                            </Badge>
                          ) : (
                            <Badge className="bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20 px-3 py-1">
                              <Ban className="h-3 w-3 mr-1" />
                              Inactif
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Button 
                              size="icon" 
                              variant="ghost" 
                              title="Modifier"
                              onClick={() => handleEditClick(agent)}
                              className="h-8 w-8 text-zinc-400 hover:text-white hover:bg-zinc-800"
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                            
                            <Button 
                              size="icon" 
                              variant="ghost" 
                              title="Réinitialiser MDP"
                              onClick={() => setResetDialog({ show: true, agent })}
                              className="h-8 w-8 text-zinc-400 hover:text-yellow-400 hover:bg-yellow-400/10"
                            >
                              <KeyRound className="h-4 w-4" />
                            </Button>
                            
                            <Button 
                              size="icon" 
                              variant="ghost" 
                              title={agent.is_active ? "Désactiver" : "Activer"}
                              onClick={() => handleToggleStatus(agent)}
                              className={`h-8 w-8 text-zinc-400 hover:bg-zinc-800 ${agent.is_active ? "hover:text-red-400" : "hover:text-emerald-400"}`}
                            >
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
          </div>
        </main>
      </div>

      {/* MODALE ÉDITION */}
      <Dialog open={!!editingAgent} onOpenChange={(open) => !open && setEditingAgent(null)}>
        <DialogContent className="bg-zinc-900 border-zinc-800 text-white sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Pencil className="h-5 w-5 text-cyan-400" />
              Modifier l'agent
            </DialogTitle>
            <DialogDescription className="text-zinc-400">
              Mettez à jour les informations de l'agent
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="firstname" className="text-zinc-400">
                Prénom
              </Label>
              <Input 
                id="firstname" 
                value={editForm.first_name} 
                onChange={(e) => setEditForm({...editForm, first_name: e.target.value})} 
                className="bg-zinc-800 border-zinc-700 text-white focus:border-cyan-500"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="lastname" className="text-zinc-400">
                Nom
              </Label>
              <Input 
                id="lastname" 
                value={editForm.last_name} 
                onChange={(e) => setEditForm({...editForm, last_name: e.target.value})} 
                className="bg-zinc-800 border-zinc-700 text-white focus:border-cyan-500"
              />
            </div>
          </div>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setEditingAgent(null)} 
              className="border-zinc-700 text-zinc-400 hover:text-white"
            >
              Annuler
            </Button>
            <Button 
              onClick={handleSaveEdit} 
              disabled={isSaving} 
              className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white"
            >
              {isSaving ? (
                <>
                  <Loader2 className="animate-spin h-4 w-4 mr-2" />
                  Enregistrement...
                </>
              ) : "Enregistrer"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* MODALE RÉINITIALISATION MDP */}
      <Dialog open={resetDialog.show} onOpenChange={(open) => !open && setResetDialog({ show: false, agent: null })}>
        <DialogContent className="bg-zinc-900 border-zinc-800 text-white sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <KeyRound className="h-5 w-5 text-yellow-400" />
              Réinitialiser le mot de passe
            </DialogTitle>
            <DialogDescription className="text-zinc-400">
              Un nouveau mot de passe sera généré et envoyé par email à l'agent
            </DialogDescription>
          </DialogHeader>
          
          {resetDialog.agent && (
            <div className="space-y-4 py-4">
              <div className="bg-zinc-800/50 p-4 rounded-lg">
                <div className="flex items-center gap-3">
                  <Avatar className="h-12 w-12 border-2 border-zinc-700">
                    <AvatarFallback className="bg-gradient-to-br from-cyan-600 to-blue-600 text-white">
                      {resetDialog.agent.first_name?.[0]}
                      {resetDialog.agent.last_name?.[0]}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h4 className="font-semibold text-white">
                      {resetDialog.agent.first_name} {resetDialog.agent.last_name}
                    </h4>
                    <p className="text-sm text-zinc-400">{resetDialog.agent.email}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Building className="h-3 w-3 text-cyan-400" />
                      <span className="text-xs text-cyan-300">{resetDialog.agent.bank_name}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-yellow-900/20 border border-yellow-700/30 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <MailWarning className="h-5 w-5 text-yellow-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-yellow-300 font-medium">
                      Confirmation requise
                    </p>
                    <p className="text-sm text-zinc-400 mt-1">
                      Cette action va générer un nouveau mot de passe aléatoire et l'envoyer par email à l'agent.
                      L'agent devra changer ce mot de passe lors de sa prochaine connexion.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setResetDialog({ show: false, agent: null })} 
              className="border-zinc-700 text-zinc-400 hover:text-white"
            >
              Annuler
            </Button>
            <Button 
              onClick={handleResetPassword}
              className="bg-gradient-to-r from-yellow-600 to-amber-600 hover:from-yellow-700 hover:to-amber-700 text-white"
            >
              <KeyRound className="h-4 w-4 mr-2" />
              Confirmer et envoyer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ManageAgentsPage;