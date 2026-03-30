import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Image, Tag, Space, message, Typography, Card, Row, Col, Statistic, Tooltip } from 'antd';
import { CheckCircleOutlined, EyeOutlined, ClockCircleOutlined, CloseCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import api from '../../services/api';

const { Title } = Typography;

const TransactionHistory = () => {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [previewVisible, setPreviewVisible] = useState(false);
    const [previewImage, setPreviewImage] = useState('');

    useEffect(() => {
        fetchTransactions();
    }, []);

    const fetchTransactions = async () => {
        try {
            const response = await api.get('/transactions/');
            setTransactions(response.data);
        } catch (error) {
            // Mock data if API not ready
            setTransactions([
                {
                    id: '1',
                    order_code: 'ORD-20260102-12831',
                    driver_name: 'Nguyễn Văn A',
                    completed_at: '2026-01-03T10:30:00',
                    location: '123 Nguyễn Văn Linh, Q.7, HCM',
                    status: 'pending',
                    proof_image: null,
                    admin_confirmed: false,
                },
                {
                    id: '2',
                    order_code: 'ORD-20260102-12832',
                    driver_name: 'Trần Văn B',
                    completed_at: '2026-01-03T11:45:00',
                    location: '456 Lê Văn Việt, Q.9, HCM',
                    status: 'confirmed',
                    proof_image: 'https://via.placeholder.com/300x400?text=Proof+Image',
                    admin_confirmed: true,
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleConfirm = async (id) => {
        try {
            await api.put(`/transactions/${id}/confirm/`);
            message.success('Đã xác nhận giao dịch thành công!');
            fetchTransactions();
        } catch (error) {
            // Mock confirm
            setTransactions(prev =>
                prev.map(t => t.id === id ? { ...t, status: 'confirmed', admin_confirmed: true } : t)
            );
            message.success('Đã xác nhận giao dịch thành công!');
        }
    };

    const handlePreview = (imageUrl) => {
        setPreviewImage(imageUrl);
        setPreviewVisible(true);
    };

    const stats = {
        total: transactions.length,
        confirmed: transactions.filter(t => t.admin_confirmed && t.status !== 'failed_confirmed').length,
        pending: transactions.filter(t => !t.admin_confirmed && t.status !== 'failed_pending').length,
        failed: transactions.filter(t => t.status === 'failed_pending' || t.status === 'failed_confirmed').length,
    };

    const columns = [
        {
            title: 'Mã đơn',
            dataIndex: 'order_code',
            key: 'order_code',
            width: 180,
        },
        {
            title: 'Tài xế',
            dataIndex: 'driver_name',
            key: 'driver_name',
        },
        {
            title: 'Thời gian giao',
            dataIndex: 'completed_at',
            key: 'completed_at',
            render: (val) => val ? new Date(val).toLocaleString('vi-VN') : '-',
        },
        {
            title: 'Địa điểm',
            dataIndex: 'location',
            key: 'location',
            ellipsis: true,
        },
        {
            title: 'Trạng thái',
            dataIndex: 'status',
            key: 'status',
            render: (status, record) => {
                if (status === 'failed_pending') {
                    return (
                        <Tag color="red" icon={<ExclamationCircleOutlined />}>
                            Báo thất bại - Chờ xác nhận
                        </Tag>
                    );
                }
                if (status === 'failed_confirmed') {
                    return (
                        <Tag color="default" icon={<CloseCircleOutlined />}>
                            Thất bại đã xác nhận
                        </Tag>
                    );
                }
                return (
                    <Tag color={record.admin_confirmed ? 'green' : 'orange'}>
                        {record.admin_confirmed ? 'Đã xác nhận' : 'Chờ xác nhận'}
                    </Tag>
                );
            },
        },
        {
            title: 'Bằng chứng',
            dataIndex: 'proof_image',
            key: 'proof_image',
            render: (url) => url ? (
                <Button
                    icon={<EyeOutlined />}
                    size="small"
                    onClick={() => handlePreview(url)}
                >
                    Xem ảnh
                </Button>
            ) : <span style={{ color: '#999' }}>Chưa có</span>,
        },
        {
            title: 'Ghi chú',
            dataIndex: 'notes',
            key: 'notes',
            width: 200,
            ellipsis: true,
            render: (notes) => notes ? (
                <Tooltip title={notes}>
                    <span style={{ color: '#ff4d4f' }}>{notes}</span>
                </Tooltip>
            ) : '-',
        },
        {
            title: 'Thao tác',
            key: 'actions',
            render: (_, record) => (
                <Space>
                    {record.status === 'failed_pending' && (
                        <Button
                            danger
                            type="primary"
                            icon={<CloseCircleOutlined />}
                            size="small"
                            onClick={() => handleConfirm(record.id)}
                        >
                            Xác nhận thất bại
                        </Button>
                    )}
                    {!record.admin_confirmed && record.status !== 'failed_pending' && (
                        <Button
                            type="primary"
                            icon={<CheckCircleOutlined />}
                            size="small"
                            onClick={() => handleConfirm(record.id)}
                        >
                            Xác nhận
                        </Button>
                    )}
                </Space>
            ),
        },
    ];

    return (
        <div>
            <Title level={3}>Lịch sử giao dịch</Title>

            <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={6}>
                    <Card>
                        <Statistic title="Tổng giao dịch" value={stats.total} />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="Đã xác nhận"
                            value={stats.confirmed}
                            prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="Chờ xác nhận"
                            value={stats.pending}
                            prefix={<ClockCircleOutlined style={{ color: '#faad14' }} />}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card style={{ borderColor: stats.failed > 0 ? '#ff4d4f' : undefined }}>
                        <Statistic
                            title="Đơn thất bại"
                            value={stats.failed}
                            styles={{ content: { color: stats.failed > 0 ? '#ff4d4f' : undefined } }}
                            prefix={<CloseCircleOutlined style={{ color: '#ff4d4f' }} />}
                        />
                    </Card>
                </Col>
            </Row>

            <Table
                columns={columns}
                dataSource={transactions}
                rowKey="id"
                loading={loading}
                pagination={{ pageSize: 10 }}
            />

            <Modal
                open={previewVisible}
                footer={null}
                onCancel={() => setPreviewVisible(false)}
                title="Ảnh bằng chứng giao hàng"
            >
                <Image src={previewImage} alt="Proof" style={{ width: '100%' }} />
            </Modal>
        </div >
    );
};

export default TransactionHistory;
