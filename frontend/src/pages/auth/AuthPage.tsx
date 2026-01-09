import { useSignIn, useSignUp, useClerk, useUser } from "@clerk/clerk-react";
import { Button } from "../../components/ui/button";
import { useState, useEffect } from "react";
import { Input } from "../../components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import PasswordStrengthMeter from "../../components/PasswordStrengthMeter";
import AuthImagePattern from "../../components/AuthImagePattern";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import ForgotPassword from "../../components/ForgotPassword"; 
import { ShieldCheck, Loader2, Building2 } from "lucide-react"; // Ajout de l'icône Building2
import { useNavigate } from "react-router-dom";

const AuthPage = () => {
  const { signIn, isLoaded: isSignInLoaded } = useSignIn();
  const { signUp, isLoaded: isSignUpLoaded } = useSignUp();
  const { setActive, signOut } = useClerk();
  const { isSignedIn, isLoaded: isUserLoaded } = useUser();
  const navigate = useNavigate();

  // --- ÉTATS DU FORMULAIRE ---
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  
  // États inscription
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [cin, setCin] = useState("");
  const [rib, setRib] = useState("");
  // SUPPRIMÉ : const [selectedBank, setSelectedBank] = useState(""); 

  const [activeTab, setActiveTab] = useState("login");
  
  // --- ÉTATS DE FLUX ---
  const [pendingVerification, setPendingVerification] = useState(false);
  const [verifying2FA, setVerifying2FA] = useState(false);
  
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // --- REDIRECTION AUTOMATIQUE ---
  useEffect(() => {
    if (isUserLoaded && isSignedIn) {
      navigate("/auth-callback");
    }
  }, [isUserLoaded, isSignedIn, navigate]);

  if (!isSignInLoaded || !isSignUpLoaded) {
    return (
      <div className="flex items-center justify-center h-screen bg-transparent">
        <Loader2 className="animate-spin text-cyan-500 h-8 w-8" />
      </div>
    );
  }

  // --- FONCTIONS DE VALIDATION & UTILITAIRES ---
  
  // Fonction pour afficher le nom de la banque à l'utilisateur
  const getRIBBankName = (ribValue: string) => {
    if (ribValue.length < 3) return null;
    const bankCode = ribValue.substring(0, 3);
    const bankMap: { [key: string]: string } = {
      "230": "CIH Banque",
      "007": "Attijariwafa Banque",
      "145": "Banque Populaire",
    };
    return bankMap[bankCode] || "Banque inconnue";
  };
  
  const validateCIN = (cinValue: string) => {
    const cinRegex = /^[A-Z]{1,2}[0-9]{4,8}$/i; 
    return cinRegex.test(cinValue);
  };

  const validateRIB = (ribValue: string) => {
    // 1. Longueur (24 chiffres)
    if (!/^\d{24}$/.test(ribValue)) {
      return { valid: false, msg: "Le RIB doit contenir exactement 24 chiffres." };
    }

    // 2. Vérification du Code Banque (3 premiers chiffres)
    const bankCode = ribValue.substring(0, 3);
    const allowedBanks = ['007', '145', '230']; 
    
    if (!allowedBanks.includes(bankCode)) {
      return { 
        valid: false, 
        msg: `Banque non supportée (Code: ${bankCode}). Seuls CIH (230), Attijari (007) et BP (145) sont acceptés.` 
      };
    }

    return { valid: true };
  };

  // --- LOGIQUE CONNEXION ---
  const handleEmailSignIn = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await signIn.create({ identifier: email, password });

      if (result.status === "complete") {
        localStorage.setItem('agentTempPassword', password); 
        await setActive({ session: result.createdSessionId });
        navigate("/auth-callback");
      } 
      else if (result.status === "needs_second_factor") {
        setVerifying2FA(true);
        setCode(""); 
        setError(null);
      }
      else {
        setError("Statut de connexion inconnu.");
      }
    } catch (err: any) {
      console.error("Erreur de connexion:", err);
      setError(err.errors?.[0]?.longMessage || "Identifiants incorrects.");
    } finally {
      setIsLoading(false);
    }
  };

  const handle2FASignIn = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await signIn.attemptSecondFactor({ strategy: "totp", code });
      if (result.status === "complete") {
        await setActive({ session: result.createdSessionId });
        navigate("/auth-callback");
      } else {
        setError("Code invalide ou incomplet.");
      }
    } catch (err: any) {
      setError("Code incorrect ou expiré.");
    } finally {
      setIsLoading(false);
    }
  };

  // --- LOGIQUE INSCRIPTION AVEC DÉTECTION AUTO ---
  const handleSignUp = async () => {
    // 1. Validations de base
    if (!firstName.trim()) { setError("Le Prénom est obligatoire"); return; }
    if (!lastName.trim()) { setError("Le Nom est obligatoire"); return; }
    if (!cin.trim()) { setError("Le CIN est obligatoire"); return; }
    if (!rib.trim()) { setError("Le RIB est obligatoire"); return; }

    // 2. Validation Format CIN
    if (!validateCIN(cin)) {
      setError("Format CIN invalide. Exemple attendu: AA123456");
      return;
    }

    // 3. Validation Format et Code Banque RIB
    const ribCheck = validateRIB(rib);
    if (!ribCheck.valid) {
      setError(ribCheck.msg || "RIB invalide");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // --- CORRECTION ICI : Extraction automatique ---
      const detectedBankCode = rib.substring(0, 3);
      
      const userData = { cin: cin.toUpperCase(), rib, bank_code: detectedBankCode }; 
      localStorage.setItem('userRegistrationData', JSON.stringify(userData));

      await signUp.create({
        emailAddress: email,
        password,
        firstName,
        lastName,
      });

      await signUp.prepareEmailAddressVerification({ strategy: "email_code" });
      setPendingVerification(true);
      setCode(""); 
    } catch (err: any) {
      console.error("Erreur d'inscription:", err);
      setError(err.errors?.[0]?.longMessage || "Erreur lors de l'inscription.");
      localStorage.removeItem('userRegistrationData');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerification = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const completeSignUp = await signUp.attemptEmailAddressVerification({ code });
      if (completeSignUp.status === "complete") {
        await setActive({ session: completeSignUp.createdSessionId });
        navigate("/auth-callback");
      }
    } catch (err: any) {
      setError(err.errors?.[0]?.longMessage || "Code de vérification invalide.");
    } finally {
      setIsLoading(false);
    }
  };

  if (showForgotPassword) return <ForgotPassword onBack={() => setShowForgotPassword(false)} />;

  const gradientButtonClass = "w-full bg-gradient-to-r from-cyan-600 via-yellow-500 to-orange-500 hover:from-cyan-700 hover:via-yellow-600 hover:to-orange-600 text-white font-bold transition-all duration-300 transform hover:scale-[1.02] shadow-lg border-0";
  const inputClass = "bg-zinc-800 border-zinc-700 text-white focus:border-cyan-500 transition-colors placeholder:text-zinc-500";

  return (
    <div className="max-w-4xl w-full mx-auto bg-zinc-900/80 backdrop-blur-xl rounded-2xl shadow-2xl overflow-hidden flex flex-col lg:flex-row relative z-10 border border-zinc-700">
      <div id="clerk-captcha"></div>
      <div className="p-8 flex-1">
        <h1 className="text-3xl font-bold text-white text-center mb-6 tracking-tight">
          Bienvenue sur <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-yellow-400 to-orange-400">FraudDetect</span>
        </h1>

        {verifying2FA ? (
           <div className="animate-in fade-in slide-in-from-bottom-4 duration-300">
             {/* ... (Bloc 2FA inchangé) ... */}
             <div className="flex flex-col items-center mb-6">
                <div className="h-16 w-16 bg-cyan-500/10 rounded-full flex items-center justify-center mb-4 ring-1 ring-cyan-500/50">
                    <ShieldCheck className="h-8 w-8 text-cyan-400" />
                </div>
                <h2 className="text-xl font-semibold text-white">Double Authentification</h2>
                <p className="text-zinc-400 text-center text-sm mt-2">
                  Veuillez entrer le code à 6 chiffres depuis votre application Authenticator.
                </p>
             </div>

            <Input
              type="text"
              placeholder="000000"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className={`${inputClass} mb-4 text-center text-2xl tracking-[0.5em] h-14`}
              maxLength={6}
              autoFocus
              onKeyDown={(e) => e.key === "Enter" && handle2FASignIn()}
            />
            {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}
            
            <Button onClick={handle2FASignIn} disabled={isLoading || code.length < 6} className={gradientButtonClass}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Valider le code"}
            </Button>
            <Button onClick={() => { setVerifying2FA(false); setCode(""); setError(null); }} variant="ghost" className="w-full text-zinc-400 hover:text-white mt-2">
              Retour à la connexion
            </Button>
           </div>
        ) 
        : pendingVerification ? (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            {/* ... (Bloc Vérification Email inchangé) ... */}
            <h2 className="text-xl font-semibold text-white text-center mb-4">Vérification Email</h2>
            <p className="text-zinc-400 text-center mb-6 text-sm">
              Un code de vérification a été envoyé à <span className="text-cyan-400">{email}</span>.
            </p>
            <Input
              type="text"
              placeholder="Code de vérification"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className={`${inputClass} mb-4 text-center tracking-widest`}
              onKeyDown={(e) => e.key === "Enter" && handleVerification()}
            />
            {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}
            <Button onClick={handleVerification} disabled={isLoading} className={gradientButtonClass}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Vérifier l'email"}
            </Button>
            <Button onClick={() => { setPendingVerification(false); setCode(""); }} variant="ghost" className="w-full text-zinc-400 hover:text-white border-zinc-700 mt-2">
              Retour
            </Button>
          </div>
        ) 
        : (
          <Tabs value={activeTab} onValueChange={(val) => { setActiveTab(val); setError(null); }} className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-zinc-800 p-1 rounded-lg mb-6">
              <TabsTrigger value="login" className="data-[state=active]:bg-zinc-700 data-[state=active]:text-white text-zinc-400">Connexion</TabsTrigger>
              <TabsTrigger value="signup" className="data-[state=active]:bg-zinc-700 data-[state=active]:text-white text-zinc-400">Inscription</TabsTrigger>
            </TabsList>

            <TabsContent value="login" className="animate-in fade-in slide-in-from-left-4 duration-300">
              {/* ... (Contenu Login inchangé) ... */}
              <div className="space-y-4">
                <Input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className={inputClass} onKeyDown={(e) => e.key === "Enter" && handleEmailSignIn()} />
                <div className="relative">
                  <Input type={showPassword ? "text" : "password"} placeholder="Mot de passe" value={password} onChange={(e) => setPassword(e.target.value)} className={`${inputClass} pr-10`} onKeyDown={(e) => e.key === "Enter" && handleEmailSignIn()} />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute inset-y-0 right-0 pr-3 flex items-center text-zinc-400 hover:text-white">
                    {showPassword ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
                {error && <p className="text-red-500 text-sm text-center bg-red-900/10 p-2 rounded border border-red-900/20">{error}</p>}
                
                <Button onClick={handleEmailSignIn} disabled={isLoading} className={gradientButtonClass}>
                  {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Se connecter"}
                </Button>
                
                <div className="text-center">
                  <Button variant="link" onClick={() => setShowForgotPassword(true)} className="text-zinc-400 hover:text-cyan-400 text-sm transition-colors">
                    Mot de passe oublié ?
                  </Button>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="signup" className="animate-in fade-in slide-in-from-right-4 duration-300">
               <div className="space-y-4">
                <div className="flex gap-4">
                  <Input type="text" placeholder="Prénom" value={firstName} onChange={(e) => setFirstName(e.target.value)} className={`${inputClass} flex-1`} />
                  <Input type="text" placeholder="Nom" value={lastName} onChange={(e) => setLastName(e.target.value)} className={`${inputClass} flex-1`} />
                </div>
                <Input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className={inputClass} />
                <div className="relative">
                  <Input type={showPassword ? "text" : "password"} placeholder="Mot de passe" value={password} onChange={(e) => setPassword(e.target.value)} className={`${inputClass} pr-10`} />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute inset-y-0 right-0 pr-3 flex items-center text-zinc-400 hover:text-white">
                    {showPassword ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input 
                    type="text" 
                    placeholder="CIN (ex: AA123456)" 
                    value={cin} 
                    onChange={(e) => setCin(e.target.value)} 
                    className={inputClass} 
                  />
                  <Input 
                    type="text" 
                    placeholder="RIB (24 chiffres)" 
                    value={rib} 
                    onChange={(e) => setRib(e.target.value)} 
                    className={inputClass} 
                    maxLength={24}
                  />
                </div>
                
                {/* --- MODIFICATION ICI : Affichage auto de la banque au lieu du Select --- */}
                {rib.length >= 3 && (
                  <div className={`text-sm p-3 rounded border flex items-center gap-2 transition-all duration-300 ${
                    getRIBBankName(rib) !== "Banque inconnue" 
                      ? "bg-cyan-950/30 border-cyan-800 text-cyan-400" 
                      : "bg-red-900/10 border-red-900/20 text-red-400"
                  }`}>
                    <Building2 className="h-4 w-4" />
                    <span>
                      {getRIBBankName(rib) === "Banque inconnue" 
                        ? "Banque non reconnue (Codes supportés: 230, 007, 145)" 
                        : `Banque détectée : ${getRIBBankName(rib)}`
                      }
                    </span>
                  </div>
                )}
                
                {error && <p className="text-red-500 text-sm text-center bg-red-900/10 p-2 rounded border border-red-900/20">{error}</p>}
                
                <PasswordStrengthMeter password={password} />
                
                <Button onClick={handleSignUp} disabled={isLoading} className={gradientButtonClass}>
                  {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "S'inscrire"}
                </Button>

                <div className="text-center mt-2">
                    <Button variant="link" onClick={() => signOut()} className="text-zinc-500 hover:text-zinc-300 text-xs">
                        Problème de connexion ? Se déconnecter
                    </Button>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        )}
      </div>
      
      <div className="flex-1 hidden lg:block bg-zinc-800 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-900/30 via-transparent to-orange-900/30 pointer-events-none z-10" />
        <AuthImagePattern title="Sécurité Unifiée" subtitle="Une protection avancée et centralisée pour CIH, Attijariwafa et BCP." />
      </div>
    </div>
  );
};

export default AuthPage;