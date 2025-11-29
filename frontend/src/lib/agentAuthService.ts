
import axios from 'axios';

// L'URL de base pour toutes les requêtes Agent
const API_BASE_URL = 'http://127.0.0.1:8000/agents'; 

// --- 1. Connexion Agent ---
// La fonction qui gère l'appel à POST /agents/login
export const loginAgent = async (email: string, password: string) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/login`, { email, password });
        // En cas de succès 200 OK, même si reset_required
        return response.data; 
        
    } catch (error) {
        // Gestion des erreurs Axios (401, 500, etc.)
        if (axios.isAxiosError(error) && error.response) {
            // Lancer une exception avec le détail de l'erreur du backend
            throw new Error(error.response.data.detail || "Échec de l'authentification. Vérifiez vos identifiants.");
        }
        throw new Error("Erreur de connexion au serveur.");
    }
};

// --- 2. Réinitialisation de Mot de Passe Agent ---
// La fonction qui gère l'appel à POST /agents/reset-password
export const resetAgentPassword = async (email: string, old_password: string, new_password: string) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/reset-password`, { 
            email, 
            old_password, 
            new_password 
        });
        return response.data; // Renvoie { status: 'success', message: '...' }
        
    } catch (error) {
         if (axios.isAxiosError(error) && error.response) {
            throw new Error(error.response.data.detail || "Échec de la réinitialisation du mot de passe.");
        }
        throw new Error("Erreur de connexion au serveur.");
    }
};