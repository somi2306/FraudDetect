import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, CheckCircle, XCircle } from 'lucide-react';
import { useBeneficiary } from '../BeneficiaryContext';

const getStatusBadge = (statut: string) => {
  const configs = {
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
  const { checks } = useBeneficiary();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mes chèques</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {checks.map((check) => (
            <div key={check.id} className="p-4 border rounded-lg flex justify-between items-center">
              <div>
                <p className="font-semibold">{check.numero}</p>
                <p className="text-sm text-gray-500">{check.banque}</p>
              </div>
              <div className="text-right">
                <p className="font-semibold">{check.montant.toLocaleString()} MAD</p>
                {getStatusBadge(check.statut)}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default CheckList;
