import { useState, useEffect } from "react";
import { useUser } from "@clerk/clerk-react";
import { QRCodeSVG } from "qrcode.react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, ShieldCheck, Smartphone } from "lucide-react";
import { useNavigate } from "react-router-dom";

// Définition d'un type partiel pour la ressource TOTP
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
          // @ts-ignore
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
      const result = await user.verifyTOTP({ code });
      if (result.verified) {
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

  // --- STYLES UNIFIÉS ---
  const gradientTextClass = "text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-yellow-400 to-orange-400";
  const gradientButtonClass = "w-full bg-gradient-to-r from-cyan-600 via-yellow-500 to-orange-500 hover:from-cyan-700 hover:via-yellow-600 hover:to-orange-600 text-white font-bold transition-all duration-300 transform hover:scale-[1.02] shadow-lg border-0";
  const inputClass = "bg-zinc-900 border-zinc-600 text-white text-center text-lg tracking-widest focus:border-cyan-500 transition-colors";

  if (!totp && !error) {
    return (
      <div className="flex items-center justify-center h-screen bg-zinc-900">
        <Loader2 className="animate-spin text-cyan-500 h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-zinc-900 p-4 relative overflow-hidden">
      
      {/* Décoration de fond */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-cyan-600/10 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-orange-600/10 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

      <Card className="w-full max-w-md bg-zinc-800/80 backdrop-blur border-zinc-700 text-white shadow-2xl z-10">
        <CardHeader className="text-center">
          <div className="mx-auto h-16 w-16 bg-zinc-900 rounded-full flex items-center justify-center mb-4 ring-1 ring-zinc-600">
             <ShieldCheck className="h-8 w-8 text-cyan-400" />
          </div>
          <CardTitle className={`text-2xl font-bold ${gradientTextClass}`}>Sécurisation Requise</CardTitle>
          <CardDescription className="text-zinc-400">
            En tant qu'administrateur, vous devez activer la double authentification.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive" className="bg-red-900/20 border-red-500/50 text-red-200">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex flex-col items-center justify-center p-4 bg-white rounded-xl mx-auto w-fit shadow-inner">
            {totp?.uri && (
              <QRCodeSVG value={totp.uri} size={180} />
            )}
          </div>

          <div className="space-y-2 text-center text-sm text-zinc-400">
            <p className="flex items-center justify-center gap-2"><Smartphone className="h-4 w-4 text-cyan-500"/> 1. Ouvrez Google Authenticator</p>
            <p>2. Scannez le QR Code ci-dessus</p>
            <p>3. Entrez le code à 6 chiffres généré</p>
          </div>

          <div className="space-y-4">
            <Input
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="000000"
              className={inputClass}
              maxLength={6}
            />
            <Button 
              onClick={handleVerify} 
              disabled={loading || code.length !== 6}
              className={gradientButtonClass}
            >
              {loading ? <Loader2 className="animate-spin mr-2 h-4 w-4" /> : "Activer et Continuer"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminTwoFactorSetup;