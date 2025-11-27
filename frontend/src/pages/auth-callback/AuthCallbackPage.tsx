// AuthCallbackPage.tsx
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
  const [userData, setUserData] = useState(() => {
    // Récupérer les données depuis le localStorage
    const saved = localStorage.getItem('userRegistrationData');
    // 'role' n'est plus dans les données sauvegardées
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    const syncUser = async () => {
      if (!isLoaded || !user || syncAttempted.current) return;

      try {
        syncAttempted.current = true;
        const token = await getToken();

        // Si on a des données supplémentaires (nouvel utilisateur)
        const payload = userData ? {
          firstName: user.firstName,
          lastName: user.lastName,
          imageUrl: user.imageUrl,
          email: user.primaryEmailAddress?.emailAddress,
          cin: userData.cin,
          rib: userData.rib,
          // 'role' est supprimé du payload
        } : {
          // Utilisateur existant qui se reconnecte
          firstName: user.firstName,
          lastName: user.lastName,
          imageUrl: user.imageUrl,
          email: user.primaryEmailAddress?.emailAddress,
          cin: null, // Envoyé comme null pour la logique backend
          rib: null, // Envoyé comme null pour la logique backend
          // 'role' est supprimé du payload
        };

        await apiClient.post(
          "/auth/callback",
          payload,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        // Nettoyer le localStorage après utilisation
        if (userData) {
          localStorage.removeItem('userRegistrationData');
        }
      } catch (error) {
        console.error("Erreur pendant la synchronisation /auth/callback", error);
      } finally {
        navigate("/");
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
          <p className="text-zinc-400 text-sm">Synchronisation...</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthCallbackPage;