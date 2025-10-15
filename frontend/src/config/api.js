const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.MODE === 'production'
    ? 'https://decision-assistant-api.onrender.com'
    : 'http://localhost:8000');
export default API_BASE_URL;
