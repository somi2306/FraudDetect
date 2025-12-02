import axios from "axios";

// Récupérer le token stocké après login
const getToken = () => {
  return localStorage.getItem("agentToken"); // Stocké dans AgentAuthPage.tsx
};

export const getAgentCheques = async () => {
  const token = getToken();
  if (!token) throw new Error("Agent non authentifié");

  const response = await axios.get("http://localhost:8000/agents/cheques/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return {
    cheques_meme_banque: response.data.cheques_meme_banque,
    cheques_autre_banque: response.data.cheques_autre_banque,
    agentName: response.data.agentName,
    agentBankId:response.data.agentBankId,
    agentEmail:response.data.agentEmail,
    beneficiaireName:response.data.beneficiaireName
  };
};
