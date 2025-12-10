import React from 'react';
import { useNavigate, useLocation } from "react-router-dom";
import { useClerk } from "@clerk/clerk-react";
import { 
  LayoutDashboard, 
  Users, 
  ShieldCheck, 
  LogOut, 
  UserCheck
} from "lucide-react";

const Sidebar = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { signOut } = useClerk();
    const activePath = location.pathname;

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
        <div className="hidden md:flex flex-col w-64 bg-white border-r border-gray-200 h-screen fixed left-0 top-0 z-50">
            {/* Logo Area */}
            <div className="p-6 flex items-center gap-3 border-b border-gray-100">
                <div className="h-10 w-10 bg-cyan-50 rounded-xl flex items-center justify-center border border-cyan-100 shadow-sm">
                    <ShieldCheck className="h-6 w-6 text-cyan-600" />
                </div>
                <div>
                    <h1 className="font-bold text-lg text-gray-900 tracking-wide">FraudDetect</h1>
                    <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Admin Panel</span>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 space-y-2 mt-6">
                {menuItems.map((item) => {
                    const isActive = activePath === item.path;
                    return (
                        <button
                            key={item.path}
                            onClick={() => navigate(item.path)}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                                isActive 
                                ? "bg-cyan-50 text-cyan-700 font-medium shadow-sm ring-1 ring-cyan-200" 
                                : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"
                            }`}
                        >
                            <item.icon className={`h-5 w-5 ${isActive ? "text-cyan-600" : "text-gray-400 group-hover:text-gray-600"}`} />
                            <span className="text-sm">{item.label}</span>
                            {isActive && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-cyan-500" />}
                        </button>
                    );
                })}
            </nav>

            {/* User & Logout */}
            <div className="p-4 border-t border-gray-200">
                <button 
                    onClick={handleSignOut}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-600 hover:bg-red-50 transition-colors"
                >
                    <LogOut className="h-5 w-5" />
                    <span className="font-medium text-sm">Se déconnecter</span>
                </button>
            </div>
        </div>
    );
};

export default Sidebar;