import React, { useState, useEffect } from "react";
import { transmettreCheque } from "@/lib/agentservice";
import { apiClient } from "@/lib/axios";
import { 
  Loader2, ScanEye, CheckCircle, AlertTriangle, ImageIcon,
  Banknote, Calendar, MapPin, User, Hash, AlignLeft, FileText, CreditCard, Edit2, AlertCircle
} from "lucide-react";

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
  isInternal: boolean; 
  onProcess: (chequeId: number, data?: any) => void;
  themeHex: string;
  agentId: number; 
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
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [editedData, setEditedData] = useState<any>(null);
  const [errors, setErrors] = useState<string[]>([]);

  useEffect(() => {
    if (cheque) {
        setAnalysisData(null);
        setEditedData(null);
        setErrors([]);
        setLoading(false);
    }
  }, [cheque?.cheque.id]);

  if (!cheque) return null;
  
  const handleInputChange = (key: string, value: string) => {
    setEditedData((prev: any) => ({
        ...prev,
        [key]: { ...prev[key], text: value }
    }));
    if (errors.includes(key)) {
        setErrors(prev => prev.filter(e => e !== key));
    }
  };

  const validateForm = () => {
      const newErrors = [];
      if (!editedData?.Montant_Chiffres?.text) newErrors.push("Montant_Chiffres");
      if (!editedData?.Num_Compte?.text) newErrors.push("Num_Compte");
      if (!editedData?.Num_Cheque?.text) newErrors.push("Num_Cheque");
      
      setErrors(newErrors);
      return newErrors.length === 0;
  };

  const handleMainAction = async () => {
    if (isInternal) {
      if (!analysisData) {
        setLoading(true);
        try {
          const response = await apiClient.post(`/agents/cheque/analyze/${cheque.cheque.id}`);
          if (response.data.status === "SUCCESS") {
             const data = response.data.data;
             setAnalysisData(data);
             const safeData = {
                 ...data,
                 Montant_Chiffres: data.Montant_Chiffres || { text: "", confidence: 0 },
                 Num_Compte: data.Num_Compte || { text: "", confidence: 0 },
                 Num_Cheque: data.Num_Cheque || { text: "", confidence: 0 },
                 Date: data.Date || { text: "", confidence: 0 },
                 Lieu: data.Lieu || { text: "", confidence: 0 },
                 Beneficiaire: data.Beneficiaire || { text: "", confidence: 0 },
                 Montant_Lettres: data.Montant_Lettres || { text: "", confidence: 0 },
                 Ligne_MICR: data.Ligne_MICR || { text: "", confidence: 0 },
             };
             setEditedData(safeData);
          } else {
             alert("L'analyse a échoué : " + response.data.message);
          }
        } catch (error: any) {
          console.error("Erreur analyse:", error);
          alert("Erreur technique lors de l'analyse.");
        } finally {
          setLoading(false);
        }
        return;
      }

      if (!validateForm()) {
          alert("Veuillez remplir les champs obligatoires (Montant, N° Compte, N° Chèque) avant de valider.");
          return;
      }

      onProcess(cheque.cheque.id, editedData); 
      onClose();

    } else {
      setLoading(true);
      try {
        const data = await transmettreCheque(cheque.cheque.id, agentId);
        alert(data.message); 
        onClose();
      } catch (error: any) {
        alert(error.message || "Erreur lors de la transmission");
      } finally {
        setLoading(false);
      }
    }
  };

  const imageUrl = cheque.cheque.imageUrl.startsWith("http") 
    ? cheque.cheque.imageUrl 
    : `http://localhost:8000${cheque.cheque.imageUrl}`;

  const getFieldConfig = (key: string) => {
    switch (key) {
      case "Montant_Chiffres": return { icon: Banknote, label: "Montant (Num) *", color: "text-emerald-600", bg: "bg-emerald-50" };
      case "Montant_Lettres": return { icon: AlignLeft, label: "Montant (Lettres)", color: "text-slate-600", bg: "bg-slate-50" };
      case "Date": return { icon: Calendar, label: "Date d'émission", color: "text-blue-600", bg: "bg-blue-50" };
      case "Lieu": return { icon: MapPin, label: "Lieu", color: "text-orange-600", bg: "bg-orange-50" };
      case "Beneficiaire": return { icon: User, label: "Bénéficiaire", color: "text-purple-600", bg: "bg-purple-50" };
      case "Num_Cheque": return { icon: Hash, label: "N° Chèque *", color: "text-gray-600", bg: "bg-gray-50" };
      case "Num_Compte": return { icon: CreditCard, label: "N° Compte *", color: "text-indigo-600", bg: "bg-indigo-50" };
      case "Ligne_MICR": return { icon: FileText, label: "MICR (CMC7)", color: "text-zinc-600", bg: "bg-zinc-50" };
      case "Signature": return { icon: ImageIcon, label: "Signature", color: "text-rose-600", bg: "bg-rose-50" };
      default: return { icon: ScanEye, label: key, color: "text-gray-600", bg: "bg-gray-50" };
    }
  };

  const renderAnalysisResults = () => {
    if (!editedData) return null;

    const orderedKeys = ["Montant_Chiffres", "Date", "Lieu", "Beneficiaire", "Montant_Lettres", "Signature", "Num_Cheque", "Num_Compte", "Ligne_MICR"];
    const allKeys = orderedKeys;

    return (
      <div className="mt-0 h-full flex flex-col">


        <div className="p-4 bg-gray-50/50 flex-1 overflow-y-auto max-h-[500px] space-y-3 rounded-b-xl border border-gray-100">
          {allKeys.map((key) => {
            const value = editedData[key] || { text: "", confidence: 0, base64_image: null };
            const confidence = parseFloat(value.confidence || 0);
            const isConfident = confidence > 0.8;
            const isSignature = key === "Signature";
            const fieldConfig = getFieldConfig(key);
            const Icon = fieldConfig.icon;
            const hasError = errors.includes(key);

            return (
                <div key={key} className={`bg-white p-3 rounded-xl border shadow-sm hover:shadow-md transition-all duration-200 group relative ${hasError ? 'border-red-500 ring-1 ring-red-500' : 'border-gray-200'}`}>
                    
                    <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2">
                            <div className={`p-1.5 rounded-md ${fieldConfig.bg}`}>
                                <Icon className={`h-4 w-4 ${fieldConfig.color}`} />
                            </div>
                            <span className={`text-xs font-bold uppercase tracking-wider ${hasError ? 'text-red-600' : 'text-gray-500'}`}>{fieldConfig.label}</span>
                        </div>
                        {value.text && !isSignature && (
                            <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border ${isConfident ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-amber-50 text-amber-700 border-amber-100'}`}>
                                {isConfident ? <CheckCircle className="h-3 w-3" /> : <AlertTriangle className="h-3 w-3" />}
                                {Math.round(confidence * 100)}%
                            </div>
                        )}
                    </div>
                    
                    {isSignature ? (
                        <div className="mt-2 p-2 bg-slate-50 rounded-lg border border-dashed border-slate-300 flex justify-center items-center group-hover:bg-white transition-colors min-h-[60px]">
                            {value.base64_image ? (
                                <img src={value.base64_image} alt="Signature" className="max-h-16 object-contain mix-blend-multiply" />
                            ) : (
                                <span className="text-xs text-gray-400 italic">Signature non détectée</span>
                            )}
                        </div>
                    ) : (
                        <div className="relative group/input">
                             <input 
                                type="text"
                                value={value.text || ""}
                                placeholder={hasError ? "Champ obligatoire" : "Non détecté - Cliquez pour ajouter"}
                                onChange={(e) => handleInputChange(key, e.target.value)}
                                className={`w-full font-mono bg-transparent border-b focus:bg-blue-50/50 focus:outline-none px-1 py-0.5 transition-colors ${
                                    hasError ? 'border-red-300 placeholder-red-300' : 'border-transparent focus:border-blue-500'
                                } ${
                                    // MODIFICATION ICI : On utilise text-sm font-medium (comme les autres) au lieu de text-2xl
                                    key === 'Montant_Chiffres' ? 'text-sm font-medium text-gray-900' : 'text-sm font-medium text-gray-900'
                                }`}
                             />
                             <Edit2 className="h-3 w-3 text-gray-300 absolute right-0 top-1/2 -translate-y-1/2 opacity-0 group-hover/input:opacity-100 transition-opacity pointer-events-none" />
                             
                             {hasError && <AlertCircle className="h-4 w-4 text-red-500 absolute right-0 top-1/2 -translate-y-1/2" />}
                        </div>
                    )}
                </div>
            );
          })}
        </div>
      </div>
    );
  };

  const getButtonConfig = () => {
    if (loading) return { text: "Traitement en cours...", color: themeHex, disabled: true };
    if (!isInternal) return { text: "➡️ Transmettre à la Banque Cible", color: '#2563EB', disabled: false };
    if (!analysisData) return { text: "🔍 Lancer l'Analyse IA", color: themeHex, disabled: false };
    return { text: "✅ Valider le Traitement", color: '#059669', disabled: false };
  };

  const btnConfig = getButtonConfig();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm p-4 animate-in fade-in duration-200" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl p-0 overflow-hidden transform transition-all duration-300 scale-100 max-h-[95vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        
        <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-white sticky top-0 z-10">
          <div>
            <div className="flex items-center gap-3">
<h2 className="text-2xl font-bold" style={{ color: themeHex }}>Traitement du Chèque #{cheque.cheque.id}</h2>
            </div>
            <p className="text-gray-500 text-sm mt-0.5 flex items-center gap-1">
               <User className="h-3 w-3" /> Bénéficiaire : <span className="font-semibold text-gray-700">{cheque.beneficiaire.name}</span>
            </p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 transition-colors">
            <span className="text-xl leading-none">&times;</span>
          </button>
        </div>

        <div className="flex-1 overflow-hidden">
            <div className="flex flex-col lg:flex-row h-full">
                <div className="flex-1 bg-zinc-900/5 p-6 flex flex-col overflow-y-auto">
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2 h-full flex items-center justify-center min-h-[400px]">
                        <img 
                            src={imageUrl} 
                            alt="Cheque" 
                            className="w-full h-auto object-contain max-h-[600px] rounded-lg"
                            onError={(e) => { (e.target as HTMLImageElement).src = "https://placehold.co/600x300/F44336/FFFFFF?text=Image+Non+Disponible"; }}
                        />
                    </div>
                </div>

                <div className={`w-full lg:w-[400px] border-l border-gray-100 bg-white flex flex-col transition-all duration-500 ${!analysisData ? 'hidden lg:flex lg:justify-center lg:items-center' : ''}`}>
                    {analysisData ? (
                        renderAnalysisResults()
                    ) : (
                        <div className="text-center p-8 text-gray-400">
                            <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-gray-100">
                                <ScanEye className="h-8 w-8 text-gray-300" />
                            </div>
                            <p className="font-medium">Aucune analyse effectuée</p>
                            <p className="text-sm mt-2">Cliquez sur "Lancer l'Analyse" pour extraire les données du chèque.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>

        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end gap-3">
          <button onClick={onClose} className="px-5 py-2.5 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-100 font-medium transition-colors shadow-sm">
            Annuler
          </button>
          <button
            onClick={handleMainAction}
            disabled={btnConfig.disabled}
            className={`px-6 py-2.5 text-white rounded-lg font-bold shadow-md hover:shadow-lg transition-all transform active:scale-[0.98] flex items-center gap-2`}
            style={{ backgroundColor: btnConfig.color }}
          >
            {loading && <Loader2 className="animate-spin h-5 w-5" />}
            {btnConfig.text}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChequeDetailModal;