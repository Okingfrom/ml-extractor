/**
 * Logger utility for frontend development
 * Provides environment-based logging with proper formatting
 */

const isDev = process.env.NODE_ENV === 'development';

const logger = {
  info: (message, ...args) => {
    if (isDev) console.log(`ℹ️ ${message}`, ...args);
  },
  
  error: (message, ...args) => {
    if (isDev) console.error(`❌ ${message}`, ...args);
  },
  
  warn: (message, ...args) => {
    if (isDev) console.warn(`⚠️ ${message}`, ...args);
  },
  
  debug: (message, ...args) => {
    if (isDev) console.debug(`🔍 ${message}`, ...args);
  },
  
  success: (message, ...args) => {
    if (isDev) console.log(`✅ ${message}`, ...args);
  },
  
  request: (method, url) => {
    if (isDev) console.log(`🚀 ${method?.toUpperCase()} ${url}`);
  },
  
  response: (method, url, status) => {
    if (isDev) console.log(`✅ ${method?.toUpperCase()} ${url} - ${status}`);
  },
  
  requestError: (method, url, status) => {
    if (isDev) console.error(`❌ ${method?.toUpperCase()} ${url} - ${status}`);
  }
};

export default logger;
