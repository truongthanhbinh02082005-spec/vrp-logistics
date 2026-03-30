import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, InputNumber, Space, message, Typography, Tag, Row, Col, Card, Progress, Statistic } from 'antd';
import { PlusOutlined, EditOutlined, EnvironmentOutlined, PieChartOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { warehouseAPI } from '../../services/api';
import { geocodeAddress } from '../../services/utils';

const { Title, Text } = Typography;

const Warehouses = () => {
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingWarehouse, setEditingWarehouse] = useState(null);
  const [selectedWarehouse, setSelectedWarehouse] = useState(null);
  const [geocoding, setGeocoding] = useState(false);
  const [form] = Form.useForm();

  // Stats state fetched from API
  const [warehouseStats, setWarehouseStats] = useState({
    shelves: {
      'A': { total: 100, used: 0, percent: 0 },
      'B': { total: 100, used: 0, percent: 0 },
      'C': { total: 100, used: 0, percent: 0 },
    },
    summary: { total_capacity_slots: 0, total_used_slots: 0, occupancy_rate: 0 }
  });

  useEffect(() => {
    fetchWarehouses();
  }, []);

  const fetchWarehouses = async () => {
    try {
      const response = await warehouseAPI.getAll();
      setWarehouses(response.data);
    } catch (error) {
      // Mock data
      setWarehouses([
        { id: '1', code: 'KHO-A', name: 'Kho Quận 1 (Demo)', address: 'Q1, HCM', lat: 10.776, lng: 106.700, area: 500, volume: 1000 },
        { id: '2', code: 'KHO-B', name: 'Kho Thủ Đức (Demo)', address: 'Thủ Đức, HCM', lat: 10.850, lng: 106.760, area: 800, volume: 2000 },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async (warehouseId) => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      const res = await fetch(`/api/orders/capacity/${warehouseId}/`, { headers });
      if (res.ok) {
        const data = await res.json();
        setWarehouseStats(data);
      } else {
        message.warning("Chưa có số liệu thống kê cho kho này (hoặc API lỗi).");
      }
    } catch (e) {
      console.error("Fetch Stats Error:", e);
    }
  };

  const handleRowClick = (record) => {
    setSelectedWarehouse(record);
    fetchStats(record.id);
  };

  const handleAdd = () => {
    setEditingWarehouse(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingWarehouse(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleSubmit = async (values) => {
    try {
      if (editingWarehouse) {
        // await warehouseAPI.update(editingWarehouse.id, values);
        message.success('Cập nhật thành công');
      } else {
        // await warehouseAPI.create(values);
        message.success('Thêm mới thành công');
      }
      setModalVisible(false);
      fetchWarehouses();
    } catch (error) {
      setModalVisible(false);
    }
  };

  const handleGeocode = async () => {
    // ... same logic
    message.info("Tính năng đang bảo trì trong demo.");
  };

  const columns = [
    { title: 'Mã kho', dataIndex: 'code', key: 'code', width: 100 },
    { title: 'Tên kho', dataIndex: 'name', key: 'name' },
    { title: 'Địa chỉ', dataIndex: 'address', key: 'address' },
    {
      title: 'Tọa độ GPS',
      key: 'gps',
      render: (_, r) => r.lat ? <Tag color="blue"><EnvironmentOutlined /> {r.lat}, {r.lng}</Tag> : <Tag>N/A</Tag>
    },
    {
      title: 'Thao tác',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button icon={<EditOutlined />} size="small" onClick={(e) => { e.stopPropagation(); handleEdit(record); }} />
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={3}>Quản lý Kho hàng & Phân bổ</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>Thêm kho</Button>
      </div>

      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Table
            columns={columns}
            dataSource={warehouses}
            rowKey="id"
            loading={loading}
            onRow={(record) => ({
              onClick: () => handleRowClick(record),
              style: { cursor: 'pointer', background: selectedWarehouse?.id === record.id ? '#e6f7ff' : '' }
            })}
            pagination={{ pageSize: 5 }}
            title={() => <Text strong type="secondary"><CheckCircleOutlined /> Click vào dòng để xem chi tiết thống kê</Text>}
          />
        </Col>

        <Col span={24}>
          {selectedWarehouse ? (
            <Card title={selectedWarehouse.name} extra={<Tag color="green">Active</Tag>}>

              <Row gutter={16} style={{ marginBottom: 24, textAlign: 'center' }}>
                <Col span={8}>
                  <Statistic title="Tổng Sức Chứa" value={warehouseStats.total_volume || 0} suffix="m³" />
                </Col>
                <Col span={8}>
                  <Statistic title="Đã Dùng" value={warehouseStats.used_volume || 0} suffix="m³" styles={{ content: { color: '#1890ff' } }} />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Tỷ lệ lấp đầy"
                    value={warehouseStats.occupancy_rate || 0}
                    suffix="%"
                    styles={{ content: { color: (warehouseStats.occupancy_rate || 0) > 90 ? '#cf1322' : '#3f8600' } }}
                  />
                </Col>
              </Row>

              <div style={{ marginTop: 16 }}>
                <Text strong>Thông tin sức chứa:</Text>
                <div style={{ marginTop: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Text>Còn trống:</Text>
                    <Text strong style={{ color: '#52c41a' }}>{(warehouseStats.remaining_volume || 0).toFixed(2)} m³</Text>
                  </div>
                  <Progress
                    percent={warehouseStats.occupancy_rate || 0}
                    strokeColor={(warehouseStats.occupancy_rate || 0) > 90 ? '#ff4d4f' : (warehouseStats.occupancy_rate || 0) > 70 ? '#faad14' : '#52c41a'}
                    size="default"
                    status="active"
                  />
                </div>
              </div>
            </Card>
          ) : (
            <Card style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ textAlign: 'center', color: '#999' }}>
                <PieChartOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                <p>Chọn một kho để xem báo cáo thống kê chi tiết</p>
              </div>
            </Card>
          )}
        </Col>
      </Row>

      {/* Warehouse CRUD Modal */}
      <Modal
        title={editingWarehouse ? 'Sửa kho' : 'Thêm kho mới'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="code" label="Mã kho" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="name" label="Tên kho" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="address" label="Địa chỉ" rules={[{ required: true }]}><Input /></Form.Item>
          <Row gutter={16}>
            <Col span={12}><Form.Item name="lat" label="Latitude"><InputNumber style={{ width: '100%' }} /></Form.Item></Col>
            <Col span={12}><Form.Item name="lng" label="Longitude"><InputNumber style={{ width: '100%' }} /></Form.Item></Col>
          </Row>
          <Form.Item><Button type="primary" htmlType="submit">Lưu lại</Button></Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Warehouses;
