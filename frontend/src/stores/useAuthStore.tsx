import { create } from "zustand";
import { apiClient } from "@/lib/axios";

interface AuthStore {
    role: string | null;  // Remplace 'isAdmin' par un rôle plus générique
    bankId: number | null; // Utile pour l'agent
    isLoading: boolean;
    error: string | null;
    syncUserRole: () => Promise<void>; // Fonction pour récupérer le rôle
    reset: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
    role: null,
    bankId: null,
    isLoading: true,
    error: null,

    syncUserRole: async () => { 
        set({ isLoading: true, error: null });
        try {
            // On appelle la route /users/me qu'on vient de modifier
            const response = await apiClient.get("/users/me");
            set({ 
                role: response.data.role,
                bankId: response.data.bank_id
            });
            console.log("Rôle synchronisé :", response.data.role);
        } catch (error: any) {
            console.error("Erreur sync rôle", error);
            set({ role: null, bankId: null, error: "Impossible de récupérer le profil" });
        } finally {
            set({ isLoading: false });
        }
    },

    reset: () => {
        set({ role: null, bankId: null, isLoading: false, error: null });
    },
}));