// src/pages/auth/AgentFirstLogin.tsx

import React, { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { Input } from '@/components/ui/input'; 
import { Button } from '@/components/ui/button';
import { resetAgentPassword } from '@/lib/agentAuthService'; 
import { FaEye, FaEyeSlash } from 'react-icons/fa';

const AgentFirstLogin: React.FC = () => {
    const navigate = useNavigate();
    
    // Récupérer l'email et l'ancien mot de passe stockés temporairement
    const email = localStorage.getItem('agentEmail') || '';
    const oldPassword = localStorage.getItem('agentTempPassword') || ''; 

    // États du formulaire
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Si les données sont manquantes, l'Agent doit repasser par la connexion
    if (!email || !oldPassword) {
        return <Navigate to="/agent/login" replace />;
    }

    const handleReset = async () => {
        if (newPassword !== confirmPassword) {
            setError('Les nouveaux mots de passe ne correspondent pas.');
            return;
        }
        if (newPassword.length < 8) { // Validation simple
            setError('Le nouveau mot de passe doit contenir au moins 8 caractères.');
            return;
        }

        setError('');
        setIsLoading(true);

        try {
            await resetAgentPassword(email, oldPassword, newPassword);

            // Succès: Nettoyer le stockage temporaire
            localStorage.removeItem('agentEmail');
            localStorage.removeItem('agentTempPassword');
            
            alert('Votre mot de passe a été modifié avec succès. Veuillez vous connecter avec votre nouveau mot de passe.');
            navigate('/agent/login'); 
            
        } catch (err: any) {
            setError(err.message || 'Une erreur est survenue lors de la modification du mot de passe.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className='max-w-md w-full p-6 bg-zinc-900 rounded-lg shadow-lg space-y-4 text-white'>
            <h2 className='text-xl font-bold text-center text-emerald-500'>Première Connexion Requise</h2>
            <p className='text-sm text-zinc-400 text-center'>Veuillez définir un nouveau mot de passe pour activer votre compte Agent.</p>
            
            {error && <p className='text-red-500 text-sm text-center'>{error}</p>}
            
            <div className="space-y-4">
                {/* Email affiché (non modifiable) */}
                <Input
                    type='email'
                    value={email}
                    readOnly
                    className='bg-zinc-800 border-zinc-700 text-white placeholder-zinc-400 opacity-70'
                />
                
                {/* NOUVEAU MOT DE PASSE */}
                <div className="relative">
                    <Input
                        type={showPassword ? 'text' : 'password'}
                        placeholder='Nouveau mot de passe'
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className='bg-zinc-800 border-zinc-700 text-white pr-10'
                    />
                    <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-zinc-400 hover:text-white"
                    >
                        {showPassword ? <FaEyeSlash /> : <FaEye />}
                    </button>
                </div>

                {/* CONFIRMER MOT DE PASSE */}
                <Input
                    type='password'
                    placeholder='Confirmer nouveau mot de passe'
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className='bg-zinc-800 border-zinc-700 text-white'
                />
            </div>

            <Button onClick={handleReset} className='w-full bg-emerald-500 hover:bg-emerald-600 text-black' disabled={isLoading || newPassword.length < 1}>
                {isLoading ? 'Modification en cours...' : 'Modifier le mot de passe'}
            </Button>
        </div>
    );
};

export default AgentFirstLogin;