import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, Space, message, Typography, Tag, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, UserOutlined, TruckOutlined } from '@ant-design/icons';
import { userAPI, vehicleAPI } from '../../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

const Drivers = () => {
    const [drivers, setDrivers] = useState([]);
    const [vehicles, setVehicles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modalVisible, setModalVisible] = useState(false);
    const [editingDriver, setEditingDriver] = useState(null);
    const [form] = Form.useForm();

    useEffect(() => {
        fetchDrivers();
        fetchVehicles();
    }, []);

    const fetchDrivers = async () => {
        try {
            const response = await userAPI.getDrivers();
            setDrivers(response.data);
        } catch (error) {
            console.error(error);
            message.error('Không thể tải danh sách tài xế!');
        } finally {
            setLoading(false);
        }
    };

    const fetchVehicles = async () => {
        try {
            const response = await vehicleAPI.getAll();
            setVehicles(response.data);
        } catch (error) {
            console.error('Failed to fetch vehicles');
        }
    };

    const handleAdd = () => {
        setEditingDriver(null);
        form.resetFields();
        setModalVisible(true);
    };

    const handleEdit = (record) => {
        setEditingDriver(record);
        form.setFieldsValue({
            ...record,
            vehicle_id: record.current_vehicle_id // Bind current vehicle
        });
        setModalVisible(true);
    };

    const handleDelete = async (id) => {
        try {
            await userAPI.delete(id);
            message.success('Đã xóa tài xế thành công!');
            fetchDrivers();
        } catch (error) {
            message.error(error.response?.data?.error || 'Có lỗi xảy ra!');
        }
    };

    const handleSubmit = async (values) => {
        try {
            values.role = 'driver'; // Force role driver

            if (editingDriver) {
                await userAPI.update(editingDriver.id, values);
                message.success('Cập nhật thông tin thành công!');
            } else {
                await userAPI.create(values);
                message.success('Tạo tài xế mới thành công!');
            }
            setModalVisible(false);
            fetchDrivers();
        } catch (error) {
            message.error(error.response?.data?.error || 'Có lỗi xảy ra!');
        }
    };

    const columns = [
        {
            title: 'Tài khoản',
            dataIndex: 'username',
            key: 'username',
            render: (text) => <b>{text}</b>,
        },
        {
            title: 'Họ tên',
            dataIndex: 'full_name',
            key: 'full_name',
        },
        {
            title: 'Số điện thoại',
            dataIndex: 'phone',
            key: 'phone',
        },
        {
            title: 'Trạng thái',
            dataIndex: 'status',
            key: 'status',
            render: (status) => (
                <Tag color={status === 'inactive' ? 'red' : 'green'}>
                    {status === 'active' || !status ? 'Hoạt động' : 'Đã khóa'}
                </Tag>
            )
        },
        {
            title: 'Xe phụ trách',
            dataIndex: 'current_vehicle',
            key: 'current_vehicle',
            render: (text) => text ? <Tag color="blue">{text}</Tag> : ''
        },
        {
            title: 'Thao tác',
            key: 'actions',
            render: (_, record) => (
                <Space>
                    <Button icon={<EditOutlined />} size="small" onClick={() => handleEdit(record)} />
                    <Popconfirm title="Bạn có chắc muốn XÓA VĨNH VIỄN tài xế này?" onConfirm={() => handleDelete(record.id)}>
                        <Button icon={<DeleteOutlined />} size="small" danger />
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
                <Title level={3}>Quản lý Tài xế</Title>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                    Thêm tài xế
                </Button>
            </div>

            <Table
                columns={columns}
                dataSource={drivers}
                rowKey="id"
                loading={loading}
                pagination={{ pageSize: 10 }}
            />

            <Modal
                title={editingDriver ? 'Cập nhật thông tin' : 'Thêm tài xế mới'}
                open={modalVisible}
                onCancel={() => setModalVisible(false)}
                footer={null}
            >
                <Form form={form} layout="vertical" onFinish={handleSubmit}>
                    {!editingDriver && (
                        <Form.Item
                            name="username"
                            label="Tên đăng nhập"
                            rules={[{ required: true, message: 'Vui lòng nhập username' }]}
                        >
                            <Input prefix={<UserOutlined />} />
                        </Form.Item>
                    )}

                    <Form.Item
                        name="full_name"
                        label="Họ và tên"
                        rules={[{ required: true, message: 'Vui lòng nhập họ tên' }]}
                    >
                        <Input />
                    </Form.Item>

                    <Form.Item name="vehicle_id" label="Gán xe phụ trách (Tùy chọn)">
                        <Select allowClear placeholder="Chọn xe để giao cho tài xế này">
                            {vehicles.map(v => (
                                <Option key={v.id} value={v.id}>
                                    {v.code} {v.is_assigned ? '(Đã có TX)' : ''}
                                </Option>
                            ))}
                        </Select>
                    </Form.Item>

                    <Form.Item
                        name="phone"
                        label="Số điện thoại"
                        rules={[{ required: true, message: 'Vui lòng nhập SĐT' }]}
                    >
                        <Input />
                    </Form.Item>

                    <Form.Item
                        name="email"
                        label="Email"
                        rules={[{ type: 'email' }]}
                    >
                        <Input />
                    </Form.Item>

                    {!editingDriver && (
                        <Form.Item
                            name="password"
                            label="Mật khẩu"
                            rules={[{ required: true, message: 'Vui lòng nhập mật khẩu' }]}
                        >
                            <Input.Password />
                        </Form.Item>
                    )}

                    {editingDriver && (
                        <Form.Item name="status" label="Trạng thái">
                            <Select>
                                <Option value="active">Hoạt động</Option>
                                <Option value="inactive">Khóa</Option>
                            </Select>
                        </Form.Item>
                    )}

                    {editingDriver && (
                        <Form.Item name="password" label="Đặt lại mật khẩu (để trống nếu không đổi)">
                            <Input.Password placeholder="Mật khẩu mới" />
                        </Form.Item>
                    )}

                    <Form.Item>
                        <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                            <Button onClick={() => setModalVisible(false)}>Hủy</Button>
                            <Button type="primary" htmlType="submit">
                                {editingDriver ? 'Cập nhật' : 'Tạo mới'}
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default Drivers;
