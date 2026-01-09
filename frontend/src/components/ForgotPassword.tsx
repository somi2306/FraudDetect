import React, { useState, useEffect } from 'react';
import { useSignIn, useClerk } from '@clerk/clerk-react'; // Ajout de useClerk
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, ArrowLeft, KeyRound, MailCheck, ShieldAlert, ShieldCheck } from 'lucide-react';

interface ForgotPasswordProps {
  onBack: () => void;
}

const ForgotPassword: React.FC<ForgotPasswordProps> = ({ onBack }) => {
  const { signIn, isLoaded } = useSignIn();
  const { signOut } = useClerk(); // Récupération de la fonction de déconnexion
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [totpCode, setTotpCode] = useState('');
  
  const [step, setStep] = useState<'email' | 'code' | 'new_password' | '2fa'>('email');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // --- 1. Nettoyage de session au démarrage ---
  // Pour éviter l'erreur "You're already signed in" si une vieille session traîne
  useEffect(() => {
    const cleanSession = async () => {
        await signOut();
    };
    cleanSession();
  }, [signOut]);

  // --- STYLES UNIFIÉS ---
  const gradientButtonClass = "w-full bg-gradient-to-r from-cyan-600 via-yellow-500 to-orange-500 hover:from-cyan-700 hover:via-yellow-600 hover:to-orange-600 text-white font-bold transition-all duration-300 transform hover:scale-[1.02] shadow-lg border-0";
  const inputClass = "bg-zinc-800 border-zinc-700 text-white focus:border-cyan-500 transition-colors placeholder:text-zinc-500";
  const gradientTextClass = "text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-yellow-400 to-orange-400";

  if (!isLoaded) return null;

  // 1. Envoyer le code Email
  const handleSendCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      // On crée une tentative de connexion de type "Reset Password"
      await signIn.create({
        strategy: 'reset_password_email_code',
        identifier: email,
      });
      setStep('code');
    } catch (err: any) {
      console.error(err);
      // Gestion spécifique si l'utilisateur est déjà connecté malgré le useEffect
      if (err.errors?.[0]?.code === "session_exists") {
          await signOut();
          setError("Session existante détectée. Veuillez réessayer.");
      } else {
          setError(err.errors?.[0]?.longMessage || "Impossible d'envoyer le code. Vérifiez l'email.");
      }
    } finally {
      setLoading(false);
    }
  };

  // 2. Valider le code (Transition locale)
  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (code.length < 6) {
        setError("Le code doit contenir 6 chiffres.");
        return;
    }
    setStep('new_password');
  };

  // 3. Réinitialiser le mot de passe (+ Check 2FA)
  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const result = await signIn.attemptFirstFactor({
        strategy: 'reset_password_email_code',
        code,
        password,
      });

      if (result.status === 'complete') {
        // --- CORRECTION MAJEURE ICI ---
        // Clerk connecte automatiquement l'utilisateur après un reset réussi.
        // Nous le déconnectons immédiatement pour forcer une reconnexion manuelle.
        await signOut(); 
        
        alert("Mot de passe modifié avec succès ! Veuillez vous reconnecter.");
        onBack();
      } 
      else if (result.status === 'needs_second_factor') {
        setStep('2fa');
      } 
      else {
        console.log(result);
        setError("La réinitialisation n'a pas pu être complétée.");
      }
    } catch (err: any) {
      console.error(err);
      const msg = err.errors?.[0]?.longMessage;
      if (msg?.includes("code")) {
          setError("Code email incorrect ou expiré.");
          setStep('code'); 
      } else {
          setError(msg || "Erreur lors de la réinitialisation.");
      }
    } finally {
      setLoading(false);
    }
  };

  // 4. Valider la 2FA (Si nécessaire)
  const handleVerify2FA = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const result = await signIn.attemptSecondFactor({
        strategy: 'totp',
        code: totpCode,
      });

      if (result.status === 'complete') {
        // Même ici, si la 2FA passe, on déconnecte pour forcer le login propre
        await signOut();
        
        alert("Sécurité validée et mot de passe changé ! Veuillez vous reconnecter.");
        onBack(); 
      } else {
        setError("Code 2FA invalide.");
      }
    } catch (err: any) {
      console.error(err);
      setError("Erreur lors de la validation 2FA.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md w-full mx-auto p-8 bg-zinc-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-zinc-700 animate-in fade-in zoom-in duration-300">
      
      {/* Header */}
      <div className="text-center mb-8">
        <div className="mx-auto h-12 w-12 bg-zinc-800 rounded-full flex items-center justify-center mb-4 ring-1 ring-zinc-700">
            {step === 'email' && <KeyRound className="h-6 w-6 text-cyan-400" />}
            {step === 'code' && <MailCheck className="h-6 w-6 text-yellow-400" />}
            {step === 'new_password' && <ShieldAlert className="h-6 w-6 text-orange-400" />}
            {step === '2fa' && <ShieldCheck className="h-6 w-6 text-emerald-400" />}
        </div>
        <h2 className={`text-2xl font-bold ${gradientTextClass}`}>
            {step === '2fa' ? 'Double Authentification' : 'Récupération'}
        </h2>
        <p className="text-zinc-400 text-sm mt-2">
            {step === 'email' && "Entrez votre email pour recevoir un code."}
            {step === 'code' && `Code envoyé à ${email}`}
            {step === 'new_password' && "Choisissez votre nouveau mot de passe."}
            {step === '2fa' && "Entrez le code de votre application Authenticator."}
        </p>
      </div>

      {error && (
        <div className="mb-6 p-3 rounded bg-red-900/20 border border-red-500/30 text-red-200 text-sm text-center">
          {error}
        </div>
      )}

      {/* ÉTAPE 1 : EMAIL */}
      {step === 'email' && (
        <form onSubmit={handleSendCode} className="space-y-4">
          <Input
            type="email"
            placeholder="votre@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={inputClass}
            required
          />
          <Button type="submit" disabled={loading} className={gradientButtonClass}>
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Envoyer le code"}
          </Button>
        </form>
      )}

      {/* ÉTAPE 2 : CODE EMAIL */}
      {step === 'code' && (
        <form onSubmit={handleVerifyCode} className="space-y-4">
          <Input
            type="text"
            placeholder="Code Email (6 chiffres)"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className={`${inputClass} text-center tracking-widest text-lg`}
            required
          />
          <Button type="submit" className={gradientButtonClass}>
            Continuer
          </Button>
          <div className="text-center">
             <Button type="button" variant="link" onClick={() => setStep('email')} className="text-zinc-500 text-xs">
                Changer d'email
             </Button>
          </div>
        </form>
      )}

      {/* ÉTAPE 3 : NOUVEAU MOT DE PASSE */}
      {step === 'new_password' && (
        <form onSubmit={handleResetPassword} className="space-y-4">
          <Input
            type="password"
            placeholder="Nouveau mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={inputClass}
            required
            minLength={8}
          />
          <Button type="submit" disabled={loading} className={gradientButtonClass}>
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Réinitialiser le mot de passe"}
          </Button>
        </form>
      )}

      {/* ÉTAPE 4 : CODE 2FA (NOUVEAU) */}
      {step === '2fa' && (
        <form onSubmit={handleVerify2FA} className="space-y-4">
          <Input
            type="text"
            placeholder="Code Authenticator (6 chiffres)"
            value={totpCode}
            onChange={(e) => setTotpCode(e.target.value)}
            className={`${inputClass} text-center tracking-widest text-lg border-emerald-500/50 focus:border-emerald-500`}
            maxLength={6}
            required
            autoFocus
          />
          <Button type="submit" disabled={loading} className={gradientButtonClass}>
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Valider la sécurité"}
          </Button>
        </form>
      )}

      {/* Footer : Bouton Retour */}
      <div className="mt-6 pt-6 border-t border-zinc-800 text-center">
        <Button 
            variant="ghost" 
            onClick={onBack} 
            className="text-zinc-400 hover:text-white hover:bg-zinc-800"
        >
          <ArrowLeft className="mr-2 h-4 w-4" /> Retour à la connexion
        </Button>
      </div>
    </div>
  );
};

export default ForgotPassword;