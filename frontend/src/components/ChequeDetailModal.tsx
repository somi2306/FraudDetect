import React, { useState } from "react";
import { transmettreCheque } from "@/lib/agentservice";


export interface Cheque {
  cheque: {
    id: number;
    imageUrl: string;
    status: string;
    date: string;
  };
  beneficiaire: {
    id: number;
    name: string;
    email: string;
  };
}

interface ChequeDetailModalProps {
  cheque: Cheque | null;
  onClose: () => void;
  isInternal: boolean; // Banque du chèque = banque de l'agent
  onProcess: (chequeId: number) => void; // Traitement interne
  themeHex: string;
  agentId: number; // ID de l'agent connecté
}

const ChequeDetailModal: React.FC<ChequeDetailModalProps> = ({
  cheque,
  onClose,
  isInternal,
  onProcess,
  themeHex,
  agentId
}) => {
  const [loading, setLoading] = useState(false);

  if (!cheque) return null;
  
  const handleMainAction = async () => {
    if (isInternal) {
      // Traitement interne
      onProcess(cheque.cheque.id);
      onClose();
    } else {
      // Transmission à l'agent de la banque cible
      setLoading(true);
      try {
        const data = await transmettreCheque(cheque.cheque.id, agentId);
        alert(data.message); // message du backend
      } catch (error: any) {
        alert(error.message || "Erreur lors de la transmission");
      } finally {
        setLoading(false);
        onClose();
      }
    }
  };

  const MainActionButton = (
    <button
      onClick={handleMainAction}
      disabled={loading}
      className={`px-4 py-2 text-white rounded font-medium transition duration-150 shadow-md ${
        isInternal ? 'hover:bg-emerald-700' : 'hover:bg-blue-700'
      }`}
      style={{
        backgroundColor: isInternal ? themeHex : '#2563EB'
      }}
    >
      {loading ? "⏳ En cours..." :
        isInternal
          ? '✅ Lancer le Traitement Interne'
          : '➡️ Transmettre à la Banque Cible'
      }
    </button>
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm" onClick={onClose}>
      <div 
        className="bg-white rounded-xl shadow-2xl w-11/12 max-w-2xl p-6 transform transition-all duration-300 scale-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Titre et fermeture */}
        <div className="flex justify-between items-start mb-4 border-b pb-2">
          <h2 className="text-2xl font-bold" style={{ color: themeHex }}>
            Détails du Chèque (ID: {cheque.cheque.id})
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-3xl leading-none"
            aria-label="Fermer la modale"
          >
            &times;
          </button>
        </div>

        {/* Infos bénéficiaire */}
        <div className="space-y-3 mb-4">
          <p className="text-lg">
            <span className="font-bold " style={{ color: themeHex }}>Bénéficiaire:</span>{" "}
            <span className="font-semibold " style={{ color: themeHex }}>
              {cheque.beneficiaire.name}
            </span>
          </p>
        </div>

        {/* Image du chèque */}
        <h3 className="text-xl font-semibold mb-2 " style={{ color: themeHex }}>
          Image du Chèque
        </h3>
        {console.log("IMAGE URL =", cheque.cheque.imageUrl)}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
         
          
         <img 
          src={`http://localhost:8000${cheque.cheque.imageUrl}`} 
          alt="Cheque"
          className="w-full h-auto object-cover max-h-96"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = "https://placehold.co/600x300/F44336/FFFFFF?text=Image+Non+Disponible";
          }}
        />
        
        

        </div>

        {/* Boutons */}
        <div className="mt-6 flex justify-end gap-3">
          {MainActionButton}
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-400 text-white rounded-lg hover:bg-gray-500 transition duration-150"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChequeDetailModal;
