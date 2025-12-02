import React from "react";

// Interface Cheque centralisée (inchangée)
export interface Cheque {
    id: number;
    beneficiaireName: string; 
    imageUrl: string; 
}

interface ChequeDetailModalProps {
    cheque: Cheque | null;
    onClose: () => void;
    // Indique si le chèque est interne (Banque Cible == Banque Agent)
    isInternal: boolean; 
    // Callback pour l'action Traiter (même banque)
    onProcess: (chequeId: number) => void; 
    // Callback pour l'action Transmettre (autre banque)
    onTransmit: (chequeId: number) => void; 
    themeHex: string
}

const ChequeDetailModal: React.FC<ChequeDetailModalProps> = ({
    cheque,
    onClose,
    isInternal,
    onProcess,
    onTransmit,
    themeHex,
}) => {
    if (!cheque) return null;

    
    const handleMainAction = () => {
        if (isInternal) {
            onProcess(cheque.id);
        } else {
            onTransmit(cheque.id);
        }
        onClose(); // Fermer la modale après l'exécution de l'action
    };

    // Définition du bouton principal basée sur le statut
    const MainActionButton = (
        <button
            onClick={handleMainAction}
            // Utilisation de couleurs distinctes
            className={`px-4 py-2 text-white rounded font-medium transition duration-150 shadow-md ${
                // Nous laissons les classes Tailwind pour le hover et la taille
                isInternal ? 'hover:bg-emerald-700' : 'hover:bg-blue-700'
            }`}
            
            // 🌟 Utilisation du style en ligne conditionnel 🌟
            style={{
                backgroundColor: isInternal ? themeHex : '#2563EB', // #2563EB est le code pour bg-blue-600
            }}
        >
            {isInternal 
                ? '✅ Lancer le Traitement Interne' 
                : '➡️ Transmettre à la Banque Cible'
            }
        </button>
    );
    // --- FIN NOUVEAU ---

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm" onClick={onClose}>
            {/* Contenu de la modale */}
            <div 
                className="bg-white rounded-xl shadow-2xl w-11/12 max-w-2xl p-6 transform transition-all duration-300 scale-100"
                onClick={(e) => e.stopPropagation()} 
            >
                {/* ... (Titre, bouton de fermeture, et détails du bénéficiaire inchangés) ... */}
                <div className="flex justify-between items-start mb-4 border-b pb-2">
                    <h2 className="text-2xl font-bold text-emerald-600">
                        Détails du Chèque (ID: {cheque.id})
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700 text-3xl leading-none"
                        aria-label="Fermer la modale"
                    >
                        &times;
                    </button>
                </div>

                <div className="space-y-3 mb-4">
                    <p className="text-lg">
                        <span className="font-bold text-gray-700">Bénéficiaire:</span>{" "}
                        <span className="font-semibold text-emerald-700">
                            {cheque.beneficiaireName}
                        </span>
                    </p>
                </div>

                <h3 className="text-xl font-semibold mb-2 text-emerald-600">
                    Image du Chèque
                </h3>
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                    <img
                        src={cheque.imageUrl}
                        alt={`Image du chèque ${cheque.id}`} 
                        className="w-full h-auto object-cover max-h-96"
                        onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.src = "https://via.placeholder.com/600x300/F44336/FFFFFF?text=Image+Non+Disponible";
                        }}
                    />
                </div>

                {/* --- NOUVEAU: Section des Boutons d'Action --- */}
                <div className="mt-6 flex justify-end gap-3">
                    
                    {/* Bouton d'Action Spécifique (Traité ou Transmis) */}
                    {MainActionButton} 
                    
                    {/* Bouton Fermer (Reste comme bouton secondaire) */}
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-gray-400 text-white rounded-lg hover:bg-gray-500 transition duration-150"
                    >
                        Fermer
                    </button>
                </div>
                {/* --- FIN NOUVEAU --- */}
            </div>
        </div>
    );
};

export default ChequeDetailModal;