import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser, useClerk } from "@clerk/clerk-react";
import { apiClient } from "@/lib/axios";

// UI Components
import { Input } from '@/components/ui/input'; 
import { Button } from '@/components/ui/button';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import { Loader2 } from 'lucide-react';

const AgentResetPassword: React.FC = () => {
    const navigate = useNavigate();
    const { user } = useUser();
    const { signOut } = useClerk();

    // On récupère le mot de passe temporaire stocké lors du login
    const [tempPassword, setTempPassword] = useState('');

    useEffect(() => {
        const storedPass = localStorage.getItem('agentTempPassword');
        if (!storedPass) {
            navigate('/auth'); 
        } else {
            setTempPassword(storedPass);
        }
    }, [navigate]);

    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleReset = async () => {
        if (!newPassword || !confirmPassword) {
            setError('Veuillez remplir tous les champs.');
            return;
        }
        if (newPassword !== confirmPassword) {
            setError('Les nouveaux mots de passe ne correspondent pas.');
            return;
        }
        if (newPassword.length < 8) {
            setError('Le nouveau mot de passe doit contenir au moins 8 caractères.');
            return;
        }

        setError('');
        setIsLoading(true);

        try {
            if (!user) throw new Error("Session invalide.");

            // 1. Logique Clerk
            await user.updatePassword({
                currentPassword: tempPassword,
                newPassword: newPassword,
                signOutOfOtherSessions: true
            });

            // 2. Logique Backend
            await apiClient.put("/agents/confirm-reset");
            
            // 3. Nettoyage
            localStorage.removeItem('agentTempPassword');

            // 4. Déconnexion et Redirection
            await signOut();
            navigate('/auth'); 
            
        } catch (err: any) {
            console.error(err);
            const msg = err.errors?.[0]?.longMessage || err.message || 'Erreur lors de la mise à jour.';
            if (msg.toLowerCase().includes("current password")) {
                setError("Erreur de session. Veuillez vous reconnecter.");
            } else if (msg.toLowerCase().includes("password has been found")) {
                setError("Mot de passe trop simple ou compromis. Choisissez-en un autre.");
            } else {
                setError(msg);
            }
        } finally {
            setIsLoading(false);
        }
    };

    // --- CLASSES CSS POUR LE STYLE UNIFIÉ ---
    const gradientTextClass = "text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-yellow-400 to-orange-400";
    const gradientButtonClass = "w-full bg-gradient-to-r from-cyan-600 via-yellow-500 to-orange-500 hover:from-cyan-700 hover:via-yellow-600 hover:to-orange-600 text-white font-bold shadow-lg border-0 transition-all duration-300 transform hover:scale-[1.02]";
    const focusClass = "focus:border-cyan-500"; // Focus couleur dominante (Cyan)

    return (
        <div className="min-h-screen w-full flex items-center justify-center bg-zinc-900 p-4">
            
            {/* CARTE (Même structure qu'avant) */}
            <div className='max-w-md w-full p-6 bg-zinc-800 rounded-xl shadow-lg space-y-4 text-white border border-zinc-700'>
                
                {/* TITRE AVEC DÉGRADÉ */}
                <h2 className={`text-xl font-bold text-center ${gradientTextClass}`}>
                    Première Connexion Requise
                </h2>
                
                <p className='text-sm text-zinc-400 text-center'>
                    Veuillez définir un nouveau mot de passe pour activer votre compte Agent.
                </p>
                
                {error && <p className='text-red-500 text-sm text-center bg-red-900/20 p-2 rounded border border-red-900/30'>{error}</p>}
                
                <div className="space-y-4">
                    {/* EMAIL (READONLY) */}
                    <Input
                        type='email'
                        value={user?.primaryEmailAddress?.emailAddress || ''}
                        readOnly
                        className='bg-zinc-900 border-zinc-600 text-white placeholder-zinc-400 opacity-70 cursor-not-allowed focus:ring-0'
                    />
                    
                    {/* NOUVEAU MOT DE PASSE */}
                    <div className="relative">
                        <Input
                            type={showPassword ? 'text' : 'password'}
                            placeholder='Nouveau mot de passe'
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            className={`bg-zinc-900 border-zinc-600 text-white pr-10 transition-colors ${focusClass}`}
                        />
                        <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute inset-y-0 right-0 pr-3 flex items-center text-zinc-400 hover:text-white"
                        >
                            {showPassword ? <FaEyeSlash /> : <FaEye />}
                        </button>
                    </div>

                    {/* CONFIRMATION */}
                    <Input
                        type='password'
                        placeholder='Confirmer nouveau mot de passe'
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className={`bg-zinc-900 border-zinc-600 text-white transition-colors ${focusClass}`}
                    />
                </div>

                {/* BOUTON AVEC DÉGRADÉ */}
                <Button 
                    onClick={handleReset} 
                    className={gradientButtonClass}
                    disabled={isLoading || newPassword.length < 1}
                >
                    {isLoading ? <Loader2 className="animate-spin mr-2 h-4 w-4" /> : 'Modifier et Se reconnecter'}
                </Button>
            </div>
        </div>
    );
};

export default AgentResetPassword;