import React, { useState } from 'react';
import { Smartphone, Monitor, Laptop, Trash2, Shield, Wifi, WifiOff, Plus, Download, RefreshCw } from 'lucide-react';
import { useDevices } from '../hooks/useDevices';

export function DeviceManager() {
  const { devices, stats: deviceStats, isLoading, error, registerDevice, trustDevice, removeDevice, fetchDevices } = useDevices();
  const [showAddDevice, setShowAddDevice] = useState(false);
  const [newDeviceName, setNewDeviceName] = useState('');
  const [newDeviceType, setNewDeviceType] = useState<'desktop' | 'mobile' | 'tablet'>('desktop');

  const getDeviceIcon = (type: string) => {
    switch (type) {
      case 'mobile':
        return Smartphone;
      case 'tablet':
        return Laptop;
      default:
        return Monitor;
    }
  };

  const handleAddDevice = async () => {
    if (!newDeviceName.trim()) return;

    try {
      await registerDevice({
        name: newDeviceName,
        device_type: newDeviceType,
        platform: navigator.platform,
        browser: navigator.userAgent.includes('Chrome') ? 'Chrome' : 'Other',
        metadata: { source: 'manual' }
      });
      
      setNewDeviceName('');
      setShowAddDevice(false);
    } catch (error) {
      console.error('Failed to add device:', error);
    }
  };

  const handleRemoveDevice = async (deviceId: string) => {
    if (confirm('Are you sure you want to remove this device?')) {
      try {
        await removeDevice(deviceId);
      } catch (error) {
        console.error('Failed to remove device:', error);
      }
    }
  };

  const handleTrustDevice = async (deviceId: string) => {
    try {
      await trustDevice(deviceId);
    } catch (error) {
      console.error('Failed to trust device:', error);
    }
  };

  const handleRefresh = () => {
    fetchDevices();
  };

  const exportDeviceData = () => {
    const data = {
      devices,
      stats: deviceStats,
      exportDate: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `clipvault-devices-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (isLoading && devices.length === 0) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading devices...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Device Management</h2>
          <p className="text-gray-400">Manage trusted devices and security settings</p>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center space-x-2 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={exportDeviceData}
            className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
          <button
            onClick={() => setShowAddDevice(true)}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Device</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-900 border border-red-700 rounded-lg p-4">
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* Device Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-500">{deviceStats.total}</div>
            <div className="text-sm text-gray-400">Total Devices</div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-500">{deviceStats.online}</div>
            <div className="text-sm text-gray-400">Online</div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-500">{deviceStats.trusted}</div>
            <div className="text-sm text-gray-400">Trusted</div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-500">{deviceStats.pending}</div>
            <div className="text-sm text-gray-400">Pending Trust</div>
          </div>
        </div>
      </div>

      {/* Add Device Modal */}
      {showAddDevice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold text-white mb-4">Add New Device</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Device Name</label>
                <input
                  type="text"
                  value={newDeviceName}
                  onChange={(e) => setNewDeviceName(e.target.value)}
                  placeholder="Enter device name"
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Device Type</label>
                <select
                  value={newDeviceType}
                  onChange={(e) => setNewDeviceType(e.target.value as 'desktop' | 'mobile' | 'tablet')}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                >
                  <option value="desktop">Desktop</option>
                  <option value="mobile">Mobile</option>
                  <option value="tablet">Tablet</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end space-x-4 mt-6">
              <button
                onClick={() => setShowAddDevice(false)}
                className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAddDevice}
                disabled={!newDeviceName.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Add Device
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Devices List */}
      <div className="space-y-4">
        {devices.length === 0 ? (
          <div className="bg-gray-800 rounded-lg p-8 border border-gray-700 text-center">
            <p className="text-gray-400 mb-4">No devices registered yet</p>
            <p className="text-sm text-gray-500">Add a device to get started with secure clipboard synchronization</p>
          </div>
        ) : (
          devices.map(device => (
            <div key={device.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {React.createElement(getDeviceIcon(device.device_type), { 
                    className: `w-8 h-8 ${device.is_online ? 'text-green-500' : 'text-gray-500'}` 
                  })}
                  <div>
                    <h3 className="text-lg font-semibold text-white">{device.name}</h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-400">
                      <span>{device.platform || 'Unknown Platform'}</span>
                      <span>•</span>
                      <span>{device.browser || 'Unknown Browser'}</span>
                      <span>•</span>
                      <span>Last seen: {new Date(device.last_seen).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    {device.is_online ? (
                      <>
                        <Wifi className="w-4 h-4 text-green-500" />
                        <span className="text-green-500 text-sm">Online</span>
                      </>
                    ) : (
                      <>
                        <WifiOff className="w-4 h-4 text-gray-500" />
                        <span className="text-gray-500 text-sm">Offline</span>
                      </>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {device.is_trusted ? (
                      <Shield className="w-4 h-4 text-green-500" />
                    ) : (
                      <Shield className="w-4 h-4 text-yellow-500" />
                    )}
                    <span className={`text-sm ${device.is_trusted ? 'text-green-500' : 'text-yellow-500'}`}>
                      {device.is_trusted ? 'Trusted' : 'Pending'}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {!device.is_trusted && (
                      <button
                        onClick={() => handleTrustDevice(device.id)}
                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm transition-colors"
                      >
                        Trust
                      </button>
                    )}
                    <button
                      onClick={() => handleRemoveDevice(device.id)}
                      className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
