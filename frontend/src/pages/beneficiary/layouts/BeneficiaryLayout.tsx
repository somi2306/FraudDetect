import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { useUser, useClerk } from '@clerk/clerk-react';
import { Bell, Menu, LayoutDashboard, List, History, LogOut } from 'lucide-react';
import UploadModal from '../components/UploadModal';
import { useBeneficiary } from '../BeneficiaryContext';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import ProfileDetails from '@/pages/profile/components/ProfileDetails';
import SecuritySettings from '@/pages/profile/components/SecuritySettings';
import { getBankLogo } from '@/config/bankThemes';

const BeneficiaryLayout = () => {
  const [menuOpen, setMenuOpen] = React.useState(false);
  const [isProfileModalOpen, setProfileModalOpen] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState<'profile' | 'security'>('profile');
  const { user } = useUser();
  const { signOut } = useClerk();
  const { notifications, theme, bankId } = useBeneficiary();
  const unreadCount = notifications.filter((n) => !n.lu).length;

  const handleSignOut = () => {
    signOut({ redirectUrl: '/' });
  };

  // Logo de la banque
  const bankLogo = getBankLogo(bankId);

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
    <div 
      className="min-h-screen"
      style={{ 
        backgroundImage: `linear-gradient(to bottom, white 0%, #f3f4f6 70%, ${theme.hex}50 100%)` 
      }}
    >
      {/* Top Navigation Bar */}
      <header 
        className="shadow-lg sticky top-0 z-40 text-white"
        style={{ backgroundColor: theme.hex }}
      >
        <div className="w-full px-8 xl:px-16">
          <div className="flex justify-between items-center h-24 gap-8">
            {/* Logo and Bank Name */}
            <div className="flex items-center flex-shrink-0">
              {/* Logo de la banque - transparent */}
              <div className="flex items-center gap-4">
                <img 
                  src={bankLogo} 
                  alt={theme.name} 
                  className="w-16 h-16 object-contain"
                />
                <div className="hidden sm:block">
                  <h1 className="font-bold text-xl tracking-wide whitespace-nowrap">{theme.name}</h1>
                  <p className="text-xs text-white/70">Espace Bénéficiaire</p>
                </div>
              </div>
              
              {/* Menu burger mobile */}
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="md:hidden p-2 hover:bg-white/20 rounded-lg ml-4"
              >
                <Menu className="w-6 h-6" />
              </button>
            </div>

            {/* Navigation principale - Desktop */}
            <nav className="hidden lg:flex items-center gap-6 flex-shrink-0">
              {menuItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 whitespace-nowrap ${
                      isActive
                        ? 'bg-white text-gray-800 shadow-md'
                        : 'text-white hover:bg-white/20'
                    }`
                  }
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>

            {/* Right Side Actions */}
            <div className="flex items-center gap-4 flex-shrink-0">
              <div className="hidden sm:block">
                <UploadModal />
              </div>
              <NavLink to="notifications" className="relative p-3 hover:bg-white/20 rounded-full transition">
                <Bell className="w-6 h-6 text-white" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                    {unreadCount}
                  </span>
                )}
              </NavLink>
              <div className="hidden md:block h-10 w-px bg-white/30 mx-2"></div>
              <button
                type="button"
                onClick={() => setProfileModalOpen(true)}
                className="flex items-center gap-3 focus:outline-none focus:ring-2 focus:ring-white/50 rounded-full p-1.5 hover:bg-white/10 transition"
              >
                <Avatar className="w-11 h-11 border-2 border-white/50">
                  <AvatarImage src={user?.imageUrl || ''} alt={displayName} />
                  <AvatarFallback className="bg-white/20 text-white font-semibold">
                    {userInitials}
                  </AvatarFallback>
                </Avatar>
                <div className="hidden lg:block text-left max-w-[140px]">
                  <p className="text-sm font-semibold text-white truncate">{displayName}</p>
                  <p className="text-xs text-white/70 truncate">{displayEmail}</p>
                </div>
              </button>
              <button
                type="button"
                onClick={handleSignOut}
                className="flex items-center gap-2 px-4 py-2.5 text-white bg-white/10 hover:bg-white/20 rounded-lg transition font-medium"
                title="Se déconnecter"
              >
                <LogOut className="w-5 h-5" />
                <span className="hidden lg:inline text-sm">Déconnecter</span>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden border-t border-white/20" style={{ backgroundColor: theme.hex }}>
            <nav className="p-4 space-y-2">
              {menuItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end
                  onClick={() => setMenuOpen(false)}
                  className={({ isActive }) =>
                    `w-full flex items-center gap-3 px-4 py-4 rounded-xl transition text-base font-semibold ${
                      isActive
                        ? 'bg-white text-gray-800 shadow-md'
                        : 'text-white hover:bg-white/20'
                    }`
                  }
                >
                  <item.icon className="w-6 h-6" />
                  <span>{item.label}</span>
                </NavLink>
              ))}
              <div className="pt-4 border-t border-white/20">
                 <UploadModal />
              </div>
              <button
                type="button"
                onClick={handleSignOut}
                className="w-full flex items-center gap-3 px-4 py-4 mt-2 text-white bg-white/10 hover:bg-white/20 rounded-xl transition font-semibold"
              >
                <LogOut className="w-6 h-6" />
                <span>Se déconnecter</span>
              </button>
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
