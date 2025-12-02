import { Card, CardContent } from "@/components/ui/card";
import { apiClient } from "@/lib/axios";
import { useUser, useAuth } from "@clerk/clerk-react";
import { Loader } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

const AuthCallbackPage = () => {
  const { isLoaded, user } = useUser();
  const { getToken } = useAuth();
  const navigate = useNavigate();
  const syncAttempted = useRef(false);
  
  // Récupération des données d'inscription (pour les bénéficiaires qui viennent de s'inscrire)
  const [userData] = useState(() => {
    const saved = localStorage.getItem('userRegistrationData');
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    const syncUser = async () => {
      // Éviter la double exécution (Strict Mode React)
      if (!isLoaded || !user || syncAttempted.current) return;

      try {
        syncAttempted.current = true;
        const token = await getToken();

        // Préparation des données pour le backend
        // Si userData existe, c'est une inscription Bénéficiaire
        // Sinon, c'est une connexion (Admin, Agent, ou Bénéficiaire existant)
        const payload = userData ? {
          firstName: user.firstName,
          lastName: user.lastName,
          imageUrl: user.imageUrl,
          email: user.primaryEmailAddress?.emailAddress,
          cin: userData.cin,
          rib: userData.rib,
        } : {
          firstName: user.firstName,
          lastName: user.lastName,
          imageUrl: user.imageUrl,
          email: user.primaryEmailAddress?.emailAddress,
          cin: null,
          rib: null,
        };

        console.log("Synchronisation avec le backend...");
        
        // Appel au backend pour créer ou mettre à jour l'utilisateur
        // Le backend doit renvoyer le role, et pour les agents : must_reset_password et bank_id
        const response = await apiClient.post(
          "/auth/callback",
          payload,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        const { role, must_reset_password, bank_id } = response.data;
        console.log("Données reçues:", { role, must_reset_password, bank_id });

        // Nettoyage du localStorage
        if (userData) {
          localStorage.removeItem('userRegistrationData');
        }

        // --- LOGIQUE DE ROUTAGE PRINCIPALE ---

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
                navigate("/agent/reset-password");
            } else {
                console.log(`Agent authentifié -> Redirection vers Dashboard Banque (ID: ${bank_id})`);
                // On redirige vers le dashboard général ou spécifique à la banque
                // Si vous avez une route dynamique : navigate(`/agent/dashboard/${bank_id}`);
                // Sinon :
                navigate("/agent/dashboard");
            }
        } 
        else {
            // CAS BÉNÉFICIAIRE (ou autre rôle par défaut)
            console.log("Utilisateur standard -> Redirection vers Profile");
            navigate("/profile");
        }

      } catch (error) {
        console.error("Erreur critique pendant la synchronisation:", error);
        // En cas d'erreur, on redirige vers une page sûre (profil ou accueil) pour ne pas bloquer
        navigate("/profile"); 
      }
    };

    syncUser();
  }, [isLoaded, user, getToken, navigate, userData]);

  return (
    <div className="h-screen w-full bg-white flex items-center justify-center">
      <Card className="w-[90%] max-w-md bg-zinc-900 border-zinc-800">
        <CardContent className="flex flex-col items-center gap-4 pt-6">
          <Loader className="size-6 text-emerald-500 animate-spin" />
          <h3 className="text-zinc-400 text-xl font-bold">Connexion en cours</h3>
          <p className="text-zinc-400 text-sm">Vérification de vos accès et redirection...</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthCallbackPage;