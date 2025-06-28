import { useState, useEffect, useCallback } from 'react';
import { apiRequest } from '../lib/api';

interface Device {
  id: string;
  name: string;
  device_type: string;
  platform?: string;
  browser?: string;
  user_id: string;
  is_trusted: boolean;
  is_online: boolean;
  last_seen: string;
  created_at: string;
  metadata?: Record<string, any>;
}

interface DeviceStats {
  total: number;
  online: number;
  trusted: number;
  pending: number;
}

export function useDevices() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [stats, setStats] = useState<DeviceStats>({ total: 0, online: 0, trusted: 0, pending: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch devices from backend
  const fetchDevices = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const devicesData = await apiRequest('/api/devices/');
      
      // Calculate stats from the devices data since the stats endpoint might not be available
      const calculatedStats = {
        total: devicesData.length,
        online: devicesData.filter((d: Device) => d.is_online).length,
        trusted: devicesData.filter((d: Device) => d.is_trusted).length,
        pending: devicesData.filter((d: Device) => !d.is_trusted).length
      };
      
      setDevices(devicesData);
      setStats(calculatedStats);
      
      console.log('✅ Devices loaded from backend:', devicesData);
      console.log('✅ Device stats calculated:', calculatedStats);
    } catch (error) {
      console.error('❌ Failed to load devices:', error);
      setError('Failed to load devices');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load devices on mount
  useEffect(() => {
    console.log('🔧 useDevices: Component mounted, fetching devices...');
    fetchDevices();
  }, [fetchDevices]);

  const registerDevice = useCallback(async (deviceData: {
    name: string;
    device_type: string;
    platform?: string;
    browser?: string;
    metadata?: Record<string, any>;
  }) => {
    try {
      setIsLoading(true);
      const newDevice = await apiRequest('/api/devices/', {
        method: 'POST',
        body: JSON.stringify(deviceData)
      });
      
      // Refresh devices list
      await fetchDevices();
      
      return newDevice;
    } catch (error) {
      console.error('Failed to register device:', error);
      setError('Failed to register device');
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [fetchDevices]);

  const trustDevice = useCallback(async (deviceId: string) => {
    try {
      await apiRequest(`/api/devices/${deviceId}/trust`, { method: 'PUT' });
      
      // Refresh devices list
      await fetchDevices();
    } catch (error) {
      console.error('Failed to trust device:', error);
      setError('Failed to trust device');
      throw error;
    }
  }, [fetchDevices]);

  const removeDevice = useCallback(async (deviceId: string) => {
    try {
      await apiRequest(`/api/devices/${deviceId}`, { method: 'DELETE' });
      
      // Refresh devices list
      await fetchDevices();
    } catch (error) {
      console.error('Failed to remove device:', error);
      setError('Failed to remove device');
      throw error;
    }
  }, [fetchDevices]);

  const updateDeviceStatus = useCallback(async (deviceId: string, isOnline: boolean) => {
    try {
      await apiRequest(`/api/devices/${deviceId}/status?is_online=${isOnline}`, { 
        method: 'PUT'
      });
      
      // Refresh devices list to show updated status
      await fetchDevices();
    } catch (error) {
      console.error('Failed to update device status:', error);
    }
  }, [fetchDevices]);

  // Auto-refresh devices every 30 seconds and simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      fetchDevices();
      
      // Simulate occasional device status changes
      if (devices.length > 0 && Math.random() > 0.7) {
        const randomDevice = devices[Math.floor(Math.random() * devices.length)];
        const newStatus = Math.random() > 0.5;
        console.log(`📱 Simulating status change for ${randomDevice.name}: ${newStatus ? 'online' : 'offline'}`);
        updateDeviceStatus(randomDevice.id, newStatus);
      }
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, [fetchDevices, devices, updateDeviceStatus]);

  return {
    devices,
    stats,
    isLoading,
    error,
    fetchDevices,
    registerDevice,
    trustDevice,
    removeDevice,
    updateDeviceStatus
  };
}
