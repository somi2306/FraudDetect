import { create } from "zustand";
import { apiClient } from "@/lib/axios";
import { getBankIdFromRib } from "@/config/bankThemes";

interface AuthStore {
    role: string | null;  // Remplace 'isAdmin' par un rôle plus générique
    bankId: number | null; // Utile pour l'agent et le bénéficiaire
    rib: string | null; // RIB du bénéficiaire
    isLoading: boolean;
    error: string | null;
    syncUserRole: () => Promise<void>; // Fonction pour récupérer le rôle
    reset: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
    role: null,
    bankId: null,
    rib: null,
    isLoading: true,
    error: null,

    syncUserRole: async () => { 
        set({ isLoading: true, error: null });
        try {
            // On appelle la route /users/me qu'on vient de modifier
            const response = await apiClient.get("/users/me");
            
            console.log("📡 API /users/me response:", response.data);
            
            // Pour les bénéficiaires, le RIB est la source de vérité pour déterminer la banque
            // On calcule toujours le bankId depuis le RIB s'il existe
            const rib = response.data.rib;
            let bankId = response.data.bank_id;
            
            // Si le RIB existe, on l'utilise pour déterminer le bankId (priorité au RIB)
            if (rib) {
                const ribBankId = getBankIdFromRib(rib);
                if (ribBankId) {
                    console.log(`🏦 BankId calculé depuis RIB (${rib.substring(0,3)}): ${ribBankId} (DB avait: ${bankId})`);
                    bankId = ribBankId;
                }
            }
            
            set({ 
                role: response.data.role,
                bankId: bankId,
                rib: rib
            });
            console.log("✅ Store mis à jour - Rôle:", response.data.role, "BankId:", bankId, "RIB:", rib);
        } catch (error: any) {
            console.error("Erreur sync rôle", error);
            set({ role: null, bankId: null, rib: null, error: "Impossible de récupérer le profil" });
        } finally {
            set({ isLoading: false });
        }
    },

    reset: () => {
        set({ role: null, bankId: null, rib: null, isLoading: false, error: null });
    },
}));