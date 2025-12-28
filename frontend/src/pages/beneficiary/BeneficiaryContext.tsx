import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/lib/axios';
import { useAuth } from '@clerk/clerk-react';
import { getBankThemeById, DEFAULT_THEME } from '@/config/bankThemes';
import type { BankTheme } from '@/config/bankThemes';
import { useAuthStore } from '@/stores/useAuthStore';

export interface Cheque {
  id: number;
  numero: string | null;
  montant: number | null;
  detailsDisponibles: boolean;
  banque: string;
  banqueId?: number;
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
  bankId: number | null;
  theme: BankTheme;
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
  bankId: null,
  theme: DEFAULT_THEME,
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
  const { bankId, rib } = useAuthStore();

  // Calculer le thème basé sur le bankId
  const theme = getBankThemeById(bankId);
  
  // Debug log
  console.log('🏦 BeneficiaryContext - bankId:', bankId, 'rib:', rib, 'theme:', theme.name);

  // Note: syncUserRole est déjà appelé dans AuthProvider, pas besoin de le refaire ici

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
        numero: c.numero_cheque ?? null,
        montant: c.montant_cheque ?? null,
        detailsDisponibles: (c.numero_cheque != null && String(c.numero_cheque).trim() !== '') || (c.montant_cheque != null),
        banque: c.banque_nom || 'Banque inconnue',
        banqueId: c.banque_id,
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
      numero: check.numero ?? null,
      montant: check.montant ?? null,
      detailsDisponibles: check.detailsDisponibles ?? false,
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
        bankId,
        theme,
        refreshChecks: fetchChecks,
        addCheck,
      }}
    >
      {children}
    </BeneficiaryContext.Provider>
  );
};
