/**
 * Navigation Bar Component
 */

import { useAuthStore } from '../stores/authStore';
import { useLanguageStore } from '../stores/languageStore';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export function Navbar() {
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useAuthStore();
  const { language, toggleLanguage } = useLanguageStore();
  const { t } = useTranslation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-gray-900 shadow-lg border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <div className="text-2xl font-bold text-blue-400">
              🏠 {t('nav.appTitle')}
            </div>
          </Link>

          {/* Right side */}
          <div className="flex items-center gap-4">
            {/* Language Switcher */}
            <button
              onClick={toggleLanguage}
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-800 rounded-md transition"
              title={language === 'en' ? 'Switch to Indonesian' : 'Beralih ke Bahasa Inggris'}
            >
              <span className="text-lg">{language === 'en' ? '🇮🇩' : '🇬🇧'}</span>
              <span>{language === 'en' ? 'ID' : 'EN'}</span>
            </button>

            {/* User info and logout - show if authenticated */}
            {isAuthenticated && (
              <div className="flex items-center gap-4">
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
          </div>
        </div>
      </div>
    </nav>
  );
}
