import type { User, Device, ClipboardItem } from '../types';

export interface SecurityEvent {
  id: string;
  timestamp: Date;
  type: 'authentication' | 'encryption' | 'access_control' | 'threat_detection' | 'policy_violation';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  source: string;
  ipAddress: string;
  userAgent: string;
  blocked: boolean;
  details: any;
}

export interface SecurityPolicy {
  encryptionAlgorithm: string;
  keyExchange: string;
  keyRotationInterval: number;
  sessionTimeout: number;
  maxFailedAttempts: number;
  requireTwoFactor: boolean;
  enableBiometric: boolean;
  allowGuestAccess: boolean;
  rateLimit: number;
  passwordPolicy: {
    minLength: number;
    requireUppercase: boolean;
    requireLowercase: boolean;
    requireNumbers: boolean;
    requireSymbols: boolean;
    maxAge: number;
  };
  accessControl: {
    ipWhitelist: string[];
    domainWhitelist: string[];
    timeRestrictions: {
      enabled: boolean;
      allowedHours: { start: number; end: number };
      allowedDays: number[];
    };
  };
  threatDetection: {
    enabled: boolean;
    maxRequestsPerMinute: number;
    suspiciousPatterns: string[];
    autoBlock: boolean;
    blockDuration: number;
  };
}

class LocalStorageService {
  private static instance: LocalStorageService;

  private constructor() {}

  public static getInstance(): LocalStorageService {
    if (!LocalStorageService.instance) {
      LocalStorageService.instance = new LocalStorageService();
    }
    return LocalStorageService.instance;
  }

  // User management
  getCurrentUser(): User | null {
    try {
      const user = localStorage.getItem('clipvault_current_user');
      return user ? JSON.parse(user) : null;
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  }

  setCurrentUser(user: User | null): void {
    try {
      if (user) {
        localStorage.setItem('clipvault_current_user', JSON.stringify(user));
      } else {
        localStorage.removeItem('clipvault_current_user');
      }
    } catch (error) {
      console.error('Failed to set current user:', error);
    }
  }

  // Device management
  getDevices(): Device[] {
    try {
      const devices = localStorage.getItem('clipvault_devices');
      if (devices) {
        return JSON.parse(devices).map((device: any) => ({
          ...device,
          lastSeen: new Date(device.lastSeen)
        }));
      }
      return [];
    } catch (error) {
      console.error('Failed to get devices:', error);
      return [];
    }
  }

  setDevices(devices: Device[]): void {
    try {
      localStorage.setItem('clipvault_devices', JSON.stringify(devices));
    } catch (error) {
      console.error('Failed to set devices:', error);
    }
  }

  getCurrentDevice(): Device | null {
    try {
      const device = localStorage.getItem('clipvault_current_device');
      if (device) {
        const parsed = JSON.parse(device);
        return {
          ...parsed,
          lastSeen: new Date(parsed.lastSeen)
        };
      }
      return null;
    } catch (error) {
      console.error('Failed to get current device:', error);
      return null;
    }
  }

  setCurrentDevice(device: Device | null): void {
    try {
      if (device) {
        localStorage.setItem('clipvault_current_device', JSON.stringify(device));
      } else {
        localStorage.removeItem('clipvault_current_device');
      }
    } catch (error) {
      console.error('Failed to set current device:', error);
    }
  }

  // Clipboard items
  getClipboardItems(): ClipboardItem[] {
    try {
      const items = localStorage.getItem('clipvault_clipboard_items');
      if (items) {
        return JSON.parse(items).map((item: any) => ({
          ...item,
          timestamp: new Date(item.timestamp)
        }));
      }
      return [];
    } catch (error) {
      console.error('Failed to get clipboard items:', error);
      return [];
    }
  }

  setClipboardItems(items: ClipboardItem[]): void {
    try {
      localStorage.setItem('clipvault_clipboard_items', JSON.stringify(items));
    } catch (error) {
      console.error('Failed to set clipboard items:', error);
    }
  }

  addClipboardItem(item: ClipboardItem): void {
    const items = this.getClipboardItems();
    items.unshift(item);
    // Keep only last 50 items
    const trimmedItems = items.slice(0, 50);
    this.setClipboardItems(trimmedItems);
  }

  removeClipboardItem(itemId: string): void {
    const items = this.getClipboardItems();
    const filteredItems = items.filter(item => item.id !== itemId);
    this.setClipboardItems(filteredItems);
  }

  clearClipboardItems(): void {
    this.setClipboardItems([]);
  }

  // Security events
  getSecurityEvents(): SecurityEvent[] {
    try {
      const events = localStorage.getItem('clipvault_security_events');
      if (events) {
        return JSON.parse(events).map((event: any) => ({
          ...event,
          timestamp: new Date(event.timestamp)
        }));
      }
      return [];
    } catch (error) {
      console.error('Failed to get security events:', error);
      return [];
    }
  }

  setSecurityEvents(events: SecurityEvent[]): void {
    try {
      localStorage.setItem('clipvault_security_events', JSON.stringify(events));
    } catch (error) {
      console.error('Failed to set security events:', error);
    }
  }

  addSecurityEvent(event: SecurityEvent): void {
    const events = this.getSecurityEvents();
    events.unshift(event);
    // Keep only last 1000 events
    const trimmedEvents = events.slice(0, 1000);
    this.setSecurityEvents(trimmedEvents);
  }

  clearSecurityEvents(): void {
    this.setSecurityEvents([]);
  }

  // Security policy
  getSecurityPolicy(): SecurityPolicy {
    try {
      const policy = localStorage.getItem('clipvault_security_policy');
      if (policy) {
        return JSON.parse(policy);
      }
      return this.getDefaultSecurityPolicy();
    } catch (error) {
      console.error('Failed to get security policy:', error);
      return this.getDefaultSecurityPolicy();
    }
  }

  setSecurityPolicy(policy: SecurityPolicy): void {
    try {
      localStorage.setItem('clipvault_security_policy', JSON.stringify(policy));
    } catch (error) {
      console.error('Failed to set security policy:', error);
    }
  }

  private getDefaultSecurityPolicy(): SecurityPolicy {
    const currentDomain = this.getCurrentDomain();
    return {
      encryptionAlgorithm: 'aes-256',
      keyExchange: 'rsa-2048',
      keyRotationInterval: 7,
      sessionTimeout: 30,
      maxFailedAttempts: 5,
      requireTwoFactor: true,
      enableBiometric: true,
      allowGuestAccess: false,
      rateLimit: 100,
      passwordPolicy: {
        minLength: 12,
        requireUppercase: true,
        requireLowercase: true,
        requireNumbers: true,
        requireSymbols: true,
        maxAge: 90
      },
      accessControl: {
        ipWhitelist: [],
        domainWhitelist: [currentDomain, 'localhost', '127.0.0.1', 'localhost:5173', '127.0.0.1:5173'],
        timeRestrictions: {
          enabled: false,
          allowedHours: { start: 9, end: 17 },
          allowedDays: [1, 2, 3, 4, 5]
        }
      },
      threatDetection: {
        enabled: true,
        maxRequestsPerMinute: 60,
        suspiciousPatterns: [
          'script',
          'eval',
          'document.cookie',
          'localStorage',
          'sessionStorage',
          'XMLHttpRequest',
          'fetch('
        ],
        autoBlock: true,
        blockDuration: 300000
      }
    };
  }

  private getCurrentDomain(): string {
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    if (port && port !== '80' && port !== '443') {
      return `${hostname}:${port}`;
    }
    
    return hostname;
  }

  // Domain whitelist
  getDomainWhitelist(): string[] {
    try {
      const whitelist = localStorage.getItem('clipvault_domain_whitelist');
      if (whitelist) {
        return JSON.parse(whitelist);
      }
      const currentDomain = this.getCurrentDomain();
      return [currentDomain, 'localhost', '127.0.0.1', 'localhost:5173', '127.0.0.1:5173'];
    } catch (error) {
      console.error('Failed to get domain whitelist:', error);
      const currentDomain = this.getCurrentDomain();
      return [currentDomain, 'localhost', '127.0.0.1'];
    }
  }

  setDomainWhitelist(domains: string[]): void {
    try {
      localStorage.setItem('clipvault_domain_whitelist', JSON.stringify(domains));
    } catch (error) {
      console.error('Failed to set domain whitelist:', error);
    }
  }

  // Utility methods
  clearAllData(): void {
    const keys = [
      'clipvault_current_user',
      'clipvault_devices',
      'clipvault_current_device',
      'clipvault_clipboard_items',
      'clipvault_security_events',
      'clipvault_security_policy',
      'clipvault_domain_whitelist',
      'clipvault_master_key',
      'clipvault_last_key_rotation'
    ];

    keys.forEach(key => {
      localStorage.removeItem(key);
    });
  }

  exportData() {
    return {
      user: this.getCurrentUser(),
      devices: this.getDevices(),
      currentDevice: this.getCurrentDevice(),
      clipboardItems: this.getClipboardItems(),
      securityEvents: this.getSecurityEvents(),
      securityPolicy: this.getSecurityPolicy(),
      domainWhitelist: this.getDomainWhitelist(),
      exportDate: new Date().toISOString()
    };
  }
}

export const storageService = LocalStorageService.getInstance();