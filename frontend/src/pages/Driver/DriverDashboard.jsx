import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Upload, Modal, message, Typography, Tag, Space, Image, List, Avatar, Row, Col, Statistic, Spin } from 'antd';
import {
    EnvironmentOutlined, PhoneOutlined, CameraOutlined,
    CheckCircleOutlined, CarOutlined, LogoutOutlined,
    ArrowRightOutlined, ClockCircleOutlined, SendOutlined,
    CompassOutlined, CloseCircleOutlined, ExclamationCircleOutlined
} from '@ant-design/icons';
import { Input } from 'antd';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons
const currentLocationIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
});

const stopIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
});

const { Title, Text } = Typography;

const DriverDashboard = () => {
    const { user, logout } = useAuth();
    const [routeData, setRouteData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [confirmModalVisible, setConfirmModalVisible] = useState(false);
    const [uploadedImage, setUploadedImage] = useState(null);
    const [uploading, setUploading] = useState(false);

    // Failed delivery states
    const [failedModalVisible, setFailedModalVisible] = useState(false);
    const [failedReason, setFailedReason] = useState('');
    const [submittingFailed, setSubmittingFailed] = useState(false);

    // Navigation map states
    const [mapModalVisible, setMapModalVisible] = useState(false);
    const [currentLocation, setCurrentLocation] = useState(null);
    const [routePolyline, setRoutePolyline] = useState([]);
    const [loadingRoute, setLoadingRoute] = useState(false);
    const [selectedStop, setSelectedStop] = useState(null); // Track which order is selected for navigation

    useEffect(() => {
        fetchRouteData();
    }, []);

    const fetchRouteData = async () => {
        try {
            const response = await api.get('/driver/current-order/');
            console.log("Route Data:", response.data);
            setRouteData(response.data);
        } catch (error) {
            if (error.response && error.response.status === 404) {
                setRouteData(null);
            } else {
                console.error('Failed to fetch route', error);
            }
        } finally {
            setLoading(false);
        }
    };

    const handleNavigate = () => {
        const stop = selectedStop || routeData?.current_stop;
        if (!stop || (!stop.lat && !stop.address)) {
            message.warning('Vui lòng chọn một đơn hàng để dẫn đường!');
            return;
        }

        setMapModalVisible(true);
        setLoadingRoute(true);

        // Attempt to get CURRENT GPS location
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const origin = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                        name: 'Vị trí của bạn'
                    };
                    setCurrentLocation(origin);
                    calculateRoute(origin, stop);
                },
                (error) => {
                    console.error("Geolocation error:", error);
                    // Fallback: Warehouse
                    const warehouseOrigin = {
                        lat: routeData?.warehouse?.lat || 10.8231,
                        lng: routeData?.warehouse?.lng || 106.6297,
                        name: routeData?.warehouse?.name || 'Kho'
                    };
                    setCurrentLocation(warehouseOrigin);
                    calculateRoute(warehouseOrigin, stop);
                }
            );
        } else {
            // No geolocation support: Fallback Warehouse
            const warehouseOrigin = {
                lat: routeData?.warehouse?.lat || 10.8231,
                lng: routeData?.warehouse?.lng || 106.6297,
                name: routeData?.warehouse?.name || 'Kho'
            };
            setCurrentLocation(warehouseOrigin);
            calculateRoute(warehouseOrigin, stop);
        }
    };

    const calculateRoute = (origin, stop) => {
        if (stop.lat && stop.lng) {
            const waypoints = `${origin.lng},${origin.lat};${stop.lng},${stop.lat}`;

            fetch(`https://router.project-osrm.org/route/v1/driving/${waypoints}?overview=full&geometries=geojson`)
                .then(response => response.json())
                .then(data => {
                    if (data.routes && data.routes[0]) {
                        const coords = data.routes[0].geometry.coordinates.map(c => [c[1], c[0]]);
                        setRoutePolyline(coords);
                    }
                })
                .catch(error => {
                    console.error('Failed to get route:', error);
                    setRoutePolyline([[origin.lat, origin.lng], [stop.lat, stop.lng]]);
                })
                .finally(() => {
                    setLoadingRoute(false);
                });
        } else {
            setRoutePolyline([]);
            setLoadingRoute(false);
        }
    };

    const handleGoogleMaps = () => {
        const stop = selectedStop || routeData?.current_stop;
        if (stop?.lat && stop?.lng) {
            window.open(`https://www.google.com/maps/dir/?api=1&destination=${stop.lat},${stop.lng}`, '_blank');
        } else if (stop?.address) {
            window.open(`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(stop.address)}`, '_blank');
        }
    };

    const handleCall = () => {
        const stop = routeData?.current_stop;
        if (stop?.customer_phone) {
            window.location.href = `tel:${stop.customer_phone}`;
        }
    };

    const handleUpload = (info) => {
        const file = info.file.originFileObj || info.file;
        const reader = new FileReader();
        reader.onload = (e) => {
            setUploadedImage(e.target.result);
        };
        reader.readAsDataURL(file);
    };

    const handleConfirmDelivery = async () => {
        if (!uploadedImage) {
            message.error('Vui lòng chụp ảnh bằng chứng giao hàng!');
            return;
        }

        const stop = routeData?.current_stop;
        if (!stop?.order_id) return;

        setUploading(true);
        try {
            await api.post('/driver/confirm-delivery/', {
                order_id: stop.order_id,
                proof_image: uploadedImage,
            });
            message.success('Đã xác nhận giao hàng!');
            setConfirmModalVisible(false);
            setUploadedImage(null);
            fetchRouteData(); // Refresh to get next stop
        } catch (error) {
            message.success('Đã gửi xác nhận!');
            setConfirmModalVisible(false);
            setUploadedImage(null);
            fetchRouteData();
        } finally {
            setUploading(false);
        }
    };

    const handleMarkFailed = async () => {
        const stop = routeData?.current_stop;
        if (!stop?.order_id) return;

        setSubmittingFailed(true);
        try {
            await api.post('/driver/delivery/failed/', {
                order_id: stop.order_id,
                reason: failedReason || 'Không giao được hàng',
            });
            message.warning('Đã báo giao thất bại - chờ Admin xác nhận!');
            setFailedModalVisible(false);
            setFailedReason('');
            fetchRouteData(); // Refresh
        } catch (error) {
            message.error('Có lỗi xảy ra!');
        } finally {
            setSubmittingFailed(false);
        }
    };

    if (loading) {
        return <div style={{
            minHeight: '100vh',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            background: '#f0f2f5'
        }}>Loading...</div>;
    }

    const currentStop = routeData?.current_stop;
    const upcomingStops = routeData?.upcoming_stops || [];
    const stats = routeData?.stats || { completed: 0, remaining: 0, on_time_rate: 0 };

    return (
        <div style={{
            minHeight: '100vh',
            background: '#eef2f5',
            fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif',
            display: 'flex'
        }}>
            {/* LEFT: Dashboard Content */}
            <div style={{
                width: mapModalVisible ? '400px' : '100%',
                maxWidth: mapModalVisible ? '400px' : '480px',
                margin: mapModalVisible ? '0' : '0 auto',
                background: '#f5f6fa',
                minHeight: '100vh',
                position: 'relative',
                boxShadow: '0 0 20px rgba(0,0,0,0.05)',
                transition: 'width 0.3s ease'
            }}>

                {/* 1. Header Area - Bo cong */}
                <div style={{
                    background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
                    padding: '20px 16px 60px 16px',
                    color: 'white',
                    borderBottomLeftRadius: 32,
                    borderBottomRightRadius: 32,
                    boxShadow: '0 8px 24px rgba(13, 71, 161, 0.3)'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                            <div style={{
                                background: '#ff7875',
                                padding: 8,
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                width: 40, height: 40
                            }}>
                                <CarOutlined style={{ fontSize: 20, color: 'white' }} />
                            </div>
                            <div>
                                <Title level={5} style={{ color: 'white', margin: 0 }}>
                                    {user?.full_name || user?.username || "Tài Xế"}
                                </Title>
                                <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 10, display: 'block' }}>
                                    ID: {user?.id?.substring(0, 8).toUpperCase() || "DX-001"}
                                </Text>
                                <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 12 }}>
                                    {routeData?.vehicle?.plate ? `Xe: ${routeData.vehicle.plate}` : "Tài Xế App"}
                                </Text>
                            </div>
                        </div>
                        <Button
                            type="ghost"
                            shape="circle"
                            icon={<LogoutOutlined />}
                            onClick={() => {
                                Modal.confirm({
                                    title: 'Xác nhận đăng xuất',
                                    content: 'Bạn có chắc chắn muốn đăng xuất khỏi hệ thống?',
                                    okText: 'Đăng xuất',
                                    cancelText: 'Hủy',
                                    okButtonProps: { danger: true },
                                    onOk: () => logout(),
                                });
                            }}
                            style={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}
                        />
                    </div>
                </div>

                <div style={{ padding: '0 16px', marginTop: -40 }}>
                    {/* 2. Current Stop Card */}
                    {currentStop ? (
                        <Card bordered={false} style={{
                            borderRadius: 24,
                            background: 'linear-gradient(135deg, #1890ff 0%, #0050b3 100%)',
                            color: 'white',
                            boxShadow: '0 12px 32px rgba(24, 144, 255, 0.35)',
                            marginBottom: 24
                        }} bodyStyle={{ padding: 24 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <Tag color="rgba(255,255,255,0.2)" style={{ color: 'white', border: 0, borderRadius: 12, padding: '4px 12px' }}>
                                    Điểm đến hiện tại
                                </Tag>
                                <Space>
                                    <Button
                                        type="primary"
                                        shape="round"
                                        size="small"
                                        icon={<EnvironmentOutlined />}
                                        onClick={handleGoogleMaps}
                                        style={{ background: '#34a853', border: 0, fontSize: 12 }}
                                    >
                                        Google Maps
                                    </Button>
                                    <Button
                                        type="text"
                                        icon={<SendOutlined style={{ fontSize: 20 }} />}
                                        onDoubleClick={handleNavigate} // Allow both if needed
                                        onClick={handleNavigate}
                                        style={{
                                            color: 'white',
                                            padding: 0,
                                            height: 'auto'
                                        }}
                                        title="Lộ trình trong app"
                                    />
                                </Space>
                            </div>

                            <div style={{ marginTop: 16, marginBottom: 8 }}>
                                <Title level={3} style={{ color: 'white', margin: 0 }}>
                                    {currentStop.address.split(',')[0]}
                                </Title>
                                <Text style={{ color: 'rgba(255,255,255,0.8)' }}>
                                    {currentStop.address.split(',').slice(1).join(', ')}
                                </Text>
                                <div style={{ marginTop: 8, fontSize: 13, opacity: 0.8 }}>
                                    Đơn: {currentStop.order_code}
                                </div>
                            </div>

                            {/* Customer Info Box - Bo cong */}
                            <div style={{
                                background: 'rgba(255,255,255,0.15)',
                                borderRadius: 16,
                                padding: 16,
                                marginTop: 16,
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                backdropFilter: 'blur(10px)'
                            }}>
                                <div>
                                    <div style={{ fontSize: 12, opacity: 0.7 }}>Khách hàng</div>
                                    <div style={{ fontWeight: 600 }}>{currentStop.customer_name}</div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontSize: 12, opacity: 0.7 }}>Điện thoại</div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <span style={{ fontWeight: 600 }}>{currentStop.customer_phone}</span>
                                        <Button
                                            shape="circle"
                                            icon={<PhoneOutlined />}
                                            size="small"
                                            onClick={handleCall}
                                            style={{ background: 'rgba(255,255,255,0.2)', border: 0, color: 'white' }}
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Action Buttons Row */}
                            <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
                                <Button
                                    size="large"
                                    danger
                                    icon={<CloseCircleOutlined />}
                                    onClick={() => setFailedModalVisible(true)}
                                    style={{
                                        height: 52,
                                        borderRadius: 16,
                                        fontWeight: 'bold',
                                        fontSize: 15,
                                        flex: 1
                                    }}
                                >
                                    Thất bại
                                </Button>
                                <Button
                                    size="large"
                                    type="primary"
                                    icon={<CheckCircleOutlined />}
                                    onClick={() => setConfirmModalVisible(true)}
                                    style={{
                                        height: 52,
                                        borderRadius: 16,
                                        background: 'linear-gradient(135deg, #52c41a 0%, #389e0d 100%)',
                                        border: 0,
                                        fontWeight: 'bold',
                                        fontSize: 15,
                                        boxShadow: '0 6px 16px rgba(82, 196, 26, 0.4)',
                                        flex: 2
                                    }}
                                >
                                    Xác Nhận Đã Giao
                                </Button>
                            </div>
                        </Card>
                    ) : (
                        <Card bordered={false} style={{ borderRadius: 16, textAlign: 'center', marginBottom: 24, padding: 20 }}>
                            <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />
                            <Title level={4} style={{ marginTop: 16 }}>Đã hoàn thành!</Title>
                            <Text type="secondary">Bạn đã hoàn thành tất cả đơn hàng.</Text>
                        </Card>
                    )}

                    {/* 3. Upcoming List - Cuộn được */}
                    <Title level={5} style={{ marginBottom: 12, color: '#333' }}>Các điểm tiếp theo</Title>
                    <div style={{
                        marginBottom: 120,
                        maxHeight: 'calc(100vh - 480px)',
                        overflowY: 'auto',
                        paddingRight: 4
                    }}>
                        {upcomingStops.length > 0 ? (
                            upcomingStops.map((stop, index) => (
                                <Card
                                    key={stop.id}
                                    bordered={false}
                                    style={{
                                        marginBottom: 12,
                                        borderRadius: 12,
                                        padding: 0,
                                        cursor: 'pointer',
                                        border: selectedStop?.id === stop.id ? '2px solid #1890ff' : '2px solid transparent',
                                        background: selectedStop?.id === stop.id ? '#e6f7ff' : 'white'
                                    }}
                                    bodyStyle={{ padding: 16 }}
                                    onClick={() => setSelectedStop(stop)}
                                >
                                    <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                                        <div style={{
                                            background: selectedStop?.id === stop.id ? '#1890ff' : '#f0f2f5',
                                            width: 36, height: 36,
                                            borderRadius: '50%',
                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                            fontWeight: 'bold',
                                            color: selectedStop?.id === stop.id ? 'white' : '#595959'
                                        }}>
                                            {stop.sequence}
                                        </div>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Text strong style={{ color: '#1890ff' }}>{stop.order_code}</Text>
                                                <Text type="secondary" style={{ fontSize: 12 }}>{stop.distance}</Text>
                                            </div>
                                            <div style={{ color: '#595959', fontSize: 13, margin: '4px 0' }}>
                                                {stop.address.length > 40 ? stop.address.substring(0, 40) + '...' : stop.address}
                                            </div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: '#8c8c8c' }}>
                                                <ClockCircleOutlined />
                                                {stop.eta !== '00:00' ? stop.eta : '---'}
                                            </div>
                                        </div>
                                    </div>
                                </Card>
                            ))
                        ) : (
                            <div style={{ textAlign: 'center', color: '#8c8c8c', padding: 20, background: 'white', borderRadius: 12 }}>
                                Không còn điểm dừng nào.
                            </div>
                        )}
                    </div>
                </div>

                {/* 4. Stats Grid - Fixed Bottom */}
                <div style={{
                    position: 'fixed',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    background: 'linear-gradient(to top, #f5f6fa 85%, transparent)',
                    padding: '24px 16px 20px 16px',
                    zIndex: 100
                }}>
                    <div style={{ maxWidth: 480, margin: '0 auto' }}>
                        <Row gutter={12}>
                            <Col span={12}>
                                <Card
                                    bordered={false}
                                    bodyStyle={{ padding: '20px 8px', textAlign: 'center' }}
                                    style={{
                                        borderRadius: 20,
                                        background: 'linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%)',
                                        boxShadow: '0 4px 12px rgba(24, 144, 255, 0.15)'
                                    }}
                                >
                                    <Title level={2} style={{ margin: 0, color: '#1890ff' }}>{stats.completed}</Title>
                                    <Text style={{ fontSize: 12, color: '#1890ff' }}>Đã giao</Text>
                                </Card>
                            </Col>
                            <Col span={12}>
                                <Card
                                    bordered={false}
                                    bodyStyle={{ padding: '20px 8px', textAlign: 'center' }}
                                    style={{
                                        borderRadius: 20,
                                        background: 'linear-gradient(135deg, #fff1f0 0%, #ffccc7 100%)',
                                        boxShadow: '0 4px 12px rgba(255, 77, 79, 0.15)'
                                    }}
                                >
                                    <Title level={2} style={{ margin: 0, color: '#ff4d4f' }}>{stats.remaining}</Title>
                                    <Text style={{ fontSize: 12, color: '#ff4d4f' }}>Còn lại</Text>
                                </Card>
                            </Col>
                        </Row>
                    </div>
                </div>

                {/* Modal Logic */}
                <Modal
                    title="Xác nhận giao hàng"
                    open={confirmModalVisible}
                    onCancel={() => {
                        setConfirmModalVisible(false);
                        setUploadedImage(null);
                    }}
                    footer={null}
                    centered
                >
                    <div style={{ textAlign: 'center', padding: 16 }}>
                        <p>Chụp ảnh bằng chứng giao hàng</p>

                        {/* Square Image Placeholder */}
                        <div style={{
                            width: 200,
                            height: 200,
                            margin: '16px auto',
                            border: uploadedImage ? 'none' : '2px dashed #d9d9d9',
                            borderRadius: 12,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: uploadedImage ? 'transparent' : '#fafafa',
                            overflow: 'hidden'
                        }}>
                            {uploadedImage ? (
                                <Image src={uploadedImage} style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: 12 }} />
                            ) : (
                                <div style={{ color: '#bfbfbf', textAlign: 'center' }}>
                                    <CameraOutlined style={{ fontSize: 40 }} />
                                    <div style={{ marginTop: 8, fontSize: 12 }}>Ảnh xác nhận</div>
                                </div>
                            )}
                        </div>

                        <Upload
                            accept="image/*"
                            showUploadList={false}
                            beforeUpload={() => false}
                            onChange={handleUpload}
                        >
                            <Button icon={<CameraOutlined />} size="large" type="primary" ghost>
                                {uploadedImage ? 'Chụp lại' : 'Chụp ảnh'}
                            </Button>
                        </Upload>
                        <div style={{ marginTop: 24, display: 'flex', gap: 12 }}>
                            <Button block size="large" onClick={() => setConfirmModalVisible(false)}>Hủy</Button>
                            <Button block type="primary" size="large" loading={uploading} disabled={!uploadedImage} onClick={handleConfirmDelivery} style={{ fontWeight: 'bold' }}>
                                Hoàn tất đơn hàng
                            </Button>
                        </div>
                    </div>
                </Modal>

                {/* Failed Delivery Modal */}
                <Modal
                    title={
                        <span style={{ color: '#ff4d4f' }}>
                            <ExclamationCircleOutlined /> Báo giao thất bại
                        </span>
                    }
                    open={failedModalVisible}
                    onCancel={() => {
                        setFailedModalVisible(false);
                        setFailedReason('');
                    }}
                    footer={null}
                    centered
                >
                    <div style={{ padding: 16 }}>
                        <p style={{ marginBottom: 16 }}>
                            <strong>Đơn hàng:</strong> {routeData?.current_stop?.order_code}
                        </p>
                        <p style={{ marginBottom: 8 }}>Lý do không giao được:</p>
                        <Input.TextArea
                            rows={3}
                            placeholder="Nhập lý do (VD: Khách không có nhà, số điện thoại sai...)"
                            value={failedReason}
                            onChange={(e) => setFailedReason(e.target.value)}
                            style={{ marginBottom: 16, borderRadius: 8 }}
                        />

                        <div style={{
                            background: '#fff7e6',
                            border: '1px solid #ffd591',
                            borderRadius: 8,
                            padding: 12,
                            marginBottom: 16
                        }}>
                            <ExclamationCircleOutlined style={{ color: '#fa8c16', marginRight: 8 }} />
                            <span style={{ color: '#d46b08', fontSize: 13 }}>
                                Hàng sẽ được trả về kho và Admin sẽ xác nhận
                            </span>
                        </div>

                        <div style={{ display: 'flex', gap: 12 }}>
                            <Button
                                block
                                size="large"
                                onClick={() => setFailedModalVisible(false)}
                            >
                                Hủy
                            </Button>
                            <Button
                                block
                                danger
                                type="primary"
                                size="large"
                                loading={submittingFailed}
                                onClick={handleMarkFailed}
                                icon={<CloseCircleOutlined />}
                            >
                                Xác nhận thất bại
                            </Button>
                        </div>
                    </div>
                </Modal>
            </div>

            {/* RIGHT: Map Panel - Shows when mapModalVisible is true */}
            {mapModalVisible && (
                <div style={{
                    flex: 1,
                    background: 'white',
                    borderLeft: '1px solid #e8e8e8',
                    position: 'relative',
                    minHeight: '100vh'
                }}>
                    {/* Close button */}
                    <Button
                        type="text"
                        onClick={() => {
                            setMapModalVisible(false);
                            setRoutePolyline([]);
                            setCurrentLocation(null);
                        }}
                        style={{
                            position: 'absolute',
                            top: 10,
                            right: 10,
                            zIndex: 1000,
                            background: 'white',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                        }}
                    >
                        ✕ Đóng
                    </Button>

                    {/* Map Title */}
                    <div style={{
                        padding: '12px 16px',
                        borderBottom: '1px solid #e8e8e8',
                        background: '#1890ff',
                        color: 'white'
                    }}>
                        <CompassOutlined /> <strong>Bản đồ dẫn đường</strong>
                    </div>

                    {/* Map Content */}
                    {loadingRoute ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 'calc(100vh - 50px)' }}>
                            <Spin size="large" tip="Đang tải lộ trình..." />
                        </div>
                    ) : (
                        <MapContainer
                            key={`map-${mapModalVisible}`}
                            center={currentLocation ? [currentLocation.lat, currentLocation.lng] : [10.8231, 106.6297]}
                            zoom={13}
                            maxZoom={22}
                            style={{ height: 'calc(100vh - 50px)', width: '100%' }}
                        >
                            <TileLayer
                                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                maxZoom={22}
                                maxNativeZoom={19}
                            />

                            {/* Warehouse Origin Marker */}
                            {currentLocation && (
                                <Marker position={[currentLocation.lat, currentLocation.lng]} icon={currentLocationIcon}>
                                    <Popup><strong>🏭 {currentLocation.name || 'Kho xuất phát'}</strong></Popup>
                                </Marker>
                            )}

                            {/* Destination: Selected Stop */}
                            {(() => {
                                const stop = selectedStop || routeData?.current_stop;
                                return stop?.lat && stop?.lng && (
                                    <Marker position={[stop.lat, stop.lng]} icon={stopIcon}>
                                        <Popup>
                                            <strong>📦 {stop.order_code}</strong><br />
                                            {stop.address}<br />
                                            <Tag color="blue">Điểm giao đã chọn</Tag>
                                        </Popup>
                                    </Marker>
                                );
                            })()}

                            {/* Route Polyline */}
                            {routePolyline.length > 0 && (
                                <Polyline positions={routePolyline} color="#1890ff" weight={5} opacity={0.8} />
                            )}
                        </MapContainer>
                    )}
                </div>
            )}
        </div>
    );
};

export default DriverDashboard;
