import { Card, CardContent } from "@/components/ui/card";
import { apiClient } from "@/lib/axios";
import { useUser, useAuth } from "@clerk/clerk-react";
import { Loader } from "lucide-react";
import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

const AuthCallbackPage = () => {
  const { isLoaded, user } = useUser();
  const { getToken } = useAuth();
  const navigate = useNavigate();
  const syncAttempted = useRef(false);

  useEffect(() => {
    const syncUser = async () => {
      // 1. Check basic conditions
      if (!isLoaded || !user || syncAttempted.current) return;

      try {
        syncAttempted.current = true;
        const token = await getToken();
        
        // Récupération des données d'inscription depuis localStorage
        const saved = localStorage.getItem('userRegistrationData');
        const userData = saved ? JSON.parse(saved) : null;
        
        console.log("userData from localStorage:", userData);

        // 2. Build the payload for backend sync
        const basePayload = {
          firstName: user.firstName,
          lastName: user.lastName,
          imageUrl: user.imageUrl,
          email: user.primaryEmailAddress?.emailAddress,
        };

        const payload = userData ? {
          // New user synchronization (using stored CIN/RIB)
          ...basePayload,
          cin: userData.cin,
          rib: userData.rib,
          bank_code: userData.bank_code || null,
        } : {
          // Existing user (CIN/RIB are sent as null, backend should fetch them)
          ...basePayload,
          cin: null,
          rib: null,
          bank_code: null,
        };

        console.log("Synchronisation avec le backend...");
        
        // Appel au backend pour créer ou mettre à jour l'utilisateur
        const response = await apiClient.post(
          "/auth/callback",
          payload,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        const { role, must_reset_password, bank_id } = response.data;
        console.log("Données reçues:", { role, must_reset_password, bank_id });

        // 3. Clean up localStorage
        if (userData) {
          localStorage.removeItem('userRegistrationData');
        }

        // --- 4. LOGIQUE DE ROUTAGE INTELLIGENTE ---

        if (role === "Admin") {
            // CAS ADMIN : Vérification de la double authentification
            if (!user.twoFactorEnabled) {
                console.log("Admin sans 2FA -> Redirection vers Setup");
                navigate("/admin/setup-2fa");
            } else {
                console.log("Admin sécurisé -> Redirection vers Dashboard");
                navigate("/admin/dashboard");
            }
        } 
        else if (role === "Agent") {
            // CAS AGENT : Vérification du changement de mot de passe obligatoire
            if (must_reset_password) {
                console.log("Premier login Agent -> Redirection vers Reset Password");
                // On stocke le mot de passe temporaire pour le reset
                // (Note : Idéalement on ne le stocke pas, mais Clerk demande le current password pour changer)
                // Ici on suppose que l'utilisateur vient de se connecter avec, donc il le connaît.
                navigate("/agent/reset-password");
            } else {
                console.log(`Agent authentifié -> Redirection vers Dashboard Banque (ID: ${bank_id})`);
                navigate("/agent/dashboard");
            }
        } 
        else {
            // CAS BÉNÉFICIAIRE (ou rôle par défaut)
            // Redirection vers le dashboard bénéficiaire au lieu du profil simple
            console.log("Bénéficiaire -> Redirection vers Dashboard");
            navigate("/beneficiary", { replace: true });
        }

      } catch (error) {
        console.error("Erreur critique pendant la synchronisation:", error);
        // En cas d'erreur backend, on redirige vers une page sûre (Beneficiary par défaut)
        // pour ne pas bloquer l'utilisateur authentifié
        navigate("/beneficiary", { replace: true }); 
      }
    };

    // Trigger sync immediately if user is loaded
    if (isLoaded && user && !syncAttempted.current) {
        syncUser();
    } else if (isLoaded && !user) {
        navigate("/auth", { replace: true });
    }
    
  }, [isLoaded, user, getToken, navigate]);

  return (
    <div className="h-screen w-full bg-zinc-950 flex items-center justify-center">
      <Card className="w-[90%] max-w-md bg-zinc-900 border-zinc-800 shadow-2xl">
        <CardContent className="flex flex-col items-center gap-4 pt-8 pb-8">
          <div className="relative">
            <div className="absolute inset-0 bg-cyan-500 blur-xl opacity-20 rounded-full animate-pulse"></div>
            <Loader className="size-10 text-cyan-500 animate-spin relative z-10" />
          </div>
          <div className="text-center space-y-2">
            <h3 className="text-white text-xl font-bold tracking-tight">Connexion en cours</h3>
            <p className="text-zinc-400 text-sm">Nous préparons votre espace sécurisé...</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthCallbackPage;