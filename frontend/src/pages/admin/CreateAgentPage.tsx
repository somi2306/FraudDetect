import { useState, useEffect } from "react";
import { apiClient } from "@/lib/axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, Copy, CheckCircle, ArrowLeft, Mail, Building2, RefreshCw } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Sidebar from "@/components/Sidebar";
import AdminHeader from "@/components/AdminHeader"; // Import

interface Bank { id: number; name: string; }

const CreateAgentPage = () => {
  const navigate = useNavigate();
  const [banks, setBanks] = useState<Bank[]>([]);
  const [loading, setLoading] = useState(false);
  
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [personalEmail, setPersonalEmail] = useState("");
  const [selectedBankId, setSelectedBankId] = useState<string>("");
  const [tempPassword, setTempPassword] = useState("");
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBanks = async () => {
      try { const res = await apiClient.get("/admin/banks"); setBanks(res.data); } 
      catch (err) { setError("Impossible de charger la liste des banques."); }
    };
    generatePassword();
    fetchBanks();
  }, []);

  const generatePassword = () => {
    const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
    let pass = "";
    for (let i = 0; i < 12; i++) { pass += chars.charAt(Math.floor(Math.random() * chars.length)); }
    setTempPassword(pass);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBankId) { setError("Veuillez sélectionner une banque."); return; }
    setLoading(true); setError(null); setSuccess(null);
    try {
      await apiClient.post("/admin/create-agent", {
        first_name: firstName, last_name: lastName, email: email,
        personal_email: personalEmail, password: tempPassword, bank_id: parseInt(selectedBankId)
      });
      setSuccess(`Agent créé ! Un email a été envoyé à ${personalEmail}.`);
    } catch (err: any) { setError("Erreur lors de la création."); } 
    finally { setLoading(false); }
  };

  const copyToClipboard = () => navigator.clipboard.writeText(tempPassword);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <Sidebar />

      <div className="md:ml-64 min-h-screen transition-all duration-300">
        <AdminHeader />

        <main className="p-8 flex flex-col items-center">
            <div className="w-full max-w-3xl mb-8 flex items-center justify-between z-10">
                <Button variant="ghost" onClick={() => navigate("/admin/manage-agents")} className="text-gray-500 hover:text-gray-900 hover:bg-gray-100">
                    <ArrowLeft className="mr-2 h-4 w-4" /> Retour à la liste
                </Button>
            </div>

            <Card className="w-full max-w-3xl bg-white border-gray-200 shadow-sm z-10">
                <CardHeader>
                <CardTitle className="text-2xl font-bold text-gray-900">
                    Ajouter un nouvel Agent
                </CardTitle>
                <CardDescription className="text-gray-500">
                    L'agent recevra ses identifiants sécurisés sur son adresse personnelle.
                </CardDescription>
                </CardHeader>
                <CardContent>
                    
                {success && (
                    <Alert className="mb-6 bg-emerald-50 border-emerald-200 text-emerald-800">
                    <CheckCircle className="h-4 w-4 text-emerald-600" />
                    <AlertTitle className="text-emerald-700 font-bold">Succès !</AlertTitle>
                    <AlertDescription>{success}</AlertDescription>
                    </Alert>
                )}

                {error && (
                    <Alert variant="destructive" className="mb-6 bg-red-50 border-red-200 text-red-800">
                    <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                <form onSubmit={handleCreate} className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2"><Label className="text-gray-700">Prénom</Label><Input placeholder="Ex: Sarah" value={firstName} onChange={(e) => setFirstName(e.target.value)} className="bg-white border-gray-300 text-gray-900" required /></div>
                        <div className="space-y-2"><Label className="text-gray-700">Nom</Label><Input placeholder="Ex: Connor" value={lastName} onChange={(e) => setLastName(e.target.value)} className="bg-white border-gray-300 text-gray-900" required /></div>
                    </div>

                    <div className="space-y-2">
                        <Label className="text-gray-700">Email Professionnel (Identifiant)</Label>
                        <div className="relative"><Building2 className="absolute left-3 top-3 h-4 w-4 text-gray-400" /><Input type="email" placeholder="agent@banque.com" value={email} onChange={(e) => setEmail(e.target.value)} className="pl-10 bg-white border-gray-300 text-gray-900" required /></div>
                    </div>

                    <div className="space-y-2">
                        <Label className="text-cyan-600 font-medium">Email Personnel (Réception MDP)</Label>
                        <div className="relative"><Mail className="absolute left-3 top-3 h-4 w-4 text-cyan-500" /><Input type="email" placeholder="perso@gmail.com" value={personalEmail} onChange={(e) => setPersonalEmail(e.target.value)} className="pl-10 bg-white border-cyan-200 text-gray-900 focus:border-cyan-500" required /></div>
                        <p className="text-xs text-gray-500">Les identifiants seront envoyés uniquement à cette adresse.</p>
                    </div>

                    <div className="space-y-2">
                        <Label className="text-gray-700">Banque d'affectation</Label>
                        <Select onValueChange={setSelectedBankId} value={selectedBankId}>
                            <SelectTrigger className="bg-white border-gray-300 text-gray-900"><SelectValue placeholder="Sélectionner une banque" /></SelectTrigger>
                            <SelectContent className="bg-white border-gray-200 text-gray-900">
                                {banks.map((bank) => (<SelectItem key={bank.id} value={bank.id.toString()} className="focus:bg-gray-100 cursor-pointer">{bank.name}</SelectItem>))}
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="p-4 bg-gray-100 rounded-lg border border-gray-200 space-y-2">
                        <div className="flex items-center justify-between">
                            <Label className="text-gray-500 text-xs uppercase tracking-wide font-semibold">Mot de passe généré</Label>
                            <Button type="button" variant="ghost" size="sm" onClick={generatePassword} className="text-gray-500 hover:text-gray-900 h-6"><RefreshCw className="h-3 w-3 mr-1" /> Régénérer</Button>
                        </div>
                        <div className="flex items-center gap-2">
                            <code className="flex-1 bg-white p-3 rounded text-gray-600 font-mono text-lg tracking-widest blur-[3px] select-none transition-all hover:blur-none hover:text-cyan-600 cursor-help border border-gray-200">{tempPassword}</code>
                            <Button type="button" size="sm" variant="ghost" onClick={copyToClipboard} title="Copier" className="text-gray-500 hover:text-gray-900"><Copy className="h-4 w-4" /></Button>
                        </div>
                    </div>

                    <Button type="submit" disabled={loading} className="w-full bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-6 shadow-md shadow-cyan-100">{loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : "Créer et Envoyer l'email"}</Button>
                </form>
                </CardContent>
            </Card>
        </main>
      </div>
    </div>
  );
};

export default CreateAgentPage;