import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Checkbox, message, Typography, ConfigProvider } from 'antd';
import { 
  UserOutlined, 
  LockOutlined, 
  CarOutlined, 
  TeamOutlined 
} from '@ant-design/icons';
import { authAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const { Title, Text } = Typography;

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [role, setRole] = useState('admin'); // 'admin' | 'driver'
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form] = Form.useForm();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await authAPI.login(values);
      const { access, refresh, user } = response.data;

      if (role === 'admin' && user.role === 'driver') {
        throw new Error('Tài khoản này không có quyền quản trị!');
      }
      if (role === 'driver' && user.role !== 'driver') {
        throw new Error('Vui lòng sử dụng tài khoản tài xế!');
      }

      login(user, { access, refresh });
      message.success('Đăng nhập thành công!');
      
      setTimeout(() => {
        if (role === 'driver') {
          navigate('/driver');
        } else {
          navigate('/routes');
        }
      }, 500);
    } catch (error) {
      message.error(error.message || error.response?.data?.error || 'Đăng nhập thất bại!');
    } finally {
      setLoading(false);
    }
  };

  const primaryBlue = '#2563eb'; // More vibrant blue
  const buttonBlue = '#1d4ed8'; // Bright royal blue
  const headerBlue = 'linear-gradient(135deg, #2563eb 0%, #dbeafe 110%)'; // Bright highlight at bottom right

  const handleRoleChange = (newRole) => {
    if (newRole === role) return;
    setRole(newRole);
  };

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: primaryBlue,
          borderRadius: 8,
          fontFamily: "'Inter', sans-serif",
        },
      }}
    >
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#f8fafc',
        padding: '24px'
      }}>
        
        {/* Main Card - Exact Image Layout */}
        <div style={{
          width: '100%',
          maxWidth: 440,
          background: '#ffffff',
          borderRadius: '16px',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.08)',
          overflow: 'hidden',
          border: '1px solid #e2e8f0'
        }}>
          
          {/* Blue Header Section */}
          <div style={{
            background: headerBlue,
            padding: '40px 32px',
            textAlign: 'center',
            color: '#ffffff'
          }}>
            {/* Logo Image Area - No white background as requested */}
            <div style={{
              width: 90,
              height: 90,
              margin: '0 auto 24px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid #ffffff',
              borderRadius: '50%',
              padding: '2px',
              boxShadow: '0 0 15px rgba(255, 255, 255, 0.1)'
            }}>
              <img 
                src="/logo2.png" 
                alt="Brand Logo" 
                style={{ width: '100%', height: '100%', objectFit: 'contain' }} 
              />
            </div>

            <Title level={2} style={{ margin: 0, fontWeight: 700, color: '#ffffff', fontSize: 24 }}>
              Hệ Thống Định Tuyến Vận Tải
            </Title>
            <Text style={{ color: '#ffffff', fontSize: 18, marginTop: 12, display: 'block', fontWeight: 800, letterSpacing: '1px' }}>
              VRP LOGISTIC
            </Text>
          </div>

          {/* Form Body Area */}
          <div style={{ padding: '32px' }}>
            
            <div style={{ textAlign: 'center', marginBottom: 28 }}>
              <Title level={4} style={{ color: '#111827', margin: 0, fontWeight: 600 }}>
                Đăng nhập hệ thống
              </Title>
            </div>

            {/* Role Switcher (Simple Tabs) */}
            <div style={{ 
              display: 'flex', 
              background: '#f1f5f9', 
              padding: '4px',
              borderRadius: '10px',
              marginBottom: 32
            }}>
              <div 
                onClick={() => handleRoleChange('admin')}
                style={{
                  flex: 1,
                  padding: '10px',
                  textAlign: 'center',
                  cursor: 'pointer',
                  borderRadius: '8px',
                  fontWeight: 600,
                  fontSize: '13px',
                  transition: 'all 0.2s',
                  background: role === 'admin' ? '#ffffff' : 'transparent',
                  color: role === 'admin' ? primaryBlue : '#64748b',
                  boxShadow: role === 'admin' ? '0 2px 6px rgba(0,0,0,0.06)' : 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                <TeamOutlined /> QUẢN TRỊ
              </div>
              <div 
                onClick={() => handleRoleChange('driver')}
                style={{
                  flex: 1,
                  padding: '10px',
                  textAlign: 'center',
                  cursor: 'pointer',
                  borderRadius: '8px',
                  fontWeight: 600,
                  fontSize: '13px',
                  transition: 'all 0.2s',
                  background: role === 'driver' ? '#ffffff' : 'transparent',
                  color: role === 'driver' ? primaryBlue : '#64748b',
                  boxShadow: role === 'driver' ? '0 2px 6px rgba(0,0,0,0.06)' : 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                <CarOutlined /> TÀI XẾ
              </div>
            </div>

            <Form form={form} layout="vertical" onFinish={onFinish} requiredMark={false}>
              <Form.Item 
                label={<span style={{ fontWeight: 600, color: '#374151' }}>Tên đăng nhập</span>}
                name="username" 
                rules={[{ required: true, message: 'Vui lòng nhập tên đăng nhập!' }]}
              >
                <Input 
                  placeholder="Nhập tên đăng nhập" 
                  size="large"
                  style={{ height: 48, borderRadius: 10, border: '1px solid #d1d5db' }}
                />
              </Form.Item>

              <Form.Item 
                label={<span style={{ fontWeight: 600, color: '#374151' }}>Mật khẩu</span>}
                name="password" 
                rules={[{ required: true, message: 'Vui lòng nhập mật khẩu!' }]}
              >
                <Input.Password 
                  placeholder="Nhập mật khẩu" 
                  size="large"
                  style={{ height: 48, borderRadius: 10, border: '1px solid #d1d5db' }}
                />
              </Form.Item>

              <div style={{ marginBottom: 12 }}></div>

              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading} 
                block 
                size="large"
                style={{ 
                  height: 52, 
                  fontWeight: 700, 
                  fontSize: 16,
                  background: buttonBlue,
                  borderColor: buttonBlue,
                  borderRadius: 10,
                  boxShadow: '0 4px 12px rgba(30, 58, 138, 0.2)'
                }}
              >
                {role === 'admin' ? 'Đăng nhập Quản Trị Viên' : 'Đăng nhập Tài Xế'}
              </Button>
            </Form>
          </div>
        </div>

        {/* Footer */}
        <div style={{ marginTop: 32, opacity: 0.5 }}>
          <Text style={{ fontSize: 11, color: '#94a3b8' }}>© 2024 VRP Distribution Management Solution</Text>
        </div>
      </div>
    </ConfigProvider>
  );
};

export default Login;
