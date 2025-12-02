// src/pages/agent/AgentAuthPage.tsx

import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import AuthImagePattern from "../../components/AuthImagePattern";
import { useNavigate } from "react-router-dom";
import { loginAgent } from "@/lib/agentAuthService"; // Votre service API
import { useAgentAuthStore } from "@/stores/useAgentAuthStore"; // Votre store Zustand
import ForgotPassword from "../../components/ForgotPassword"; 
// Assurez-vous d'importer FloatingShape si vous l'utilisez dans ce fichier

const AgentAuthPage = () => {
  const { login } = useAgentAuthStore();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);

  const handleAgentLogin = async () => {
    setError(null);
    setIsLoading(true);

    try {
      const result = await loginAgent(email, password); 

      // 1. Cas : Réinitialisation requise (must_reset_password = True)
      if (result.status === "reset_required") {
        
        // Stockage temporaire des identifiants
        localStorage.setItem('agentEmail', email);
        localStorage.setItem('agentTempPassword', password); 
        
        // Redirection vers l'écran de réinitialisation forcée
        navigate("/agent/first-login"); 
        
      } 
      // 2. Cas : Connexion réussie (JWT reçu)
      else if (result.access_token) {
        
        // Connexion via le store Zustand
        // Le rôle est ici codé en dur comme 'AGENT', ajustez si l'API le renvoie.
        login(result.access_token, result.user_id, email, 'AGENT'); 
        localStorage.setItem("agentToken", result.access_token);
        console.log(localStorage.getItem("agentToken"));

        // Redirection vers le tableau de bord Agent
        navigate("/agent/dashboard"); 
        
      } else {
        setError("Réponse serveur inattendue.");
      }

    } catch (err: any) {
      // Cas : Échec d'authentification (401 Unauthorized)
      setError(err.message || "Échec de la connexion.");
      
    } finally {
      setIsLoading(false);
    }
  };
  
  // Utilisation du ForgotPassword existant si l'Agent l'utilise après sa première connexion
  if (showForgotPassword) {
    return <ForgotPassword onBack={() => setShowForgotPassword(false)} />;
  }

  return (
    <div className="max-w-4xl w-full mx-auto bg-zinc-900 bg-opacity-50 backdrop-filter backdrop-blur-xl rounded-2xl shadow-xl overflow-hidden flex flex-col lg:flex-row relative z-10">
      <div className="p-8 flex-1">
        <h1 className="text-2xl font-bold text-white text-center mb-6">Connexion Agent</h1>

        <div className="space-y-4 mt-4">
          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="bg-zinc-800 border-zinc-700 text-white"
          />
          <div className="relative">
            <Input
              type={showPassword ? "text" : "password"}
              placeholder="Mot de passe"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-zinc-800 border-zinc-700 text-white pr-10"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-zinc-400 hover:text-white"
            >
              {showPassword ? <FaEyeSlash /> : <FaEye />}
            </button>
          </div>
          
          {error && <p className="text-red-500 text-sm text-center">{error}</p>}
          
          <Button
            onClick={handleAgentLogin}
            className="w-full bg-emerald-500 hover:bg-emerald-600 text-black"
            disabled={isLoading}
          >
            {isLoading ? "Connexion en cours..." : "Se connecter"}
          </Button>
          
          <div className="text-center">
            <Button
              variant="link"
              onClick={() => setShowForgotPassword(true)}
              className="text-zinc-400 hover:text-white"
            >
              Mot de passe oublié ?
            </Button>
          </div>
        </div>
      </div>
      <div className="flex-1 hidden lg:block">
        <AuthImagePattern
          title="Espace Agent"
          subtitle="Gérez les bénéficiaires et les détections de fraude"
        />
      </div>
    </div>
  );
};

export default AgentAuthPage;