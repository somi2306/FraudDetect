import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, CheckCircle, XCircle, Loader } from 'lucide-react';
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
                  className="p-4 border rounded-lg flex justify-between items-center hover:shadow-md transition-shadow"
                  style={{ borderLeftWidth: '4px', borderLeftColor: bankTheme.hex }}
                >
                  <div className="flex items-center gap-4">
                    {/* Logo de la banque */}
                    <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center overflow-hidden border-2" style={{ borderColor: bankTheme.hex }}>
                      <img 
                        src={bankTheme.logo} 
                        alt={bankTheme.name}
                        className="w-10 h-10 object-contain"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = '/logos/default.png';
                        }}
                      />
                    </div>
                    <div>
                      <p className="font-semibold">
                        {check.numero ? check.numero : 'En attente de traitement'}
                      </p>
                      <p className="text-sm text-gray-500">{check.banque}</p>
                      <p className="text-xs text-gray-400">{check.dateDepot}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    {check.montant == null ? (
                      <p className="text-sm text-gray-500">En attente de traitement</p>
                    ) : (
                      <p className="font-semibold text-lg">{check.montant.toLocaleString()} MAD</p>
                    )}
                    {getStatusBadge(check.statut)}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CheckList;
