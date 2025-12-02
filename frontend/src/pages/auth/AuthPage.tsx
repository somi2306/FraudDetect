import { useSignIn, useSignUp, useClerk, useUser } from "@clerk/clerk-react";
import { Button } from "../../components/ui/button";
import { useState, useEffect } from "react";
import { Input } from "../../components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import PasswordStrengthMeter from "../../components/PasswordStrengthMeter";
import AuthImagePattern from "../../components/AuthImagePattern";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import ForgotPassword from "../../components/ForgotPassword"; 
import { ShieldCheck, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

const AuthPage = () => {
  const { signIn, isLoaded: isSignInLoaded } = useSignIn();
  const { signUp, isLoaded: isSignUpLoaded } = useSignUp();
  const { setActive } = useClerk();
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

  const [activeTab, setActiveTab] = useState("login");
  
  // --- ÉTATS DE FLUX ---
  const [pendingVerification, setPendingVerification] = useState(false); // Pour l'email à l'inscription
  const [verifying2FA, setVerifying2FA] = useState(false); // Pour le TOTP à la connexion
  
  const [code, setCode] = useState(""); // Utilisé pour Email ET TOTP
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // --- REDIRECTION AUTOMATIQUE SI DÉJÀ CONNECTÉ ---
  useEffect(() => {
    if (isUserLoaded && isSignedIn) {
      navigate("/auth-callback");
    }
  }, [isUserLoaded, isSignedIn, navigate]);

  if (!isSignInLoaded || !isSignUpLoaded) {
    return (
      <div className="flex items-center justify-center h-screen bg-zinc-900">
        <Loader2 className="animate-spin text-emerald-500 h-8 w-8" />
      </div>
    );
  }

  // --- LOGIQUE CONNEXION (LOGIN) ---
  const handleEmailSignIn = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await signIn.create({
        identifier: email,
        password,
      });

      if (result.status === "complete") {
        // --- AJOUT IMPORTANT ---
        // On sauvegarde le mot de passe temporairement pour le cas "Premier Login Agent"
        localStorage.setItem('agentTempPassword', password); 
        // -----------------------

        await setActive({ session: result.createdSessionId });
        navigate("/auth-callback");
      }
      // DÉTECTION DU 2FA (POUR LES ADMINS)
      else if (result.status === "needs_second_factor") {
        setVerifying2FA(true);
        setCode(""); 
        setError(null);
      }
      else {
        console.log(result);
        setError("Statut de connexion inconnu.");
      }
    } catch (err: any) {
      console.error("Erreur de connexion:", err);
      setError(err.errors?.[0]?.longMessage || "Identifiants incorrects.");
    } finally {
      setIsLoading(false);
    }
  };

  // --- LOGIQUE VALIDATION 2FA (TOTP) ---
  const handle2FASignIn = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await signIn.attemptSecondFactor({
        strategy: "totp",
        code: code,
      });

      if (result.status === "complete") {
        await setActive({ session: result.createdSessionId });
        navigate("/auth-callback");
      } else {
        setError("Code invalide ou incomplet.");
      }
    } catch (err: any) {
      console.error("Erreur 2FA:", err);
      setError("Code incorrect ou expiré.");
    } finally {
      setIsLoading(false);
    }
  };

  // --- LOGIQUE INSCRIPTION (SIGNUP) ---
  const handleSignUp = async () => {
    if (!cin.trim()) { setError("Le CIN est obligatoire"); return; }
    if (!rib.trim()) { setError("Le RIB est obligatoire"); return; }
    setIsLoading(true);
    setError(null);

    try {
      const userData = { cin, rib };
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

  // --- LOGIQUE VERIFICATION EMAIL (INSCRIPTION) ---
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

  return (
    <div className="max-w-4xl w-full mx-auto bg-zinc-900 bg-opacity-50 backdrop-filter backdrop-blur-xl rounded-2xl shadow-xl overflow-hidden flex flex-col lg:flex-row relative z-10">
      <div id="clerk-captcha"></div>
      <div className="p-8 flex-1">
        <h1 className="text-2xl font-bold text-white text-center mb-6">Bienvenue</h1>

        {/* --- CAS 1 : VÉRIFICATION 2FA (ADMIN) --- */}
        {verifying2FA ? (
           <div className="animate-in fade-in slide-in-from-bottom-4 duration-300">
             <div className="flex flex-col items-center mb-6">
                <div className="h-16 w-16 bg-emerald-500/10 rounded-full flex items-center justify-center mb-4">
                    <ShieldCheck className="h-8 w-8 text-emerald-500" />
                </div>
                <h2 className="text-xl font-semibold text-white">Double Authentification</h2>
                <p className="text-zinc-400 text-center text-sm mt-2">
                  Veuillez ouvrir Google Authenticator et entrer le code à 6 chiffres.
                </p>
             </div>

            <Input
              type="text"
              placeholder="000000"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="bg-zinc-800 border-zinc-700 text-white mb-4 text-center text-2xl tracking-[0.5em] h-14"
              maxLength={6}
              autoFocus
              onKeyDown={(e) => e.key === "Enter" && handle2FASignIn()}
            />
            {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}
            
            <Button
              onClick={handle2FASignIn}
              disabled={isLoading || code.length < 6}
              className="w-full bg-emerald-500 hover:bg-emerald-600 text-black mb-4 font-bold"
            >
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Valider le code
            </Button>
            <Button
              onClick={() => { setVerifying2FA(false); setCode(""); setError(null); }}
              variant="ghost"
              className="w-full text-zinc-400 hover:text-white"
            >
              Retour à la connexion
            </Button>
           </div>
        ) 
        // --- CAS 2 : VÉRIFICATION EMAIL (INSCRIPTION) ---
        : pendingVerification ? (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            <h2 className="text-xl font-semibold text-white text-center mb-4">Vérification Email</h2>
            <p className="text-zinc-400 text-center mb-6 text-sm">
              Un code de vérification a été envoyé à <span className="text-emerald-400">{email}</span>.
            </p>
            <Input
              type="text"
              placeholder="Code de vérification"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="bg-zinc-800 border-zinc-700 text-white mb-4 text-center tracking-widest"
              onKeyDown={(e) => e.key === "Enter" && handleVerification()}
            />
            {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}
            <Button
              onClick={handleVerification}
              disabled={isLoading}
              className="w-full bg-emerald-500 hover:bg-emerald-600 text-black mb-4"
            >
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Vérifier l'email
            </Button>
            <Button
              onClick={() => { setPendingVerification(false); setCode(""); }}
              variant="outline"
              className="w-full bg-zinc-800 hover:bg-zinc-700 text-white border-zinc-700"
            >
              Retour
            </Button>
          </div>
        ) 
        // --- CAS 3 : FORMULAIRES LOGIN / SIGNUP ---
        : (
          <Tabs value={activeTab} onValueChange={(val) => { setActiveTab(val); setError(null); }} className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-zinc-800">
              <TabsTrigger value="login" className="text-white">Connexion</TabsTrigger>
              <TabsTrigger value="signup" className="text-white">Inscription</TabsTrigger>
            </TabsList>

            <TabsContent value="login" className="animate-in fade-in slide-in-from-left-4 duration-300">
              <div className="space-y-4 mt-4">
                <Input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-zinc-800 border-zinc-700 text-white"
                  onKeyDown={(e) => e.key === "Enter" && handleEmailSignIn()}
                />
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Mot de passe"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-zinc-800 border-zinc-700 text-white pr-10"
                    onKeyDown={(e) => e.key === "Enter" && handleEmailSignIn()}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-zinc-400 hover:text-white"
                  >
                    {showPassword ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
                {error && <p className="text-red-500 text-sm text-center">{error}</p>}
                <Button
                  onClick={handleEmailSignIn}
                  disabled={isLoading}
                  className="w-full bg-emerald-500 hover:bg-emerald-600 text-black font-bold"
                >
                  {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                  Se connecter
                </Button>
                <div className="text-center">
                  <Button
                    variant="link"
                    onClick={() => setShowForgotPassword(true)}
                    className="text-zinc-400 hover:text-white text-sm"
                  >
                    Mot de passe oublié ?
                  </Button>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="signup" className="animate-in fade-in slide-in-from-right-4 duration-300">
               <div className="space-y-4 mt-4">
                <div className="flex gap-4">
                  <Input type="text" placeholder="Prénom" value={firstName} onChange={(e) => setFirstName(e.target.value)} className="bg-zinc-800 border-zinc-700 text-white flex-1" />
                  <Input type="text" placeholder="Nom" value={lastName} onChange={(e) => setLastName(e.target.value)} className="bg-zinc-800 border-zinc-700 text-white flex-1" />
                </div>
                <Input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="bg-zinc-800 border-zinc-700 text-white" />
                <div className="relative">
                  <Input type={showPassword ? "text" : "password"} placeholder="Mot de passe" value={password} onChange={(e) => setPassword(e.target.value)} className="bg-zinc-800 border-zinc-700 text-white pr-10" />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute inset-y-0 right-0 pr-3 flex items-center text-zinc-400 hover:text-white">
                    {showPassword ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input type="text" placeholder="CIN" value={cin} onChange={(e) => setCin(e.target.value)} className="bg-zinc-800 border-zinc-700 text-white" />
                  <Input type="text" placeholder="RIB" value={rib} onChange={(e) => setRib(e.target.value)} className="bg-zinc-800 border-zinc-700 text-white" />
                </div>
                {error && <p className="text-red-500 text-sm text-center">{error}</p>}
                <PasswordStrengthMeter password={password} />
                <Button onClick={handleSignUp} disabled={isLoading} className="w-full bg-emerald-500 hover:bg-emerald-600 text-black font-bold">
                  {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                  S'inscrire
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        )}
      </div>
      <div className="flex-1 hidden lg:block">
        <AuthImagePattern
          title="FraudDetect"
          subtitle="Bienvenue sur la plateforme de détection de fraude"
        />
      </div>
    </div>
  );
};

export default AuthPage;