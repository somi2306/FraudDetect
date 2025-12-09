import { apiClient } from "@/lib/axios"; // <-- On utilise notre client configuré pour Clerk

export interface BeneficiaireData {
  id: number;
  name: string;
  email: string;
}

export interface ChequeItem {
  cheque: {
    id: number;
    amount: number;
    status: string;
    date: string;
  };
  beneficiaire: BeneficiaireData;
}

export interface AgentDashboardResponse {
    cheques_meme_banque: ChequeItem[];
    cheques_autre_banque: ChequeItem[];
    agentName: string;
    agentEmail: string;
    agentBankId: number;
}


export const getAgentCheques = async (): Promise<AgentDashboardResponse> => {
  const response = await apiClient.get("/agents/cheques/me");

  return {
    cheques_meme_banque: response.data.cheques_meme_banque,
    cheques_autre_banque: response.data.cheques_autre_banque,
    agentName: response.data.agentName,
    agentBankId: response.data.agentBankId,
    agentEmail: response.data.agentEmail
  };
};

export const transmettreCheque = async (chequeId: number, agentId: number) => {
    const response = await apiClient.post(
        `/agents/cheque/transmettre/${chequeId}`,
        { agent_id: agentId } // <-- ici dans le body
    );
    return response.data;
};


export const getChequesTransmis = async () => {
  const response = await apiClient.get(`/agents/cheques/transmis`);
  return response.data;
};

export async function getAgentInfo() {
    const res = await apiClient.get("/agents/me");
    
    return res.data;
}

export async function getChequesTraite() {
    const res = await apiClient.get("/agents/cheques/traites");
    
    return res.data;
}




