import { EncryptionService } from './encryption';
import { SecurityManager } from './securityManager';
import { storageService } from '../lib/storage';
import { apiRequest } from '../lib/api';
import type { ClipboardItem } from '../types';

export class ClipboardService {
  private static instance: ClipboardService;
  private encryption: EncryptionService;
  private security: SecurityManager;
  private listeners: ((item: ClipboardItem) => void)[] = [];

  private constructor() {
    this.encryption = EncryptionService.getInstance();
    this.security = SecurityManager.getInstance();
    this.initializeClipboardMonitoring();
  }

  public static getInstance(): ClipboardService {
    if (!ClipboardService.instance) {
      ClipboardService.instance = new ClipboardService();
    }
    return ClipboardService.instance;
  }

  private initializeClipboardMonitoring() {
    // Monitor copy events
    document.addEventListener('copy', this.handleCopyEvent.bind(this));
    
    // Monitor paste events
    document.addEventListener('paste', this.handlePasteEvent.bind(this));
  }

  private async handleCopyEvent(event: ClipboardEvent) {
    try {
      const clipboardData = event.clipboardData?.getData('text/plain');
      if (clipboardData && clipboardData.trim()) {
        // Validate access before capturing
        const validation = this.security.validateAccess({
          content: clipboardData,
          domain: window.location.hostname
        });

        if (!validation.allowed) {
          this.security.logSecurityEvent({
            type: 'access_control',
            severity: 'medium',
            description: `Clipboard capture blocked: ${validation.reason}`,
            source: 'clipboard_service',
            blocked: true,
            details: { reason: validation.reason }
          });
          return;
        }

        await this.captureClipboardData(clipboardData);
      }
    } catch (error) {
      console.error('Failed to capture clipboard data:', error);
      this.security.logSecurityEvent({
        type: 'encryption',
        severity: 'high',
        description: 'Clipboard capture failed',
        source: 'clipboard_service',
        blocked: false,
        details: { error: error instanceof Error ? error.message : String(error) }
      });
    }
  }

  private handlePasteEvent(_event: ClipboardEvent) {
    // Log paste events for audit
    this.security.logSecurityEvent({
      type: 'access_control',
      severity: 'low',
      description: 'Clipboard paste event detected',
      source: 'clipboard_service',
      blocked: false,
      details: { timestamp: new Date() }
    });
  }

  public async captureClipboardData(data: string): Promise<ClipboardItem> {
    const deviceName = this.getDeviceName();
    const domain = window.location.hostname || 'localhost';
    
    // Validate access
    const validation = this.security.validateAccess({
      content: data,
      domain: domain
    });

    if (!validation.allowed) {
      throw new Error(`Access denied: ${validation.reason}`);
    }

    // Encrypt the data
    const { encrypted, iv } = this.encryption.encrypt(data);
    
    // Determine content type
    const contentType = this.detectContentType(data);
    
    const clipboardItem: ClipboardItem = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      content: data,
      content_type: contentType,
      domain,
      created_at: new Date().toISOString(),
      encryptedContent: encrypted,
      iv: iv,
      encrypted: true,
      timestamp: new Date(),
      deviceName,
      contentType,
      hash: this.encryption.generateHash(data)
    };

    // Store locally for immediate access
    storageService.addClipboardItem(clipboardItem);
    
    // Save to backend database
    try {
      await apiRequest('/api/clipboard/', {
        method: 'POST',
        body: JSON.stringify({
          content: data,
          content_type: contentType,
          domain: domain,
          metadata: { 
            source: 'automatic',
            deviceName,
            encrypted: true
          }
        })
      });

      console.log('✅ Clipboard item saved to backend database');
    } catch (error) {
      console.error('❌ Failed to save clipboard item to backend:', error);
      // Continue with local storage even if backend fails
    }
    
    // Log successful capture
    this.security.logSecurityEvent({
      type: 'encryption',
      severity: 'low',
      description: 'Clipboard data encrypted and stored',
      source: 'clipboard_service',
      blocked: false,
      details: { 
        contentType, 
        domain, 
        deviceName,
        dataLength: data.length 
      }
    });
    
    // Notify listeners
    this.notifyListeners(clipboardItem);
    
    return clipboardItem;
  }

  private detectContentType(data: string): 'text' | 'password' | 'code' {
    // Enhanced content type detection with security considerations
    const lowerData = data.toLowerCase();
    
    // Password detection patterns
    if (lowerData.includes('password') || 
        lowerData.includes('secret') || 
        lowerData.includes('token') ||
        lowerData.includes('key') ||
        /^\*+$/.test(data) ||
        /^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]{8,}$/.test(data)) {
      return 'password';
    }
    
    // Code detection patterns
    if (lowerData.includes('function') || 
        lowerData.includes('const') || 
        lowerData.includes('let') ||
        lowerData.includes('var') ||
        lowerData.includes('class') || 
        lowerData.includes('{') || 
        lowerData.includes('import') || 
        lowerData.includes('export') ||
        lowerData.includes('def ') ||
        lowerData.includes('public ') ||
        lowerData.includes('private ') ||
        /^\s*<[^>]+>/.test(data)) { // HTML/XML
      return 'code';
    }
    
    return 'text';
  }

  private getDeviceName(): string {
    let deviceName = localStorage.getItem('clipvault_device_name');
    if (!deviceName) {
      const platform = navigator.platform;
      const userAgent = navigator.userAgent;
      
      if (platform.includes('Mac')) {
        deviceName = 'MacBook';
      } else if (platform.includes('Win')) {
        deviceName = 'Windows PC';
      } else if (userAgent.includes('Mobile')) {
        deviceName = 'Mobile Device';
      } else {
        deviceName = 'Desktop';
      }
      
      localStorage.setItem('clipvault_device_name', deviceName);
    }
    return deviceName;
  }

  public getStoredItems(): ClipboardItem[] {
    return storageService.getClipboardItems();
  }

  public async copyToClipboard(item: ClipboardItem): Promise<boolean> {
    try {
      // Validate access with security manager
      const validation = this.security.validateAccess({
        domain: item.domain,
        content: item.content
      });

      if (!validation.allowed) {
        this.security.logSecurityEvent({
          type: 'access_control',
          severity: 'medium',
          description: `Clipboard access denied: ${validation.reason}`,
          source: 'clipboard_service',
          blocked: true,
          details: { 
            itemId: item.id, 
            domain: item.domain,
            reason: validation.reason 
          }
        });
        throw new Error(`Access denied: ${validation.reason}`);
      }

      // Check domain whitelist
      if (!this.isDomainAllowed(item.domain)) {
        throw new Error('Domain not whitelisted');
      }

      // Decrypt the content
      const decryptedContent = item.encryptedContent 
        ? this.encryption.decrypt(item.encryptedContent, item.iv!)
        : item.content;

      if (!decryptedContent) {
        throw new Error('Failed to decrypt content');
      }

      // Copy to clipboard
      await navigator.clipboard.writeText(decryptedContent);
      
      // Log successful access
      this.security.logSecurityEvent({
        type: 'access_control',
        severity: 'low',
        description: 'Clipboard content accessed successfully',
        source: 'clipboard_service',
        blocked: false,
        details: { 
          itemId: item.id, 
          domain: item.domain,
          contentType: item.contentType 
        }
      });
      
      return true;
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      this.security.logSecurityEvent({
        type: 'access_control',
        severity: 'high',
        description: 'Clipboard access failed',
        source: 'clipboard_service',
        blocked: true,
        details: { 
          itemId: item.id, 
          error: error instanceof Error ? error.message : String(error)
        }
      });
      return false;
    }
  }

  private isDomainAllowed(domain: string): boolean {
    const whitelist = storageService.getDomainWhitelist();
    const currentDomain = window.location.hostname || 'localhost';
    
    return whitelist.includes(domain) || 
           whitelist.includes(currentDomain) || 
           whitelist.includes('*') ||
           domain === currentDomain;
  }

  public updateDomainWhitelist(domains: string[]) {
    storageService.setDomainWhitelist(domains);
    
    this.security.logSecurityEvent({
      type: 'access_control',
      severity: 'medium',
      description: 'Domain whitelist updated',
      source: 'clipboard_service',
      blocked: false,
      details: { domains }
    });
  }

  public addListener(callback: (item: ClipboardItem) => void) {
    this.listeners.push(callback);
  }

  public removeListener(callback: (item: ClipboardItem) => void) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  private notifyListeners(item: ClipboardItem) {
    this.listeners.forEach(listener => {
      try {
        listener(item);
      } catch (error) {
        console.error('Listener error:', error);
      }
    });
  }

  public clearAllData() {
    storageService.clearClipboardItems();
    
    this.security.logSecurityEvent({
      type: 'access_control',
      severity: 'medium',
      description: 'All clipboard data cleared',
      source: 'clipboard_service',
      blocked: false,
      details: { timestamp: new Date() }
    });
  }

  public deleteItem(itemId: string) {
    storageService.removeClipboardItem(itemId);
    
    this.security.logSecurityEvent({
      type: 'access_control',
      severity: 'low',
      description: 'Clipboard item deleted',
      source: 'clipboard_service',
      blocked: false,
      details: { itemId }
    });
  }
}