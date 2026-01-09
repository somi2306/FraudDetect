// src/components/AgentNavbar.tsx

import React, { useEffect, useState, useRef } from "react";

import { FaCheckCircle, FaClipboardList, FaInbox, FaSignOutAlt } from "react-icons/fa";
import { useClerk } from "@clerk/clerk-react"; // <--- Import Clerk
import { useNavigate } from "react-router-dom"; // <--- Pour la redirection
import { getChequesTransmis } from "@/lib/agentservice";

import { useAuth } from "@clerk/clerk-react";


// Définition des types pour les props (Inchangé)
interface AgentNavbarProps {
    agentName: string;
    agentEmail: string;
    agentBankId: number | null;
    themePrimary: string;
    themeSecondary: string;
    getBankLogo: (bankId: number | null) => string;
}

// Composant AgentNavbar
const AgentNavbar: React.FC<AgentNavbarProps> = ({
    agentName,
    agentEmail,
    agentBankId,
    themePrimary,
    themeSecondary,
    getBankLogo,
}) => {
    // --- LOGIQUE DE DÉCONNEXION ---
    const { signOut } = useClerk();
    const navigate = useNavigate();

    const wsRef = useRef<WebSocket | null>(null);
    const [receivedCount, setReceivedCount] = useState(0);

    const handleSignOut = async () => {
        await signOut();
        navigate("/auth");
    };

    const handlDashboard = async () => {
        navigate("/agent/dashboard")
    }
    const handleChequesTraites = async () => {
        navigate("/agent/cheques/traites")
    }
    const handlChequesTransmis = async () => {
        
        navigate("/agent/cheques/transmis");
    };
    


    




    return (
        <nav className={`${themePrimary} text-white p-4 shadow-xl sticky top-0 z-20`}>
            <div className="flex justify-between items-center max-w-7xl mx-auto">

                {/* Logo et Message d'accueil (INCHANGÉ) */}
                <div className="flex items-center gap-3">
                    <img
                        src={getBankLogo(agentBankId)}
                        alt="Logo Banque"
                        className="w-16 h-16 object-contain p-0 bg-transparent"
                    />
                    <div className="flex flex-col justify-center">
                        <h1 className="text-xl font-medium">
                            Bienvenue {agentName}
                        </h1>
                        <p className="text-sm font-light opacity-90 -mt-1">
                            {agentEmail}
                        </p>
                    </div>
                </div>

                {/* Boutons d'action/navigation */}
                <div className="flex items-center gap-4">
                    {/* Bouton 1 (INCHANGÉ) */}
                    <button
                        onClick={handlDashboard}
                        className={`px-4 py-2 ${themeSecondary} rounded-full text-sm font-semibold hover:${themeSecondary.replace('-800', '-700')} transition duration-150 shadow-md flex items-center gap-2`}>
                        <FaClipboardList className="text-base" />
                        Chèques à traiter
                    </button>

                    {/* Bouton 2 (INCHANGÉ) */}
                    <button
                        onClick={handlChequesTransmis}
                        className={`relative px-4 py-2 ${themeSecondary} rounded-full text-sm font-semibold hover:${themeSecondary.replace('-800', '-700')} transition duration-150 shadow-md flex items-center gap-2`}
                    >
                        <FaInbox className="text-base" />
                        Chèques reçues

                    </button>



                    {/* Bouton 3 (INCHANGÉ) */}
                    <button
                        onClick={handleChequesTraites}
                        className={`px-4 py-2 ${themeSecondary} rounded-full text-sm font-semibold hover:${themeSecondary.replace('-800', '-700')} transition duration-150 shadow-md flex items-center gap-2`}>
                        <FaCheckCircle className="text-base" />
                        Chèques traités
                    </button>

                    {/* Bouton Déconnexion (MODIFIÉ : onClick + signOut au lieu de Link to="/agent/login") */}
                    <button
                        onClick={handleSignOut}
                        className={`px-4 py-2 ${themeSecondary} rounded-full text-sm font-semibold hover:${themeSecondary.replace('-800', '-700')} transition duration-150 shadow-md flex items-center gap-2 cursor-pointer`}
                    >
                        <FaSignOutAlt className="text-base" />
                        Déconnexion
                    </button>
                </div>
            </div>
        </nav>
    );
};

export default AgentNavbar;