import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Select, Space, message, Typography, Tag, Card, Row, Col, List, Badge, Spin, Tabs, Dropdown, Menu, Progress, Tooltip } from 'antd';
import { PlusOutlined, EnvironmentOutlined, CarOutlined, AimOutlined, RocketOutlined, LoadingOutlined } from '@ant-design/icons';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Tooltip as LeafletTooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { routeAPI, orderAPI, vehicleAPI, warehouseAPI, userAPI } from '../../services/api';

// Component để tự động zoom vào vùng có lộ trình
const FitBounds = ({ routeFeatures, warehouses }) => {
  const map = useMap();

  // Create a stable dependency key based on content that changes the boundary
  const routeMarkersKey = routeFeatures.map(rf => `${rf.id}-${rf.itemMarkers.length}`).join('|');
  const warehouseKey = warehouses.map(w => w.id).join('|');

  useEffect(() => {
    const allPoints = [];

    // Thu thập tất cả điểm từ routes
    routeFeatures.forEach(rf => {
      rf.itemMarkers.forEach(m => {
        if (m.position) allPoints.push(m.position);
      });
    });

    // Thu thập điểm từ warehouses
    warehouses.forEach(w => {
      if (w.latitude && w.longitude) {
        allPoints.push([parseFloat(w.latitude), parseFloat(w.longitude)]);
      }
    });

    // Nếu có điểm, fit bounds
    if (allPoints.length > 0) {
      const bounds = L.latLngBounds(allPoints);
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 13 });
    }
  }, [map, routeMarkersKey, warehouseKey]); // Chỉ re-fit khi số lượng route/markers hoặc warehouse thay đổi

  return null;
};

const { Title, Text } = Typography;

// Fix Leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons
const warehouseIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const deliveryIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Invisible icon for text labels on polyline
const textIcon = (text) => L.divIcon({
  className: 'custom-text-icon',
  html: `<div style="background-color: #ffe58f; padding: 2px 5px; border: 1px solid #d46b08; border-radius: 4px; font-weight: bold; font-size: 12px; color: #000; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">${text}</div>`,
  iconSize: [80, 24],
  iconAnchor: [40, 12]
});

const RoutesPage = () => {
  const [routes, setRoutes] = useState([]);
  const [pendingOrders, setPendingOrders] = useState([]);
  const [availableVehicles, setAvailableVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [optimizeModalVisible, setOptimizeModalVisible] = useState(false);
  const [form] = Form.useForm();

  // Distance matrix states
  const [matrixModalVisible, setMatrixModalVisible] = useState(false);
  const [matrixData, setMatrixData] = useState(null);
  const [matrixLoading, setMatrixLoading] = useState(false);
  const [matrixOrderIds, setMatrixOrderIds] = useState([]);

  // Default center: Ho Chi Minh City
  const mapCenter = [10.8231, 106.6297];

  useEffect(() => {
    fetchData();
  }, []);

  // Auto-polling: Tự động refresh data mỗi 5 giây để cập nhật bản đồ
  useEffect(() => {
    const interval = setInterval(() => {
      fetchData();
    }, 5000); // 5 giây

    return () => clearInterval(interval);
  }, []);

  // Refresh data when opening optimization modal to get latest driver/vehicle assignments
  useEffect(() => {
    if (optimizeModalVisible) {
      fetchData();
    }
  }, [optimizeModalVisible]);

  const fetchData = async () => {
    try {
      const [routesRes, ordersRes, vehiclesRes, warehousesRes, driversRes] = await Promise.all([
        routeAPI.getAll(),
        orderAPI.getPending(),
        vehicleAPI.getAvailable(),
        warehouseAPI.getAll(),
        userAPI.getDrivers(),
      ]);
      setRoutes(routesRes.data);
      setPendingOrders(ordersRes.data);
      setAvailableVehicles(vehiclesRes.data);
      setWarehouses(warehousesRes.data.filter(w => 
        !w.name.toLowerCase().includes('tphcm') && 
        !w.name.toLowerCase().includes('đà nẵng') &&
        !w.name.toLowerCase().includes('da nang') &&
        !w.name.toLowerCase().includes('hcm')
      ));
      setDrivers(driversRes.data);

    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async (values) => {
    setOptimizing(true);
    await new Promise(resolve => setTimeout(resolve, 1500));

    try {
      // Gửi order_ids và driver_ids cho backend
      const payload = { 
        order_ids: values.order_ids,
        driver_ids: values.driver_ids
      };

      const response = await routeAPI.optimize(payload);
      const routesCreated = response.data.routes?.length || 0;
      const packingSummary = response.data.bin_packing_summary;

      setOptimizeModalVisible(false);
      form.resetFields();

      if (routesCreated > 0) {
        Modal.success({
          title: 'Tối ưu lộ trình hoàn tất!',
          content: (
            <div>
              <p>Đã tạo thành công <b>{routesCreated}</b> lộ trình.</p>
              {packingSummary?.unassigned_orders > 0 && (
                <p style={{ color: 'red' }}>⚠️ Còn <b>{packingSummary.unassigned_orders}</b> đơn hàng vượt quá tải trọng xe, vui lòng điều thêm xe.</p>
              )}
            </div>
          ),
          width: 500
        });
      } else {
        message.warning('Tối ưu hoàn tất nhưng chưa tạo lộ trình nào.');
      }

      await fetchData();
    } catch (error) {
      message.error(error.response?.data?.error || 'Có lỗi xảy ra khi tối ưu lộ trình!');
    } finally {
      setOptimizing(false);
    }
  };

  const handleStartRoute = async (id) => {
    try {
      await routeAPI.start(id);
      message.success('Đã bắt đầu lộ trình!');
      fetchData();
    } catch (error) {
      message.error('Có lỗi xảy ra!');
    }
  };

  const handleCompleteRoute = async (id) => {
    try {
      await routeAPI.complete(id);
      message.success('Đã hoàn thành lộ trình!');
      fetchData();
    } catch (error) {
      message.error('Có lỗi xảy ra!');
    }
  };

  const handleShowMatrix = async (warehouseId) => {
    // Tìm các lộ trình (routes) đang thuộc về kho này
    const warehouseRoutes = routes.filter(r => String(r.warehouse_id) === String(warehouseId));

    // Lấy tất cả order_id từ các điểm dừng của các lộ trình đó
    let ids = [];
    warehouseRoutes.forEach(route => {
      if (route.stops) {
        ids = ids.concat(route.stops.map(s => s.order_id));
      }
    });

    if (ids.length === 0) {
      message.warning('Kho này chưa có đơn hàng nào được lên lộ trình (chưa được Tối ưu)!');
      return;
    }

    if (ids.length < 2) {
      message.warning('Cần ít nhất 2 điểm giao để xem ma trận khoảng cách!');
      return;
    }

    setMatrixOrderIds(ids);
    setMatrixLoading(true);
    setMatrixModalVisible(true);
    try {
      const res = await routeAPI.getDistanceMatrix({ order_ids: ids });
      setMatrixData(res.data);
    } catch (err) {
      message.error(err.response?.data?.error || 'Không thể tải ma trận!');
      setMatrixModalVisible(false);
    } finally {
      setMatrixLoading(false);
    }
  };

  // Helper: color cell by distance value
  const getCellColor = (val, max) => {
    if (val === 0) return '#f0f0f0';
    const ratio = val / max;
    const r = Math.round(255 * ratio);
    const g = Math.round(180 * (1 - ratio));
    return `rgba(${r}, ${g}, 80, 0.25)`;
  };

  const statusColors = {
    pending: 'gold',
    in_progress: 'processing',
    completed: 'success',
    cancelled: 'error',
  };

  const statusLabels = {
    pending: 'Chờ thực hiện',
    in_progress: 'Đang giao',
    completed: 'Hoàn thành',
    cancelled: 'Đã hủy',
  };

  // Prepare map features
  const warehouseMarkers = warehouses.filter(w => w.latitude && w.longitude);

  // Calculate polylines and markers for active routes (derive directly from routes)
  const activeRoutes = routes.filter(r => r.status === 'pending' || r.status === 'in_progress');
  
  const routeFeatures = activeRoutes.map((route, idx) => {
    const warehouse = warehouses.find(w => w.id === route.warehouse_id) || warehouses[0];
    let startPoint = mapCenter;
    if (warehouse && warehouse.latitude && warehouse.longitude) {
      const lat = parseFloat(warehouse.latitude);
      const lng = parseFloat(warehouse.longitude);
      if (!isNaN(lat) && !isNaN(lng)) {
        startPoint = [lat, lng];
      }
    }

    // Sort stops by sequence
    const stops = (route.stops || []).sort((a, b) => a.sequence - b.sequence);

    const segments = [];
    const itemMarkers = [];
    let currentPoint = startPoint;

    stops.forEach((stop) => {
      const lat = parseFloat(stop.latitude);
      const lng = parseFloat(stop.longitude);
      
      if (!isNaN(lat) && !isNaN(lng)) {
        const nextPoint = [lat, lng];

        // Create segment from current to next
        const midPoint = [
          (currentPoint[0] + nextPoint[0]) / 2,
          (currentPoint[1] + nextPoint[1]) / 2
        ];

        segments.push({
          positions: [currentPoint, nextPoint],
          code: stop.order_code || `Order ${stop.id?.slice(0, 4) || idx}`, 
          midPoint: midPoint,
        });

        itemMarkers.push({
          position: nextPoint,
          orderCode: stop.order_code,
          address: stop.address
        });

        currentPoint = nextPoint;
      }
    });

    // Color for distinct routes
    const colors = ['blue', 'green', 'purple', 'orange', 'red'];
    const color = colors[idx % colors.length];

    return {
      id: route.id,
      segments: segments,
      itemMarkers: itemMarkers,
      color: color,
      code: route.code
    };
  });

  return (
    <div>
      <Title level={4} style={{ marginBottom: 8 }}>Quản lý Vận tải</Title>

      <Row gutter={12}>
        {/* Routes List - LEFT */}
        <Col xs={24} lg={9}>
          <Card
            title="Danh sách lộ trình"
            extra={
              <Button
                type="primary"
                icon={<RocketOutlined />}
                onClick={() => setOptimizeModalVisible(true)}
                size="small"
              >
                Tối ưu
              </Button>
            }
            bodyStyle={{ padding: 8, height: 'calc(100vh - 180px)', overflowY: 'auto' }}
          >
            <Table
              dataSource={routes.filter(r => ['pending', 'in_progress', 'completed', 'failed'].includes(r.status))}
              rowKey="id"
              loading={loading}
              size="middle"
              pagination={{
                pageSize: 10,
                size: 'small'
              }}
              columns={[
                {
                  title: 'Mã lộ trình',
                  dataIndex: 'code',
                  key: 'code',
                  render: t => <b style={{ fontSize: 13 }}>{t}</b>
                },
                {
                  title: 'Tài xế & Xe',
                  key: 'driver_vehicle',
                  width: 180,
                  render: (_, record) => (
                    <div style={{ fontSize: 12 }}>
                      <div style={{ marginBottom: 4 }}><CarOutlined /> <b>{record.vehicle_plate || '—'}</b></div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                        {record.drivers?.map(d => (
                          <Tag key={d.id} color="blue" style={{ fontSize: 11, margin: 0, padding: '2px 6px' }}>
                            {d.name}
                          </Tag>
                        ))}
                      </div>
                    </div>
                  )
                },
                {
                  title: 'Lấp đầy',
                  key: 'utilization',
                  width: 140,
                  render: (_, record) => {
                    const weight = record.total_weight || 0;
                    const cap = record.capacity_kg || 1000;
                    const pct = Math.min(100, Math.round((weight / cap) * 100));
                    let color = '#52c41a';
                    if (pct > 90) color = '#f5222d';
                    else if (pct > 75) color = '#faad14';

                    return (
                      <div style={{ minWidth: 100 }}>
                        <Progress 
                          percent={pct} 
                          size="small" 
                          strokeColor={color}
                          format={() => `${pct}%`}
                        />
                        <div style={{ fontSize: 10, color: '#8c8c8c', marginTop: -4 }}>
                          {weight} / {cap} kg
                        </div>
                      </div>
                    );
                  }
                },
                {
                  title: 'Trạng thái',
                  dataIndex: 'status',
                  key: 'status',
                  render: (status) => <Tag color={statusColors[status]} style={{ fontSize: 11, margin: 0 }}>{statusLabels[status]}</Tag>
                },
              ]}
            />
          </Card>
        </Col>

        {/* Map Section - RIGHT */}
        <Col xs={24} lg={15}>
          <Card
            title={<><EnvironmentOutlined /> Bản đồ lộ trình</>}
            bodyStyle={{ padding: 8 }}
          >
            <div style={{ height: 'calc(100vh - 180px)' }}>
              <MapContainer center={mapCenter} zoom={12} maxZoom={22} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>'
                  url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                  maxZoom={22}
                  maxNativeZoom={20}
                />

                {/* Tự động zoom vào vùng có lộ trình */}
                <FitBounds routeFeatures={routeFeatures} warehouses={warehouseMarkers} />

                {/* Warehouse markers */}
                {warehouseMarkers.map((w, idx) => (
                  <Marker
                    key={`wh-${idx}`}
                    position={[parseFloat(w.latitude), parseFloat(w.longitude)]}
                    icon={warehouseIcon}
                  >
                    <Popup><strong>🏭 {w.name}</strong><br />{w.code}</Popup>
                  </Marker>
                ))}

                {/* Active Route Segments & Markers */}
                {routeFeatures.map((rf) => (
                  <React.Fragment key={rf.id}>
                    {/* Draw segments and midpoint labels */}
                    {rf.segments.map((seg, sIdx) => (
                      <React.Fragment key={`seg-${rf.id}-${sIdx}`}>
                        <Polyline
                          positions={seg.positions}
                          color={rf.color}
                          weight={4}
                          opacity={0.7}
                        />
                        {/* Label on path */}
                        <Marker position={seg.midPoint} icon={textIcon(seg.code)} zIndexOffset={100} />
                      </React.Fragment>
                    ))}

                    {/* Delivery points */}
                    {rf.itemMarkers.map((m, mIdx) => (
                      <Marker
                        key={`m-${rf.id}-${mIdx}`}
                        position={m.position}
                        icon={deliveryIcon}
                      >
                        <LeafletTooltip direction="top" offset={[0, -20]} opacity={1}>
                          {m.orderCode}
                        </LeafletTooltip>
                        <Popup>{m.address}</Popup>
                      </Marker>
                    ))}
                  </React.Fragment>
                ))}
              </MapContainer>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Optimize Modal with Loading Effect */}
      <Modal
        title="Tối ưu lộ trình - OR-Tools VRP"
        open={optimizeModalVisible}
        onCancel={() => !optimizing && setOptimizeModalVisible(false)}
        footer={null}
        width={600}
        maskClosable={!optimizing}
        closable={!optimizing}
      >
        {optimizing ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
            <div style={{ marginTop: 24, fontSize: 16 }}>Đang chạy thuật toán tối ưu VRP...</div>
            <div style={{ marginTop: 8, color: '#999' }}>Vui lòng đợi trong giây lát</div>
          </div>
        ) : (
          <Form form={form} layout="vertical" onFinish={handleOptimize}>
            <Form.Item name="order_ids" label="Chọn đơn hàng cần giao" rules={[{ required: true, message: 'Vui lòng chọn ít nhất 1 đơn hàng' }]}>
              <Select mode="multiple" placeholder="Chọn đơn hàng..." maxTagCount="responsive">
                {pendingOrders.map(o => {
                  const warehouseName = warehouses.find(w => String(w.id) === String(o.warehouse_id))?.name || 'Chưa có kho';
                  return (
                    <Select.Option key={o.id} value={o.id}>
                      {o.code} - {o.customer_name} ({warehouseName})
                    </Select.Option>
                  );
                })}
              </Select>
            </Form.Item>

            <Form.Item name="driver_ids" label="Chọn tài xế (Xe tương ứng sẽ chạy)" rules={[{ required: true, message: 'Vui lòng chọn ít nhất 1 tài xế' }]}>
              <Select mode="multiple" placeholder="Chọn tài xế..." maxTagCount="responsive">
                {drivers.filter(d => d.status !== 'inactive' && !d.has_active_route).map(d => (
                  <Select.Option key={d.id} value={d.id}>
                    👤 {d.full_name || d.username} {d.current_vehicle ? `(Xe: ${d.current_vehicle})` : ''}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            <div style={{ marginBottom: 16, padding: 12, background: '#f6ffed', borderRadius: 8, border: '1px solid #b7eb8f' }}>
              <Text type="success">🎒 <b>Bin Packing (FFD)</b> tự động chia đơn vào xe của tài xế đã chọn</Text>
              <br />
              <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
                *Lưu ý: Mỗi tài xế chỉ chạy đúng xe đã được gán cố định. Lộ trình có thể có nhiều tài xế đi cùng.
              </div>
            </div>

            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit" icon={<AimOutlined />}>
                  Tối ưu với Bin Packing + OR-Tools
                </Button>
                <Button onClick={() => setOptimizeModalVisible(false)}>Hủy</Button>
              </Space>
            </Form.Item>
          </Form>
        )}
      </Modal>

      {/* Distance Matrix Modal */}
      <Modal
        title={<><AimOutlined /> Ma trận khoảng cách (km) – Haversine</>}
        open={matrixModalVisible}
        onCancel={() => { setMatrixModalVisible(false); setMatrixData(null); }}
        footer={null}
        width={900}
        centered
        bodyStyle={{ maxHeight: '80vh', overflowY: 'auto' }}
      >
        {matrixLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin size="large" tip="Đang tính toán các ma trận khoảng cách..." />
          </div>
        ) : matrixData?.is_multi && matrixData.matrices ? (
          <div>
            <Tabs defaultActiveKey="0" type="card" style={{ marginBottom: 0 }}>
              {matrixData.matrices.map((matrixObj, mIndex) => {
                const maxVal = Math.max(...matrixObj.matrix.flat().filter(v => v > 0));
                return (
                  <Tabs.TabPane
                    tab={<><span>🏭 {matrixObj.warehouse_name}</span><Badge count={matrixObj.size} style={{ backgroundColor: '#52c41a', marginLeft: 8 }} /></>}
                    key={mIndex.toString()}
                  >
                    <div style={{ padding: '16px 0 8px 0', overflowX: 'auto', borderTop: '0' }}>
                      <table style={{ borderCollapse: 'collapse', fontSize: 12, width: '100%', border: '1px solid #f0f0f0', borderRadius: 8 }}>
                        <thead>
                          <tr>
                            <th style={{ padding: '6px 10px', background: '#1890ff', color: 'white', border: '1px solid #ddd', minWidth: 80, position: 'sticky', left: 0, zIndex: 10 }}>
                              Từ \ Đến
                            </th>
                            {matrixObj.labels.map((label, j) => (
                              <th key={j} style={{
                                padding: '6px 8px', background: j === 0 ? '#FFA07A' : '#1890ff',
                                color: 'white', border: '1px solid #ddd',
                                maxWidth: 90, overflow: 'hidden', whiteSpace: 'nowrap',
                                textOverflow: 'ellipsis', fontSize: 11
                              }} title={label}>
                                {label.length > 12 ? label.slice(0, 10) + '…' : label}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {matrixObj.matrix.map((row, i) => (
                            <tr key={i}>
                              <td style={{
                                padding: '5px 10px', fontWeight: 600, border: '1px solid #ddd',
                                background: i === 0 ? '#FFF3E0' : '#fafafa',
                                whiteSpace: 'nowrap', maxWidth: 100,
                                overflow: 'hidden', textOverflow: 'ellipsis', fontSize: 11,
                                position: 'sticky', left: 0, zIndex: 9
                              }} title={matrixObj.labels[i]}>
                                {matrixObj.labels[i].length > 12 ? matrixObj.labels[i].slice(0, 10) + '…' : matrixObj.labels[i]}
                              </td>
                              {row.map((val, j) => (
                                <td key={j} style={{
                                  padding: '5px 8px', textAlign: 'center',
                                  border: '1px solid #ddd',
                                  background: getCellColor(val, maxVal),
                                  fontWeight: val === 0 ? 400 : 500,
                                  color: val === 0 ? '#ccc' : '#333',
                                }}>
                                  {val === 0 ? '—' : val.toFixed(1)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </Tabs.TabPane>
                );
              })}
            </Tabs>

            <div style={{ marginTop: 12, display: 'flex', gap: 16, alignItems: 'center', fontSize: 12, color: '#888', padding: '12px 0', borderTop: '1px solid #eee' }}>
              <span>Màu sắc:</span>
              <span style={{ background: 'rgba(0,180,80,0.25)', padding: '2px 10px', borderRadius: 4 }}>🟢 Gần</span>
              <span style={{ background: 'rgba(255,90,80,0.25)', padding: '2px 10px', borderRadius: 4 }}>🔴 Xa</span>
              <span style={{ marginLeft: 'auto' }}>🏭: Kho xuất phát | Tính bằng Haversine (km)</span>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
};

export default RoutesPage;
