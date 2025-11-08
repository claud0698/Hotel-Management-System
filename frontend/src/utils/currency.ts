/**
 * Currency Formatting Utilities
 * Formats numbers as Indonesian Rupiah (IDR) with proper separators
 */

/**
 * Format number as Indonesian Rupiah
 * Example: 500000 → "Rp 500.000"
 */
export const formatCurrency = (amount: number | string): string => {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;

  if (isNaN(num)) {
    return 'Rp 0';
  }

  return `Rp ${num.toLocaleString('id-ID')}`;
};

/**
 * Format number with thousands separator (no currency symbol)
 * Example: 500000 → "500.000"
 */
export const formatNumber = (amount: number | string): string => {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;

  if (isNaN(num)) {
    return '0';
  }

  return num.toLocaleString('id-ID');
};

/**
 * Parse currency input and return number
 * Example: "500.000" → 500000
 */
export const parseCurrency = (value: string): number => {
  // Remove "Rp " prefix if present
  const cleaned = value.replace(/^Rp\s?/, '').trim();
  // Replace dots with nothing (they're just separators)
  const normalized = cleaned.replace(/\./g, '');
  return parseInt(normalized, 10) || 0;
};

/**
 * Format currency for display with rounding
 * Useful for showing calculated values
 */
export const formatCurrencyDecimal = (amount: number | string, decimals: number = 0): string => {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;

  if (isNaN(num)) {
    return 'Rp 0';
  }

  const rounded = Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals);
  return `Rp ${rounded.toLocaleString('id-ID', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`;
};
