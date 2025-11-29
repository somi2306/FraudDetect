// src/pages/agent/AgentRoutes.tsx

import React from 'react';
import { Routes, Route } from 'react-router-dom';

// Les composants qui seront utilisés dans ces routes
import AgentAuthProvider from '../../providers/AgentAuthProvider'; 
import AgentAuthPage from './AgentAuthPage';                      
import AgentFirstLogin from './AgentFirstLogin';            
import FloatingShape from '../../components/FloatingShape';       
import AgentProtectedRoute from '@/components/AgentProtectedRoute';

// ❌ L'IMPORT SUIVANT EST SUPPRIMÉ :
// import AgentDashboard from '../admin/AgentDashboard'; 

// --- Composant Temporaire de Substitution ---
const TempAgentDashboard = () => (
    <div className='text-white p-8 bg-zinc-800 rounded-lg'>
        <h2 className='text-2xl text-emerald-400'>Tableau de bord Agent (À Construire)</h2>
        <p>Connexion Agent réussie. Le composant final doit être créé ici.</p>
    </div>
);
// ---------------------------------------------


const AgentRoutes: React.FC = () => {
  return (
    <AgentAuthProvider> 
      <Routes>
        
        {/* 1. Route de Connexion Agent (/agent/login) */}
        <Route path="login" element={
            <div className='min-h-screen bg-gradient-to-br from-gray-900 via-green-900 to-emerald-900 flex items-center justify-center relative overflow-hidden'>
                <FloatingShape color='bg-green-500' size='w-64 h-64' top='-5%' left='10%' delay={0} />
                <FloatingShape color='bg-emerald-500' size='w-48 h-48' top='70%' left='80%' delay={5} />
                <FloatingShape color='bg-lime-500' size='w-32 h-32' top='40%' left='-10%' delay={2} />
                <AgentAuthPage /> 
            </div>
        } />
        
        {/* 2. Route de Réinitialisation forcée (/agent/first-login) */}
        <Route path="first-login" element={
            <div className='min-h-screen bg-gradient-to-br from-gray-900 via-green-900 to-emerald-900 flex items-center justify-center relative overflow-hidden'>
                <FloatingShape color='bg-green-500' size='w-64 h-64' top='-5%' left='10%' delay={0} />
                <FloatingShape color='bg-emerald-500' size='w-48 h-48' top='70%' left='80%' delay={5} />
                <FloatingShape color='bg-lime-500' size='w-32 h-32' top='40%' left='-10%' delay={2} />
                <AgentFirstLogin /> 
            </div>
        } />

        {/* 3. Routes Protégées (ex: /agent/dashboard) */}
        <Route 
            path="dashboard" 
            element={
                <AgentProtectedRoute requiredRole="AGENT">
                    {/* ✅ Utilisation du composant temporaire */}
                    <TempAgentDashboard /> 
                </AgentProtectedRoute>
            } 
        />
        
        <Route path="*" element={<div>Page Agent non trouvée</div>} />
      </Routes>
    </AgentAuthProvider>
  );
};

export default AgentRoutes;