import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import { Bell, Menu, LayoutDashboard, List, History } from 'lucide-react';
import UploadModal from '../components/UploadModal';
import { useBeneficiary } from '../BeneficiaryContext';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import ProfileDetails from '@/pages/profile/components/ProfileDetails';
import SecuritySettings from '@/pages/profile/components/SecuritySettings';

const BeneficiaryLayout = () => {
  const [menuOpen, setMenuOpen] = React.useState(false);
  const [isProfileModalOpen, setProfileModalOpen] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState<'profile' | 'security'>('profile');
  const { user } = useUser();
  const { notifications } = useBeneficiary();
  const unreadCount = notifications.filter((n) => !n.lu).length;

  React.useEffect(() => {
    if (isProfileModalOpen) {
      setActiveTab('profile');
    }
  }, [isProfileModalOpen]);

  const userInitials = React.useMemo(() => {
    const first = user?.firstName?.[0] || '';
    const last = user?.lastName?.[0] || '';
    const fallback = user?.primaryEmailAddress?.emailAddress?.[0] || 'U';
    const initials = `${first}${last}`.trim();
    return initials || fallback.toUpperCase();
  }, [user]);

  const displayName = React.useMemo(() => {
    const name = `${user?.firstName || ''} ${user?.lastName || ''}`.trim();
    return name || user?.username || user?.primaryEmailAddress?.emailAddress || 'Utilisateur';
  }, [user]);

  const displayEmail = user?.primaryEmailAddress?.emailAddress || user?.emailAddresses?.[0]?.emailAddress || '';

  const menuItems = [
    { to: '/beneficiary', label: 'Tableau de bord', icon: LayoutDashboard },
    { to: 'checks', label: 'Mes Chèques', icon: List },
    { to: 'history', label: 'Historique', icon: History },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Main Nav */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="md:hidden p-2 -ml-2 hover:bg-gray-100 rounded-lg"
              >
                <Menu className="w-6 h-6" />
              </button>
              
              <nav className="hidden md:flex items-center gap-6">
                {menuItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end
                    className={({ isActive }) =>
                      `flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition ${
                        isActive
                          ? 'bg-blue-50 text-blue-700'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`
                    }
                  >
                    <item.icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </NavLink>
                ))}
              </nav>
            </div>

            {/* Right Side Actions */}
            <div className="flex items-center gap-4">
              <div className="hidden sm:block">
                <UploadModal />
              </div>
              <NavLink to="notifications" className="relative p-2 hover:bg-gray-100 rounded-full transition">
                <Bell className="w-6 h-6 text-gray-700" />
                {unreadCount > 0 && (
                  <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {unreadCount}
                  </span>
                )}
              </NavLink>
              <button
                type="button"
                onClick={() => setProfileModalOpen(true)}
                className="flex items-center gap-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 rounded-full"
              >
                <Avatar className="w-10 h-10">
                  <AvatarImage src={user?.imageUrl || ''} alt={displayName} />
                  <AvatarFallback className="bg-blue-600 text-white font-semibold">
                    {userInitials}
                  </AvatarFallback>
                </Avatar>
                <div className="hidden lg:block text-left">
                  <p className="text-sm font-medium text-gray-900 truncate">{displayName}</p>
                  <p className="text-xs text-gray-600 truncate">{displayEmail}</p>
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden bg-white border-t">
            <nav className="p-4 space-y-2">
              {menuItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end
                  onClick={() => setMenuOpen(false)}
                  className={({ isActive }) =>
                    `w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 font-medium'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`
                  }
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </NavLink>
              ))}
              <div className="pt-4 border-t">
                 <UploadModal />
              </div>
            </nav>
          </div>
        )}
      </header>
      
      {/* Main Content */}
      <main className="container mx-auto p-4 md:p-6">
        <Outlet />
      </main>

      <Dialog open={isProfileModalOpen} onOpenChange={setProfileModalOpen}>
        <DialogContent className="w-full max-w-4xl">
          <DialogHeader>
            <DialogTitle>Mon profil</DialogTitle>
          </DialogHeader>
          <Tabs value={activeTab} onValueChange={(val) => setActiveTab(val as 'profile' | 'security')} className="mt-4">
            <TabsList className="grid grid-cols-2 w-full max-w-sm">
              <TabsTrigger value="profile">Profil</TabsTrigger>
              <TabsTrigger value="security">Sécurité</TabsTrigger>
            </TabsList>
            <TabsContent value="profile" className="mt-4">
              <ProfileDetails />
            </TabsContent>
            <TabsContent value="security" className="mt-4">
              <SecuritySettings />
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BeneficiaryLayout;
