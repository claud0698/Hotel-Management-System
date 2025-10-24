/**
 * Sidebar Navigation Component
 */

import { Link, useLocation } from 'react-router-dom';

const menuItems = [
  { label: 'Dashboard', icon: '📊', path: '/' },
  { label: 'Rooms', icon: '🏘️', path: '/rooms' },
  { label: 'Tenants', icon: '👥', path: '/tenants' },
  { label: 'Payments', icon: '💰', path: '/payments' },
  { label: 'Expenses', icon: '💸', path: '/expenses' },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 bg-gray-900 text-white h-screen sticky top-0 overflow-y-auto">
      <div className="p-6">
        <h2 className="text-lg font-bold mb-8">Management</h2>

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
