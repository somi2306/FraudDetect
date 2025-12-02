import { useState, useEffect } from "react";
import { useUser } from "@clerk/clerk-react";
import { QRCodeSVG } from "qrcode.react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

// Définition d'un type partiel pour la ressource TOTP pour éviter les erreurs TypeScript strictes
interface TOTPResource {
  id: string;
  secret?: string;
  uri?: string;
  verified: boolean;
  backupCodes?: string[];
}

const AdminTwoFactorSetup = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [totp, setTotp] = useState<TOTPResource | null>(null);
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const setupTOTP = async () => {
      if (!user) return;

      if (user.twoFactorEnabled) {
        navigate("/");
        return;
      }

      if (!totp) {
        try {
          // @ts-ignore - Le type retourné par Clerk est compatible mais parfois incomplet dans les définitions
          const totpResource = await user.createTOTP();
          setTotp(totpResource);
        } catch (err) {
          console.error("Erreur création TOTP", err);
          setError("Impossible de générer le code QR.");
        }
      }
    };
    setupTOTP();
  }, [user, navigate, totp]);

  const handleVerify = async () => {
    if (!user) return;
    setLoading(true);
    setError("");

    try {
      // CORRECTION ICI : Utiliser user.verifyTOTP au lieu de totp.attemptVerification
      const result = await user.verifyTOTP({ code });
      
      // CORRECTION ICI : Vérifier la propriété booléenne 'verified'
      if (result.verified) {
        // Optionnel : Vous pouvez créer des codes de secours ici si nécessaire
        // await user.createBackupCode(); 
        
        navigate("/"); 
      } else {
        setError("Code incorrect. Veuillez réessayer.");
      }
    } catch (err: any) {
      console.error(err);
      setError(err.errors?.[0]?.longMessage || "Erreur de vérification.");
    } finally {
      setLoading(false);
    }
  };

  if (!totp && !error) {
    return (
      <div className="flex items-center justify-center h-screen bg-zinc-900">
        <Loader2 className="animate-spin text-emerald-500 h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-zinc-900 p-4">
      <Card className="w-full max-w-md bg-zinc-800 border-zinc-700 text-white">
        <CardHeader>
          <CardTitle className="text-emerald-500">Sécurisation Admin Requise</CardTitle>
          <CardDescription className="text-zinc-400">
            En tant qu'administrateur, vous devez activer la double authentification.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive" className="bg-red-900/50 border-red-800 text-red-200">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex flex-col items-center justify-center p-4 bg-white rounded-lg mx-auto w-fit">
            {totp?.uri && (
              <QRCodeSVG value={totp.uri} size={180} />
            )}
          </div>

          <div className="space-y-2 text-center text-sm text-zinc-300">
            <p>1. Ouvrez Google Authenticator sur votre téléphone.</p>
            <p>2. Scannez le QR Code ci-dessus.</p>
            <p>3. Entrez le code à 6 chiffres généré.</p>
          </div>

          <div className="space-y-4">
            <Input
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="000000"
              className="bg-zinc-900 border-zinc-600 text-white text-center text-lg tracking-widest"
              maxLength={6}
            />
            <Button 
              onClick={handleVerify} 
              disabled={loading || code.length !== 6}
              className="w-full bg-emerald-500 hover:bg-emerald-600 text-black font-bold"
            >
              {loading ? <Loader2 className="animate-spin mr-2 h-4 w-4" /> : null}
              Activer et Continuer
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminTwoFactorSetup;