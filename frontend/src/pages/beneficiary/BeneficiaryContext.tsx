import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/lib/axios';
import { useAuth } from '@clerk/clerk-react';

export interface Cheque {
  id: number;
  numero: string;
  montant: number;
  banque: string;
  dateDepot: string;
  statut: string;
  imageUrl?: string;
}

export interface Notification {
  id: number;
  message: string;
  date: string;
  lu: boolean;
}

export interface ChequeStats {
  pending: number;
  approved: number;
  rejected: number;
}

interface BeneficiaryContextType {
  checks: Cheque[];
  notifications: Notification[];
  stats: ChequeStats;
  loading: boolean;
  error: string | null;
  refreshChecks: () => Promise<void>;
  addCheck: (check: Partial<Cheque>) => void;
}

const defaultStats: ChequeStats = { pending: 0, approved: 0, rejected: 0 };

const BeneficiaryContext = createContext<BeneficiaryContextType>({
  checks: [],
  notifications: [],
  stats: defaultStats,
  loading: false,
  error: null,
  refreshChecks: async () => {},
  addCheck: () => {},
});

export const useBeneficiary = () => useContext(BeneficiaryContext);

// Map backend status to frontend status
const mapStatus = (status: string | null): string => {
  if (!status) return 'en_cours';
  const mapping: Record<string, string> = {
    pending: 'en_cours',
    approved: 'approuve',
    rejected: 'rejete',
    en_cours: 'en_cours',
    approuve: 'approuve',
    rejete: 'rejete',
  };
  return mapping[status.toLowerCase()] || 'en_cours';
};

export const BeneficiaryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [checks, setChecks] = useState<Cheque[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState<ChequeStats>(defaultStats);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { getToken, isSignedIn } = useAuth();

  const fetchChecks = useCallback(async () => {
    if (!isSignedIn) return;
    
    setLoading(true);
    setError(null);

    try {
      const token = await getToken();
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch cheques
      const chequesResponse = await apiClient.get('/cheques/mes-cheques', { headers });
      const chequesData = chequesResponse.data || [];

      const mappedChecks: Cheque[] = chequesData.map((c: any) => ({
        id: c.id,
        numero: c.numero_cheque || `CHQ${c.id.toString().padStart(6, '0')}`,
        montant: c.montant_cheque || 0,
        banque: c.banque_nom || 'Banque inconnue',
        dateDepot: c.date_depot ? new Date(c.date_depot).toISOString().split('T')[0] : '',
        statut: mapStatus(c.status),
        imageUrl: c.image_url,
      }));

      setChecks(mappedChecks);

      // Fetch stats
      const statsResponse = await apiClient.get('/cheques/stats', { headers });
      setStats(statsResponse.data || defaultStats);

    } catch (err: any) {
      console.error('Error fetching cheques:', err);
      setError(err.message || 'Erreur lors du chargement des chèques');
    } finally {
      setLoading(false);
    }
  }, [getToken, isSignedIn]);

  useEffect(() => {
    if (isSignedIn) {
      fetchChecks();
    }
  }, [isSignedIn, fetchChecks]);

  const addCheck = (check: Partial<Cheque>) => {
    const newCheck: Cheque = {
      id: Date.now(),
      numero: check.numero || `CHQ${Date.now()}`,
      montant: check.montant || 0,
      banque: check.banque || '',
      dateDepot: check.dateDepot || new Date().toISOString().split('T')[0],
      statut: check.statut || 'en_cours',
      imageUrl: check.imageUrl,
    };
    setChecks((prev) => [newCheck, ...prev]);
    // Refresh to get real data after upload
    setTimeout(() => fetchChecks(), 1000);
  };

  return (
    <BeneficiaryContext.Provider
      value={{
        checks,
        notifications,
        stats,
        loading,
        error,
        refreshChecks: fetchChecks,
        addCheck,
      }}
    >
      {children}
    </BeneficiaryContext.Provider>
  );
};
