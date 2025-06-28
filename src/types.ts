export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  organization: string;
}

export type SyncStatus = 'connected' | 'connecting' | 'syncing' | 'offline';

export interface ClipboardItem {
  id: string;
  content: string;
  content_type: string; // Backend format
  contentType?: 'text' | 'password' | 'code'; // Frontend format (optional for compatibility)
  domain: string;
  user_id?: string; // Backend format
  created_at: string; // Backend format (ISO string)
  timestamp?: Date; // Frontend format (optional for compatibility)
  deviceName?: string; // Frontend format (optional)
  encrypted?: boolean; // Frontend format (optional)
  encryptedContent?: string;
  iv?: string;
  hash?: string;
  metadata?: Record<string, any>; // Backend format
}

export interface Device {
  id: string;
  name: string;
  type: 'desktop' | 'laptop' | 'mobile' | 'tablet';
  status: 'online' | 'offline';
  lastSeen: Date;
  platform: string;
  ipAddress: string;
  trusted: boolean;
}

export interface AuditLog {
  id: string;
  timestamp: Date;
  action: string;
  user: string;
  device: string;
  status: 'success' | 'warning' | 'error' | 'info';
  ipAddress: string;
  details: string;
  hashChain: string;
}