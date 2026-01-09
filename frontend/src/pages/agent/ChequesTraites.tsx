// src/pages/ChequesTraites.tsx
import React, { useEffect, useState } from "react";
import { getChequesTraite, getAgentInfo } from "@/lib/agentservice";
import AgentLayout from "@/layouts/AgentLayout";
import ChequeCard from "@/components/ChequeCard"; // ton composant modifié
import { getTheme } from "@/utils/bankTheme";

interface ChequeItem {
  cheque: {
    id: number;
    imageUrl: string;
    status: string;
    date: string;
  };
  beneficiaire: any;
}

interface Agent {
  bankId: string | number;
  [key: string]: any;
}

const ChequesTraites = () => {
  const [agent, setAgent] = useState<Agent | null>(null);
  const [cheques, setCheques] = useState<ChequeItem[]>([]);
  const [selectedCheque, setSelectedCheque] = useState<ChequeItem | null>(null);

  useEffect(() => {
    (async () => {
      const agentInfo = await getAgentInfo();
      setAgent(agentInfo);

      const chequesData = await getChequesTraite(); // récupère les chèques traités
      setCheques(chequesData);
    })();
  }, []);

  if (!agent) return <div>Chargement...</div>;

  const handleViewDetails = (cheque: any) => {
    // Ici tu peux ouvrir la modale pour voir les détails du chèque
    console.log("Voir détails du chèque", cheque);
  };

  

  return (
    <AgentLayout agent={agent}>
      <h1 className="text-2xl font-bold mb-4">Chèques Traités</h1>
      {cheques.length === 0 ? (
        <p>Aucun chèque traité pour le moment.</p>
      ) : (
       

        <div className="flex flex-col gap-4 w-full">
          
          {cheques.map((item) => (
                <ChequeCard
                    key={item.cheque.id}           // ID réel du chèque
                    cheque={item}
                    beneficiaire={item.beneficiaire}
                    onViewDetails={() => setSelectedCheque(item)}
                    themeHex={getTheme(agent.bankId).hex} // couleur
                />
            ))}

        </div>
      )}
        
      
    </AgentLayout>
  );
};

export default ChequesTraites;
