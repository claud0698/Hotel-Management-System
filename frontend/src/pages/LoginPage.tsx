/**
 * Login Page
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useLanguageStore } from '../stores/languageStore';
import { useTranslation } from 'react-i18next';
import { Alert } from '../components/ui';

export function LoginPage() {
  const navigate = useNavigate();
  const { login, isLoading, error, clearError } = useAuthStore();
  const { language, toggleLanguage } = useLanguageStore();
  const { t } = useTranslation();
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [showError, setShowError] = useState(false);

  useEffect(() => {
    // Show error for 5 seconds when it changes
    if (error) {
      setShowError(true);
      const timer = setTimeout(() => {
        setShowError(false);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setShowError(false);

    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      // Error is already stored in the store
      setShowError(true);
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center">
      <div className="w-full max-w-md">
        {/* Language Switcher */}
        <div className="flex justify-end mb-4">
          <button
            onClick={toggleLanguage}
            className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition"
          >
            <span className="text-lg">{language === 'en' ? '🇮🇩' : '🇬🇧'}</span>
            <span>{language === 'en' ? 'ID' : 'EN'}</span>
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="text-5xl mb-2">🏠</div>
            <h1 className="text-3xl font-bold text-gray-900">{t('nav.appTitle')}</h1>
            <p className="text-gray-600 mt-2">{t('auth.loginTitle')}</p>
          </div>

          {/* Error Message - Enhanced Alert */}
          {showError && error && (
            <div className="mb-4">
              <Alert
                type="error"
                title="Login Failed"
                message={error}
                onClose={() => {
                  setShowError(false);
                  clearError();
                }}
                dismissible
              />
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('auth.username')}
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder={t('auth.enterUsername')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
              <p className="text-xs text-gray-500 mt-1">Demo: admin</p>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('auth.password')}
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t('auth.enterPassword')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
              <p className="text-xs text-gray-500 mt-1">Demo: admin123</p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition"
            >
              {isLoading ? t('auth.loggingIn') : t('auth.loginButton')}
            </button>
          </form>

          {/* Info Box */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-700">
              <strong>Demo Mode:</strong> Using hardcoded credentials for development.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
