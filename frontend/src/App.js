import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import viVN from 'antd/locale/vi_VN';
import { AuthProvider, useAuth } from './context/AuthContext';
import MainLayout from './components/Layout/MainLayout';
import Login from './pages/Login/Login.jsx';
// Dashboard removed
import Warehouses from './pages/Warehouses/Warehouses.jsx';
import Vehicles from './pages/Vehicles/Vehicles.jsx';
import Drivers from './pages/Drivers/Drivers.jsx';
import Orders from './pages/Orders/Orders.jsx';
import RoutesPage from './pages/Routes/Routes.jsx';
import Reports from './pages/Reports/Reports.jsx';
import TransactionHistory from './pages/TransactionHistory/TransactionHistory.jsx';
import BenchmarkLab from './pages/Benchmark/BenchmarkLab.jsx';
import DriverDashboard from './pages/Driver/DriverDashboard.jsx';
import './App.css';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>Loading...</div>;
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
};

const AppRoutes = () => {
  const { user } = useAuth();

  // Driver gets their own interface
  if (user?.role === 'driver') {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/driver" element={
          <PrivateRoute>
            <DriverDashboard />
          </PrivateRoute>
        } />
        <Route path="*" element={<Navigate to="/driver" replace />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={
        <PrivateRoute>
          <MainLayout />
        </PrivateRoute>
      }>
        <Route index element={<Navigate to="/routes" replace />} />
        <Route path="warehouses" element={<Warehouses />} />
        <Route path="benchmark" element={<BenchmarkLab />} />
        <Route path="vehicles" element={<Vehicles />} />
        <Route path="drivers" element={<Drivers />} />
        <Route path="orders" element={<Orders />} />
        <Route path="routes" element={<RoutesPage />} />
        <Route path="reports" element={<Reports />} />
        <Route path="transactions" element={<TransactionHistory />} />
      </Route>
      <Route path="/driver" element={
        <PrivateRoute>
          <DriverDashboard />
        </PrivateRoute>
      } />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

function App() {
  return (
    <ConfigProvider locale={viVN}>
      <AuthProvider>
        <Router>
          <AppRoutes />
        </Router>
      </AuthProvider>
    </ConfigProvider>
  );
}

export default App;
