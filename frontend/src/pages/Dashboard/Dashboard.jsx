import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Typography } from 'antd';
import {
  ShoppingCartOutlined,
  CarOutlined,
  ShopOutlined,
  NodeIndexOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { reportAPI } from '../../services/api';
import Loading from '../../components/Common/Loading';

const { Title } = Typography;

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await reportAPI.getDashboard();
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Loading />;

  return (
    <div>
      <Title level={3} className="page-header">Dashboard</Title>
      
      <Row gutter={[16, 16]}>
        {/* Orders Stats */}
        <Col xs={24} sm={12} lg={6}>
          <Card className="dashboard-card">
            <Statistic
              title="Tổng đơn hàng"
              value={data?.orders?.total || 0}
              prefix={<ShoppingCartOutlined style={{ color: '#1890ff' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="dashboard-card">
            <Statistic
              title="Đơn chờ xử lý"
              value={data?.orders?.pending || 0}
              prefix={<ClockCircleOutlined style={{ color: '#faad14' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="dashboard-card">
            <Statistic
              title="Đơn đã giao"
              value={data?.orders?.completed || 0}
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="dashboard-card">
            <Statistic
              title="Đơn hôm nay"
              value={data?.orders?.today || 0}
              prefix={<ShoppingCartOutlined style={{ color: '#722ed1' }} />}
            />
          </Card>
        </Col>

        {/* Vehicles Stats */}
        <Col xs={24} sm={12} lg={6}>
          <Card className="dashboard-card">
            <Statistic
              title="Tổng xe"
              value={data?.vehicles?.total || 0}
              prefix={<CarOutlined style={{ color: '#1890ff' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="dashboard-card">
            <Statistic
              title="Xe sẵn sàng"
              value={data?.vehicles?.available || 0}
              prefix={<CarOutlined style={{ color: '#52c41a' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="dashboard-card">
            <Statistic
              title="Tổng kho"
              value={data?.warehouses?.total || 0}
              prefix={<ShopOutlined style={{ color: '#eb2f96' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="dashboard-card">
            <Statistic
              title="Lộ trình hoạt động"
              value={data?.routes?.active || 0}
              prefix={<NodeIndexOutlined style={{ color: '#fa541c' }} />}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
