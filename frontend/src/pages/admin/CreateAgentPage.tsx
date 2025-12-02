import { useState, useEffect } from "react";
import { apiClient } from "@/lib/axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, Copy, CheckCircle, ArrowLeft, Mail } from "lucide-react";
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
  const [personalEmail, setPersonalEmail] = useState(""); // <--- NOUVEAU
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
      
      // --- CORRECTION DE LA GESTION D'ERREUR ---
      const detail = err.response?.data?.detail;
      
      if (typeof detail === 'string') {
        // Cas d'une erreur simple (ex: "Email déjà utilisé")
        setError(detail);
      } else if (Array.isArray(detail)) {
        // Cas d'une erreur de validation Pydantic (422)
        // On prend le premier message d'erreur de la liste
        const validationError = detail[0]?.msg || "Erreur de validation des données";
        const field = detail[0]?.loc?.[1] ? `(Champ: ${detail[0].loc[1]})` : "";
        setError(`${validationError} ${field}`);
      } else {
        setError("Une erreur technique est survenue.");
      }
      // -----------------------------------------
      
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(tempPassword);
  };

  return (
    <div className="min-h-screen bg-zinc-900 p-8 text-white flex flex-col items-center">
      
      <div className="w-full max-w-2xl mb-8 flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate("/admin/dashboard")} className="text-zinc-400 hover:text-white">
            <ArrowLeft className="mr-2 h-4 w-4" /> Retour au Dashboard
        </Button>
        <h1 className="text-2xl font-bold">Gestion des Agents</h1>
      </div>

      <Card className="w-full max-w-2xl bg-zinc-800 border-zinc-700">
        <CardHeader>
          <CardTitle className="text-emerald-500">Ajouter un nouvel Agent</CardTitle>
          <CardDescription className="text-zinc-400">
            L'agent recevra ses identifiants sur son adresse personnelle.
          </CardDescription>
        </CardHeader>
        <CardContent>
            
          {success && (
            <Alert className="mb-6 bg-emerald-900/50 border-emerald-800 text-emerald-200">
              <CheckCircle className="h-4 w-4" />
              <AlertTitle>Succès !</AlertTitle>
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          {error && (
            <Alert variant="destructive" className="mb-6 bg-red-900/50 border-red-800 text-red-200">
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
                        className="bg-zinc-900 border-zinc-600 text-white"
                        required
                    />
                </div>
                <div className="space-y-2">
                    <Label className="text-zinc-300">Nom</Label>
                    <Input 
                        placeholder="Ex: Connor" 
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        className="bg-zinc-900 border-zinc-600 text-white"
                        required
                    />
                </div>
            </div>

            <div className="space-y-2">
                <Label className="text-zinc-300">Email Professionnel (Identifiant de connexion)</Label>
                <div className="relative">
                    <Building2 className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                    <Input 
                        type="email"
                        placeholder="agent@banque.com" 
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="bg-zinc-900 border-zinc-600 text-white pl-10"
                        required
                    />
                </div>
            </div>

            {/* --- NOUVEAU CHAMP --- */}
            <div className="space-y-2">
                <Label className="text-emerald-400">Email Personnel (Réception du mot de passe)</Label>
                <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-emerald-500" />
                    <Input 
                        type="email"
                        placeholder="perso@gmail.com" 
                        value={personalEmail}
                        onChange={(e) => setPersonalEmail(e.target.value)}
                        className="bg-zinc-900 border-emerald-500/50 text-white pl-10 focus:border-emerald-500"
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
                    <SelectTrigger className="bg-zinc-900 border-zinc-600 text-white">
                        <SelectValue placeholder="Sélectionner une banque" />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-800 border-zinc-700 text-white">
                        {banks.map((bank) => (
                            <SelectItem key={bank.id} value={bank.id.toString()}>
                                {bank.name}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-700 space-y-2 opacity-75">
                <Label className="text-zinc-400 text-xs uppercase tracking-wide">Mot de passe généré</Label>
                <div className="flex items-center gap-2">
                    <code className="flex-1 bg-black p-3 rounded text-zinc-500 font-mono text-lg tracking-widest blur-[2px] select-none">
                        {tempPassword}
                    </code>
                    <Button type="button" size="sm" variant="ghost" onClick={copyToClipboard} title="Copier">
                        <Copy className="h-4 w-4" />
                    </Button>
                </div>
                <p className="text-xs text-zinc-500">
                    Ce mot de passe sera envoyé automatiquement par email.
                </p>
            </div>

            <Button 
                type="submit" 
                disabled={loading}
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3"
            >
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Créer et Envoyer l'email"}
            </Button>

          </form>
        </CardContent>
      </Card>
    </div>
  );
};

// Petite icône manquante
import { Building2 } from "lucide-react"; 

export default CreateAgentPage;