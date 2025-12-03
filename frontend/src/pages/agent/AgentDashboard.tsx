import React, { useEffect, useState } from "react";
import { getAgentCheques } from "@/lib/agentservice"; 
import ChequeCard from "../../components/ChequeCard"; 
import ChequeDetailModal from "../../components/ChequeDetailModal"; 
// Assurez-vous que le type Cheque est bien exporté ou re-déclarez-le ici si besoin
import type { Cheque } from "../../components/ChequeDetailModal"; 
import AgentNavbar from "../../components/AgentNavbar";
import { useAuthStore } from "@/stores/useAuthStore"; // Pour récupérer l'ID banque si besoin localement

// --- Configuration des Thèmes et Logos ---
const BANK_LOGOS: { [key: number]: string } = {
    17: "/logos/Cih.png",
    18: "/logos/tijari.png",
    19: "/logos/bcp.png",
    0:  "/logos/default.png",
};

const BANK_THEMES: { [key: number]: { primary: string, secondary: string, text: string, hex: string } } = {
    17: { primary: "bg-cyan-600", secondary: "bg-cyan-800", text: "text-cyan-700", hex: "#06B6D4" }, // CIH
    18: { primary: "bg-yellow-600", secondary: "bg-yellow-800", text: "text-yellow-700", hex: "#ca8a04" }, // Attijari
    19: { primary: "bg-orange-500", secondary: "bg-orange-700", text: "text-orange-700", hex: "#f97316" }, // BCP
    0:  { primary: "bg-emerald-600", secondary: "bg-emerald-800", text: "text-emerald-700", hex: "#059669" } // Default
};

const getThemeClasses = (bankId: number | null) => BANK_THEMES[bankId || 0] || BANK_THEMES[0];
const getBankLogo = (bankId: number | null) => BANK_LOGOS[bankId || 0] || BANK_LOGOS[0];

const AgentDashboard = () => {
    // États
    const [chequesMemeBanque, setChequesMemeBanque] = useState<Cheque[]>([]);
    const [chequesAutreBanque, setChequesAutreBanque] = useState<Cheque[]>([]);
    const [agentName, setAgentName] = useState<string>("Chargement...");
    const [agentEmail, setAgentEmail] = useState<string>("");
    const [agentBankId, setAgentBankId] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);

    // États UI
    const [openMemeBanque, setOpenMemeBanque] = useState(true); 
    const [openAutreBanque, setOpenAutreBanque] = useState(false); 
    const [selectedCheque, setSelectedCheque] = useState<Cheque | null>(null);

    // Thème actuel
    const theme = getThemeClasses(agentBankId);

    // Chargement des données
    useEffect(() => {
        const fetchCheques = async () => {
            setLoading(true);
            try {
                // Appel au service qui utilise maintenant apiClient (Clerk)
                const data = await getAgentCheques(); 
                
                // Adaptation des données si nécessaire selon votre backend réel
                setChequesMemeBanque(data.cheques_meme_banque as any);
                setChequesAutreBanque(data.cheques_autre_banque as any);
                setAgentName(data.agentName);
                setAgentEmail(data.agentEmail);
                setAgentBankId(data.agentBankId);
            } catch (err) {
                console.error("Erreur dashboard:", err);
                setAgentName("Erreur chargement");
            } finally {
                setLoading(false);
            }
        };

        fetchCheques();
    }, []);

    const handleProcessCheque = (chequeId: number) => {
        console.log(`Traitement ID: ${chequeId}`);
        // Ici appel API apiClient.post(...)
        setChequesMemeBanque(prev => prev.filter(ch => ch.id !== chequeId));
    };

    const handleTransmitCheque = (chequeId: number) => {
        console.log(`Transmission ID: ${chequeId}`);
        // Ici appel API apiClient.post(...)
        setChequesAutreBanque(prev => prev.filter(ch => ch.id !== chequeId));
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4"></div>
                    <p className="text-gray-600">Chargement de votre espace...</p>
                </div>
            </div>
        );
    }

    // Rendu Liste
    const renderChequeList = (cheques: Cheque[]) => (
        <div className="p-4 space-y-3 bg-gray-50/50 min-h-[100px]">
            {cheques.length === 0 ? (
                <p className="text-gray-400 italic text-center py-4">Aucun chèque dans cette section.</p>
            ) : (
                cheques.map((ch) => (
                    <ChequeCard
                        key={ch.id}
                        cheque={ch}
                        onViewDetails={setSelectedCheque}
                        themeHex={theme.hex}
                    />
                ))
            )}
        </div>
    );

    return (
        <div className="min-h-screen transition-colors duration-500" 
            style={{ 
                background: `linear-gradient(to bottom, #ffffff 0%, #f3f4f6 100%)` 
            }}>
            
            <AgentNavbar
                agentName={agentName}
                agentEmail={agentEmail}
                agentBankId={agentBankId}
                themePrimary={theme.primary}
                themeSecondary={theme.secondary}
                getBankLogo={getBankLogo}
            />

            <div className="p-6 max-w-7xl mx-auto space-y-8">
                
                {/* --- STATS --- */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className={`bg-white p-6 rounded-2xl shadow-sm border-l-8`} style={{ borderColor: theme.hex }}>
                        <p className="text-gray-500 font-medium uppercase tracking-wide text-xs">Traitement Interne</p>
                        <div className="flex justify-between items-end">
                            <p className="text-4xl font-bold text-gray-800">{chequesMemeBanque.length}</p>
                            <span className={`text-xs px-2 py-1 rounded-full bg-opacity-10 ${theme.text} bg-current`}>
                                À valider
                            </span>
                        </div>
                    </div>
                    <div className={`bg-white p-6 rounded-2xl shadow-sm border-l-8 border-gray-300`}>
                        <p className="text-gray-500 font-medium uppercase tracking-wide text-xs">Compensation (Autres banques)</p>
                        <div className="flex justify-between items-end">
                            <p className="text-4xl font-bold text-gray-800">{chequesAutreBanque.length}</p>
                            <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">
                                En attente
                            </span>
                        </div>
                    </div>
                </div>
                
                {/* --- LISTES DÉPLIANTES --- */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    
                    {/* Colonne 1 : Interne */}
                    <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
                        <button
                            className={`w-full p-4 flex justify-between items-center text-white font-semibold transition-colors ${theme.primary}`}
                            onClick={() => setOpenMemeBanque(!openMemeBanque)}
                        >
                            <span>🏦 Chèques {agentBankId === 17 ? 'CIH' : agentBankId === 18 ? 'Attijari' : 'Banque'}</span>
                            <span className={`transform transition-transform ${openMemeBanque ? 'rotate-180' : ''}`}>▼</span>
                        </button>
                        {openMemeBanque && renderChequeList(chequesMemeBanque)}
                    </div>

                    {/* Colonne 2 : Externe */}
                    <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
                        <button
                            className={`w-full p-4 flex justify-between items-center text-white font-semibold transition-colors bg-gray-700 hover:bg-gray-800`}
                            onClick={() => setOpenAutreBanque(!openAutreBanque)}
                        >
                            <span>🌍 Chèques Confrères</span>
                            <span className={`transform transition-transform ${openAutreBanque ? 'rotate-180' : ''}`}>▼</span>
                        </button>
                        {openAutreBanque && renderChequeList(chequesAutreBanque)}
                    </div>
                </div>
            </div>

            {/* MODALE */}
            {selectedCheque && (
                <ChequeDetailModal
                    cheque={selectedCheque}
                    onClose={() => setSelectedCheque(null)}
                    isInternal={chequesMemeBanque.some(ch => ch.id === selectedCheque.id)}
                    onProcess={handleProcessCheque}
                    onTransmit={handleTransmitCheque}
                    themeHex={theme.hex}
                />
            )}
        </div>
    );
};

export default AgentDashboard;