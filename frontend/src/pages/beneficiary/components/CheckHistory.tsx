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
  const { checks, loading, error } = useBeneficiary();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 animate-spin text-blue-600" />
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
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Numéro</TableHead>
          <TableHead>Banque</TableHead>
          <TableHead>Montant</TableHead>
          <TableHead>Date de dépôt</TableHead>
          <TableHead>Statut</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {checks.map((check) => (
          <TableRow key={check.id}>
            <TableCell>{check.numero}</TableCell>
            <TableCell>{check.banque}</TableCell>
            <TableCell>{check.montant.toLocaleString()} MAD</TableCell>
            <TableCell>{check.dateDepot}</TableCell>
            <TableCell>{getStatusBadge(check.statut)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export default CheckHistory;
