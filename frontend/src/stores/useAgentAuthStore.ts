// src/stores/useAgentAuthStore.ts (Exemple avec Zustand)

import { create } from 'zustand';

interface AgentAuthStore {
  accessToken: string | null;
  user: { id: number; email: string; role: string } | null;
  isLoggedIn: boolean;
  
  // Fonction appelée après une connexion réussie
  login: (token: string, userId: number, email: string, role: string) => void;
  logout: () => void;
  initializeAuth: () => void; // Pour charger l'état au démarrage
}

const TOKEN_STORAGE_KEY = 'agent_access_token';
const USER_STORAGE_KEY = 'agent_user_data';

export const useAgentAuthStore = create<AgentAuthStore>((set) => ({
  accessToken: null,
  user: null,
  isLoggedIn: false,

  initializeAuth: () => {
    // Charger l'état depuis localStorage
    const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    const storedUser = localStorage.getItem(USER_STORAGE_KEY);

    if (storedToken && storedUser) {
        try {
            const userData = JSON.parse(storedUser);
            set({ 
                accessToken: storedToken,
                user: userData,
                isLoggedIn: true 
            });
        } catch (e) {
            console.error("Erreur de parsing des données Agent:", e);
            // Nettoyage en cas de corruption
            localStorage.removeItem(TOKEN_STORAGE_KEY);
            localStorage.removeItem(USER_STORAGE_KEY);
        }
    }
  },

  login: (token, userId, email, role) => {
    const userData = { id: userId, email, role };
    
    set({
      accessToken: token,
      user: userData,
      isLoggedIn: true,
    });

    localStorage.setItem(TOKEN_STORAGE_KEY, token);
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));
  },

  logout: () => {
    set({
      accessToken: null,
      user: null,
      isLoggedIn: false,
    });
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
  },
}));