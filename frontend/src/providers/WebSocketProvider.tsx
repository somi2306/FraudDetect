import React, { createContext, useContext, useEffect, useRef } from 'react';
import { useUser } from '@clerk/clerk-react';
import { useToast } from "@/hooks/use-toast";
import { Bell, CheckCircle, AlertTriangle } from 'lucide-react';

const WebSocketContext = createContext<WebSocket | null>(null);

export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }: { children: React.ReactNode }) => {
    const { user, isSignedIn } = useUser();
    const { toast } = useToast();
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (isSignedIn && user) {
            // URL du WebSocket (adaptez le port si nécessaire)
            const wsUrl = `ws://localhost:8000/ws/${user.id}`;
            
            ws.current = new WebSocket(wsUrl);

            ws.current.onopen = () => {
                console.log("🟢 WebSocket connecté");
            };

            ws.current.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log("📩 Notification reçue:", data);

                // Affichage du Toast selon le type
                handleNotification(data);
            };

            ws.current.onclose = () => {
                console.log("🔴 WebSocket déconnecté");
            };

            return () => {
                ws.current?.close();
            };
        }
    }, [isSignedIn, user]);

    const handleNotification = (data: any) => {
        let icon = <Bell className="h-5 w-5" />;
        let className = "bg-blue-600 text-white border-none";

        if (data.type === "CHEQUE_RECEIVED") {
            icon = <AlertTriangle className="h-5 w-5" />;
            className = "bg-orange-500 text-white border-none";
        } else if (data.type === "CHEQUE_PROCESSED") {
            icon = <CheckCircle className="h-5 w-5" />;
            className = "bg-emerald-600 text-white border-none";
        }

        toast({
            title: data.title,
            description: data.message,
            action: icon,
            className: className,
            duration: 5000,
        });
        
        // Petit son de notification (optionnel)
        const audio = new Audio('/notification.mp3'); // Assurez-vous d'avoir un fichier son dans public/
        audio.play().catch(e => console.log("Audio play failed", e));
    };

    return (
        <WebSocketContext.Provider value={ws.current}>
            {children}
        </WebSocketContext.Provider>
    );
};