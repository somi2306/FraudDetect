import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { User, Shield } from "lucide-react";

// --- IMPORTS DES COMPOSANTS PARTAGÉS ---
// On réutilise les composants existants sans les dupliquer
import ProfileDetails from "../profile/components/ProfileDetails";
import SecuritySettings from "../profile/components/SecuritySettings";

// --- IMPORTS LAYOUT ADMIN ---
import Sidebar from "@/components/Sidebar";
import AdminHeader from "@/components/AdminHeader";

const AdminProfilePage = () => {
  const [activeTab, setActiveTab] = useState("profile");

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
        
        {/* Sidebar Fixe */}
        <Sidebar />

        <div className="md:ml-64 min-h-screen transition-all duration-300">
            
            {/* Header Admin */}
            <AdminHeader />

            <main className="p-8 space-y-8 max-w-5xl mx-auto">
                
                <div className="mb-6">
                    <h1 className="text-2xl font-bold text-gray-900">Mon Profil Administrateur</h1>
                    <p className="text-gray-500">Gérez vos informations personnelles et la sécurité de votre compte.</p>
                </div>

                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                    <div className="grid grid-cols-1 lg:grid-cols-[250px_1fr] gap-6">
                        
                        {/* Menu Latéral des Tabs */}
                        <Card className="bg-white shadow-sm border-gray-200 h-fit">
                            <CardContent className="p-2">
                                <TabsList className="flex flex-col h-auto bg-transparent space-y-1 w-full">
                                    <TabsTrigger
                                        value="profile"
                                        className="w-full justify-start px-4 py-2 text-sm font-medium text-gray-600 data-[state=active]:bg-cyan-50 data-[state=active]:text-cyan-700 rounded-md transition-colors"
                                    >
                                        <User className="mr-2 h-4 w-4" /> Profil
                                    </TabsTrigger>
                                    <TabsTrigger
                                        value="security"
                                        className="w-full justify-start px-4 py-2 text-sm font-medium text-gray-600 data-[state=active]:bg-cyan-50 data-[state=active]:text-cyan-700 rounded-md transition-colors"
                                    >
                                        <Shield className="mr-2 h-4 w-4" /> Sécurité
                                    </TabsTrigger>
                                </TabsList>
                            </CardContent>
                        </Card>

                        {/* Contenu des Tabs */}
                        <div className="space-y-6">
                            
                            <TabsContent value="profile" className="mt-0">
                                <Card className="bg-white shadow-sm border-gray-200">
                                    <CardHeader>
                                        <CardTitle className="text-gray-900">Détails du profil</CardTitle>
                                        <CardDescription className="text-gray-500">
                                            Vos informations d'identité (synchronisées avec Clerk).
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        {/* Réutilisation du composant partagé */}
                                        <ProfileDetails />
                                    </CardContent>
                                </Card>
                            </TabsContent>

                            <TabsContent value="security" className="mt-0">
                                <Card className="bg-white shadow-sm border-gray-200">
                                    <CardHeader>
                                        <CardTitle className="text-gray-900">Sécurité</CardTitle>
                                        <CardDescription className="text-gray-500">
                                            Gérez votre mot de passe et vos sessions actives.
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        {/* Réutilisation du composant partagé */}
                                        <SecuritySettings />
                                    </CardContent>
                                </Card>
                            </TabsContent>

                        </div>
                    </div>
                </Tabs>
            </main>
        </div>
    </div>
  );
};

export default AdminProfilePage;