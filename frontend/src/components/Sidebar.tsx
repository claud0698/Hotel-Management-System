/**
 * Sidebar Navigation Component
 */

import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useUIStore } from '../stores/uiStore';

export function Sidebar() {
  const location = useLocation();
  const { t } = useTranslation();
  const { isSidebarOpen, closeSidebar } = useUIStore();

  const menuItems = [
    { label: t('nav.dashboard'), icon: '📊', path: '/' },
    { label: t('nav.rooms'), icon: '🏘️', path: '/rooms' },
    { label: 'Reservations', icon: '📅', path: '/reservations' },
    { label: 'Guests', icon: '👥', path: '/guests' },
    { label: t('nav.payments'), icon: '💰', path: '/payments' },
    { label: t('nav.expenses'), icon: '💸', path: '/expenses' },
    { label: t('nav.users'), icon: '👤', path: '/users' },
  ];

  const handleNavigation = () => {
    // Close sidebar on mobile after navigation
    if (window.innerWidth < 768) {
      closeSidebar();
    }
  };

  return (
    <>
      {/* Mobile overlay backdrop */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 md:hidden z-40"
          onClick={closeSidebar}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed md:static top-16 left-0 h-[calc(100vh-4rem)] w-64 bg-gray-900 text-white overflow-y-auto transition-transform duration-300 ease-in-out z-50 md:z-auto ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="p-6">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-lg font-bold">{t('nav.management')}</h2>
            {/* Close button visible on mobile */}
            <button
              onClick={closeSidebar}
              className="md:hidden text-gray-400 hover:text-gray-200"
              aria-label="Close sidebar"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <nav className="space-y-2">
            {menuItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={handleNavigation}
                className={`flex items-center gap-3 px-4 py-3 rounded-md transition ${
                  location.pathname === item.path
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800'
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </Link>
            ))}
          </nav>
        </div>
      </aside>
    </>
  );
}
