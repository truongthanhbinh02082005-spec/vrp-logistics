import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, Modal, Form, Input, InputNumber, Select, Space, message, Typography, Tag, Popconfirm, Row, Col, Upload, Card, Statistic, Divider } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, UploadOutlined, SearchOutlined, FileExcelOutlined, EnvironmentOutlined } from '@ant-design/icons';
import { orderAPI, warehouseAPI } from '../../services/api';
import * as XLSX from 'xlsx';
import { geocodeAddress } from '../../services/utils';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Search } = Input;

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [filteredOrders, setFilteredOrders] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [editingOrder, setEditingOrder] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [searchText, setSearchText] = useState('');
  const [importedData, setImportedData] = useState([]);
  const [geocoding, setGeocoding] = useState(false);
  const [selectedImportWarehouse, setSelectedImportWarehouse] = useState(null); // Warehouse for batch import
  const [form] = Form.useForm();

  const fetchOrders = useCallback(async () => {
    try {
      const params = statusFilter ? { status: statusFilter } : {};
      const response = await orderAPI.getAll(params);
      setOrders(response.data);
      setFilteredOrders(response.data);
    } catch (error) {
      message.error('Không thể tải danh sách đơn hàng!');
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  const fetchWarehouses = async () => {
    try {
      const response = await warehouseAPI.getAll();
      setWarehouses(response.data.filter(w => 
        !w.name.toLowerCase().includes('tphcm') && 
        !w.name.toLowerCase().includes('đà nẵng') &&
        !w.name.toLowerCase().includes('da nang') &&
        !w.name.toLowerCase().includes('hcm')
      ));
    } catch (error) {
      console.error('Failed to fetch warehouses');
    }
  };

  useEffect(() => {
    fetchOrders();
    fetchWarehouses();
  }, [fetchOrders]);

  useEffect(() => {
    if (searchText) {
      const filtered = orders.filter(o =>
        o.code?.toLowerCase().includes(searchText.toLowerCase()) ||
        o.customer_name?.toLowerCase().includes(searchText.toLowerCase())
      );
      setFilteredOrders(filtered);
    } else {
      setFilteredOrders(orders);
    }
  }, [searchText, orders]);

  const handleAdd = () => {
    setEditingOrder(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingOrder(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await orderAPI.delete(id);
      message.success('Xóa đơn hàng thành công!');
      fetchOrders();
    } catch (error) {
      message.error('Không thể xóa đơn hàng!');
    }
  };

  const handleDeleteAll = async () => {
    try {
      const response = await orderAPI.deleteAll();
      message.success(response.data.message || 'Đã xóa tất cả đơn hàng!');
      fetchOrders();
    } catch (error) {
      message.error('Không thể xóa đơn hàng!');
    }
  };

  const handleSubmit = async (values) => {
    try {
      // Auto-generate coordinates if missing (Simulation for Map)
      if (!values.delivery_latitude && !values.delivery_longitude) {
        if (editingOrder && editingOrder.delivery_lat) {
          values.delivery_latitude = editingOrder.delivery_lat;
          values.delivery_longitude = editingOrder.delivery_lng;
        } else {
          // Random HCM coordinates
          const minLat = 10.72; const maxLat = 10.85;
          const minLng = 106.60; const maxLng = 106.75;
          values.delivery_latitude = (minLat + Math.random() * (maxLat - minLat)).toFixed(6);
          values.delivery_longitude = (minLng + Math.random() * (maxLng - minLng)).toFixed(6);
        }
      }
      if (editingOrder) {
        await orderAPI.update(editingOrder.id, values);
        message.success('Cập nhật đơn hàng thành công!');
      } else {
        await orderAPI.create(values);
        message.success('Thêm đơn hàng thành công!');
      }
      setModalVisible(false);
      fetchOrders();
    } catch (error) {
      message.error('Có lỗi xảy ra!');
    }
  };



  const handleGeocode = async () => {
    const address = form.getFieldValue('customer_address');
    if (!address) {
      message.warning('Vui lòng nhập địa chỉ trước!');
      return;
    }
    setGeocoding(true);
    try {
      const result = await geocodeAddress(address);
      if (result) {
        form.setFieldsValue({
          delivery_latitude: result.lat,
          delivery_longitude: result.lng
        });
        message.success('Đã tìm thấy tọa độ!');
      } else {
        message.error('Không tìm thấy tọa độ!');
      }
    } catch (error) {
      message.error('Lỗi khi lấy tọa độ!');
    } finally {
      setGeocoding(false);
    }
  };

  const handleUpload = async (info) => {
    const file = info.file;
    if (info.file.status === 'uploading') return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

        const rows = jsonData.slice(1); // Skip header

        if (rows.length === 0) {
          message.warning('File không có dữ liệu!');
          return;
        }

        const ordersToPreview = rows.map((row, index) => {
          // File format 8 cột: customer_name | customer_phone | customer_address | notes | quantity | cod_amount | weight | volume
          return {
            key: index,
            customer_name: row[0] || '',
            customer_phone: row[1] ? String(row[1]) : '',
            customer_address: row[2] || '',
            notes: row[3] || '',
            quantity: parseInt(row[4]) || 1,
            cod_amount: parseFloat(row[5]) || 0,
            weight: parseFloat(row[6]) || 0,
            volume: parseFloat(row[7]) || 0,
            status: 'pending'
          };
        }).filter(o => o.customer_address && o.customer_name);

        if (ordersToPreview.length === 0) {
          message.error('Không đọc được dữ liệu. Vui lòng kiểm tra cột Địa chỉ.');
          return;
        }

        setImportedData(ordersToPreview);
        message.success(`Đã đọc ${ordersToPreview.length} dòng.Vui lòng kiểm tra và xác nhận.`);
      } catch (error) {
        console.error(error);
        message.error('Lỗi đọc file!');
      }
    };
    reader.readAsArrayBuffer(file);
  };

  const handleImportConfirm = async () => {
    if (importedData.length === 0 || !selectedImportWarehouse) return;

    // Step 1: Check capacity based on VOLUME (m³)
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      const res = await fetch(`/api/orders/capacity/${selectedImportWarehouse}/`, { headers });

      if (res.ok) {
        const capacity = await res.json();
        // Tính tổng volume sẽ import (mỗi đơn default 0.01 m³ nếu không có)
        const totalImportVolume = importedData.reduce((sum, item) => sum + (parseFloat(item.volume) || 0.01), 0);
        const remainingVolume = capacity.remaining_volume;

        // Nếu volume import vượt quá sức chứa còn lại -> Cảnh báo
        if (totalImportVolume > remainingVolume) {
          const confirmed = window.confirm(
            `⚠️ CẢNH BÁO QUÁ TẢI KHO!\n\n` +
            `Kho: ${capacity.warehouse_name}\n` +
            `Sức chứa còn lại: ${remainingVolume.toFixed(2)} m³\n` +
            `Tổng thể tích import: ${totalImportVolume.toFixed(2)} m³\n` +
            `Vượt quá: ${(totalImportVolume - remainingVolume).toFixed(2)} m³\n\n` +
            `Bạn có muốn tiếp tục không?`
          );

          if (!confirmed) {
            message.info('Đã hủy import.');
            return;
          }
        }
      }
    } catch (e) {
      console.error('Capacity check failed:', e);
      // Nếu lỗi check thì vẫn cho import (fallback)
    }

    // Step 2: Proceed with BULK import (1 request instead of N requests)
    setLoading(true);
    message.loading(`Đang import ${importedData.length} đơn hàng...`, 0);

    try {
      // Xác định vùng tọa độ dựa vào kho đã chọn
      const selectedWarehouseData = warehouses.find(w => w.id === selectedImportWarehouse);
      let latRange = { min: 10.72, max: 10.85 };  // Default: TPHCM
      let lngRange = { min: 106.60, max: 106.75 };

      if (selectedWarehouseData) {
        const whName = selectedWarehouseData.name.toLowerCase();
        if (whName.includes('cần thơ') || whName.includes('can tho')) {
          // Cần Thơ
          latRange = { min: 10.00, max: 10.08 };
          lngRange = { min: 105.70, max: 105.80 };
        } else if (whName.includes('đà nẵng') || whName.includes('da nang')) {
          // Đà Nẵng
          latRange = { min: 16.00, max: 16.10 };
          lngRange = { min: 108.15, max: 108.25 };
        }
        // TPHCM giữ nguyên default
      }

      // Prepare orders for bulk API
      const ordersToImport = importedData.map(item => ({
        customer_name: item.customer_name,
        customer_phone: item.customer_phone,
        customer_address: item.customer_address,
        cod_amount: item.cod_amount || 0,
        weight: parseFloat(item.weight) || 1.0,
        volume: parseFloat(item.volume) || 0.01,
        notes: item.notes || 'Hàng hóa',
        delivery_latitude: (latRange.min + Math.random() * (latRange.max - latRange.min)).toFixed(6),
        delivery_longitude: (lngRange.min + Math.random() * (lngRange.max - lngRange.min)).toFixed(6),
      }));

      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/orders/bulk/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          orders: ordersToImport,
          warehouse_id: selectedImportWarehouse
        })
      });

      message.destroy(); // Clear loading message
      const result = await response.json();

      if (response.ok) {
        setImportedData([]);
        setSelectedImportWarehouse(null);
        message.success(`Hoàn tất! ${result.success}/${result.total} đơn thành công`);
        fetchOrders();
      } else {
        message.error(result.error || 'Import thất bại');
      }
    } catch (error) {
      message.destroy();
      console.error('Bulk import error:', error);
      message.error('Có lỗi xảy ra khi import!');
    }

    setLoading(false);
    setImportModalVisible(false);
  };

  const stats = {
    total: orders.length,
    pending: orders.filter(o => o.status === 'pending').length,
    delivered: orders.filter(o => o.status === 'delivered').length,
    inTransit: orders.filter(o => o.status === 'in_transit').length,
  };

  const statusColors = {
    pending: 'gold',
    confirmed: 'blue',
    assigned: 'cyan',
    picked_up: 'geekblue',
    in_transit: 'purple',
    delivered: 'green',
    cancelled: 'red',
    failed: 'volcano',
  };

  const statusLabels = {
    pending: 'Chờ xử lý',
    confirmed: 'Đã xác nhận',
    assigned: 'Đã phân công',
    picked_up: 'Đã lấy hàng',
    in_transit: 'Đang giao',
    delivered: 'Đã giao',
    cancelled: 'Đã hủy',
    failed: 'Thất bại',
  };

  const columns = [
    {
      title: 'Mã đơn',
      dataIndex: 'code',
      key: 'code',
      width: 150,
    },
    {
      title: 'Khách hàng',
      dataIndex: 'customer_name',
      key: 'customer_name',
    },
    {
      title: 'SĐT',
      dataIndex: 'customer_phone',
      key: 'customer_phone',
      width: 120,
    },
    {
      title: 'Địa chỉ',
      dataIndex: 'customer_address',
      key: 'customer_address',
      ellipsis: true,
    },
    {
      title: 'Tên hàng',
      dataIndex: 'notes',
      key: 'notes',
      width: 150,
      ellipsis: true,
      render: (val) => {
        if (!val) return '-';
        try {
          const items = JSON.parse(val);
          return items.map(i => i.name).join(', ');
        } catch {
          return val; // Nếu không phải JSON thì hiện raw
        }
      },
    },
    {
      title: 'Kênh',
      dataIndex: 'channel',
      key: 'channel',
      width: 80,
      render: (val) => val || '-',
    },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => <Tag color={statusColors[status]}>{statusLabels[status]}</Tag>,
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
      {/* Stats Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="Tổng đơn hàng" value={stats.total} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Chờ xử lý" value={stats.pending} styles={{ content: { color: '#faad14' } }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Đang giao" value={stats.inTransit} styles={{ content: { color: '#722ed1' } }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Đã giao" value={stats.delivered} styles={{ content: { color: '#52c41a' } }} />
          </Card>
        </Col>
      </Row>

      {/* Header with actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 8 }}>
        <Title level={3} style={{ margin: 0 }}>Quản lý Đơn hàng</Title>
        <Space wrap>
          <Search
            placeholder="Tìm theo mã đơn, khách hàng..."
            allowClear
            style={{ width: 250 }}
            onSearch={setSearchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <Select
            style={{ width: 150 }}
            placeholder="Lọc trạng thái"
            allowClear
            value={statusFilter || undefined}
            onChange={(val) => setStatusFilter(val || '')}
          >
            {Object.entries(statusLabels).map(([key, label]) => (
              <Select.Option key={key} value={key}>{label}</Select.Option>
            ))}
          </Select>
          <Button icon={<UploadOutlined />} onClick={() => setImportModalVisible(true)}>
            Import Excel
          </Button>
          <Popconfirm
            title="Xóa đơn hàng chưa giao?"
            description="Sẽ xóa tất cả đơn chưa giao (pending, assigned, in_transit). Đơn đã giao sẽ được giữ lại!"
            onConfirm={handleDeleteAll}
            okText="Xóa"
            cancelText="Hủy"
            okButtonProps={{ danger: true }}
          >
            <Button danger icon={<DeleteOutlined />}>
              Xóa đơn chưa giao
            </Button>
          </Popconfirm>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            Tạo đơn
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={filteredOrders}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      {/* Upload Modal */}
      <Modal
        title="Import đơn hàng từ Excel/PDF"
        open={importModalVisible}
        onCancel={() => setImportModalVisible(false)}
        footer={null}
        width={500}
      >
        <div style={{ padding: 24 }}>
          {importedData.length === 0 ? (
            <div style={{ textAlign: 'center' }}>
              <FileExcelOutlined style={{ fontSize: 64, color: '#52c41a', marginBottom: 16 }} />
              <p>Upload file Excel (Tên | SĐT | Địa chỉ | COD | Ghi chú)</p>
              <Upload
                accept=".xlsx,.xls,.csv"
                showUploadList={false}
                beforeUpload={() => false}
                onChange={handleUpload}
              >
                <Button icon={<UploadOutlined />} size="large" type="primary">
                  Chọn file
                </Button>
              </Upload>
            </div>
          ) : (
            <>
              {/* Bước 1: Chọn Kho cho tất cả đơn */}
              <div style={{ marginBottom: 16, padding: 12, background: '#fffbe6', borderRadius: 8, border: '1px solid #ffe58f' }}>
                <Text strong style={{ display: 'block', marginBottom: 8 }}>⚠️ Chọn Kho chứa cho {importedData.length} đơn hàng này:</Text>
                <Select
                  style={{ width: '100%' }}
                  placeholder="Chọn kho"
                  value={selectedImportWarehouse}
                  onChange={setSelectedImportWarehouse}
                >
                  {warehouses.map(w => (
                    <Select.Option key={w.id} value={w.id}>{w.name}</Select.Option>
                  ))}
                </Select>
              </div>

              <Table
                dataSource={importedData}
                pagination={{ pageSize: 5 }}
                scroll={{ y: 200 }}
                size="small"
                columns={[
                  { title: 'Tên', dataIndex: 'customer_name', key: 'name' },
                  { title: 'SĐT', dataIndex: 'customer_phone', key: 'phone' },
                  { title: 'Địa chỉ', dataIndex: 'customer_address', key: 'address', ellipsis: true },
                  { title: 'COD', dataIndex: 'cod_amount', key: 'cod' },
                ]}
              />
              <div style={{ marginTop: 16, textAlign: 'right' }}>
                <Space>
                  <Button onClick={() => { setImportedData([]); setSelectedImportWarehouse(null); }}>Chọn lại</Button>
                  <Button
                    type="primary"
                    onClick={handleImportConfirm}
                    loading={loading}
                    disabled={!selectedImportWarehouse}
                  >
                    Xác nhận Import ({importedData.length})
                  </Button>
                </Space>
              </div>
            </>
          )}
        </div>
      </Modal>

      {/* Add/Edit Order Modal */}
      <Modal
        title={editingOrder ? 'Sửa đơn hàng' : 'Thêm đơn hàng mới'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={700}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="customer_name" label="Tên khách hàng" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="customer_phone" label="SĐT" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="channel" label="Kênh bán hàng">
                <Select placeholder="Chọn kênh">
                  <Select.Option value="online">Online</Select.Option>
                  <Select.Option value="offline">Offline</Select.Option>
                  <Select.Option value="shopee">Shopee</Select.Option>
                  <Select.Option value="lazada">Lazada</Select.Option>
                  <Select.Option value="tiktok">TikTok Shop</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="warehouse_id"
                label="Kho hàng (Bắt buộc)"
                rules={[{ required: true, message: 'Vui lòng chọn kho!' }]}
                tooltip="Đơn hàng sẽ được xếp vào kho này"
              >
                <Select placeholder="Chọn kho chứa đơn">
                  {warehouses.map(w => (
                    <Select.Option key={w.id} value={w.id}>{w.name}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Form.Item label="Địa chỉ giao">
            <Space.Compact style={{ width: '100%' }}>
              <Form.Item
                name="customer_address"
                noStyle
                rules={[{ required: true, message: 'Vui lòng nhập địa chỉ' }]}
              >
                <TextArea rows={2} placeholder="Nhập địa chỉ..." />
              </Form.Item>
              <Button onClick={handleGeocode} loading={geocoding} icon={<EnvironmentOutlined />} type="primary">Lấy tọa độ</Button>
            </Space.Compact>
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="delivery_latitude" label="Vĩ độ">
                <InputNumber style={{ width: '100%' }} step={0.000001} placeholder="Ví dụ: 10.762..." />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="delivery_longitude" label="Kinh độ">
                <InputNumber style={{ width: '100%' }} step={0.000001} placeholder="Ví dụ: 106.660..." />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={24}>
              <Form.Item name="cod_amount" label="Tiền COD">
                <InputNumber style={{ width: '100%' }} min={0} formatter={v => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="notes" label="Ghi chú / Items">
            <TextArea rows={2} placeholder="Mô tả hàng hóa..." />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingOrder ? 'Cập nhật' : 'Tạo đơn'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>Hủy</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal >
    </div >
  );
};

export default Orders;
