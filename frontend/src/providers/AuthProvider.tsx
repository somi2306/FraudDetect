import { apiClient } from "@/lib/axios";
import { useAuthStore } from "@/stores/useAuthStore";
import { useAuth } from "@clerk/clerk-react";
import { Loader } from "lucide-react";
import { useEffect, useState } from "react";

const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const { getToken, userId, isLoaded, isSignedIn } = useAuth();
    // On utilise la nouvelle fonction syncUserRole
    const { syncUserRole } = useAuthStore();
    const [isReady, setIsReady] = useState(false);

    useEffect(() => {
        if (!isLoaded) return;

        const interceptorId = apiClient.interceptors.request.use(async (config) => {
            const token = await getToken();
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        }, (error) => Promise.reject(error));

        const initAuth = async () => {
            if (isSignedIn && userId) {
                // On synchronise le rôle dès qu'on a un user connecté
                await syncUserRole();
            }
            setIsReady(true);
        };

        initAuth();

        return () => {
            apiClient.interceptors.request.eject(interceptorId);
        };
    }, [isLoaded, isSignedIn, userId, getToken, syncUserRole]);

    if (!isLoaded || !isReady) {
        return (
            <div className='h-screen w-full flex items-center justify-center bg-zinc-900'>
                <Loader className='size-8 text-emerald-500 animate-spin' />
            </div>
        );
    }

    return <>{children}</>;
};

export default AuthProvider;