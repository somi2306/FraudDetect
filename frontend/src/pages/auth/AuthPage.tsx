// AuthPage.tsx
import { useSignIn, useSignUp, useClerk } from "@clerk/clerk-react";
import { Button } from "../../components/ui/button";
import { useState } from "react";
import { Input } from "../../components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import PasswordStrengthMeter from "../../components/PasswordStrengthMeter";
import AuthImagePattern from "../../components/AuthImagePattern";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import ForgotPassword from "../../components/ForgotPassword"; 
// Les imports pour 'Select' ont été supprimés

const AuthPage = () => {
  const { signIn, isLoaded: isSignInLoaded } = useSignIn();
  const { signUp, isLoaded: isSignUpLoaded } = useSignUp();
  const { setActive } = useClerk();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [cin, setCin] = useState("");
  const [rib, setRib] = useState("");
  // const [role, setRole] = useState(""); // <-- Supprimé
  const [activeTab, setActiveTab] = useState("login");
  const [pendingVerification, setPendingVerification] = useState(false);
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);

  if (!isSignInLoaded || !isSignUpLoaded) return null;

  const handleEmailSignIn = async () => {
    try {
      const result = await signIn.create({
        identifier: email,
        password,
      });

      if (result.status === "complete") {
        await setActive({ session: result.createdSessionId });
        window.location.href = "/auth-callback";
      }
    } catch (err: any) {
      console.error("Erreur de connexion:", err);
      setError(err.errors?.[0]?.longMessage || "Une erreur s'est produite lors de la connexion.");
    }
  };

  const handleSignUp = async () => {
    // Validation des champs supplémentaires
    if (!cin.trim()) {
      setError("Le CIN est obligatoire");
      return;
    }
    if (!rib.trim()) {
      setError("Le RIB est obligatoire");
      return;
    }
    // La validation du rôle a été supprimée

    try {
      // Sauvegarder les données supplémentaires dans le localStorage
      const userData = { cin, rib }; // 'role' a été supprimé de cet objet
      localStorage.setItem('userRegistrationData', JSON.stringify(userData));

      await signUp.create({
        emailAddress: email,
        password,
        firstName,
        lastName,
      });

      await signUp.prepareEmailAddressVerification({ strategy: "email_code" });
      setPendingVerification(true);
    } catch (err: any) {
      console.error("Erreur d'inscription:", err);
      setError(err.errors?.[0]?.longMessage || "Une erreur s'est produite lors de l'inscription.");
      // Nettoyer en cas d'erreur
      localStorage.removeItem('userRegistrationData');
    }
  };

  const handleVerification = async () => {
    try {
      const completeSignUp = await signUp.attemptEmailAddressVerification({ code });

      if (completeSignUp.status === "complete") {
        await setActive({ session: completeSignUp.createdSessionId });
        window.location.href = "/auth-callback";
      }
    } catch (err: any) {
      console.error("Erreur de vérification:", err);
      setError(err.errors?.[0]?.longMessage || "Code de vérification invalide.");
    }
  };

  if (showForgotPassword) {
    return <ForgotPassword onBack={() => setShowForgotPassword(false)} />;
  }

  return (
    <div className="max-w-4xl w-full mx-auto bg-zinc-900 bg-opacity-50 backdrop-filter backdrop-blur-xl rounded-2xl shadow-xl overflow-hidden flex flex-col lg:flex-row relative z-10">
      <div id="clerk-captcha"></div>
      <div className="p-8 flex-1">
        <h1 className="text-2xl font-bold text-white text-center mb-6">Bienvenue</h1>

        {pendingVerification ? (
          <>
            <p className="text-zinc-400 text-center mb-4">
              Un code de vérification a été envoyé à {email}.
            </p>
            <Input
              type="text"
              placeholder="Code de vérification"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="bg-zinc-800 border-zinc-700 text-white mb-4"
            />
            {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}
            <Button
              onClick={handleVerification}
              className="w-full bg-emerald-500 hover:bg-emerald-600 text-black mb-4"
            >
              Vérifier
            </Button>
            <Button
              onClick={() => setPendingVerification(false)}
              variant="outline"
              className="w-full bg-zinc-800 hover:bg-zinc-700 text-white border-zinc-700"
            >
              Retour
            </Button>
          </>
        ) : (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-zinc-800">
              <TabsTrigger value="login" className="text-white">Connexion</TabsTrigger>
              <TabsTrigger value="signup" className="text-white">Inscription</TabsTrigger>
            </TabsList>

            <TabsContent value="login">
              <div className="space-y-4 mt-4">
                <Input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-zinc-800 border-zinc-700 text-white"
                />
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Mot de passe"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-zinc-800 border-zinc-700 text-white pr-10"
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
                  className="w-full bg-emerald-500 hover:bg-emerald-600 text-black"
                >
                  Se connecter avec Email
                </Button>
                <div className="text-center">
                  <Button
                    variant="link"
                    onClick={() => setShowForgotPassword(true)}
                    className="text-zinc-400 hover:text-white"
                  >
                    Mot de passe oublié ?
                  </Button>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="signup">
              <div className="space-y-4 mt-4">
                <div className="flex gap-4">
                  <Input
                    type="text"
                    placeholder="Prénom"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    className="bg-zinc-800 border-zinc-700 text-white flex-1"
                  />
                  <Input
                    type="text"
                    placeholder="Nom"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    className="bg-zinc-800 border-zinc-700 text-white flex-1"
                  />
                </div>
                <Input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-zinc-800 border-zinc-700 text-white"
                />
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Mot de passe"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-zinc-800 border-zinc-700 text-white pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-zinc-400 hover:text-white"
                  >
                    {showPassword ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
                
                {/* CHAMPS CIN ET RIB */}
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    type="text"
                    placeholder="CIN"
                    value={cin}
                    onChange={(e) => setCin(e.target.value)}
                    className="bg-zinc-800 border-zinc-700 text-white"
                  />
                  <Input
                    type="text"
                    placeholder="RIB"
                    value={rib}
                    onChange={(e) => setRib(e.target.value)}
                    className="bg-zinc-800 border-zinc-700 text-white"
                  />
                </div>
                
                {/* Le bloc <Select> pour le rôle a été supprimé d'ici */}

                {error && <p className="text-red-500 text-sm text-center">{error}</p>}
                <PasswordStrengthMeter password={password} />
                <Button
                  onClick={handleSignUp}
                  className="w-full bg-emerald-500 hover:bg-emerald-600 text-black"
                >
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