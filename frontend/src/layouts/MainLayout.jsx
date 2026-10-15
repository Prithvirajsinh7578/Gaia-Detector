import { useEffect } from 'react';
import { useLocation, Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar/Navbar';
import Footer from '../components/Footer/Footer';

/**
 * Main layout wrapper with Navbar, Footer, and scroll-to-top on route change.
 */
export default function MainLayout() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [pathname]);

  return (
    <div className="min-h-screen animated-gradient-bg relative">
      {/* Background ambient glow orbs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-primary-purple/10 rounded-full blur-[120px] animate-pulse-glow" />
        <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-primary-cyan/10 rounded-full blur-[120px] animate-pulse-glow" style={{ animationDelay: '1.5s' }} />
        <div className="absolute top-3/4 left-1/2 w-64 h-64 bg-primary-cyan/5 rounded-full blur-[100px] animate-pulse-glow" style={{ animationDelay: '3s' }} />
      </div>

      <Navbar />
      <main className="relative z-10">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
