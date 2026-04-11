import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix marker icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

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

const RouteMap = ({ warehouses = [], orders = [], routes = [], center = [10.8231, 106.6297] }) => {
  return (
    <MapContainer center={center} zoom={10} style={{ height: '100%', width: '100%' }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        maxZoom={22}
        maxNativeZoom={20}
      />
      
      {/* Warehouse markers */}
      {warehouses.map((warehouse) => (
        warehouse.latitude && warehouse.longitude && (
          <Marker
            key={warehouse.id}
            position={[warehouse.latitude, warehouse.longitude]}
            icon={warehouseIcon}
          >
            <Popup>
              <strong>{warehouse.name}</strong>
              <br />
              {warehouse.address}
            </Popup>
          </Marker>
        )
      ))}
      
      {/* Order/Delivery markers */}
      {orders.map((order) => (
        order.delivery_latitude && order.delivery_longitude && (
          <Marker
            key={order.id}
            position={[order.delivery_latitude, order.delivery_longitude]}
            icon={deliveryIcon}
          >
            <Popup>
              <strong>{order.code}</strong>
              <br />
              {order.customer_name}
              <br />
              {order.customer_address}
            </Popup>
          </Marker>
        )
      ))}
      
      {/* Route lines */}
      {routes.map((route, index) => (
        route.stops && route.stops.length > 1 && (
          <Polyline
            key={route.id || index}
            positions={route.stops
              .filter(s => s.latitude && s.longitude)
              .map(s => [s.latitude, s.longitude])}
            color={['blue', 'green', 'red', 'purple', 'orange'][index % 5]}
            weight={3}
          />
        )
      ))}
    </MapContainer>
  );
};

export default RouteMap;
