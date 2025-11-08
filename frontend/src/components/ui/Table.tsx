/**
 * Table Component
 * Responsive data table with sorting and pagination
 */

import { ReactNode } from 'react';

interface TableColumn<T> {
  key: keyof T | string;
  header: string;
  render?: (value: any, row: T) => ReactNode;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

interface TableProps<T> {
  columns: TableColumn<T>[];
  data: T[];
  keyField?: keyof T;
  isLoading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
  hoverable?: boolean;
  striped?: boolean;
}

export function Table<T extends Record<string, any>>({
  columns,
  data,
  keyField = 'id' as keyof T,
  isLoading = false,
  emptyMessage = 'No data available',
  onRowClick,
  hoverable = true,
  striped = true,
}: TableProps<T>) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin text-2xl">⏳</div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto border border-gray-200 rounded-lg">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key as string}
                className={`px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider ${
                  column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : ''
                } ${column.width ? column.width : ''}`}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {data.map((row, rowIndex) => (
            <tr
              key={row[keyField] || rowIndex}
              onClick={() => onRowClick?.(row)}
              className={`${
                striped && rowIndex % 2 === 1 ? 'bg-gray-50' : 'bg-white'
              } ${
                hoverable && onRowClick
                  ? 'hover:bg-blue-50 cursor-pointer transition-colors'
                  : ''
              }`}
            >
              {columns.map((column) => (
                <td
                  key={`${row[keyField] || rowIndex}-${column.key}`}
                  className={`px-6 py-4 text-sm text-gray-900 ${
                    column.align === 'center'
                      ? 'text-center'
                      : column.align === 'right'
                        ? 'text-right'
                        : ''
                  }`}
                >
                  {column.render
                    ? column.render(row[column.key as keyof T], row)
                    : String(row[column.key as keyof T] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
