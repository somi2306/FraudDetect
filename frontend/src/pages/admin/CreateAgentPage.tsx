import { useState, useEffect } from "react";
import { apiClient } from "@/lib/axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, Copy, CheckCircle, ArrowLeft, Mail, Building2, UserPlus } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface Bank {
  id: number;
  name: string;
}

const CreateAgentPage = () => {
  const navigate = useNavigate();
  const [banks, setBanks] = useState<Bank[]>([]);
  const [loading, setLoading] = useState(false);
  
  // États du formulaire
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
      try {
        const res = await apiClient.get("/admin/banks");
        setBanks(res.data);
      } catch (err) {
        console.error("Erreur chargement banques", err);
        setError("Impossible de charger la liste des banques.");
      }
    };
    generatePassword();
    fetchBanks();
  }, []);

  const generatePassword = () => {
    const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
    let pass = "";
    for (let i = 0; i < 12; i++) {
      pass += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setTempPassword(pass);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBankId) { setError("Veuillez sélectionner une banque."); return; }
    
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await apiClient.post("/admin/create-agent", {
        first_name: firstName,
        last_name: lastName,
        email: email,
        personal_email: personalEmail,
        password: tempPassword,
        bank_id: parseInt(selectedBankId)
      });

      setSuccess(`Agent créé ! Un email a été envoyé à ${personalEmail}.`);
      
    } catch (err: any) {
      console.error(err);
      const detail = err.response?.data?.detail;
      
      if (typeof detail === 'string') {
        setError(detail);
      } else if (Array.isArray(detail)) {
        const validationError = detail[0]?.msg || "Erreur de validation des données";
        const field = detail[0]?.loc?.[1] ? `(Champ: ${detail[0].loc[1]})` : "";
        setError(`${validationError} ${field}`);
      } else {
        setError("Une erreur technique est survenue.");
      }
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(tempPassword);
  };

  // --- STYLES UNIFIÉS ---
  const gradientTextClass = "text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-yellow-400 to-orange-400";
  const gradientButtonClass = "w-full bg-gradient-to-r from-cyan-600 via-yellow-500 to-orange-500 hover:from-cyan-700 hover:via-yellow-600 hover:to-orange-600 text-white font-bold transition-all duration-300 transform hover:scale-[1.01] shadow-lg border-0 py-6";
  const inputClass = "bg-zinc-900 border-zinc-600 text-white focus:border-cyan-500 transition-colors placeholder:text-zinc-500";

  return (
    <div className="min-h-screen bg-zinc-900 p-8 text-white flex flex-col items-center relative overflow-hidden">
      
      {/* Fonds décoratifs (Comme AdminPage) */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-cyan-600/5 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-orange-600/5 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

      <div className="w-full max-w-2xl mb-8 flex items-center justify-between z-10">
        <Button variant="ghost" onClick={() => navigate("/admin/dashboard")} className="text-zinc-400 hover:text-white hover:bg-zinc-800">
            <ArrowLeft className="mr-2 h-4 w-4" /> Retour au Dashboard
        </Button>
        <h1 className="text-2xl font-bold flex items-center gap-2">
            <UserPlus className="h-6 w-6 text-cyan-500" />
            Gestion des Agents
        </h1>
      </div>

      <Card className="w-full max-w-2xl bg-zinc-800/80 backdrop-blur border-zinc-700 shadow-2xl z-10">
        <CardHeader>
          <CardTitle className={`text-2xl font-bold ${gradientTextClass}`}>
            Ajouter un nouvel Agent
          </CardTitle>
          <CardDescription className="text-zinc-400">
            L'agent recevra ses identifiants sécurisés sur son adresse personnelle.
          </CardDescription>
        </CardHeader>
        <CardContent>
            
          {success && (
            <Alert className="mb-6 bg-cyan-900/20 border-cyan-500/50 text-cyan-200">
              <CheckCircle className="h-4 w-4 text-cyan-400" />
              <AlertTitle className="text-cyan-400 font-bold">Succès !</AlertTitle>
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          {error && (
            <Alert variant="destructive" className="mb-6 bg-red-900/20 border-red-500/50 text-red-200">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleCreate} className="space-y-6">
            
            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <Label className="text-zinc-300">Prénom</Label>
                    <Input 
                        placeholder="Ex: Sarah" 
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        className={inputClass}
                        required
                    />
                </div>
                <div className="space-y-2">
                    <Label className="text-zinc-300">Nom</Label>
                    <Input 
                        placeholder="Ex: Connor" 
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        className={inputClass}
                        required
                    />
                </div>
            </div>

            <div className="space-y-2">
                <Label className="text-zinc-300">Email Professionnel (Identifiant)</Label>
                <div className="relative">
                    <Building2 className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                    <Input 
                        type="email"
                        placeholder="agent@banque.com" 
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className={`${inputClass} pl-10`}
                        required
                    />
                </div>
            </div>

            <div className="space-y-2">
                <Label className="text-cyan-400 font-medium">Email Personnel (Réception MDP)</Label>
                <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-cyan-500" />
                    <Input 
                        type="email"
                        placeholder="perso@gmail.com" 
                        value={personalEmail}
                        onChange={(e) => setPersonalEmail(e.target.value)}
                        className={`${inputClass} pl-10 border-cyan-500/30 focus:border-cyan-500`}
                        required
                    />
                </div>
                <p className="text-xs text-zinc-500">
                    Les identifiants seront envoyés uniquement à cette adresse.
                </p>
            </div>

            <div className="space-y-2">
                <Label className="text-zinc-300">Banque d'affectation</Label>
                <Select onValueChange={setSelectedBankId} value={selectedBankId}>
                    <SelectTrigger className="bg-zinc-900 border-zinc-600 text-white focus:ring-cyan-500/50">
                        <SelectValue placeholder="Sélectionner une banque" />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-800 border-zinc-700 text-white">
                        {banks.map((bank) => (
                            <SelectItem key={bank.id} value={bank.id.toString()} className="focus:bg-zinc-700 cursor-pointer">
                                {bank.name}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            <div className="p-4 bg-zinc-900/50 rounded-lg border border-zinc-700/50 space-y-2">
                <Label className="text-zinc-500 text-xs uppercase tracking-wide font-semibold">Mot de passe généré (Aperçu)</Label>
                <div className="flex items-center gap-2">
                    <code className="flex-1 bg-black/40 p-3 rounded text-zinc-500 font-mono text-lg tracking-widest blur-[3px] select-none transition-all hover:blur-none hover:text-cyan-400 cursor-help">
                        {tempPassword}
                    </code>
                    <Button type="button" size="sm" variant="ghost" onClick={copyToClipboard} title="Copier" className="text-zinc-400 hover:text-white">
                        <Copy className="h-4 w-4" />
                    </Button>
                </div>
            </div>

            <Button 
                type="submit" 
                disabled={loading}
                className={gradientButtonClass}
            >
                {loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : "Créer et Envoyer l'email"}
            </Button>

          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default CreateAgentPage;