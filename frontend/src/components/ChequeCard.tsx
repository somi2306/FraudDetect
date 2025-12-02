import React from 'react';
// Importation de l'interface Cheque depuis le fichier de la Modale
import type {Cheque} from "./ChequeDetailModal"; 


interface ChequeCardProps {
    cheque: Cheque;
    // Les props isOpen et onToggleDetails ne sont plus nécessaires pour ce design
    // isOpen: boolean; 
    // onToggleDetails: (chequeId: number) => void;
    onViewDetails: (cheque: Cheque) => void;
    themeHex:string;
}

// NOTE: Le composant parent (AgentDashboard.tsx) devra cesser de passer 
// les props 'isOpen' et 'onToggleDetails' à ChequeCard.

const ChequeCard: React.FC<ChequeCardProps> = ({ 
    cheque, 
    // Retrait des props inutilisés : isOpen, onToggleDetails
    onViewDetails ,
    themeHex
}) => {
    return (
        // Utilisation d'un div simple, centré verticalement, pour ressembler à la maquette
        <div 
            key={cheque.id} 
            // Style de carte simple et élégant, comme dans la maquette
            className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm border border-gray-200 transition duration-150 ease-in-out hover:shadow-md hover:border-emerald-400"
        >
            
            {/* Conteneur pour les informations du chèque (ID + Bénéficiaire) */}
            <div className="flex-1 min-w-0 pr-4">
                {/* ID du Chèque (texte principal) */}
                <p className="text-sm font-semibold text-gray-800 truncate">
                    Chèque ID: <span className="text-gray-600">{cheque.id}</span>
                </p>
                {/* Bénéficiaire */}
                <p className="text-xs text-gray-500 truncate mt-1">
                    Bénéficiaire: <span className="font-medium text-gray-700">{cheque.beneficiaireName}</span>
                </p>
            </div>

            {/* Bouton pour les détails (Ouvre la Modale) */}
            <button
                onClick={() => onViewDetails(cheque)}
                className="flex items-center px-4 py-2  text-white rounded-lg font-medium text-sm hover:bg-emerald-600 transition duration-150 shadow-md whitespace-nowrap"
                style={{
                backgroundColor:themeHex
            }}>
                <span className="mr-1">🔍</span> Voir les détails
            </button>
        </div>
    );
};

export default ChequeCard;