// Fichier : FraudDetect-feature-auth/frontend/src/lib/axios.ts
import axios from "axios";

export const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
    withCredentials: true // <== CECI EST ESSENTIEL
});