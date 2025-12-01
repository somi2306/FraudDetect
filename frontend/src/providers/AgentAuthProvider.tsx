// src/providers/AgentAuthProvider.tsx
import { apiClient } from "@/lib/axios"; // Votre instance Axios
import { useAgentAuthStore } from "@/stores/useAgentAuthStore";
import { useEffect, useState } from "react";
import { Loader } from "lucide-react"; // Si vous voulez un loader

const AgentAuthProvider = ({ children }: { children: React.ReactNode }) => {
    const { initializeAuth, accessToken } = useAgentAuthStore();
    const [isLoaded, setIsLoaded] = useState(false);

    // 1. Initialisation : Charger l'état depuis localStorage
    useEffect(() => {
        initializeAuth();
        setIsLoaded(true); // L'état initial est chargé
    }, [initializeAuth]);

    // 2. Intercepteur : Injecter le JWT de l'Agent dans les requêtes
    useEffect(() => {
        // L'intercepteur ne doit s'appliquer que si nous avons un jeton Agent
        if (!isLoaded) return; 

        // Nous utilisons le jeton directement du store (pas de Clerk.getToken)
        const interceptor = apiClient.interceptors.request.use(async (config) => {
            if (accessToken && config.url && config.url.startsWith('/agents')) {
                // N'injecter le jeton que pour les routes Agent pour éviter les conflits
                config.headers.Authorization = `Bearer ${accessToken}`;
            }
            return config;
        });

        return () => {
            apiClient.interceptors.request.eject(interceptor);
        };
    }, [isLoaded, accessToken]); // Déclencher quand l'état est chargé ou que le jeton change

    if (!isLoaded) {
         return (
             <div className='h-screen w-full flex items-center justify-center'>
                 <Loader className='size-8 text-emerald-500 animate-spin' />
             </div>
         );
    }

    return <>{children}</>;
};

export default AgentAuthProvider;