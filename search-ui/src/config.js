export const REACT_APP_API_BASE_URL = localStorage.getItem('api_base_url') || process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001';
export const SECRET_KEY_FOR_API = process.env.REACT_APP_SECRET_KEY_FOR_API;