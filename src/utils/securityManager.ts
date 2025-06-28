import CryptoJS from 'crypto-js';
import { storageService, type SecurityEvent, type SecurityPolicy } from '../lib/storage';
import type { ClipboardItem } from '../types';

export { SecurityEvent, SecurityPolicy };

export class SecurityManager {
  private static instance: SecurityManager;
  private failedAttempts: Map<string, number> = new Map();
  private blockedIPs: Map<string, Date> = new Map();
  private requestCounts: Map<string, { count: number; resetTime: number }> = new Map();
  private listeners: ((events: SecurityEvent[]) => void)[] = [];

  private constructor() {
    this.startSecurityMonitoring();
    this.initializeThreatDetection();
  }

  public static getInstance(): SecurityManager {
    if (!SecurityManager.instance) {
      SecurityManager.instance = new SecurityManager();
    }
    return SecurityManager.instance;
  }

  private startSecurityMonitoring() {
    // Monitor for suspicious activity
    setInterval(() => {
      this.checkForSuspiciousActivity();
      this.cleanupExpiredBlocks();
      this.rotateKeysIfNeeded();
    }, 60000); // Check every minute

    // Monitor clipboard access patterns
    document.addEventListener('copy', this.handleClipboardEvent.bind(this));
    document.addEventListener('paste', this.handleClipboardEvent.bind(this));

    // Monitor page visibility for session management
    document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
  }

  private initializeThreatDetection() {
    // Monitor for XSS attempts
    const originalConsoleError = console.error;
    console.error = (...args) => {
      const message = args.join(' ');
      if (message.includes('script') || message.includes('eval')) {
        this.logSecurityEvent({
          type: 'threat_detection',
          severity: 'high',
          description: 'Potential XSS attempt detected in console',
          source: 'console_monitor',
          blocked: true,
          details: { message }
        });
      }
      originalConsoleError.apply(console, args);
    };

    // Monitor for suspicious DOM modifications
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              const element = node as Element;
              if (element.tagName === 'SCRIPT' || element.innerHTML.includes('javascript:')) {
                this.logSecurityEvent({
                  type: 'threat_detection',
                  severity: 'critical',
                  description: 'Suspicious script injection detected',
                  source: 'dom_monitor',
                  blocked: true,
                  details: { tagName: element.tagName, innerHTML: element.innerHTML }
                });
              }
            }
          });
        }
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  public validateAccess(request: {
    ipAddress?: string;
    userAgent?: string;
    domain?: string;
    content?: string;
  }): { allowed: boolean; reason?: string } {
    const clientIP = request.ipAddress || this.getClientIP();
    const userAgent = request.userAgent || navigator.userAgent;
    const domain = request.domain || this.getCurrentDomain();

    // Check if IP is blocked
    if (this.isIPBlocked(clientIP)) {
      return { allowed: false, reason: 'IP address is temporarily blocked' };
    }

    // Check rate limiting
    if (!this.checkRateLimit(clientIP)) {
      this.logSecurityEvent({
        type: 'access_control',
        severity: 'medium',
        description: 'Rate limit exceeded',
        source: clientIP,
        blocked: true,
        details: { userAgent, domain }
      });
      return { allowed: false, reason: 'Rate limit exceeded' };
    }

    // Check domain whitelist
    if (!this.isDomainAllowed(domain)) {
      this.logSecurityEvent({
        type: 'access_control',
        severity: 'medium',
        description: 'Domain not whitelisted',
        source: clientIP,
        blocked: true,
        details: { domain, userAgent }
      });
      return { allowed: false, reason: 'Domain not authorized' };
    }

    // Check time restrictions
    if (!this.isTimeAllowed()) {
      return { allowed: false, reason: 'Access not allowed at this time' };
    }

    // Check for suspicious content
    if (request.content && this.containsSuspiciousContent(request.content)) {
      this.logSecurityEvent({
        type: 'threat_detection',
        severity: 'high',
        description: 'Suspicious content detected',
        source: clientIP,
        blocked: true,
        details: { content: request.content.substring(0, 100) }
      });
      return { allowed: false, reason: 'Content contains suspicious patterns' };
    }

    return { allowed: true };
  }

  private getCurrentDomain(): string {
    // Get the current domain, handling localhost with port
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    if (port && port !== '80' && port !== '443') {
      return `${hostname}:${port}`;
    }
    
    return hostname;
  }

  private getClientIP(): string {
    // In a real implementation, this would get the actual client IP
    return '192.168.1.' + Math.floor(Math.random() * 254 + 1);
  }

  private isIPBlocked(ip: string): boolean {
    const blockTime = this.blockedIPs.get(ip);
    if (blockTime) {
      const now = new Date();
      const policy = storageService.getSecurityPolicy();
      if (now.getTime() - blockTime.getTime() < policy.threatDetection.blockDuration) {
        return true;
      } else {
        this.blockedIPs.delete(ip);
      }
    }
    return false;
  }

  private checkRateLimit(ip: string): boolean {
    const now = Date.now();
    const minute = Math.floor(now / 60000);
    const key = `${ip}_${minute}`;
    
    const current = this.requestCounts.get(key) || { count: 0, resetTime: minute };
    
    if (current.resetTime < minute) {
      current.count = 1;
      current.resetTime = minute;
    } else {
      current.count++;
    }
    
    this.requestCounts.set(key, current);
    
    const policy = storageService.getSecurityPolicy();
    return current.count <= policy.threatDetection.maxRequestsPerMinute;
  }

  private isDomainAllowed(domain: string): boolean {
    const whitelist = storageService.getDomainWhitelist();
    
    // Check for exact match
    if (whitelist.includes(domain)) {
      return true;
    }
    
    // Check for wildcard
    if (whitelist.includes('*')) {
      return true;
    }
    
    // Check for localhost variations - be more permissive
    if (domain === 'localhost' || domain.startsWith('localhost:') || 
        domain === '127.0.0.1' || domain.startsWith('127.0.0.1:')) {
      return whitelist.some(allowed => 
        allowed === 'localhost' || 
        allowed.startsWith('localhost:') ||
        allowed === '127.0.0.1' ||
        allowed.startsWith('127.0.0.1:')
      );
    }
    
    return false;
  }

  private isTimeAllowed(): boolean {
    const policy = storageService.getSecurityPolicy();
    if (!policy.accessControl.timeRestrictions.enabled) {
      return true;
    }

    const now = new Date();
    const hour = now.getHours();
    const day = now.getDay();
    
    const { allowedHours, allowedDays } = policy.accessControl.timeRestrictions;
    
    return allowedDays.includes(day) && 
           hour >= allowedHours.start && 
           hour <= allowedHours.end;
  }

  private containsSuspiciousContent(content: string): boolean {
    const policy = storageService.getSecurityPolicy();
    const patterns = policy.threatDetection.suspiciousPatterns;
    return patterns.some(pattern => content.toLowerCase().includes(pattern.toLowerCase()));
  }

  private handleClipboardEvent(event: ClipboardEvent) {
    const eventType = event.type;
    const timestamp = new Date();
    
    // Log clipboard access for audit
    this.logSecurityEvent({
      type: 'access_control',
      severity: 'low',
      description: `Clipboard ${eventType} event`,
      source: 'clipboard_monitor',
      blocked: false,
      details: { eventType, timestamp }
    });

    // Check for rapid clipboard access (potential data exfiltration)
    const events = storageService.getSecurityEvents();
    const recentEvents = events.filter(e => 
      e.type === 'access_control' && 
      e.description.includes('Clipboard') &&
      timestamp.getTime() - e.timestamp.getTime() < 10000 // Last 10 seconds
    );

    if (recentEvents.length > 10) {
      this.logSecurityEvent({
        type: 'threat_detection',
        severity: 'high',
        description: 'Rapid clipboard access detected - potential data exfiltration',
        source: 'clipboard_monitor',
        blocked: false,
        details: { eventCount: recentEvents.length }
      });
    }
  }

  private handleVisibilityChange() {
    if (document.hidden) {
      this.logSecurityEvent({
        type: 'access_control',
        severity: 'low',
        description: 'Session paused - tab hidden',
        source: 'session_monitor',
        blocked: false,
        details: { timestamp: new Date() }
      });
    } else {
      this.logSecurityEvent({
        type: 'access_control',
        severity: 'low',
        description: 'Session resumed - tab visible',
        source: 'session_monitor',
        blocked: false,
        details: { timestamp: new Date() }
      });
    }
  }

  private checkForSuspiciousActivity() {
    const now = new Date();
    const lastHour = new Date(now.getTime() - 3600000);
    
    const events = storageService.getSecurityEvents();
    const recentEvents = events.filter(e => e.timestamp > lastHour);
    const failedAttempts = recentEvents.filter(e => 
      e.type === 'authentication' && e.description.includes('failed')
    );
    
    if (failedAttempts.length > 10) {
      this.logSecurityEvent({
        type: 'threat_detection',
        severity: 'critical',
        description: 'Multiple failed authentication attempts detected',
        source: 'security_monitor',
        blocked: true,
        details: { attemptCount: failedAttempts.length }
      });
    }
  }

  private cleanupExpiredBlocks() {
    const now = new Date();
    const expiredIPs: string[] = [];
    const policy = storageService.getSecurityPolicy();
    
    this.blockedIPs.forEach((blockTime, ip) => {
      if (now.getTime() - blockTime.getTime() >= policy.threatDetection.blockDuration) {
        expiredIPs.push(ip);
      }
    });
    
    expiredIPs.forEach(ip => {
      this.blockedIPs.delete(ip);
      this.logSecurityEvent({
        type: 'access_control',
        severity: 'low',
        description: 'IP block expired',
        source: 'security_monitor',
        blocked: false,
        details: { ip }
      });
    });
  }

  private rotateKeysIfNeeded() {
    const lastRotation = localStorage.getItem('clipvault_last_key_rotation');
    const now = new Date();
    const policy = storageService.getSecurityPolicy();
    
    if (lastRotation) {
      const lastRotationDate = new Date(lastRotation);
      const daysSinceRotation = (now.getTime() - lastRotationDate.getTime()) / (1000 * 60 * 60 * 24);
      
      if (daysSinceRotation >= policy.keyRotationInterval) {
        this.rotateEncryptionKeys();
      }
    } else {
      localStorage.setItem('clipvault_last_key_rotation', now.toISOString());
    }
  }

  private rotateEncryptionKeys() {
    // Generate new master key
    const newKey = CryptoJS.lib.WordArray.random(256/8).toString();
    localStorage.setItem('clipvault_master_key', newKey);
    localStorage.setItem('clipvault_last_key_rotation', new Date().toISOString());
    
    this.logSecurityEvent({
      type: 'encryption',
      severity: 'medium',
      description: 'Encryption keys rotated',
      source: 'key_manager',
      blocked: false,
      details: { timestamp: new Date() }
    });
  }

  public logSecurityEvent(event: Partial<SecurityEvent>) {
    const securityEvent: SecurityEvent = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      type: event.type || 'access_control',
      severity: event.severity || 'low',
      description: event.description || 'Security event',
      source: event.source || 'unknown',
      ipAddress: event.ipAddress || this.getClientIP(),
      userAgent: event.userAgent || navigator.userAgent,
      blocked: event.blocked || false,
      details: event.details || {}
    };

    storageService.addSecurityEvent(securityEvent);
    this.notifyListeners();

    // Auto-block if critical threat detected
    const policy = storageService.getSecurityPolicy();
    if (securityEvent.severity === 'critical' && policy.threatDetection.autoBlock) {
      this.blockedIPs.set(securityEvent.ipAddress, new Date());
    }
  }

  public getSecurityEvents(): SecurityEvent[] {
    return storageService.getSecurityEvents();
  }

  public getSecurityPolicy(): SecurityPolicy {
    return storageService.getSecurityPolicy();
  }

  public updateSecurityPolicy(policy: Partial<SecurityPolicy>) {
    const currentPolicy = storageService.getSecurityPolicy();
    const updatedPolicy = { ...currentPolicy, ...policy };
    storageService.setSecurityPolicy(updatedPolicy);
    
    this.logSecurityEvent({
      type: 'policy_violation',
      severity: 'medium',
      description: 'Security policy updated',
      source: 'admin_panel',
      blocked: false,
      details: { updatedFields: Object.keys(policy) }
    });
  }

  public updateDomainWhitelist(domains: string[]) {
    storageService.setDomainWhitelist(domains);
    
    this.logSecurityEvent({
      type: 'access_control',
      severity: 'medium',
      description: 'Domain whitelist updated',
      source: 'admin_panel',
      blocked: false,
      details: { domains }
    });
  }

  public validatePassword(password: string): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    const policy = storageService.getSecurityPolicy();

    if (password.length < policy.passwordPolicy.minLength) {
      errors.push(`Password must be at least ${policy.passwordPolicy.minLength} characters long`);
    }

    if (policy.passwordPolicy.requireUppercase && !/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }

    if (policy.passwordPolicy.requireLowercase && !/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }

    if (policy.passwordPolicy.requireNumbers && !/\d/.test(password)) {
      errors.push('Password must contain at least one number');
    }

    if (policy.passwordPolicy.requireSymbols && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('Password must contain at least one special character');
    }

    return { valid: errors.length === 0, errors };
  }

  public getSecurityMetrics() {
    const now = new Date();
    const last24Hours = new Date(now.getTime() - 86400000);
    const last7Days = new Date(now.getTime() - 604800000);

    const events = storageService.getSecurityEvents();
    const recentEvents = events.filter(e => e.timestamp > last24Hours);
    const weeklyEvents = events.filter(e => e.timestamp > last7Days);

    const threatEvents = recentEvents.filter(e => e.type === 'threat_detection');
    const blockedEvents = recentEvents.filter(e => e.blocked);
    const criticalEvents = recentEvents.filter(e => e.severity === 'critical');

    const baseMetrics = {
      totalEvents: events.length,
      last24Hours: recentEvents.length,
      last7Days: weeklyEvents.length,
      threatsDetected: threatEvents.length,
      blockedAttempts: blockedEvents.length,
      criticalAlerts: criticalEvents.length,
      blockedIPs: this.blockedIPs.size
    };

    return {
      ...baseMetrics,
      securityScore: this.calculateSecurityScore(baseMetrics)
    };
  }

  private calculateSecurityScore(metrics: {
    totalEvents: number;
    last24Hours: number;
    last7Days: number;
    threatsDetected: number;
    blockedAttempts: number;
    criticalAlerts: number;
    blockedIPs: number;
  }): number {
    let score = 100;

    // Deduct points for security issues
    score -= metrics.criticalAlerts * 10;
    score -= metrics.threatsDetected * 5;
    score -= metrics.blockedAttempts * 2;

    // Add points for good security practices
    const policy = storageService.getSecurityPolicy();
    if (policy.requireTwoFactor) score += 5;
    if (policy.enableBiometric) score += 5;
    if (policy.threatDetection.enabled) score += 10;
    if (!policy.allowGuestAccess) score += 5;

    return Math.max(0, Math.min(100, score));
  }

  public addListener(callback: (events: SecurityEvent[]) => void) {
    this.listeners.push(callback);
  }

  public removeListener(callback: (events: SecurityEvent[]) => void) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  private notifyListeners() {
    const events = storageService.getSecurityEvents();
    this.listeners.forEach(listener => {
      try {
        listener(events);
      } catch (error) {
        console.error('Security listener error:', error);
      }
    });
  }

  public exportSecurityData() {
    return {
      events: storageService.getSecurityEvents(),
      policy: storageService.getSecurityPolicy(),
      metrics: this.getSecurityMetrics(),
      exportDate: new Date().toISOString()
    };
  }

  public clearSecurityEvents() {
    storageService.clearSecurityEvents();
    this.notifyListeners();
  }
}