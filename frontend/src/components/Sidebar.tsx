import React from 'react';
import { useNavigate, useLocation } from "react-router-dom";
import { useClerk } from "@clerk/clerk-react";
import { 
  LayoutDashboard, 
  Users, 
  ShieldCheck, 
  LogOut, 
  UserPlus,
  UserCheck // Nouvelle icône pour les bénéficiaires
} from "lucide-react";

interface SidebarProps {
    activePath: string;
}

const Sidebar: React.FC<SidebarProps> = ({ activePath }) => {
    const navigate = useNavigate();
    const { signOut } = useClerk();

    const handleSignOut = async () => {
        await signOut();
        navigate("/auth");
    };

    const menuItems = [
        { 
            icon: LayoutDashboard, 
            label: "Vue d'ensemble", 
            path: "/admin/dashboard" 
        },
        { 
            icon: Users, 
            label: "Gérer les Agents", 
            path: "/admin/manage-agents" 
        },
        { 
            icon: UserCheck, 
            label: "Gérer les Bénéficiaires", 
            path: "/admin/manage-beneficiaries" 
        },
    ];

    return (
        <div className="hidden md:flex flex-col w-64 bg-zinc-900 border-r border-zinc-800 h-screen fixed left-0 top-0 z-50">
            {/* Logo Area */}
            <div className="p-6 flex items-center gap-3">
                <div className="h-10 w-10 bg-zinc-800 rounded-xl flex items-center justify-center border border-zinc-700 shadow-lg">
                    <ShieldCheck className="h-6 w-6 text-cyan-400" />
                </div>
                <div>
                    <h1 className="font-bold text-lg text-white tracking-wide">FraudDetect</h1>
                    
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 space-y-2 mt-4">
                {menuItems.map((item) => {
                    const isActive = activePath === item.path;
                    return (
                        <button
                            key={item.path}
                            onClick={() => navigate(item.path)}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                                isActive 
                                ? "bg-gradient-to-r from-cyan-900/50 to-blue-900/50 text-cyan-400 border border-cyan-500/20 shadow-lg shadow-cyan-900/20" 
                                : "text-zinc-400 hover:bg-zinc-800 hover:text-white"
                            }`}
                        >
                            <item.icon className={`h-5 w-5 ${isActive ? "text-cyan-400" : "text-zinc-500 group-hover:text-white"}`} />
                            <span className="font-medium text-sm">{item.label}</span>
                            {isActive && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]" />}
                        </button>
                    );
                })}
            </nav>

            {/* User & Logout */}
            <div className="p-4 border-t border-zinc-800">
                <button 
                    onClick={handleSignOut}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-400 hover:bg-red-900/10 transition-colors"
                >
                    <LogOut className="h-5 w-5" />
                    <span className="font-medium text-sm">Se déconnecter</span>
                </button>
            </div>
        </div>
    );
};

export default Sidebar;