// src/components/AgentDashboard.tsx

import React, { useEffect, useState } from "react";
import { getAgentCheques } from "@/lib/agentservice"; // Assurez-vous que ce service existe
import ChequeCard from "../../components/ChequeCard"; 
import ChequeDetailModal from "../../components/ChequeDetailModal"; 
import type {Cheque} from "../../components/ChequeDetailModal"; 
import AgentNavbar from "../../components/AgentNavbar";


// --- 🎨 Logique de Thème (Ajout pour la personnalisation si nécessaire) ---
// Mappage des IDs de banque aux couleurs Tailwind CSS (exemple)
const BANK_THEMES: { [key: number]: { primary: string, secondary: string, text: string } } = {
    // 0: Thème par défaut (votre thème "emerald")
    0: { primary: 'bg-emerald-600', secondary: 'bg-emerald-800', text: 'text-emerald-600' },
    // 1: Exemple de banque A
    1: { primary: 'bg-red-700', secondary: 'bg-red-900', text: 'text-red-700' },
    // 2: Exemple de banque B
    2: { primary: 'bg-indigo-600', secondary: 'bg-indigo-800', text: 'text-indigo-600' },
};

const getThemeClasses = (bankId: number | null) => {
    return BANK_THEMES[bankId || 0] || BANK_THEMES[0];
};


const AgentDashboard = () => {
    // États de données
    const [chequesMemeBanque, setChequesMemeBanque] = useState<Cheque[]>([]);
    const [chequesAutreBanque, setChequesAutreBanque] = useState<Cheque[]>([]);
    const [agentName, setAgentName] = useState<string>("Chargement...");
    const [agentEmail, setAgentEmail] = useState<string>("Chargement...");
    const [agentBankId, setAgentBankId] = useState<number | null>(null); // Ajout de l'ID de la banque
    
    const [loading, setLoading] = useState(true);

    // États d'interaction
    const [openMemeBanque, setOpenMemeBanque] = useState(true); 
    const [openAutreBanque, setOpenAutreBanque] = useState(false); 
    const [openCheques, setOpenCheques] = useState<number[]>([]); 
    const [selectedCheque, setSelectedCheque] = useState<Cheque | null>(null); // Chèque pour la modale

    // --- Fonctions d'Action (Définition des Callbacks) ---

    // Fonction pour gérer le Traitement Interne (Même banque)
    const handleProcessCheque = (chequeId: number) => {
        console.log(`Traitement INTERNE du chèque ID: ${chequeId} initié.`);
        // [TODO: APPEL API ICI] : Marquer le chèque comme traité/en cours.
        // Mise à jour de l'état local (retirer le chèque de la liste)
        setChequesMemeBanque(prev => prev.filter(ch => ch.id !== chequeId));
    };
    // --- 🏦 Logos par banque ---
    const BANK_LOGOS: { [key: number]: string } = {
    17: "/logos/Cih.png",        // CIH
    18: "/logos/tijari.png",     // Attijariwafa
    19: "/logos/bcp.png",        // Banque Populaire
    0:  "/logos/default.png",    // logo par défaut
};
// Thèmes selon ID de banque
const BANK_THEMES: { [key: number]: { primary: string, secondary: string, text: string,hex: string } } = {
    17: { // CIH
        primary: "bg-cyan-600",
        secondary: "bg-cyan-800",
        text: "text-cyan-700",
        hex: "#06B6D4"
    },
    18: { // Attijariwafa
        primary: "bg-yellow-600",
        secondary: "bg-yellow-800",
        text: "text-yellow-700",
        hex: "#6b3e0b"
    },
    19: { // Banque Populaire
        primary: "bg-orange-300",
        secondary: "bg-orange-400",
        text: "text-orange-700",
        hex: "#d27722ff"
    },
    0: { // default
        primary: "bg-emerald-600",
        secondary: "bg-emerald-800",
        text: "text-emerald-700",
        hex: "#059669"
    }
};

const getThemeClasses = (bankId: number | null) => {
    return BANK_THEMES[bankId || 0] || BANK_THEMES[0];
};


    const getBankLogo = (bankId: number | null) => {
    return BANK_LOGOS[bankId || 0] || BANK_LOGOS[0];
};
    // --- Application du Thème ---
    const theme = getThemeClasses(agentBankId);
    // Fonction pour gérer la Transmission Interbancaire (Autre banque)
    const handleTransmitCheque = (chequeId: number) => {
        console.log(`Transmission du chèque ID: ${chequeId} à la banque cible initiée.`);
        // [TODO: APPEL API ICI] : Marquer le chèque comme transmis.
        // Mise à jour de l'état local (retirer le chèque de la liste)
        setChequesAutreBanque(prev => prev.filter(ch => ch.id !== chequeId));
    };

    // --- Cycle de Vie et Récupération des Données ---

    useEffect(() => {
        const fetchCheques = async () => {
            setLoading(true);
            try {
                // Assurez-vous que getAgentCheques retourne également agentBankId
                const data = await getAgentCheques(); 
                setChequesMemeBanque(data.cheques_meme_banque);
                setChequesAutreBanque(data.cheques_autre_banque);
                setAgentName(data.agentName);
                setAgentEmail(data.agentEmail);
                setAgentBankId(data.agentBankId); // Assurez-vous que l'API renvoie ce champ
            } catch (err) {
                console.error("Erreur lors de la récupération des chèques:", err);
                setAgentName("Agent Inconnu");
            } finally {
                setLoading(false);
            }
        };

        fetchCheques();
    }, []);

    

    // Ouvre la modale des détails du chèque
    const handleChequeClick = (cheque: Cheque) => {
        setSelectedCheque(cheque);
    };

    if (loading)
        return (
            <div className="min-h-screen" 
            >
                <div className="text-center">
                    <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-600 mx-auto mb-3"></div>
                    <p className="text-gray-700 text-lg">Chargement des chèques en cours...</p>
                </div>
            </div>
        );

    // Fonction de rendu pour une liste de chèques, utilisant ChequeCard
    const renderChequeList = (cheques: Cheque[]) => (
        <div className="p-4 space-y-3">
            {cheques.length === 0 ? (
                <p className="text-gray-500 italic p-2 text-center">Aucun chèque disponible pour le moment.</p>
            ) : (
                cheques.map((ch) => (
                    <ChequeCard
                        key={ch.id}
                        cheque={ch}
                        onViewDetails={handleChequeClick}
                        themeHex={theme.hex}
                    />
                ))
            )}
        </div>
    );

    

    return (
        <div className="min-h-screen" 
            style={{ 
                // Utilise le dégradé CSS standard pour plus de flexibilité
                backgroundImage: `linear-gradient(to bottom, white 0%, #f3f4f6 70%, ${theme.hex}50 100%)` 
            }}>
            
            {/* 🌟 NOUVEAU: Utilisation du composant AgentNavbar 🌟 */}
            <AgentNavbar
                agentName={agentName}
                agentEmail={agentEmail}
                agentBankId={agentBankId}
                themePrimary={theme.primary}
                themeSecondary={theme.secondary}
                getBankLogo={getBankLogo}
            />

            <div className="p-6 max-w-7xl mx-auto">
                
                {/* Cartes récapitulatives */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    {/* Carte Même Banque (utilise les couleurs du thème) */}
                    <div 
                        className="bg-white p-5 rounded-xl shadow-lg border-l-4" 
                        style={{ borderColor: theme.hex }} 
                    >
                        <p className="text-gray-500 font-medium">Chèques de votre banque (À traiter)</p>
                        <p className="text-3xl font-extrabold" style={{ color: theme.text.replace('text-', '') }}>
                            {chequesMemeBanque.length}
                        </p>
                    </div>
                    {/* Carte Autre Banque (garde le bleu pour la distinction interbancaire) */}
                    <div className="bg-white p-5 rounded-xl shadow-lg border-l-4 "  style={{ borderColor: theme.hex }} >
                        <p className="text-gray-500 font-medium">Chèques d'autres banques (À Transmettre)</p>
                        <p className="text-3xl font-extrabold " style={{ color: theme.text.replace('text-', '') }}>
                            {chequesAutreBanque.length}
                        </p>
                    </div>
                </div>
                
                {/* Conteneurs des listes */}
                <div className="flex flex-col lg:flex-row gap-6">
                    
                    {/* Liste Chèques Même Banque (utilise theme.primary) */}
                    <div className="flex-1 bg-white rounded-xl shadow-2xl overflow-hidden">
                        <button
                            className={`w-full text-left p-5 font-extrabold text-xl text-white transition duration-150 flex justify-between items-center ${openMemeBanque ? theme.primary : theme.primary.replace('-600', '-500')}`}
                            onClick={() => setOpenMemeBanque(!openMemeBanque)}
                            aria-expanded={openMemeBanque}
                        >
                            🏦 Chèques de votre banque ({chequesMemeBanque.length})
                            <span className="text-2xl transform transition-transform duration-300">
                                {openMemeBanque ? "▲" : "▼"}
                            </span>
                        </button>
                        {openMemeBanque && renderChequeList(chequesMemeBanque)}
                    </div>

                    {}
                    <div className="flex-1 bg-white rounded-xl shadow-2xl overflow-hidden">
                        <button
                            className={`w-full text-left p-5 font-extrabold text-xl text-white transition duration-150 flex justify-between items-center ${openMemeBanque ? theme.secondary : theme.secondary.replace('-600', '-500')}`}
                            onClick={() => setOpenAutreBanque(!openAutreBanque)}
                            aria-expanded={openAutreBanque}
                        >
                            🌍 Chèques d'autres banques ({chequesAutreBanque.length})
                            <span className="text-2xl transform transition-transform duration-300">
                                {openAutreBanque ? "▲" : "▼"}
                            </span>
                        </button>
                        {openAutreBanque && renderChequeList(chequesAutreBanque)}
                    </div>
                </div>
            </div>

            {/* Modale affichée en haut de l'arbre DOM */}
            <ChequeDetailModal
                cheque={selectedCheque}
                onClose={() => setSelectedCheque(null)}
                
                // Détermine si le chèque est interne à la banque de l'agent.
                isInternal={chequesMemeBanque.some(ch => ch.id === selectedCheque?.id)}
                
                // Passage des fonctions d'action
                onProcess={handleProcessCheque}
                onTransmit={handleTransmitCheque}
                themeHex={theme.hex}
            />
        </div>
    );
};

export default AgentDashboard;