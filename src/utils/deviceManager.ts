import type { Device } from '../types';

export class DeviceManager {
  private static instance: DeviceManager;
  private devices: Device[] = [];
  private currentDevice: Device | null = null;
  private listeners: ((devices: Device[]) => void)[] = [];

  private constructor() {
    this.initializeCurrentDevice();
    this.loadStoredDevices();
    this.startDeviceMonitoring();
  }

  public static getInstance(): DeviceManager {
    if (!DeviceManager.instance) {
      DeviceManager.instance = new DeviceManager();
    }
    return DeviceManager.instance;
  }

  private initializeCurrentDevice() {
    const deviceInfo = this.detectDeviceInfo();
    const storedDevice = localStorage.getItem('clipvault_current_device');
    
    if (storedDevice) {
      try {
        this.currentDevice = JSON.parse(storedDevice);
        // Update last seen and status
        this.currentDevice!.lastSeen = new Date();
        this.currentDevice!.status = 'online';
      } catch (error) {
        console.error('Failed to parse stored device:', error);
        this.currentDevice = this.createNewDevice(deviceInfo);
      }
    } else {
      this.currentDevice = this.createNewDevice(deviceInfo);
    }

    // Store current device
    localStorage.setItem('clipvault_current_device', JSON.stringify(this.currentDevice));
  }

  private detectDeviceInfo() {
    const userAgent = navigator.userAgent;
    const platform = navigator.platform;
    
    let deviceType: Device['type'] = 'desktop';
    let deviceName = 'Unknown Device';
    let platformName = 'Unknown OS';

    // Detect device type and name
    if (/Mobile|Android|iPhone|iPad/.test(userAgent)) {
      if (/iPad/.test(userAgent)) {
        deviceType = 'tablet';
        deviceName = 'iPad';
        platformName = 'iPadOS';
      } else if (/iPhone/.test(userAgent)) {
        deviceType = 'mobile';
        deviceName = 'iPhone';
        platformName = 'iOS';
      } else if (/Android/.test(userAgent)) {
        deviceType = 'mobile';
        deviceName = 'Android Device';
        platformName = 'Android';
      }
    } else if (platform.includes('Mac')) {
      deviceType = 'laptop';
      deviceName = 'MacBook';
      platformName = 'macOS';
    } else if (platform.includes('Win')) {
      deviceType = 'desktop';
      deviceName = 'Windows PC';
      platformName = 'Windows';
    } else if (platform.includes('Linux')) {
      deviceType = 'desktop';
      deviceName = 'Linux PC';
      platformName = 'Linux';
    }

    // Get more specific device info if available
    if (userAgent.includes('Chrome')) {
      platformName += ' (Chrome)';
    } else if (userAgent.includes('Firefox')) {
      platformName += ' (Firefox)';
    } else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
      platformName += ' (Safari)';
    } else if (userAgent.includes('Edge')) {
      platformName += ' (Edge)';
    }

    return {
      type: deviceType,
      name: deviceName,
      platform: platformName
    };
  }

  private createNewDevice(deviceInfo: any): Device {
    return {
      id: this.generateDeviceId(),
      name: deviceInfo.name,
      type: deviceInfo.type,
      status: 'online',
      lastSeen: new Date(),
      platform: deviceInfo.platform,
      ipAddress: '192.168.1.' + Math.floor(Math.random() * 254 + 1), // Simulated IP
      trusted: true // Auto-trust current device
    };
  }

  private generateDeviceId(): string {
    // Generate a unique device ID based on browser fingerprint
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx!.textBaseline = 'top';
    ctx!.font = '14px Arial';
    ctx!.fillText('Device fingerprint', 2, 2);
    
    const fingerprint = canvas.toDataURL() + 
                       navigator.userAgent + 
                       navigator.language + 
                       screen.width + 'x' + screen.height +
                       new Date().getTimezoneOffset();
    
    // Simple hash function
    let hash = 0;
    for (let i = 0; i < fingerprint.length; i++) {
      const char = fingerprint.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    
    return Math.abs(hash).toString(36);
  }

  private loadStoredDevices() {
    try {
      const stored = localStorage.getItem('clipvault_devices');
      if (stored) {
        this.devices = JSON.parse(stored).map((device: any) => ({
          ...device,
          lastSeen: new Date(device.lastSeen)
        }));
      }
      
      // Add current device if not already in list
      if (this.currentDevice && !this.devices.find(d => d.id === this.currentDevice!.id)) {
        this.devices.unshift(this.currentDevice);
      }
      
      this.saveDevices();
    } catch (error) {
      console.error('Failed to load stored devices:', error);
      this.devices = this.currentDevice ? [this.currentDevice] : [];
    }
  }

  private startDeviceMonitoring() {
    // Update current device status periodically
    setInterval(() => {
      if (this.currentDevice) {
        this.currentDevice.lastSeen = new Date();
        this.currentDevice.status = 'online';
        this.updateDevice(this.currentDevice);
      }
    }, 30000); // Update every 30 seconds

    // Simulate other devices going online/offline
    setInterval(() => {
      this.devices.forEach(device => {
        if (device.id !== this.currentDevice?.id) {
          // Random chance to change status
          if (Math.random() < 0.1) {
            device.status = device.status === 'online' ? 'offline' : 'online';
            if (device.status === 'online') {
              device.lastSeen = new Date();
            }
          }
        }
      });
      this.saveDevices();
      this.notifyListeners();
    }, 10000); // Check every 10 seconds

    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (this.currentDevice) {
        this.currentDevice.status = document.hidden ? 'offline' : 'online';
        this.currentDevice.lastSeen = new Date();
        this.updateDevice(this.currentDevice);
      }
    });
  }

  public getDevices(): Device[] {
    return [...this.devices];
  }

  public getCurrentDevice(): Device | null {
    return this.currentDevice;
  }

  public addDevice(deviceInfo: Partial<Device>): Device {
    const newDevice: Device = {
      id: this.generateDeviceId(),
      name: deviceInfo.name || 'New Device',
      type: deviceInfo.type || 'desktop',
      status: 'offline',
      lastSeen: new Date(),
      platform: deviceInfo.platform || 'Unknown',
      ipAddress: deviceInfo.ipAddress || '192.168.1.' + Math.floor(Math.random() * 254 + 1),
      trusted: false
    };

    this.devices.unshift(newDevice);
    this.saveDevices();
    this.notifyListeners();
    
    return newDevice;
  }

  public updateDevice(updatedDevice: Device): void {
    const index = this.devices.findIndex(d => d.id === updatedDevice.id);
    if (index !== -1) {
      this.devices[index] = { ...updatedDevice };
      this.saveDevices();
      this.notifyListeners();
    }
  }

  public removeDevice(deviceId: string): boolean {
    const initialLength = this.devices.length;
    this.devices = this.devices.filter(d => d.id !== deviceId);
    
    if (this.devices.length < initialLength) {
      this.saveDevices();
      this.notifyListeners();
      return true;
    }
    return false;
  }

  public toggleDeviceTrust(deviceId: string): boolean {
    const device = this.devices.find(d => d.id === deviceId);
    if (device) {
      device.trusted = !device.trusted;
      this.updateDevice(device);
      return device.trusted;
    }
    return false;
  }

  public getDeviceStats() {
    const total = this.devices.length;
    const online = this.devices.filter(d => d.status === 'online').length;
    const trusted = this.devices.filter(d => d.trusted).length;
    const untrusted = total - trusted;

    return {
      total,
      online,
      offline: total - online,
      trusted,
      untrusted
    };
  }

  private saveDevices() {
    try {
      localStorage.setItem('clipvault_devices', JSON.stringify(this.devices));
      if (this.currentDevice) {
        localStorage.setItem('clipvault_current_device', JSON.stringify(this.currentDevice));
      }
    } catch (error) {
      console.error('Failed to save devices:', error);
    }
  }

  public addListener(callback: (devices: Device[]) => void) {
    this.listeners.push(callback);
  }

  public removeListener(callback: (devices: Device[]) => void) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  private notifyListeners() {
    this.listeners.forEach(listener => {
      try {
        listener([...this.devices]);
      } catch (error) {
        console.error('Device listener error:', error);
      }
    });
  }

  public exportDeviceData() {
    return {
      devices: this.devices,
      currentDevice: this.currentDevice,
      exportDate: new Date().toISOString()
    };
  }

  public clearAllDevices() {
    this.devices = this.currentDevice ? [this.currentDevice] : [];
    this.saveDevices();
    this.notifyListeners();
  }
}