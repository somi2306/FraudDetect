import React from 'react';
import type { Cheque } from "./ChequeDetailModal";

interface ChequeCardProps {
    cheque: Cheque;
    beneficiaire: { id: number; name: string; bankName: string };
    onViewDetails: (cheque: Cheque) => void;
    themeHex: string;
}

const ChequeCard: React.FC<ChequeCardProps> = ({
    cheque,
    onViewDetails,
    themeHex
}) => {
    const isProcessed = cheque.cheque.status === "approved" || cheque.cheque.status === "rejected";

    return (
        <div
            key={cheque.cheque.id}
            className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm border border-gray-200 transition duration-150 ease-in-out hover:shadow-md hover:border-emerald-400"
        >
            {/* Infos du chèque */}
            <div className="flex-1 min-w-0 pr-4">
                <p className="text-sm font-semibold text-gray-800 truncate">
                    Chèque ID: <span className="text-gray-600">{cheque.cheque.id}</span>
                </p>
                <p className="text-xs text-gray-500 truncate mt-1">
                    Bénéficiaire: <span className="font-medium text-gray-700">{cheque.beneficiaire.name}</span>
                </p>
                {cheque.cheque.status === "transmitted" && (
                    <p className="text-sm text-gray-500 mt-1">
                        Banque : {cheque.beneficiaire.bankName}
                    </p>
                )}

                {/* Afficher le statut et le score si traité */}
                {isProcessed && (
                    <div className="mt-2">
                        <p className={`text-sm font-semibold ${cheque.cheque.status === "approved" ? "text-emerald-600" : "text-red-600"
                            }`}>
                            Statut: {cheque.cheque.status.toUpperCase()}
                        </p>

                    </div>
                )}
            </div>

            {/* Bouton détails */}
            {/* Bouton détails / envoyer résultat */}
            {isProcessed  ? (
                <button
                    onClick={() => onViewDetails(cheque)}
                    className="flex items-center px-4 py-2 text-white rounded-lg font-medium text-sm hover:bg-emerald-600 transition duration-150 shadow-md whitespace-nowrap"
                    style={{ backgroundColor: themeHex }}
                >
                    📨 Envoyer le résultat au bénéficiaire
                </button>
            ) : (
                <button
                    onClick={() => onViewDetails(cheque)}
                    className="flex items-center px-4 py-2 text-white rounded-lg font-medium text-sm hover:bg-emerald-600 transition duration-150 shadow-md whitespace-nowrap"
                    style={{ backgroundColor: themeHex }}
                >
                    🔍 Voir les détails
                </button>
            )}

        </div>
    );
};

export default ChequeCard;
