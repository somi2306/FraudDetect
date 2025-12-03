import { apiClient } from "@/lib/axios"; // <-- On utilise notre client configuré pour Clerk

export interface ChequeData {
    id: number;
    amount: number;
    beneficiaireName: string;
    status: string;
    date: string;
    // ... autres champs
}

export interface AgentDashboardResponse {
    cheques_meme_banque: ChequeData[];
    cheques_autre_banque: ChequeData[];
    agentName: string;
    agentEmail: string;
    agentBankId: number;
    beneficiaireName?: string;
}

export const getAgentCheques = async (): Promise<AgentDashboardResponse> => {
  // PLUS BESOIN de récupérer le token manuellement ici.
  // apiClient (configuré dans AuthProvider.tsx) injecte le token Clerk automatiquement.

  // On appelle la nouvelle route qu'on vient de créer dans agents.py
  // Note: apiClient a déjà baseURL configuré (/api ou http://localhost:8000)
  const response = await apiClient.get("/agents/cheques/me");

  return {
    cheques_meme_banque: response.data.cheques_meme_banque,
    cheques_autre_banque: response.data.cheques_autre_banque,
    agentName: response.data.agentName,
    agentBankId: response.data.agentBankId,
    agentEmail: response.data.agentEmail,
    beneficiaireName: response.data.beneficiaireName
  };
};