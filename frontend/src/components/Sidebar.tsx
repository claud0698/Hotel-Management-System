/**
 * Sidebar Navigation Component
 */

import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export function Sidebar() {
  const location = useLocation();
  const { t } = useTranslation();

  const menuItems = [
    { label: t('nav.dashboard'), icon: '📊', path: '/' },
    { label: t('nav.rooms'), icon: '🏘️', path: '/rooms' },
    { label: t('nav.tenants'), icon: '👥', path: '/tenants' },
    { label: t('nav.payments'), icon: '💰', path: '/payments' },
    { label: t('nav.expenses'), icon: '💸', path: '/expenses' },
  ];

  return (
    <aside className="w-64 bg-gray-900 text-white h-screen sticky top-0 overflow-y-auto">
      <div className="p-6">
        <h2 className="text-lg font-bold mb-8">{t('nav.management')}</h2>

        <nav className="space-y-2">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
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
  );
}
