import React from 'react';
import { useUser, useClerk } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import { Bell, Menu, Search, User, LogOut, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const AdminHeader = () => {
    const { user } = useUser();
    const { signOut } = useClerk();
    const navigate = useNavigate();

    const handleSignOut = async () => {
        await signOut();
        navigate("/auth");
    };

    return (
        <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-gray-200 px-8 py-4 flex items-center justify-between shadow-sm">
            <div className="md:hidden">
                <Button variant="ghost" size="icon">
                    <Menu className="h-6 w-6 text-gray-500" />
                </Button>
            </div>
            
            <div className="flex-1 hidden md:flex max-w-md">
            </div>

            <div className="flex items-center gap-4 ml-auto">
                
                <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-medium text-gray-900">{user?.fullName}</p>
                        <p className="text-xs text-gray-500">Super Admin</p>
                    </div>

                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="relative h-10 w-10 rounded-full p-0 border-2 border-white shadow-sm hover:ring-2 hover:ring-cyan-100 transition-all">
                                <Avatar className="h-10 w-10">
                                    <AvatarImage src={user?.imageUrl} />
                                    <AvatarFallback className="bg-cyan-600 text-white">AD</AvatarFallback>
                                </Avatar>
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent className="w-56" align="end" forceMount>
                            <DropdownMenuLabel className="font-normal">
                                <div className="flex flex-col space-y-1">
                                    <p className="text-sm font-medium leading-none">{user?.fullName}</p>
                                    <p className="text-xs leading-none text-muted-foreground">{user?.primaryEmailAddress?.emailAddress}</p>
                                </div>
                            </DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            
                            {/* Lien vers la page PROFIL ADMIN */}
                            <DropdownMenuItem onClick={() => navigate("/admin/profile")} className="cursor-pointer">
                                <User className="mr-2 h-4 w-4" />
                                <span>Mon Profil</span>
                            </DropdownMenuItem>
                            
                            <DropdownMenuItem onClick={() => navigate("/admin/setup-2fa")} className="cursor-pointer">
                                <Settings className="mr-2 h-4 w-4" />
                                <span>Configuration 2FA</span>
                            </DropdownMenuItem>
                            
                            <DropdownMenuSeparator />
                            
                            <DropdownMenuItem onClick={handleSignOut} className="cursor-pointer text-red-600 focus:text-red-600 focus:bg-red-50">
                                <LogOut className="mr-2 h-4 w-4" />
                                <span>Se déconnecter</span>
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            </div>
        </header>
    );
};

export default AdminHeader;