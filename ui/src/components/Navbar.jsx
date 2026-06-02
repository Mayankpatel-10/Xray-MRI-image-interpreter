import { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Moon, Sun, Menu, X, Activity, LogIn, User, LogOut } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import authService from '../services/authService';

const Navbar = () => {
  const { isDark, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  
  const isAuthPage = location.pathname === '/login' || location.pathname === '/signup';

  useEffect(() => {
    const checkAuth = () => {
      const authenticated = authService.isAuthenticated();
      setIsAuthenticated(authenticated);
      if (authenticated) {
        const user = authService.getCurrentUser();
        setCurrentUser(user);
      } else {
        setCurrentUser(null);
      }
    };

    checkAuth();
    
    // Listen for storage events (for cross-tab sync)
    const handleStorageChange = () => {
      checkAuth();
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [location]);

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
    setCurrentUser(null);
    navigate('/login');
  };

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Home', href: '#home' },
    { name: 'Upload', href: '#upload' },
    { name: 'About', href: '#about' },
    { name: 'Contact', href: '#contact' },
  ];

  const scrollToSection = (e, href) => {
    e.preventDefault();
    if (location.pathname !== '/') {
      navigate('/', { state: { scrollTo: href } });
    } else {
      const element = document.querySelector(href);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }
    setIsMenuOpen(false);
  };

  useEffect(() => {
    if (location.pathname === '/' && location.state?.scrollTo) {
      const targetSection = location.state.scrollTo;
      const timer = setTimeout(() => {
        const element = document.querySelector(targetSection);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
        navigate('/', { replace: true, state: {} });
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [location, navigate]);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/70 dark:bg-gray-900/70 backdrop-blur-xl shadow-md border-b border-white/20 dark:border-gray-700/30'
          : 'bg-white/50 dark:bg-gray-900/50 backdrop-blur-lg border-b border-white/10 dark:border-gray-700/20'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <Activity className="w-8 h-8 text-medical-600 dark:text-medical-400" />
            <span className="text-xl font-bold text-medical-600 dark:text-medical-400">
              MedScan AI
            </span>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {!isAuthPage && navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={(e) => scrollToSection(e, link.href)}
                className="relative text-gray-700 dark:text-gray-300 hover:text-medical-600 dark:hover:text-medical-400 transition-colors font-medium after:content-[''] after:absolute after:bottom-[-4px] after:left-0 after:w-0 after:h-[2px] after:bg-medical-600 dark:after:bg-medical-400 after:transition-all after:duration-300 hover:after:w-full"
              >
                {link.name}
              </a>
            ))}
            {!isAuthPage && isAuthenticated && (
              <Link
                to="/history"
                className={`relative font-medium transition-colors after:content-[''] after:absolute after:bottom-[-4px] after:left-0 after:h-[2px] after:bg-medical-600 dark:after:bg-medical-400 after:transition-all after:duration-300 hover:after:w-full ${
                  location.pathname === '/history'
                    ? 'text-medical-600 dark:text-medical-400 after:w-full'
                    : 'text-gray-700 dark:text-gray-300 hover:text-medical-600 dark:hover:text-medical-400 after:w-0'
                }`}
              >
                History
              </Link>
            )}
            {!isAuthPage && isAuthenticated && currentUser ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <User className="w-4 h-4 text-medical-600 dark:text-medical-400" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {currentUser.name}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors font-medium"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              </div>
            ) : !isAuthPage && (
              <Link
                to="/login"
                className="flex items-center gap-2 bg-medical-600 hover:bg-medical-700 text-white px-4 py-2 rounded-lg transition-colors font-medium shadow-sm"
              >
                <LogIn className="w-4 h-4" />
                Login
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-4">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Toggle menu"
            >
              {isMenuOpen ? (
                <X className="w-6 h-6 text-gray-700 dark:text-gray-300" />
              ) : (
                <Menu className="w-6 h-6 text-gray-700 dark:text-gray-300" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex flex-col gap-4">
              {!isAuthPage && navLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  onClick={(e) => scrollToSection(e, link.href)}
                  className="relative text-gray-700 dark:text-gray-300 hover:text-medical-600 dark:hover:text-medical-400 transition-colors font-medium px-2 after:content-[''] after:absolute after:bottom-[-4px] after:left-0 after:w-0 after:h-[2px] after:bg-medical-600 dark:after:bg-medical-400 after:transition-all after:duration-300 hover:after:w-full"
                >
                  {link.name}
                </a>
              ))}
              {!isAuthPage && isAuthenticated && (
                <Link
                  to="/history"
                  onClick={() => setIsMenuOpen(false)}
                  className={`font-medium px-2 transition-colors ${
                    location.pathname === '/history'
                      ? 'text-medical-600 dark:text-medical-400'
                      : 'text-gray-700 dark:text-gray-300 hover:text-medical-600 dark:hover:text-medical-400'
                  }`}
                >
                  History
                </Link>
              )}
              {!isAuthPage && isAuthenticated && currentUser ? (
                <div className="flex flex-col gap-3">
                  <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg w-fit">
                    <User className="w-4 h-4 text-medical-600 dark:text-medical-400" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {currentUser.name}
                    </span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors font-medium w-fit"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </div>
              ) : !isAuthPage && (
                <Link
                  to="/login"
                  className="flex items-center gap-2 bg-medical-600 hover:bg-medical-700 text-white px-4 py-2 rounded-lg transition-colors font-medium w-fit shadow-sm"
                >
                  <LogIn className="w-4 h-4" />
                  Login
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
