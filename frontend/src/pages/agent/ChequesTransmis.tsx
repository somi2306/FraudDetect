// src/pages/ChequesTransmis.tsx
import React, { useEffect, useState } from "react";
import { getChequesTransmis, getAgentInfo } from "@/lib/agentservice";
import AgentLayout from "@/layouts/AgentLayout";
import ChequeCard from "@/components/ChequeCard";
import ChequeDetailModal from "@/components/ChequeDetailModal";
import {getTheme} from "@/utils/bankTheme"

interface Agent {
    bankId: string;
    [key: string]: any;
}

const ChequesTransmisPage = () => {
    const [agent, setAgent] = useState<Agent | null>(null);
    const [cheques, setCheques] = useState<any[]>([]);
    const [selectedCheque, setSelectedCheque] = useState(null);

    useEffect(() => {
        (async () => {
            const agentInfo = await getAgentInfo();
            setAgent(agentInfo);

            const ch = await getChequesTransmis();
            setCheques(ch);
        })();
    }, []);

    if (!agent) return <p>Chargement...</p>;

    return (
        <AgentLayout agent={agent}>
            <div className="bg-white p-5 rounded-xl shadow-lg border-l-4 mb-6">
                <p className="text-gray-500 font-medium">Total Chèques Transmis</p>
                <p className="text-3xl font-extrabold">{cheques.length}</p>
            </div>

            {cheques.map((item) => (
                <ChequeCard
                    key={item.cheque.id}           // ID réel du chèque
                    cheque={item}           // seulement l'objet cheque
                    beneficiaire={item.beneficiaire} // le bénéficiaire
                    onViewDetails={() => setSelectedCheque(item)}
                    themeHex={getTheme(agent.bankId).hex} // couleur
                />
            ))}



            <ChequeDetailModal
                cheque={selectedCheque}
                onClose={() => setSelectedCheque(null)}
                isInternal={true}
                themeHex={getTheme(agent.bankId).hex}
                onProcess={() => {}}
                agentId={Number(agent.bankId)}
            />
        </AgentLayout>
    );
};

export default ChequesTransmisPage;
