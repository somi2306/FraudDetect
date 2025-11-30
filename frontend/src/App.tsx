import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom';
import BeneficiaryLayout from './pages/beneficiary/layouts/BeneficiaryLayout';
import Dashboard from './pages/beneficiary/Dashboard';
import CheckList from './pages/beneficiary/components/CheckList';
import CheckHistory from './pages/beneficiary/components/CheckHistory';
import Notifications from './pages/beneficiary/components/Notifications';
import { Button } from './components/ui/button';
import { BeneficiaryProvider } from './pages/beneficiary/BeneficiaryContext';

function Home() {
  return (
    <>
      <h1 className='text-red-500'>Vite + React</h1>
      <h2 className="text-blue-600 font-bold text-2xl mt-4">
        Tailwind fonctionne !
        <Button className="ml-4">Cliquez-moi</Button>
      </h2>
    </>
  )
}

function App() {
  return (
    <Router>
      <BeneficiaryProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/beneficiary" element={<BeneficiaryLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="checks" element={<CheckList />} />
            <Route path="history" element={<CheckHistory />} />
            <Route path="notifications" element={<Notifications />} />
          </Route>
        </Routes>
      </BeneficiaryProvider>
    </Router>
  )
}

export default App;
