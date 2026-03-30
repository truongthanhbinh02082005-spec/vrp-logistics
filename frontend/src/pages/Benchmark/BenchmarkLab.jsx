import React, { useState, useEffect } from 'react';
import {
  Table, Button, Card, Row, Col, Typography, Tag, Space, Spin, Alert,
  Statistic, Progress, Divider, Tooltip, Badge, Tabs, InputNumber, message
} from 'antd';
import {
  PlayCircleOutlined, ThunderboltOutlined, AimOutlined, BarChartOutlined,
  LoadingOutlined, CheckCircleOutlined, InfoCircleOutlined,
  ExperimentOutlined, TableOutlined, EnvironmentOutlined
} from '@ant-design/icons';
import { benchmarkAPI } from '../../services/api';
import { MapContainer, Marker, Popup, Polyline, Tooltip as LeafletTooltip, useMap } from 'react-leaflet';
import L, { CRS } from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const depotIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const customerIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [20, 32],
  iconAnchor: [10, 32],
  popupAnchor: [1, -34],
  shadowSize: [32, 32]
});

const { Title, Text } = Typography;

// ─── Color helpers ──────────────────────────────────────────────────
const gapColor = (gap) => {
  if (gap === null || gap === undefined) return '#999';
  if (gap <= 5) return '#52c41a';
  if (gap <= 15) return '#faad14';
  return '#ff4d4f';
};

const fillColor = (f) => {
  if (f >= 85) return '#52c41a';
  if (f >= 60) return '#faad14';
  return '#ff4d4f';
};

const getCellColor = (val, max) => {
  if (val === 0) return '#f0f0f0';
  const ratio = val / max;
  const r = Math.round(255 * ratio);
  const g = Math.round(180 * (1 - ratio));
  return `rgba(${r}, ${g}, 80, 0.3)`;
};

const FitBounds = ({ points }) => {
  const map = useMap();
  useEffect(() => {
    if (points && points.length > 0) {
      try {
        const bounds = L.latLngBounds(points);
        map.fitBounds(bounds, { padding: [50, 50], animate: false });
      } catch (err) {
        console.error('Benchmark FitBounds error:', err);
      }
    }
  }, [map, points]);
  return null;
};

const BenchmarkMap = ({ result, height = 600, isBaseline = false }) => {
  if (!result || !result.nodes_coord) return null;
  
  const routes = isBaseline ? (result.baseline_routes || []) : (result.routes || []);
  const { nodes_coord } = result;
  
  const nodeLookup = nodes_coord.reduce((acc, n) => {
    acc[n.id] = [n.y, n.x]; 
    return acc;
  }, {});

  const points = nodes_coord.map(n => [n.y, n.x]);
  const colors = ['#1890ff', '#52c41a', '#722ed1', '#fa8c16', '#eb2f96', '#2f54eb', '#faad14', '#13c2c2'];
  const depotNode = nodes_coord.find(n => n.is_depot);

  return (
    <div style={{ height, border: '1px solid #f0f0f0', borderRadius: 8, overflow: 'hidden', position: 'relative' }}>
      <MapContainer 
        key={`benchmark-map-${result.instance}-${height}-${isBaseline}`}
        crs={CRS.Simple} 
        center={[0, 0]} 
        zoom={1} 
        style={{ height: '100%', width: '100%', background: '#fff' }}
      >
        <FitBounds points={points} />
        
        {routes.map((r, idx) => {
          const path = [];
          if (depotNode && nodeLookup[depotNode.id]) path.push(nodeLookup[depotNode.id]);
          
          r.stops.forEach(nodeId => {
            if (nodeLookup[nodeId]) path.push(nodeLookup[nodeId]);
          });
          
          if (depotNode && nodeLookup[depotNode.id]) path.push(nodeLookup[depotNode.id]);

          return (
            <Polyline 
              key={`route-${r.route_id || idx}`} 
              positions={path} 
              color={isBaseline ? '#8c8c8c' : colors[idx % colors.length]} 
              weight={isBaseline ? 2 : 3} 
              dashArray={isBaseline ? '5, 5' : ''}
              opacity={0.8}
            >
              <Popup>
                <div style={{ padding: 4 }}>
                  <Title level={5}>{isBaseline ? 'Lộ trình Baseline' : `Lộ trình tối ưu #${r.route_id}`}</Title>
                  <Text>Khoảng cách: <b>{r.distance}</b> units</Text><br/>
                  <Text>Số điểm giao: <b>{r.num_stops}</b></Text>
                </div>
              </Popup>
            </Polyline>
          );
        })}

        {nodes_coord.map(node => {
          const lat = parseFloat(node.y);
          const lng = parseFloat(node.x);
          if (isNaN(lat) || isNaN(lng)) return null;
          return (
            <Marker 
              key={`node-${node.id}`} 
              position={[lat, lng]} 
              icon={node.is_depot ? depotIcon : customerIcon}
            >
            <Popup>
              <div style={{ padding: 4 }}>
                <Title level={5}>{node.is_depot ? '🏁 KHO (Depot)' : `👤 Khách hàng #${node.id}`}</Title>
                <Text>Tọa độ: <b>({node.x}, {node.y})</b></Text><br/>
                <Text>Nhu cầu: <b>{node.demand}</b></Text>
              </div>
            </Popup>
            <LeafletTooltip direction="top" offset={[0, -20]} opacity={0.9} permanent={node.is_depot}>
              {node.is_depot ? 'DEPOT' : `C${node.id}`}
            </LeafletTooltip>
          </Marker>
          );
        })}
      </MapContainer>
      {isBaseline && <div style={{ position: 'absolute', top: 10, right: 10, zIndex: 1000, background: 'rgba(255,255,255,0.8)', padding: '2px 8px', borderRadius: 4, border: '1px solid #ccc' }}>Baseline (Tham chiếu)</div>}
    </div>
  );
};

const MetricsCard = ({ result }) => {
  if (!result) return null;
  const { metrics, results, instance, routes, distance_matrix, comment } = result;

  return (
    <div style={{ padding: '0 8px' }}>
      <Alert 
        type="info" 
        showIcon 
        style={{ marginBottom: 16 }}
        message={<Text strong>{instance} — {comment}</Text>}
      />

      <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card size="small" style={{ background: '#f6ffed' }}>
            <Statistic title="OR-Tools (Tối ưu)" value={results.ortools_cost} suffix="units"
              styles={{ content: { color: '#389e0d', fontWeight: 700 } }} />
            {results.bks_cost && <Text type="secondary" style={{ fontSize: 11 }}>BKS: {results.bks_cost}</Text>}
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small" style={{ background: '#fff7e6' }}>
            <Statistic title="Baseline (Simulation)" value={results.baseline_cost} suffix="units"
              styles={{ content: { color: '#d46b08', fontWeight: 700 } }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title={<>Cải thiện (Gap) <Tooltip title="(Baseline - OR-Tools) / Baseline × 100%"><InfoCircleOutlined /></Tooltip></>}
              value={metrics.gap_vs_baseline_pct} suffix="%"
              styles={{ content: { color: gapColor(metrics.gap_vs_baseline_pct), fontWeight: 700 } }}
            />
            {metrics.gap_vs_bks_pct !== null && (
              <Text style={{ fontSize: 11, color: gapColor(metrics.gap_vs_bks_pct) }}>
                vs BKS: {metrics.gap_vs_bks_pct >= 0 ? '+' : ''}{metrics.gap_vs_bks_pct}%
              </Text>
            )}
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic title="Hệ số lấp đầy" value={metrics.fill_factor_pct} suffix="%" styles={{ content: { color: fillColor(metrics.fill_factor_pct), fontWeight: 700 } }} />
            <Progress percent={metrics.fill_factor_pct} showInfo={false} strokeColor={fillColor(metrics.fill_factor_pct)} size="small" />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title={<Space><EnvironmentOutlined /> Bản đồ OR-Tools (Tối ưu)</Space>} size="small">
            <BenchmarkMap result={result} height={400} isBaseline={false} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title={<Space><EnvironmentOutlined /> Bản đồ Baseline (Mặc định)</Space>} size="small">
            <BenchmarkMap result={result} height={400} isBaseline={true} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={24}>
          <Card title={<Space><AimOutlined /> Ma trận Khoảng cách EUC_2D</Space>} size="small">
            {distance_matrix ? (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ borderCollapse: 'collapse', fontSize: 11, minWidth: '100%', border: '1px solid #f0f0f0' }}>
                  <thead>
                    <tr>
                      <th style={{ padding: '4px 8px', background: '#fafafa', borderBottom: '2px solid #1890ff', position: 'sticky', left: 0, zIndex: 10 }}>Từ\Đến</th>
                      {distance_matrix.labels.map((label, j) => (
                        <th key={j} style={{ padding: '4px 8px', background: '#fafafa', borderBottom: '2px solid #1890ff', textAlign: 'center' }}>{label}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {distance_matrix.matrix.map((row, i) => {
                      const maxVal = Math.max(...distance_matrix.matrix.flat().filter(v => v > 0));
                      return (
                        <tr key={i}>
                          <td style={{ padding: '4px 8px', fontWeight: 700, background: i === 0 ? '#fff3e0' : '#fafafa', borderBottom: '1px solid #f0f0f0', position: 'sticky', left: 0, zIndex: 9 }}>
                            {distance_matrix.labels[i]}
                          </td>
                          {row.map((val, j) => (
                            <td key={j} style={{ padding: '4px 8px', textAlign: 'center', borderBottom: '1px solid #f0f0f0', backgroundColor: getCellColor(val, maxVal), color: val === 0 ? '#ccc' : '#333' }}>
                              {val === 0 ? '—' : val}
                            </td>
                          ))}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : <Alert type="warning" message="Không có dữ liệu ma trận khoảng cách" />}
          </Card>
        </Col>
      </Row>

      <Card title={<Space><TableOutlined /> Chi tiết lộ trình tối ưu</Space>} size="small">
        <Table size="small" dataSource={routes} rowKey="route_id" pagination={false} columns={[
          { title: 'Xe', dataIndex: 'route_id', key: 'rid', width: 60, render: v => <b>#{v}</b> },
          { title: 'Thứ tự giao', dataIndex: 'stops', key: 'stops', render: (nodes) => <Text style={{ fontSize: 11 }}>{nodes.join(' → ')}</Text> },
          { title: 'Độ dài', dataIndex: 'distance', key: 'dist', width: 100, align: 'right' },
          { title: 'Lấp đầy', key: 'fill', width: 120, render: (_, r) => <Progress percent={r.fill_pct} size="small" strokeColor={fillColor(r.fill_pct)} /> },
        ]} />
      </Card>
    </div>
  );
};

const BenchmarkLab = () => {
  const [instances, setInstances] = useState([]);
  const [loadingInstances, setLoadingInstances] = useState(false);
  const [runningInstance, setRunningInstance] = useState(null);
  const [runningAll, setRunningAll] = useState(false);
  const [timeLimit, setTimeLimit] = useState(15);
  const [singleResult, setSingleResult] = useState(null);
  const [allResults, setAllResults] = useState([]);
  const [activeTab, setActiveTab] = useState('instances');
  const [hasSavedAll, setHasSavedAll] = useState(false);
  const [lastRunDate, setLastRunDate] = useState(null);
  const [savedAllResults, setSavedAllResults] = useState([]);

  useEffect(() => {
    fetchInstances();
  }, []);

  const fetchInstances = async () => {
    setLoadingInstances(true);
    try {
      const res = await benchmarkAPI.listInstances();
      setInstances(res.data.instances || []);
      setHasSavedAll(res.data.has_saved_all || false);
      setLastRunDate(res.data.last_run_date || null);
      setSavedAllResults(res.data.saved_all_results || []);
    } catch (e) {
      message.error('Không thể tải danh sách benchmark: ' + (e.response?.data?.error || e.message));
    } finally {
      setLoadingInstances(false);
    }
  };

  const handleRunSingle = async (name) => {
    setRunningInstance(name);
    setSingleResult(null);
    setActiveTab('result');
    try {
      const res = await benchmarkAPI.runInstance({ name, time_limit: timeLimit });
      setSingleResult(res.data);
    } catch (e) {
      message.error('Lỗi khi chạy ' + name + ': ' + (e.response?.data?.error || e.message));
      setActiveTab('instances');
    } finally {
      setRunningInstance(null);
    }
  };
  const handleViewSavedAll = () => {
    setAllResults(savedAllResults);
    setActiveTab('all');
  };

  const handleRunAll = async () => {
    setRunningAll(true);
    setAllResults([]);
    setActiveTab('all');
    try {
      const res = await benchmarkAPI.runAll({ time_limit: timeLimit });
      setAllResults(res.data.results || []);
    } catch (e) {
      message.error('Lỗi khi chạy tất cả: ' + (e.response?.data?.error || e.message));
    } finally {
      setRunningAll(false);
    }
  };

  const instanceColumns = [
    { title: 'Tên', dataIndex: 'name', key: 'name', render: (name) => <b style={{ fontFamily: 'monospace' }}>{name}</b> },
    { title: 'n (khách)', dataIndex: 'dimension', key: 'dim', width: 90, render: v => v - 1 },
    { title: 'k (xe)', dataIndex: 'num_trucks', key: 'k', width: 70 },
    { title: 'Sức chứa/xe', dataIndex: 'capacity', key: 'cap', width: 100 },
    { title: 'BKS (tối ưu)', dataIndex: 'bks', key: 'bks', width: 110, render: v => v ? <Tag color="blue">{v}</Tag> : <Text type="secondary">—</Text> },
    {
      title: 'Hành động', key: 'action', width: 200,
      render: (_, record) => (
        <Space>
          <Tooltip title={record.last_run ? `Chạy gần nhất: ${new Date(record.last_run).toLocaleString()}` : ''}>
            <Button type="primary" size="small"
              icon={runningInstance === record.name ? <LoadingOutlined /> : <PlayCircleOutlined />}
              loading={runningInstance === record.name}
              disabled={!!runningInstance || runningAll}
              onClick={() => handleRunSingle(record.name)}
            >Chạy</Button>
          </Tooltip>
        </Space>
      )
    },
  ];

  const allResultColumns = [
    { title: 'Instance', dataIndex: 'name', key: 'name', fixed: 'left', width: 130, render: v => <b style={{ fontFamily: 'monospace', fontSize: 12 }}>{v}</b> },
    { title: 'n', dataIndex: 'n', key: 'n', width: 50 },
    { title: 'k', dataIndex: 'k', key: 'k', width: 45 },
    { title: 'BKS', dataIndex: 'bks', key: 'bks', width: 65, render: v => v ?? '—' },
    { title: 'Baseline', dataIndex: 'baseline', key: 'base', width: 80 },
    {
      title: 'OR-Tools', dataIndex: 'ortools', key: 'ort', width: 85,
      render: (v, r) => <span style={{ fontWeight: 700, color: v <= r.baseline ? '#52c41a' : '#ff4d4f' }}>{v}</span>
    },
    {
      title: 'Gap vs Baseline', dataIndex: 'gap_vs_baseline_pct', key: 'gapb', width: 120,
      render: v => <Tag color={v > 0 ? 'green' : 'orange'}>{v >= 0 ? '+' : ''}{v}%</Tag>
    },
    {
      title: 'Gap vs BKS', dataIndex: 'gap_vs_bks_pct', key: 'gapbks', width: 100,
      render: v => v !== null && v !== undefined
        ? <Tag color={v <= 5 ? 'green' : v <= 15 ? 'orange' : 'red'}>{v >= 0 ? '+' : ''}{v}%</Tag>
        : <Text type="secondary">—</Text>
    },
    {
      title: 'Fill Factor', dataIndex: 'fill_factor_pct', key: 'fill', width: 120,
      render: v => <Progress percent={v} size="small" strokeColor={fillColor(v)} format={p => `${p}%`} />,
      sorter: (a, b) => a.fill_factor_pct - b.fill_factor_pct,
    },
    {
      title: 'Mật độ', dataIndex: 'density', key: 'dens', width: 90,
      render: v => v?.toFixed(4) ?? '—',
      sorter: (a, b) => a.density - b.density,
    },
    { title: 'Xe dùng', dataIndex: 'vehicles_used', key: 'veh', width: 80, render: (v, r) => `${v}/${r.k}` },
    {
      title: 'Trạng thái', dataIndex: 'error', key: 'err', width: 100,
      render: v => v
        ? <Text type="danger" style={{ fontSize: 11 }}>❌ {v}</Text>
        : <CheckCircleOutlined style={{ color: '#52c41a' }} />
    },
  ];

  const summaryStats = allResults.filter(r => !r.error);
  const avgGapBks = summaryStats.filter(r => r.gap_vs_bks_pct !== null && r.gap_vs_bks_pct !== undefined).map(r => r.gap_vs_bks_pct);
  const avgGapBaseline = summaryStats.map(r => r.gap_vs_baseline_pct);
  const avgFill = summaryStats.map(r => r.fill_factor_pct);
  const mean = arr => arr.length ? (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(2) : '—';

  const tabItems = [
    {
      key: 'instances',
      label: <><TableOutlined /> Danh sách Instance ({instances.length})</>,
      children: (
        <Card size="small">
          <Alert type="info" showIcon style={{ marginBottom: 12 }}
            message={
              <span>
                <b>{instances.length}</b> instances từ tập dữ liệu chuẩn Augerat A-series.
                Mỗi instance có <b>BKS</b> (Best Known Solution) — nghiệm tốt nhất đã biết.
                Chọn một instance và nhấn <b>Chạy</b> để xem kết quả chi tiết.
              </span>
            }
          />
          <Table dataSource={instances} columns={instanceColumns} rowKey="name"
            loading={loadingInstances} size="small" pagination={{ pageSize: 30 }} />
        </Card>
      ),
    },
    {
      key: 'result',
      label: (
        <>
          <BarChartOutlined /> Kết quả đơn
          {singleResult && <Badge count="✓" style={{ backgroundColor: '#52c41a', marginLeft: 6 }} />}
          {runningInstance && <LoadingOutlined style={{ marginLeft: 6 }} />}
        </>
      ),
      children: runningInstance ? (
        <div style={{ textAlign: 'center', padding: 80 }}>
          <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
          <div style={{ marginTop: 24, fontSize: 16 }}>Đang chạy OR-Tools trên <b>{runningInstance}</b>...</div>
          <div style={{ marginTop: 8, color: '#999' }}>
            Time limit: {timeLimit}s — GUIDED_LOCAL_SEARCH + PATH_CHEAPEST_ARC
          </div>
        </div>
      ) : singleResult ? (
        <Card size="small"><MetricsCard result={singleResult} /></Card>
      ) : (
        <div style={{ textAlign: 'center', padding: 60, color: '#999' }}>
          <ExperimentOutlined style={{ fontSize: 48, opacity: 0.3 }} />
          <div style={{ marginTop: 16 }}>Chọn một instance và nhấn <b>Chạy</b> để xem kết quả</div>
        </div>
      ),
    },
    {
      key: 'map',
      label: <><EnvironmentOutlined /> Bản đồ giả lập {singleResult && <Badge dot color="#52c41a" />}</>,
      children: singleResult ? (
        <Card size="small">
          <Alert type="info" showIcon style={{ marginBottom: 12 }}
            message={<span>Mô phỏng lộ trình của <b>{singleResult.instance}</b> trên hệ tọa độ Descarte (abstract plane). Cam = Kho, Xanh = Điểm giao.</span>}
          />
          <BenchmarkMap result={singleResult} />
        </Card>
      ) : (
        <div style={{ textAlign: 'center', padding: 60, color: '#999' }}>
          <EnvironmentOutlined style={{ fontSize: 48, opacity: 0.3 }} />
          <div style={{ marginTop: 16 }}>Chạy một instance để hiển thị bản đồ mô phỏng</div>
        </div>
      ),
    },
    {
      key: 'all',
      label: (
        <>
          <ThunderboltOutlined /> Bảng so sánh tổng hợp
          {allResults.length > 0 && <Badge count={allResults.length} style={{ backgroundColor: '#722ed1', marginLeft: 6 }} />}
          {hasSavedAll && allResults.length === 0 && <Badge count="Lịch sử" style={{ backgroundColor: '#52c41a', marginLeft: 6 }} />}
          {runningAll && <LoadingOutlined style={{ marginLeft: 6 }} />}
        </>
      ),
      children: runningAll ? (
        <div style={{ textAlign: 'center', padding: 80 }}>
          <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
          <div style={{ marginTop: 24, fontSize: 16 }}>
            Đang chạy OR-Tools trên tất cả <b>{instances.length}</b> instances...
          </div>
          <div style={{ marginTop: 8, color: '#999' }}>Time limit mỗi instance: {timeLimit}s</div>
        </div>
      ) : allResults.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <Row gutter={[12, 12]}>
            <Col span={4}><Card size="small"><Statistic title="Thành công" value={summaryStats.length} suffix={`/ ${allResults.length}`} /></Card></Col>
            <Col span={5}><Card size="small"><Statistic title="Gap TB vs BKS" value={mean(avgGapBks)} suffix="%" valueStyle={{ color: gapColor(parseFloat(mean(avgGapBks))) }} /></Card></Col>
            <Col span={5}><Card size="small"><Statistic title="Gap TB vs Baseline" value={mean(avgGapBaseline)} suffix="%" valueStyle={{ color: '#52c41a' }} /></Card></Col>
            <Col span={5}><Card size="small"><Statistic title="Fill Factor TB" value={mean(avgFill)} suffix="%" valueStyle={{ color: fillColor(parseFloat(mean(avgFill))) }} /></Card></Col>
            <Col span={5}><Card size="small"><Statistic title="Lỗi" value={allResults.length - summaryStats.length} valueStyle={{ color: allResults.length - summaryStats.length > 0 ? '#ff4d4f' : '#52c41a' }} /></Card></Col>
          </Row>

          <Card size="small" title={<Space><ThunderboltOutlined /> Bảng so sánh chỉ số</Space>}>
            <Table dataSource={allResults} columns={allResultColumns} rowKey="name"
              size="small" pagination={false} scroll={{ x: 1000 }} />
          </Card>

          <Divider orientation="center" style={{ margin: '12px 0' }}>
            <Text type="secondary" strong style={{ fontSize: 14 }}>
              <BarChartOutlined /> CHI TIẾT LỘ TRÌNH & BẢN ĐỒ GIẢ LẬP
            </Text>
          </Divider>

          {allResults.filter(r => !r.error).map(res => (
            <Card key={res.name} size="small" hoverable style={{ border: '1px solid #d9d9d9' }}>
               <MetricsCard result={res} />
            </Card>
          ))}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: 60, color: '#999' }}>
          <ThunderboltOutlined style={{ fontSize: 48, opacity: 0.3 }} />
          <div style={{ marginTop: 16 }}>Nhấn <b>Chạy TẤT CẢ</b> để so sánh tất cả instances</div>
        </div>
      ),
    },
  ];

  return (
    <div style={{ padding: '0 4px' }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>
            <ExperimentOutlined /> VRP Algorithm Benchmark Lab
          </Title>
          <Text type="secondary">Augerat A-series CVRP — OR-Tools vs Nearest Neighbor Baseline</Text>
        </Col>
        <Col>
          <Space>
            <Text>Time limit:</Text>
            <InputNumber min={5} max={120} value={timeLimit} onChange={setTimeLimit} style={{ width: 80 }} />
            <Text type="secondary">s</Text>
            <Button
              type="primary"
              icon={runningAll ? <LoadingOutlined /> : <ThunderboltOutlined />}
              loading={runningAll}
              disabled={!!runningInstance}
              onClick={handleRunAll}
              style={{ background: '#722ed1', borderColor: '#722ed1' }}
            >
              Chạy TẤT CẢ ({instances.length})
            </Button>
            {hasSavedAll && (
              <Tooltip title={`Lịch sử chạy: ${new Date(lastRunDate).toLocaleString()}`}>
                 <Button onClick={handleViewSavedAll} icon={<BarChartOutlined />} style={{ borderColor: '#52c41a', color: '#52c41a' }}>
                   Xem lịch sử tổng hợp
                 </Button>
              </Tooltip>
            )}
          </Space>
        </Col>
      </Row>

      <Tabs activeKey={activeTab} onChange={setActiveTab} type="card" items={tabItems} />
    </div>
  );
};

export default BenchmarkLab;
