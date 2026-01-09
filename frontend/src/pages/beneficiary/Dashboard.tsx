import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useBeneficiary } from './BeneficiaryContext';
import { Loader } from 'lucide-react';

const Dashboard = () => {
  const { stats, loading, error } = useBeneficiary();

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

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Tableau de bord</h1>
      </div>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Chèques en attente</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.pending}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Chèques approuvés</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.approved}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Chèques rejetés</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.rejected}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
