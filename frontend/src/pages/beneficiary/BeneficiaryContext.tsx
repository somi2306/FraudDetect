import React, { createContext, useContext, useState } from 'react';

const mockChecks = [
  {
    id: 1,
    numero: "CHQ001234",
    montant: 5000,
    banque: "Attijariwafa Bank",
    dateDepot: "2024-11-28",
    statut: "en_cours",
  },
  {
    id: 2,
    numero: "CHQ001235",
    montant: 12500,
    banque: "BMCE Bank",
    dateDepot: "2024-11-27",
    statut: "approuve",
  },
  {
    id: 3,
    numero: "CHQ001236",
    montant: 3200,
    banque: "Banque Populaire",
    dateDepot: "2024-11-26",
    statut: "rejete",
  },
];

const mockNotifications = [
  {
    id: 1,
    message: "Votre chèque CHQ001235 a été approuvé",
    date: "2024-11-28 10:30",
    lu: false,
  },
  {
    id: 2,
    message: "Nouveau commentaire de l'agent sur CHQ001234",
    date: "2024-11-28 09:15",
    lu: false,
  },
  {
    id: 3,
    message: "Le chèque CHQ001236 a été rejeté",
    date: "2024-11-27 14:00",
    lu: true,
  },
];

const BeneficiaryContext = createContext({
  checks: mockChecks,
  notifications: mockNotifications,
  addCheck: (check) => {},
});

export const useBeneficiary = () => useContext(BeneficiaryContext);

export const BeneficiaryProvider = ({ children }) => {
  const [checks, setChecks] = useState(mockChecks);
  const [notifications, setNotifications] = useState(mockNotifications);

  const addCheck = (check) => {
    const newCheck = { ...check, id: checks.length + 1 };
    setChecks([newCheck, ...checks]);
  };

  return (
    <BeneficiaryContext.Provider value={{ checks, notifications, addCheck }}>
      {children}
    </BeneficiaryContext.Provider>
  );
};
