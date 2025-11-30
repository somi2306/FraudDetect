import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
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

const CheckHistory = () => {
  const { checks } = useBeneficiary();

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
