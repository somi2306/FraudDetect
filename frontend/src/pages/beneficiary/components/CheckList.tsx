import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, CheckCircle, XCircle, Loader, Eye } from 'lucide-react';
import { useBeneficiary } from '../BeneficiaryContext';
import { getBankThemeById } from '@/config/bankThemes';

const getStatusBadge = (statut: string) => {
  const configs: Record<string, { color: string; icon: typeof Clock; label: string }> = {
    en_cours: { color: 'bg-blue-100 text-blue-800', icon: Clock, label: 'En cours' },
    approuve: { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: 'Approuvé' },
    rejete: { color: 'bg-red-100 text-red-800', icon: XCircle, label: 'Rejeté' },
  };
  const config = configs[statut];
  if (!config) return null;
  const Icon = config.icon;
  return (
    <Badge className={`px-3 py-1 text-sm font-medium flex items-center gap-1 ${config.color}`}>
      <Icon className="w-4 h-4" />
      {config.label}
    </Badge>
  );
};

const CheckList = () => {
  const { checks, loading, error, theme } = useBeneficiary();
  const [selectedCheckImage, setSelectedCheckImage] = useState<string | null>(null);

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <Loader className="w-8 h-8 animate-spin" style={{ color: theme.hex }} />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="text-red-500 text-center py-8">
          {error}
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader className="border-b-2" style={{ borderBottomColor: theme.hex }}>
          <CardTitle style={{ color: theme.hex }}>Mes chèques</CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          {checks.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Aucun chèque trouvé</p>
          ) : (
            <div className="space-y-4">
              {checks.map((check) => {
                const bankTheme = getBankThemeById(check.banqueId);
                return (
                  <div 
                    key={check.id} 
                    className="p-4 border rounded-lg flex items-center gap-4 hover:shadow-md transition-shadow"
                    style={{ borderLeftWidth: '4px', borderLeftColor: bankTheme.hex }}
                  >
                    {/* Image du chèque avec bouton oeil */}
                    <div className="relative w-20 h-20 flex-shrink-0 bg-gray-100 rounded border border-gray-300 flex items-center justify-center">
                      {check.imageUrl ? (
                        <>
                          <img 
                            src={check.imageUrl} 
                            alt="Chèque"
                            className="w-full h-full object-cover rounded"
                          />
                          <button
                            onClick={() => setSelectedCheckImage(check.imageUrl!)}
                            className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 hover:bg-opacity-40 transition-all rounded"
                            title="Voir l'image du chèque"
                          >
                            <Eye className="w-6 h-6 text-white opacity-0 hover:opacity-100 transition-opacity" />
                          </button>
                        </>
                      ) : (
                        <span className="text-xs text-gray-400">Pas d'image</span>
                      )}
                    </div>
                    
                    {/* Informations du chèque */}
                    <div className="flex-grow">
                      <p className="font-semibold text-gray-900">{check.banque}</p>
                      <p className="text-sm text-gray-600">Dépôt: {check.dateDepot}</p>
                    </div>

                    {/* Statut */}
                    <div className="flex-shrink-0">
                      {getStatusBadge(check.statut)}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal pour voir l'image en grand */}
      {selectedCheckImage && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedCheckImage(null)}
        >
          <div className="bg-white rounded-lg max-w-2xl max-h-96 overflow-auto" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setSelectedCheckImage(null)}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-2xl bg-white rounded-full w-8 h-8 flex items-center justify-center"
              style={{ top: '-40px', right: '-40px' }}
            >
              ×
            </button>
            <img 
              src={selectedCheckImage} 
              alt="Chèque agrandi"
              className="w-full h-auto"
            />
          </div>
        </div>
      )}
    </>
  );
};

export default CheckList;