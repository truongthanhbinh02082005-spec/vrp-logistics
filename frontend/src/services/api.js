import axios from 'axios';

const API_URL = '/api/';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const userAPI = {
  getAll: () => api.get('auth/users/'),
  getDrivers: () => api.get('auth/drivers/'),
  create: (data) => api.post('auth/register/', data),
  update: (id, data) => api.put(`auth/users/${id}/`, data),
  delete: (id) => api.delete(`auth/users/${id}/`),
};

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Debug: log API request info
    console.log('API Request:', config.method?.toUpperCase(), config.url, token ? '(with token)' : '(no token)');
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Chỉ redirect nếu không phải đang ở trang login
      if (!window.location.pathname.includes('/login')) {
        console.error('401 Unauthorized - redirecting to login');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (data) => api.post('auth/login/', data),
  register: (data) => api.post('auth/register/', data),
  profile: () => api.get('auth/profile/'),
  logout: (data) => api.post('auth/logout/', data),
  getDrivers: () => api.get('auth/drivers/'),
};

// Warehouse APIs
export const warehouseAPI = {
  getAll: () => api.get('warehouses/'),
  getById: (id) => api.get(`warehouses/${id}/`),
  create: (data) => api.post('warehouses/', data),
  update: (id, data) => api.put(`warehouses/${id}/`, data),
  delete: (id) => api.delete(`warehouses/${id}/`),
};

// Vehicle APIs
export const vehicleAPI = {
  getAll: () => api.get('vehicles/'),
  getById: (id) => api.get(`vehicles/${id}/`),
  create: (data) => api.post('vehicles/', data),
  update: (id, data) => api.put(`vehicles/${id}/`, data),
  delete: (id) => api.delete(`vehicles/${id}/`),
  getAvailable: () => api.get('vehicles/available/'),
};

// Order APIs
export const orderAPI = {
  getAll: (params) => api.get('orders/', { params }),
  getById: (id) => api.get(`orders/${id}/`),
  create: (data) => api.post('orders/', data),
  update: (id, data) => api.put(`orders/${id}/`, data),
  delete: (id) => api.delete(`orders/${id}/`),
  deleteAll: () => api.delete('orders/delete-all/'),
  getPending: () => api.get('orders/pending/'),
  updateStatus: (id, data) => api.put(`orders/${id}/status/`, data),
  assign: (id, data) => api.put(`orders/${id}/assign/`, data),
  bulkImport: (data) => api.post('orders/bulk/', data),
  checkCapacity: (warehouseId) => api.get(`orders/capacity/${warehouseId}/`),
};

// Transport/Route APIs
export const routeAPI = {
  getAll: (params) => api.get('transport/routes/', { params }),
  getById: (id) => api.get(`transport/routes/${id}/`),
  create: (data) => api.post('transport/routes/', data),
  update: (id, data) => api.put(`transport/routes/${id}/`, data),
  delete: (id) => api.delete(`transport/routes/${id}/`),
  deleteAll: () => api.delete('transport/routes/delete-all/'),
  start: (id) => api.post(`transport/routes/${id}/start/`),
  complete: (id) => api.post(`transport/routes/${id}/complete/`),
  optimize: (data) => api.post('transport/optimize/', data),
  getDistanceMatrix: (data) => api.post('transport/distance-matrix/', data),
};

// Report APIs
export const reportAPI = {
  getDashboard: () => api.get('reports/dashboard/'),
  getOrderReport: () => api.get('reports/orders/'),
  getVehicleReport: () => api.get('reports/vehicles/'),
  getRouteReport: () => api.get('reports/routes/'),
  getPerformance: () => api.get('reports/performance/'),
};

// Transaction APIs
export const transactionAPI = {
  getAll: () => api.get('transactions/'),
  getById: (id) => api.get(`transactions/${id}/`),
  create: (data) => api.post('transactions/', data),
  confirm: (id) => api.put(`transactions/${id}/confirm/`),
  getPending: () => api.get('transactions/pending/'),
};

// Driver APIs
export const driverAPI = {
  getCurrentOrder: () => api.get('driver/current-order/'),
  getOrders: () => api.get('driver/orders/'),
  confirmDelivery: (data) => api.post('driver/confirm-delivery/', data),
};

// Benchmark APIs
export const benchmarkAPI = {
  listInstances: () => api.get('/benchmark/instances/'),
  runInstance: (data) => api.post('/benchmark/run/', data),
  runAll: (data) => api.post('/benchmark/run-all/', data),
};

export default api;
