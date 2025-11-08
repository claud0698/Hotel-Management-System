/**
 * Navigation Bar Component
 */

import { useAuthStore } from '../stores/authStore';
import { useLanguageStore } from '../stores/languageStore';
import { useUIStore } from '../stores/uiStore';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export function Navbar() {
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useAuthStore();
  const { language, toggleLanguage } = useLanguageStore();
  const { toggleSidebar } = useUIStore();
  const { t } = useTranslation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-gray-900 shadow-lg border-b border-gray-800">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Hamburger menu - visible on mobile only */}
          {isAuthenticated && (
            <button
              onClick={toggleSidebar}
              className="md:hidden flex items-center justify-center w-10 h-10 rounded-md text-gray-300 hover:bg-gray-800 transition"
              aria-label="Toggle sidebar"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          )}

          {/* Logo */}
          <Link to="/" className="flex items-center">
            <div className="text-xl md:text-2xl font-bold text-blue-400">
              🏠 <span className="hidden sm:inline">{t('nav.appTitle')}</span>
            </div>
          </Link>

          {/* Right side */}
          <div className="flex items-center gap-2 sm:gap-4">
            {/* Language Switcher */}
            <button
              onClick={toggleLanguage}
              className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-2 text-xs sm:text-sm font-medium text-gray-300 hover:bg-gray-800 rounded-md transition"
              title={language === 'en' ? 'Switch to Indonesian' : 'Beralih ke Bahasa Inggris'}
            >
              <span className="text-lg">{language === 'en' ? '🇮🇩' : '🇬🇧'}</span>
              <span className="hidden sm:inline">{language === 'en' ? 'ID' : 'EN'}</span>
            </button>

            {/* User info and logout - show if authenticated */}
            {isAuthenticated && (
              <div className="hidden sm:flex items-center gap-4">
                <span className="text-sm text-gray-300">
                  {t('common.welcome')}, <strong className="text-white">{user?.username || 'User'}</strong>
                </span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition"
                >
                  {t('common.logout')}
                </button>
              </div>
            )}

            {/* Mobile logout button */}
            {isAuthenticated && (
              <button
                onClick={handleLogout}
                className="sm:hidden px-3 py-2 text-xs font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition"
                title={t('common.logout')}
              >
                ↪️
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
