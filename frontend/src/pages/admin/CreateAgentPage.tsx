import { useState, useEffect } from "react";
import { apiClient } from "@/lib/axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Loader2, 
  Copy, 
  CheckCircle, 
  ArrowLeft, 
  Mail, 
  Building, 
  UserPlus, 
  Shield,
  KeyRound,
  RefreshCw,
  AlertCircle,
  Eye,
  EyeOff,
  UserCheck,
  Send,
  Lock,
  Building2
} from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import Sidebar from "@/components/Sidebar";
import { useUser } from "@clerk/clerk-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface Bank {
  id: number;
  name: string;
}

const CreateAgentPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const { user } = useUser();
  
  const [banks, setBanks] = useState<Bank[]>([]);
  const [loading, setLoading] = useState(false);
  const [banksLoading, setBanksLoading] = useState(true);
  
  // États du formulaire
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [personalEmail, setPersonalEmail] = useState("");
  const [selectedBankId, setSelectedBankId] = useState<string>("");
  
  const [tempPassword, setTempPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [activeTab, setActiveTab] = useState("form");
  const [agentCreated, setAgentCreated] = useState<any>(null);

  useEffect(() => {
    const fetchBanks = async () => {
      setBanksLoading(true);
      try {
        const res = await apiClient.get("/admin/banks");
        setBanks(res.data);
      } catch (err) {
        console.error("Erreur chargement banques", err);
        toast({
          title: "Erreur",
          description: "Impossible de charger la liste des banques.",
          variant: "destructive"
        });
      } finally {
        setBanksLoading(false);
      }
    };
    
    generateStrongPassword();
    fetchBanks();
  }, []);

  const calculatePasswordStrength = (password: string) => {
    let strength = 0;
    if (password.length >= 8) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[a-z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password)) strength += 15;
    if (/[^A-Za-z0-9]/.test(password)) strength += 10;
    return Math.min(strength, 100);
  };

  const generateStrongPassword = () => {
    const chars = {
      lowercase: "abcdefghijklmnopqrstuvwxyz",
      uppercase: "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
      numbers: "0123456789",
      symbols: "!@#$%^&*"
    };
    
    let password = "";
    
    // Assurer au moins un caractère de chaque type
    password += chars.lowercase.charAt(Math.floor(Math.random() * chars.lowercase.length));
    password += chars.uppercase.charAt(Math.floor(Math.random() * chars.uppercase.length));
    password += chars.numbers.charAt(Math.floor(Math.random() * chars.numbers.length));
    password += chars.symbols.charAt(Math.floor(Math.random() * chars.symbols.length));
    
    // Compléter avec des caractères aléatoires
    const allChars = chars.lowercase + chars.uppercase + chars.numbers + chars.symbols;
    for (let i = password.length; i < 16; i++) {
      password += allChars.charAt(Math.floor(Math.random() * allChars.length));
    }
    
    // Mélanger le mot de passe
    password = password.split('').sort(() => Math.random() - 0.5).join('');
    
    setTempPassword(password);
    setPasswordStrength(calculatePasswordStrength(password));
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBankId) {
      toast({
        title: "Validation requise",
        description: "Veuillez sélectionner une banque.",
        variant: "destructive"
      });
      return;
    }
    
    setLoading(true);

    try {
      const response = await apiClient.post("/admin/create-agent", {
        first_name: firstName,
        last_name: lastName,
        email: email,
        personal_email: personalEmail,
        password: tempPassword,
        bank_id: parseInt(selectedBankId)
      });

      setAgentCreated({
        ...response.data,
        firstName,
        lastName,
        email,
        personalEmail,
        bankName: banks.find(b => b.id === parseInt(selectedBankId))?.name
      });
      
      toast({
        title: "Agent créé avec succès",
        description: `Un email a été envoyé à ${personalEmail} avec les identifiants.`,
        className: "bg-yellow-500/10 border-yellow-500/30 text-white"
      });
      
      setActiveTab("confirmation");

    } catch (err: any) {
      console.error(err);
      const detail = err.response?.data?.detail;
      
      let errorMessage = "Une erreur technique est survenue.";
      
      if (typeof detail === 'string') {
        errorMessage = detail;
      } else if (Array.isArray(detail)) {
        const validationError = detail[0]?.msg || "Erreur de validation des données";
        const field = detail[0]?.loc?.[1] ? `(Champ: ${detail[0].loc[1]})` : "";
        errorMessage = `${validationError} ${field}`;
      }
      
      toast({
        title: "Erreur",
        description: errorMessage,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copié",
      description: `${label} copié dans le presse-papier`,
      className: "bg-cyan-500/10 border-cyan-500/30 text-white"
    });
  };

  const resetForm = () => {
    setFirstName("");
    setLastName("");
    setEmail("");
    setPersonalEmail("");
    setSelectedBankId("");
    generateStrongPassword();
    setActiveTab("form");
    setAgentCreated(null);
  };

 const getPasswordStrengthColor = () => {
    if (passwordStrength >= 80) return "bg-emerald-500";
    if (passwordStrength >= 60) return "bg-yellow-500";
    if (passwordStrength >= 40) return "bg-orange-500";
    return "bg-red-500";
  };

  const getPasswordStrengthText = () => {
    if (passwordStrength >= 80) return "Fort";
    if (passwordStrength >= 60) return "Bon";
    if (passwordStrength >= 40) return "Moyen";
    return "Faible";
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-white font-sans selection:bg-cyan-500/30">
      <Sidebar activePath={location.pathname} />

      <div className="md:ml-64 min-h-screen transition-all duration-300">
        <header className="sticky top-0 z-40 bg-zinc-950/90 backdrop-blur-lg border-b border-zinc-800/50 px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              onClick={() => navigate("/admin/manage-agents")} 
              className="text-zinc-400 hover:text-white hover:bg-zinc-800"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Retour
            </Button>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-3 pl-3 border-l border-zinc-800">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-white">{user?.fullName}</p>
              </div>
              <Avatar className="h-10 w-10 border-2 border-zinc-800">
                <AvatarImage src={user?.imageUrl} />
                <AvatarFallback className="bg-orange-500 text-white">
                  {user?.firstName?.[0]}
                  {user?.lastName?.[0]}
                </AvatarFallback>
              </Avatar>
            </div>
          </div>
        </header>

        <main className="p-8">
          <div className="max-w-4xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-yellow-500 to-orange-500">
                Ajouter un nouvel Agent
              </h1>
              <p className="text-zinc-400 mt-2">
                Créez un compte agent avec des identifiants sécurisés
              </p>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid w-full grid-cols-2 bg-zinc-900 border border-zinc-800 p-1">
                <TabsTrigger 
                  value="form" 
                  className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500/20 data-[state=active]:to-blue-900/20"
                >
                  <UserPlus className="h-4 w-4 mr-2" />
                  Formulaire
                </TabsTrigger>
                <TabsTrigger 
                  value="confirmation" 
                  className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-yellow-500/20 data-[state=active]:to-orange-500/20"
                  disabled={!agentCreated}
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Confirmation
                </TabsTrigger>
              </TabsList>

              <TabsContent value="form" className="space-y-6">
                <Card className="bg-zinc-900/50 border-zinc-800">
                  <CardHeader>
                    <CardTitle className="text-xl font-semibold text-white">
                      Informations de l'agent
                    </CardTitle>
                    <CardDescription className="text-zinc-400">
                      Renseignez les informations de base du nouvel agent
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleCreate} className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-3">
                          <Label htmlFor="firstName" className="text-zinc-300">
                            Prénom <span className="text-red-500">*</span>
                          </Label>
                          <Input
                            id="firstName"
                            placeholder="Ex: Sarah"
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                            className="bg-zinc-900 border-zinc-800 text-white focus:border-cyan-500"
                            required
                          />
                        </div>
                        
                        <div className="space-y-3">
                          <Label htmlFor="lastName" className="text-zinc-300">
                            Nom <span className="text-red-500">*</span>
                          </Label>
                          <Input
                            id="lastName"
                            placeholder="Ex: Connor"
                            value={lastName}
                            onChange={(e) => setLastName(e.target.value)}
                            className="bg-zinc-900 border-zinc-800 text-white focus:border-cyan-500"
                            required
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-3">
                          <Label htmlFor="email" className="text-zinc-300">
                            Email professionnel <span className="text-red-500">*</span>
                          </Label>
                          <div className="relative">
                            <Building2 className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                            <Input
                              id="email"
                              type="email"
                              placeholder="agent@banque.com"
                              value={email}
                              onChange={(e) => setEmail(e.target.value)}
                              className="pl-10 bg-zinc-900 border-zinc-800 text-white focus:border-cyan-500"
                              required
                            />
                          </div>

                        </div>
                        
                        <div className="space-y-3">
                          <Label htmlFor="personalEmail" className="text-zinc-300">
                            Email personnel <span className="text-red-500">*</span>
                          </Label>
                          <div className="relative">
                            <Mail className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                            <Input
                              id="personalEmail"
                              type="email"
                              placeholder="perso@gmail.com"
                              value={personalEmail}
                              onChange={(e) => setPersonalEmail(e.target.value)}
                              className="pl-10 bg-zinc-900 border-zinc-800 text-white focus:border-cyan-500"
                              required
                            />
                          </div>
                        
                        </div>
                      </div>

                      <div className="space-y-3">
                        <Label htmlFor="bank" className="text-zinc-300">
                          Banque d'affectation <span className="text-red-500">*</span>
                        </Label>
                        <Select 
                          onValueChange={setSelectedBankId} 
                          value={selectedBankId}
                          disabled={banksLoading}
                        >
                          <SelectTrigger className="bg-zinc-900 border-zinc-800 text-white focus:ring-cyan-500/50">
                            <SelectValue placeholder={banksLoading ? "Chargement des banques..." : "Sélectionner une banque"} />
                          </SelectTrigger>
                          <SelectContent className="bg-zinc-900 border-zinc-800 text-white">
                            {banks.map((bank) => (
                              <SelectItem 
                                key={bank.id} 
                                value={bank.id.toString()} 
                                className="focus:bg-zinc-800 cursor-pointer hover:bg-zinc-800"
                              >
                                <div className="flex items-center gap-2">
                                  <Building className="h-4 w-4 text-cyan-400" />
                                  {bank.name}
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

 <Card className="bg-zinc-900/80 border-zinc-700">
                        <CardHeader className="pb-3">
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-lg font-semibold text-white">
                              Mot de passe sécurisé
                            </CardTitle>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={generateStrongPassword}
                              className="text-zinc-400 hover:text-white"
                            >
                              <RefreshCw className="h-4 w-4 mr-2" />
                              Régénérer
                            </Button>
                          </div>
                          <CardDescription className="text-zinc-400">
                            Ce mot de passe sera envoyé à l'agent par email
                          </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <Label className="text-zinc-300">Mot de passe temporaire</Label>
                              <Badge className={`${getPasswordStrengthColor()} text-white`}>
                                {getPasswordStrengthText()}
                              </Badge>
                            </div>
                            
                            <div className="relative">
                              <Input
                                type={showPassword ? "text" : "password"}
                                value={tempPassword}
                                readOnly
                                className="font-mono text-lg tracking-wider bg-black/40 border-zinc-700 text-white pr-24"
                              />
                              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => setShowPassword(!showPassword)}
                                  className="h-8 w-8 text-zinc-400 hover:text-white"
                                >
                                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                </Button>
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => copyToClipboard(tempPassword, "Mot de passe")}
                                  className="h-8 w-8 text-zinc-400 hover:text-white"
                                >
                                  <Copy className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                            
                            <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                              <div 
                                className={`h-full transition-all duration-300 ${getPasswordStrengthColor()}`}
                                style={{ width: `${passwordStrength}%` }}
                              />
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                            <div className="flex items-center gap-1">
                              <div className={`h-2 w-2 rounded-full ${tempPassword.length >= 8 ? "bg-yellow-500" : "bg-zinc-700"}`} />
                              <span className="text-zinc-400">8+ caractères</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <div className={`h-2 w-2 rounded-full ${/[A-Z]/.test(tempPassword) ? "bg-orange-500" : "bg-zinc-700"}`} />
                              <span className="text-zinc-400">Majuscule</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <div className={`h-2 w-2 rounded-full ${/[0-9]/.test(tempPassword) ? "bg-cyan-500" : "bg-zinc-700"}`} />
                              <span className="text-zinc-400">Chiffre</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <div className={`h-2 w-2 rounded-full ${/[^A-Za-z0-9]/.test(tempPassword) ? "bg-yellow-500" : "bg-zinc-700"}`} />
                              <span className="text-zinc-400">Spécial</span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      <div className="flex gap-4 pt-4">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => navigate("/admin/manage-agents")}
                          className="flex-1 border-zinc-700 text-zinc-400 hover:text-white"
                        >
                          Annuler
                        </Button>
                        <Button
                          type="submit"
                          disabled={loading || banksLoading}
                          className="flex-1 bg-gradient-to-r from-cyan-500 to-yellow-500 hover:from-cyan-600 hover:to-yellow-600 text-white shadow-lg shadow-cyan-500/30"
                        >
                          {loading ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Création en cours...
                            </>
                          ) : (
                            <>
                              <Send className="mr-2 h-4 w-4" />
                              Créer l'agent et envoyer l'email
                            </>
                          )}
                        </Button>
                      </div>
                    </form>
                  </CardContent>
                </Card>
              </TabsContent>

               <TabsContent value="confirmation" className="space-y-6">
                {agentCreated && (
                  <>
                    <Card className="bg-gradient-to-br from-emerald-900/20 to-green-900/20 border-emerald-800">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="p-3 rounded-full bg-emerald-500/20 border border-emerald-500/30">
                              <CheckCircle className="h-8 w-8 text-emerald-400" />
                            </div>
                            <div>
                              <CardTitle className="text-2xl font-bold text-white">
                                Agent créé avec succès !
                              </CardTitle>
                              <CardDescription className="text-emerald-300/80">
                                L'agent a été notifié par email
                              </CardDescription>
                            </div>
                          </div>
                          <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
                            <UserCheck className="h-3 w-3 mr-1" />
                            Compte actif
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="space-y-4">
                            
                            
                            <div>
                              <Label className="text-zinc-300 text-sm">Nom complet</Label>
                              <p className="text-lg font-semibold text-white">
                                {agentCreated.firstName} {agentCreated.lastName}
                              </p>
                            </div>
                            
                            <div>
                              <Label className="text-zinc-300 text-sm">Email professionnel</Label>
                              <div className="flex items-center gap-2">
                                <p className="text-cyan-300">{agentCreated.email}</p>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => copyToClipboard(agentCreated.email, "Email professionnel")}
                                  className="h-6 w-6 p-0 text-zinc-400"
                                >
                                  <Copy className="h-3 w-3" />
                                </Button>
                              </div>
                            </div>
                            
                            <div>
                              <Label className="text-zinc-300 text-sm">Email de notification</Label>
                              <p className="text-cyan-300">{agentCreated.personalEmail}</p>
                            </div>
                            
                            <div>
                              <Label className="text-zinc-300 text-sm">Banque</Label>
                              <div className="flex items-center gap-2 mt-1">
                                <Building className="h-4 w-4 text-cyan-400" />
                                <span className="text-cyan-300">{agentCreated.bankName}</span>
                              </div>
                            </div>
                          </div>
                          
                          <Card className="bg-zinc-900/50 border-zinc-800">
                            <CardHeader>
                              <CardTitle className="text-lg font-semibold text-white flex items-center gap-2">
                                <KeyRound className="h-5 w-5 text-yellow-400" />
                                Identifiants envoyés
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="space-y-3">
                                <div>
                                  <Label className="text-zinc-300 text-sm">Identifiant de connexion</Label>
                                  <div className="flex items-center gap-2">
                                    <code className="flex-1 bg-black/40 p-2 rounded text-cyan-300 font-mono">
                                      {agentCreated.email}
                                    </code>
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      onClick={() => copyToClipboard(agentCreated.email, "Identifiant")}
                                      className="h-8 w-8 text-zinc-400"
                                    >
                                      <Copy className="h-4 w-4" />
                                    </Button>
                                  </div>
                                </div>
                                
                                <div>
                                  <Label className="text-zinc-300 text-sm">Mot de passe temporaire</Label>
                                  <div className="flex items-center gap-2">
                                    <code className="flex-1 bg-black/40 p-2 rounded text-yellow-300 font-mono">
                                      {tempPassword}
                                    </code>
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      onClick={() => copyToClipboard(tempPassword, "Mot de passe")}
                                      className="h-8 w-8 text-zinc-400"
                                    >
                                      <Copy className="h-4 w-4" />
                                    </Button>
                                  </div>
                                </div>
                                
                            
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      </CardContent>
                      <CardFooter className="flex justify-between border-t border-zinc-800/50 pt-6">
                        <Button
                          variant="outline"
                          onClick={() => navigate("/admin/manage-agents")}
                          className="border-zinc-700 text-zinc-400 hover:text-white"
                        >
                          <ArrowLeft className="mr-2 h-4 w-4" />
                          Retour à la liste
                        </Button>
                        <div className="flex gap-3">
                          <Button
                            variant="outline"
                            onClick={resetForm}
                            className="border-zinc-700 text-zinc-400 hover:text-white"
                          >
                            <UserPlus className="mr-2 h-4 w-4" />
                            Ajouter un autre agent
                          </Button>
                        </div>
                      </CardFooter>
                    </Card>
                  </>
                )}
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>
    </div>
  );
};

export default CreateAgentPage;