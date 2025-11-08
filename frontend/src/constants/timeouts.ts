/**
 * Timeout Constants
 * Centralized timeout values for consistent UX across the app
 */

export const TIMEOUTS = {
  // Alert/Notification timeouts
  ALERT_ERROR: 30000,      // 30 seconds for error alerts
  ALERT_SUCCESS: 5000,     // 5 seconds for success messages
  ALERT_WARNING: 10000,    // 10 seconds for warnings
  ALERT_INFO: 8000,        // 8 seconds for info messages

  // API timeouts
  API_REQUEST: 30000,      // 30 seconds for API requests
  API_SLOW_THRESHOLD: 5000, // Warn if API takes longer than 5s

  // Debounce/Throttle
  SEARCH_DEBOUNCE: 300,    // 300ms for search input debounce
  FORM_DEBOUNCE: 500,      // 500ms for form field debounce

  // Loading states
  MIN_LOADING_TIME: 300,   // Minimum loading time to avoid flickering
  SKELETON_FADE: 200,      // Fade animation duration

  // General
  SHORT_DELAY: 200,        // Quick transitions
  MEDIUM_DELAY: 500,       // Standard transitions
  LONG_DELAY: 1000,        // Slow transitions
} as const;

export default TIMEOUTS;
