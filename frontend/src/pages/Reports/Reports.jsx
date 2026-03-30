import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Typography, Statistic, Table, Button, message, Space, Progress, Divider, Spin, Modal } from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  CarOutlined,
  TrophyOutlined,
  DownloadOutlined,
  DollarOutlined,
  EnvironmentOutlined,
  UserOutlined,
  PieChartOutlined,
  BarChartOutlined,
  AimOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title as ChartTitle } from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { reportAPI, warehouseAPI, routeAPI } from '../../services/api';
import Loading from '../../components/Common/Loading';
import { Select } from 'antd';

const { Option } = Select;

ChartJS.register(CategoryScale, LinearScale, BarElement, ChartTitle);

const { Title, Text } = Typography;

const statusLabels = {
  pending: 'Chờ xử lý',
  confirmed: 'Đã xác nhận',
  processing: 'Đang xử lý',
  picked_up: 'Đã lấy hàng',
  in_transit: 'Đang giao hàng',
  delivered: 'Đã giao hàng',
  failed: 'Giao hàng lỗi',
  cancelled: 'Đã hủy',
  returned: 'Đã trả hàng',
};

const Reports = () => {
  const [orderReport, setOrderReport] = useState(null);
  const [vehicleReport, setVehicleReport] = useState(null);
  const [routeReport, setRouteReport] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [warehouses, setWarehouses] = useState([]);
  const [selectedWarehouse, setSelectedWarehouse] = useState(null);
  const [matrices, setMatrices] = useState([]);
  const [loadingMatrix, setLoadingMatrix] = useState(false);

  useEffect(() => {
    fetchReports();
    fetchWarehouses();
  }, []);

  const fetchWarehouses = async () => {
    try {
      const res = await warehouseAPI.getAll();
      setWarehouses(res.data);
      if (res.data.length > 0) {
        setSelectedWarehouse(res.data[0].id);
        fetchDistanceMatrix(res.data[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch warehouses:', error);
    }
  };

  const fetchDistanceMatrix = async (whId) => {
    setLoadingMatrix(true);
    try {
      const res = await routeAPI.getDistanceMatrix({ warehouse_id: whId });
      setMatrices(res.data.matrices || []);
    } catch (error) {
      console.error('Failed to fetch distance matrix:', error);
      setMatrices([]);
    } finally {
      setLoadingMatrix(false);
    }
  };

  const fetchReports = async () => {
    try {
      const [orderRes, vehicleRes, routeRes, perfRes] = await Promise.all([
        reportAPI.getOrderReport(),
        reportAPI.getVehicleReport(),
        reportAPI.getRouteReport(),
        reportAPI.getPerformance(),
      ]);
      setOrderReport(orderRes.data);
      setVehicleReport(vehicleRes.data);
      setRouteReport(routeRes.data);
      setPerformance(perfRes.data);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
      setPerformance({
        delivery_success_rate: 0,
        total_deliveries: 0,
        average_delivery_time_minutes: 0,
        vehicle_utilization_rate: 0,
      });
      setOrderReport({
        status_breakdown: [],
        orders_by_date: [],
      });
      setVehicleReport({
        status_breakdown: [],
        type_breakdown: [],
        total_capacity: 0,
        average_capacity: 0,
      });
      setRouteReport({
        status_breakdown: [],
        routes_this_week: 0,
        total_distance_km: 0,
        average_distance_km: 0,
        avg_time: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExportExcel = () => {
    message.loading('Đang tạo file Excel...', 1).then(() => {
      const totalDeliveredWeight = routeReport?.total_delivered_weight_kg || 0;
      const totalUsedCapacity = routeReport?.total_used_vehicle_capacity_kg || 0;
      const originalDistance = routeReport?.total_original_distance_km || 0;
      const optimizedDistance = routeReport?.total_optimized_distance_km || 0;

      const csvContent = [
        'Báo cáo VRP Logistics',
        '',
        'Chỉ số,Giá trị',
        `Tỷ lệ giao thành công,${performance?.delivery_success_rate || 0}%`,
        `Tổng đơn đã giao,${performance?.total_deliveries || 0}`,
        `Tổng quãng đường thuật toán tối ưu,"${optimizedDistance.toLocaleString('vi-VN')} km"`,
        `Tổng quãng đường gốc ban đầu,"${originalDistance.toLocaleString('vi-VN')} km"`,
        `Tổng lượt xe điều động,${routeReport?.status_breakdown?.reduce((acc, s) => acc + s.count, 0) || 0}`,
        `Khối lượng đã giao,"${totalDeliveredWeight.toLocaleString('vi-VN')} kg"`,
        `Tổng tải trọng xe điều động,"${totalUsedCapacity.toLocaleString('vi-VN')} kg"`,
        `Hệ số lấp đầy tải trọng,${totalUsedCapacity > 0 ? ((totalDeliveredWeight / totalUsedCapacity) * 100).toFixed(1) : 0}%`,
        `Mật độ giao hàng (Đơn/km),${routeReport?.delivery_density?.toFixed(4) || 0}`,
        `Số điểm giao tuần này,${routeReport?.routes_this_week || 0}`,
        '',
        'Đơn hàng theo trạng thái',
        ...(orderReport?.status_breakdown?.map(s => `${statusLabels[s.status] || s.status},${s.count}`) || []),
      ].join('\n');

      const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `bao-cao-${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      message.success('Đã xuất file báo cáo thành công!');
    });
  };

  const handleClearMatrix = () => {
    Modal.confirm({
      title: 'Xóa tất cả lộ trình và ma trận?',
      content: 'Thao tác này sẽ xóa sạch các lộ trình hiện tại và đưa toàn bộ đơn hàng về trạng thái chờ. Bạn có chắc chắn?',
      okText: 'Xóa sạch',
      okType: 'danger',
      cancelText: 'Hủy',
      onOk: async () => {
        try {
          await routeAPI.deleteAll();
          message.success('Đã xóa sạch lộ trình và ma trận thành công!');
          fetchDistanceMatrix(selectedWarehouse);
          fetchReports();
        } catch (error) {
          message.error('Không thể xóa lộ trình!');
        }
      }
    });
  };

  if (loading) return <Loading />;

  // Calculate derived stats
  // No status breakdown needed for this layout

  // Caculate metrics for display
  const totalDeliveredWeight = routeReport?.total_delivered_weight_kg || 0;
  const totalUsedCapacity = routeReport?.total_used_vehicle_capacity_kg || 0;
  
  const originalDistance = routeReport?.total_original_distance_km || 0;
  const optimizedDistance = routeReport?.total_optimized_distance_km || 0;
  const distanceSavings = originalDistance > 0 ? (((originalDistance - optimizedDistance) / originalDistance) * 100).toFixed(1) : 0;
  
  const estimatedCost = routeReport?.estimated_cost_vnd || (optimizedDistance * 5000);

  const orderStatusColumns = [];

  const handleWarehouseChange = (value) => {
    setSelectedWarehouse(value);
    fetchDistanceMatrix(value);
  };

  const getCellColor = (val, max) => {
    if (val === 0) return '#f0f0f0';
    const ratio = val / max;
    const r = Math.round(255 * ratio);
    const g = Math.round(180 * (1 - ratio));
    return `rgba(${r}, ${g}, 80, 0.2)`;
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Báo cáo Tối ưu</Title>
        <Space>
          <Button danger icon={<DeleteOutlined />} onClick={handleClearMatrix} size="large">
            Xóa ma trận
          </Button>
          <Button type="primary" icon={<DownloadOutlined />} onClick={handleExportExcel} size="large">
            Xuất Excel
          </Button>
        </Space>
      </div>

      {/* Top Rows for Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={4}><Card><Statistic title="Sản lượng giao (Đơn)" value={performance?.total_deliveries || 0} prefix={<TrophyOutlined style={{ color: '#1890ff' }} />} /></Card></Col>
        <Col xs={24} sm={12} lg={5}><Card><Statistic title="Tỷ lệ giao thành công" value={performance?.delivery_success_rate || 0} suffix="%" prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />} /></Card></Col>
        <Col xs={24} sm={12} lg={5}><Card><Statistic title="Mật độ giao hàng" value={routeReport?.delivery_density?.toFixed(4) || 0} prefix={<EnvironmentOutlined style={{ color: '#722ed1' }} />} /></Card></Col>
        <Col xs={24} sm={12} lg={5}><Card><Statistic title="Tổng xe điều động" value={routeReport?.status_breakdown?.reduce((acc, s) => acc + s.count, 0) || 0} prefix={<CarOutlined style={{ color: '#faad14' }} />} /></Card></Col>
        <Col xs={24} sm={12} lg={5}><Card><Statistic title="Hệ số lấp đầy" value={totalUsedCapacity > 0 ? ((totalDeliveredWeight / totalUsedCapacity) * 100).toFixed(1) : 0} suffix="%" prefix={<BarChartOutlined style={{ color: '#eb2f96' }} />} /></Card></Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={24}>
          <Card title={<><TrophyOutlined /> Hiệu quả Tối ưu (OR-Tools & Bin Packing)</>}>
            <Row gutter={[32, 32]}>
              <Col span={12}>
                <div style={{ marginBottom: 20 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Text>Quãng đường bản đồ cung cấp (Gốc)</Text>
                    <Text strong>{originalDistance.toLocaleString()} km</Text>
                  </div>
                  <Progress percent={100} showInfo={false} strokeColor="#d9d9d9" />
                </div>
                <div style={{ marginBottom: 20 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Text>Quãng đường thuật toán tối ưu</Text>
                    <div>
                        <Text strong style={{ color: '#52c41a' }}>{optimizedDistance.toLocaleString()} km</Text>
                        {originalDistance > 0 && <Text type="success" style={{ marginLeft: 8 }}>(↓ {distanceSavings}%)</Text>}
                    </div>
                  </div>
                  <Progress percent={originalDistance > 0 ? (optimizedDistance / originalDistance) * 100 : 0} strokeColor="#52c41a" />
                </div>
              </Col>
              
              <Col span={12}>
                <div style={{ marginBottom: 20 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Text>Khối lượng tất cả đơn hàng đã giao</Text>
                    <Text strong>{totalDeliveredWeight.toLocaleString()} kg</Text>
                  </div>
                  <Progress percent={totalUsedCapacity > 0 ? (totalDeliveredWeight / totalUsedCapacity) * 100 : 0} strokeColor="#1890ff" />
                </div>
                <div style={{ marginBottom: 10 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Text>Khối lượng tất cả xe đã sử dụng (Tổng tải trọng)</Text>
                    <Text strong>{totalUsedCapacity.toLocaleString()} kg</Text>
                  </div>
                  <Progress percent={100} showInfo={false} strokeColor="#d9d9d9" />
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title={<Space><AimOutlined /> Ma trận Khoảng cách Tối ưu</Space>} extra={
            <Select 
              value={selectedWarehouse} 
              onChange={handleWarehouseChange} 
              style={{ width: 220 }}
              placeholder="Chọn kho hàng"
            >
              {warehouses.map(wh => (
                <Option key={wh.id} value={wh.id}>{wh.name}</Option>
              ))}
            </Select>
          }>
            {loadingMatrix ? (
              <div style={{ textAlign: 'center', padding: 40 }}><Spin tip="Đang tải ma trận..." /></div>
            ) : matrices.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                {matrices.map((m, idx) => (
                  <div key={idx}>
                    <Title level={5}>{m.warehouse_name}</Title>
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ borderCollapse: 'collapse', fontSize: 11, minWidth: '100%', border: '1px solid #f0f0f0' }}>
                        <thead>
                          <tr>
                            <th style={{ padding: '8px', background: '#fafafa', borderBottom: '2px solid #1890ff', position: 'sticky', left: 0, zIndex: 10 }}>Từ\Đến</th>
                            {m.labels.map((label, j) => (
                              <th key={j} style={{ padding: '8px', background: '#fafafa', borderBottom: '2px solid #1890ff', textAlign: 'center' }}>{label}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {m.matrix.map((row, i) => {
                            const maxVal = Math.max(...m.matrix.flat().filter(v => v > 0)) || 1;
                            return (
                              <tr key={i}>
                                <td style={{ padding: '8px', fontWeight: 700, background: i === 0 ? '#fff7e6' : '#fafafa', borderBottom: '1px solid #f0f0f0', position: 'sticky', left: 0, zIndex: 9 }}>
                                  {m.labels[i]}
                                </td>
                                {row.map((val, j) => (
                                  <td key={j} style={{ padding: '8px', textAlign: 'center', borderBottom: '1px solid #f0f0f0', backgroundColor: getCellColor(val, maxVal), color: val === 0 ? '#ccc' : '#333' }}>
                                    {val === 0 ? '—' : val}
                                  </td>
                                ))}
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>Không có đơn hàng nào tại kho này để hiển thị ma trận.</div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Reports;
