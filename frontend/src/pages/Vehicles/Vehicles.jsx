import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, InputNumber, Select, Space, message, Typography, Tag, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { vehicleAPI, userAPI } from '../../services/api';

const { Title } = Typography;

const Vehicles = () => {
  const [vehicles, setVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchVehicles();
    fetchDrivers();
  }, []);

  const fetchVehicles = async () => {
    try {
      const response = await vehicleAPI.getAll();
      setVehicles(response.data);
    } catch (error) {
      message.error('Không thể tải danh sách xe!');
    } finally {
      setLoading(false);
    }
  };

  const fetchDrivers = async () => {
    try {
      const response = await userAPI.getAll({ role: 'driver' });
      setDrivers(response.data);
    } catch (error) {
      console.error('Failed to fetch drivers');
    }
  };

  const handleAdd = () => {
    setEditingVehicle(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingVehicle(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await vehicleAPI.delete(id);
      message.success('Xóa xe thành công!');
      fetchVehicles();
    } catch (error) {
      message.error('Không thể xóa xe!');
    }
  };

  const handleSubmit = async (values) => {
    try {
      if (editingVehicle) {
        await vehicleAPI.update(editingVehicle.id, values);
        message.success('Cập nhật xe thành công!');
      } else {
        await vehicleAPI.create(values);
        message.success('Thêm xe thành công!');
      }
      setModalVisible(false);
      fetchVehicles();
    } catch (error) {
      message.error('Có lỗi xảy ra!');
    }
  };

  const columns = [
    {
      title: 'Mã xe',
      dataIndex: 'code',
      key: 'code',
      width: 150,
    },
    {
      title: 'Loại xe',
      dataIndex: 'vehicle_type',
      key: 'vehicle_type',
      render: (type) => {
        const labels = { truck: 'Xe tải', van: 'Xe van', motorcycle: 'Xe máy' };
        return labels[type] || type;
      },
    },
    {
      title: 'Hãng',
      dataIndex: 'brand',
      key: 'brand',
    },
    {
      title: 'Tải trọng (kg)',
      dataIndex: 'capacity',
      key: 'capacity',
      align: 'right',
    },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = { available: 'green', busy: 'blue', maintenance: 'orange', inactive: 'red' };
        const labels = { available: 'Sẵn sàng', busy: 'Đang chạy', maintenance: 'Bảo trì', inactive: 'Ngừng' };
        return <Tag color={colors[status]}>{labels[status]}</Tag>;
      },
    },
    {
      title: 'Thao tác',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button icon={<EditOutlined />} size="small" onClick={() => handleEdit(record)} />
          <Popconfirm title="Xác nhận xóa?" onConfirm={() => handleDelete(record.id)}>
            <Button icon={<DeleteOutlined />} size="small" danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={3}>Quản lý Phương tiện</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          Thêm xe
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={vehicles}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={editingVehicle ? 'Sửa xe' : 'Thêm xe mới'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="code" label="Mã xe" rules={[{ required: true }]}>
            <Input />
          </Form.Item>

          <Form.Item name="driver_id" label="Tài xế phụ trách">
            <Select placeholder="Chọn tài xế" allowClear>
              {drivers.map(d => (
                <Select.Option key={d.id} value={d.id}>
                  {d.full_name} ({d.username})
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Space style={{ width: '100%' }} size="large">
            <Form.Item name="vehicle_type" label="Loại xe">
              <Select style={{ width: 200 }}>
                <Select.Option value="truck">Xe tải</Select.Option>
                <Select.Option value="van">Xe van</Select.Option>
                <Select.Option value="motorcycle">Xe máy</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item name="brand" label="Hãng xe">
              <Input style={{ width: 200 }} />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="large">
            <Form.Item name="capacity" label="Tải trọng (kg)">
              <InputNumber style={{ width: 200 }} min={0} />
            </Form.Item>
            <Form.Item name="volume_capacity" label="Thể tích (m³)">
              <InputNumber style={{ width: 200 }} min={0} step={0.1} />
            </Form.Item>
          </Space>
          <Space style={{ width: '100%' }} size="large">
            <Form.Item name="fuel_type" label="Nhiên liệu">
              <Select style={{ width: 200 }}>
                <Select.Option value="diesel">Diesel</Select.Option>
                <Select.Option value="gasoline">Xăng</Select.Option>
                <Select.Option value="electric">Điện</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item name="status" label="Trạng thái">
              <Select style={{ width: 200 }}>
                <Select.Option value="available">Sẵn sàng</Select.Option>
                <Select.Option value="busy">Đang chạy</Select.Option>
                <Select.Option value="maintenance">Bảo trì</Select.Option>
                <Select.Option value="inactive">Ngừng</Select.Option>
              </Select>
            </Form.Item>
          </Space>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingVehicle ? 'Cập nhật' : 'Thêm mới'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>Hủy</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Vehicles;
