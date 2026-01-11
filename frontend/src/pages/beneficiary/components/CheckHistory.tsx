import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Clock, CheckCircle, XCircle, Loader } from 'lucide-react';
import { useBeneficiary } from '../BeneficiaryContext';

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

const CheckHistory = () => {
  const { checks, loading, error, theme } = useBeneficiary();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 animate-spin" style={{ color: theme.hex }} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-500 text-center py-8">
        {error}
      </div>
    );
  }

  if (checks.length === 0) {
    return (
      <div className="text-gray-500 text-center py-8">
        Aucun chèque dans l'historique
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b-2" style={{ borderBottomColor: theme.hex }}>
        <h2 className="text-xl font-bold" style={{ color: theme.hex }}>Historique des chèques</h2>
      </div>
      <Table>
        <TableHeader>
          <TableRow style={{ backgroundColor: `${theme.hex}10` }}>
            <TableHead>Numéro</TableHead>
            <TableHead>Banque</TableHead>
            <TableHead>Montant</TableHead>
            <TableHead>Date de dépôt</TableHead>
            <TableHead>Statut</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {checks.map((check) => (
            <TableRow key={check.id} className="hover:bg-gray-50">
              <TableCell className="font-medium">
                {check.numero ? check.numero : 'En attente de traitement'}
              </TableCell>
              <TableCell>{check.banque}</TableCell>
              <TableCell>
                {check.montant == null ? 'En attente de traitement' : `${check.montant.toLocaleString()} MAD`}
              </TableCell>
              <TableCell>{check.dateDepot}</TableCell>
              <TableCell>{getStatusBadge(check.statut)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default CheckHistory;
