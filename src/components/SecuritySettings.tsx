import React, { useState, useEffect } from 'react';
import { Shield, Globe, Key, Lock, Plus, Trash2, Eye, EyeOff, Save, AlertTriangle, CheckCircle, Activity, Download, RefreshCw } from 'lucide-react';
import { ClipboardService } from '../utils/clipboard';
import { SecurityManager, type SecurityPolicy, type SecurityEvent } from '../utils/securityManager';

export function SecuritySettings() {
  const [whitelistedDomains, setWhitelistedDomains] = useState<string[]>([]);
  const [newDomain, setNewDomain] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [securityPolicy, setSecurityPolicy] = useState<SecurityPolicy | null>(null);
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([]);
  const [securityMetrics, setSecurityMetrics] = useState<any>({});
  const [activeTab, setActiveTab] = useState('policy');

  const clipboardService = ClipboardService.getInstance();
  const securityManager = SecurityManager.getInstance();

  useEffect(() => {
    // Load initial data
    const policy = securityManager.getSecurityPolicy();
    setSecurityPolicy(policy);
    setWhitelistedDomains(policy.accessControl.domainWhitelist);
    setSecurityEvents(securityManager.getSecurityEvents());
    setSecurityMetrics(securityManager.getSecurityMetrics());

    // Listen for security updates
    const handleSecurityUpdate = (events: SecurityEvent[]) => {
      setSecurityEvents(events);
      setSecurityMetrics(securityManager.getSecurityMetrics());
    };

    securityManager.addListener(handleSecurityUpdate);

    // Refresh metrics periodically
    const interval = setInterval(() => {
      setSecurityMetrics(securityManager.getSecurityMetrics());
    }, 30000);

    return () => {
      securityManager.removeListener(handleSecurityUpdate);
      clearInterval(interval);
    };
  }, []);

  const addDomain = () => {
    if (newDomain && !whitelistedDomains.includes(newDomain)) {
      const updatedDomains = [...whitelistedDomains, newDomain];
      setWhitelistedDomains(updatedDomains);
      securityManager.updateDomainWhitelist(updatedDomains);
      clipboardService.updateDomainWhitelist(updatedDomains);
      setNewDomain('');
      
      showNotification('Domain added successfully!', 'success');
    }
  };

  const removeDomain = (domain: string) => {
    const updatedDomains = whitelistedDomains.filter(d => d !== domain);
    setWhitelistedDomains(updatedDomains);
    securityManager.updateDomainWhitelist(updatedDomains);
    clipboardService.updateDomainWhitelist(updatedDomains);
    
    showNotification('Domain removed successfully!', 'success');
  };

  const updateSecurityPolicy = (updates: Partial<SecurityPolicy>) => {
    if (securityPolicy) {
      const newPolicy = { ...securityPolicy, ...updates };
      setSecurityPolicy(newPolicy);
      securityManager.updateSecurityPolicy(updates);
      showNotification('Security policy updated!', 'success');
    }
  };

  const saveAllSettings = () => {
    if (securityPolicy) {
      securityManager.updateSecurityPolicy(securityPolicy);
      showNotification('All security settings saved!', 'success');
    }
  };

  const exportSecurityData = () => {
    const data = securityManager.exportSecurityData();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `clipvault-security-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Security data exported successfully!', 'success');
  };

  const clearSecurityEvents = () => {
    securityManager.clearSecurityEvents();
    showNotification('Security events cleared!', 'success');
  };

  const showNotification = (message: string, type: 'success' | 'error' | 'warning') => {
    const notification = document.createElement('div');
    const bgColor = type === 'success' ? 'bg-green-600' : type === 'warning' ? 'bg-yellow-600' : 'bg-red-600';
    notification.className = `fixed top-4 right-4 ${bgColor} text-white px-4 py-2 rounded-lg shadow-lg z-50`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 3000);
  };

  const getSecurityScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-500';
    if (score >= 70) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500';
      case 'high': return 'text-orange-500';
      case 'medium': return 'text-yellow-500';
      case 'low': return 'text-blue-500';
      default: return 'text-gray-500';
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    return new Date(timestamp).toLocaleString();
  };

  if (!securityPolicy) {
    return <div className="text-white">Loading security settings...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Security Center</h2>
          <p className="text-gray-400">Advanced security configuration and monitoring</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={exportSecurityData}
            className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
          <button
            onClick={saveAllSettings}
            className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Save className="w-4 h-4" />
            <span>Save All</span>
          </button>
        </div>
      </div>

      {/* Security Score Dashboard */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-lg p-6 border border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className={`text-4xl font-bold mb-2 ${getSecurityScoreColor(securityMetrics.securityScore || 0)}`}>
              {securityMetrics.securityScore || 0}
            </div>
            <div className="text-sm text-gray-400">Security Score</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-500 mb-2">{securityMetrics.criticalAlerts || 0}</div>
            <div className="text-sm text-gray-400">Critical Alerts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-500 mb-2">{securityMetrics.threatsDetected || 0}</div>
            <div className="text-sm text-gray-400">Threats Detected</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-500 mb-2">{securityMetrics.blockedAttempts || 0}</div>
            <div className="text-sm text-gray-400">Blocked Attempts</div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-800 rounded-lg p-1">
        {[
          { id: 'policy', label: 'Security Policy', icon: Shield },
          { id: 'domains', label: 'Domain Control', icon: Globe },
          { id: 'encryption', label: 'Encryption', icon: Key },
          { id: 'monitoring', label: 'Monitoring', icon: Activity },
          { id: 'events', label: 'Security Events', icon: AlertTriangle }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === tab.id 
                ? 'bg-blue-600 text-white' 
                : 'text-gray-400 hover:text-white hover:bg-gray-700'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Security Policy Tab */}
      {activeTab === 'policy' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-xl font-semibold text-white mb-4">Authentication Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Session Timeout (minutes)
                  </label>
                  <input
                    type="number"
                    value={securityPolicy.sessionTimeout}
                    onChange={(e) => updateSecurityPolicy({ sessionTimeout: parseInt(e.target.value) })}
                    className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Max Failed Login Attempts
                  </label>
                  <input
                    type="number"
                    value={securityPolicy.maxFailedAttempts}
                    onChange={(e) => updateSecurityPolicy({ maxFailedAttempts: parseInt(e.target.value) })}
                    className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div className="space-y-3">
                  <label className="flex items-center space-x-3">
                    <input 
                      type="checkbox" 
                      checked={securityPolicy.requireTwoFactor}
                      onChange={(e) => updateSecurityPolicy({ requireTwoFactor: e.target.checked })}
                      className="form-checkbox text-blue-600" 
                    />
                    <span className="text-gray-300">Require two-factor authentication</span>
                  </label>
                  <label className="flex items-center space-x-3">
                    <input 
                      type="checkbox" 
                      checked={securityPolicy.enableBiometric}
                      onChange={(e) => updateSecurityPolicy({ enableBiometric: e.target.checked })}
                      className="form-checkbox text-blue-600" 
                    />
                    <span className="text-gray-300">Enable biometric authentication</span>
                  </label>
                  <label className="flex items-center space-x-3">
                    <input 
                      type="checkbox" 
                      checked={securityPolicy.allowGuestAccess}
                      onChange={(e) => updateSecurityPolicy({ allowGuestAccess: e.target.checked })}
                      className="form-checkbox text-blue-600" 
                    />
                    <span className="text-gray-300">Allow guest access</span>
                  </label>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-xl font-semibold text-white mb-4">Password Policy</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Minimum Length
                  </label>
                  <input
                    type="number"
                    value={securityPolicy.passwordPolicy.minLength}
                    onChange={(e) => updateSecurityPolicy({ 
                      passwordPolicy: { 
                        ...securityPolicy.passwordPolicy, 
                        minLength: parseInt(e.target.value) 
                      } 
                    })}
                    className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Password Max Age (days)
                  </label>
                  <input
                    type="number"
                    value={securityPolicy.passwordPolicy.maxAge}
                    onChange={(e) => updateSecurityPolicy({ 
                      passwordPolicy: { 
                        ...securityPolicy.passwordPolicy, 
                        maxAge: parseInt(e.target.value) 
                      } 
                    })}
                    className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div className="space-y-2">
                  {[
                    { key: 'requireUppercase', label: 'Require uppercase letters' },
                    { key: 'requireLowercase', label: 'Require lowercase letters' },
                    { key: 'requireNumbers', label: 'Require numbers' },
                    { key: 'requireSymbols', label: 'Require special characters' }
                  ].map(item => (
                    <label key={item.key} className="flex items-center space-x-3">
                      <input 
                        type="checkbox" 
                        checked={securityPolicy.passwordPolicy[item.key as keyof typeof securityPolicy.passwordPolicy] as boolean}
                        onChange={(e) => updateSecurityPolicy({ 
                          passwordPolicy: { 
                            ...securityPolicy.passwordPolicy, 
                            [item.key]: e.target.checked 
                          } 
                        })}
                        className="form-checkbox text-blue-600" 
                      />
                      <span className="text-gray-300">{item.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4">Threat Detection</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Max Requests per Minute
                </label>
                <input
                  type="number"
                  value={securityPolicy.threatDetection.maxRequestsPerMinute}
                  onChange={(e) => updateSecurityPolicy({ 
                    threatDetection: { 
                      ...securityPolicy.threatDetection, 
                      maxRequestsPerMinute: parseInt(e.target.value) 
                    } 
                  })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Block Duration (minutes)
                </label>
                <input
                  type="number"
                  value={securityPolicy.threatDetection.blockDuration / 60000}
                  onChange={(e) => updateSecurityPolicy({ 
                    threatDetection: { 
                      ...securityPolicy.threatDetection, 
                      blockDuration: parseInt(e.target.value) * 60000 
                    } 
                  })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>
            <div className="mt-4 space-y-3">
              <label className="flex items-center space-x-3">
                <input 
                  type="checkbox" 
                  checked={securityPolicy.threatDetection.enabled}
                  onChange={(e) => updateSecurityPolicy({ 
                    threatDetection: { 
                      ...securityPolicy.threatDetection, 
                      enabled: e.target.checked 
                    } 
                  })}
                  className="form-checkbox text-blue-600" 
                />
                <span className="text-gray-300">Enable threat detection</span>
              </label>
              <label className="flex items-center space-x-3">
                <input 
                  type="checkbox" 
                  checked={securityPolicy.threatDetection.autoBlock}
                  onChange={(e) => updateSecurityPolicy({ 
                    threatDetection: { 
                      ...securityPolicy.threatDetection, 
                      autoBlock: e.target.checked 
                    } 
                  })}
                  className="form-checkbox text-blue-600" 
                />
                <span className="text-gray-300">Auto-block suspicious IPs</span>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Domain Control Tab */}
      {activeTab === 'domains' && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
            <Globe className="w-5 h-5 mr-2 text-purple-500" />
            Domain Whitelist Management
          </h3>
          <p className="text-gray-400 mb-4">
            Only whitelisted domains can decrypt and access clipboard data. This ensures sensitive information 
            is only accessible in approved contexts.
          </p>
          
          <div className="flex space-x-2 mb-4">
            <input
              type="text"
              value={newDomain}
              onChange={(e) => setNewDomain(e.target.value)}
              placeholder="Enter domain (e.g., github.com)"
              className="flex-1 bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
              onKeyPress={(e) => e.key === 'Enter' && addDomain()}
            />
            <button
              onClick={addDomain}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add</span>
            </button>
          </div>

          <div className="space-y-2">
            {whitelistedDomains.map(domain => (
              <div key={domain} className="flex items-center justify-between bg-gray-900 rounded-lg p-3">
                <div className="flex items-center space-x-3">
                  <Globe className="w-4 h-4 text-green-500" />
                  <span className="text-white">{domain}</span>
                  {domain === window.location.hostname && (
                    <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded-full">Current</span>
                  )}
                </div>
                <button
                  onClick={() => removeDomain(domain)}
                  className="text-gray-400 hover:text-red-400 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Encryption Tab */}
      {activeTab === 'encryption' && (
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <Key className="w-5 h-5 mr-2 text-blue-500" />
              Encryption Configuration
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Encryption Algorithm
                </label>
                <select 
                  value={securityPolicy.encryptionAlgorithm}
                  onChange={(e) => updateSecurityPolicy({ encryptionAlgorithm: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                >
                  <option value="aes-256">AES-256 (Recommended)</option>
                  <option value="aes-192">AES-192</option>
                  <option value="aes-128">AES-128</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Key Exchange Method
                </label>
                <select 
                  value={securityPolicy.keyExchange}
                  onChange={(e) => updateSecurityPolicy({ keyExchange: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                >
                  <option value="rsa-2048">RSA-2048 (Current)</option>
                  <option value="rsa-4096">RSA-4096</option>
                  <option value="ecdh-p256">ECDH P-256</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Key Rotation Interval (days)
                </label>
                <input
                  type="number"
                  value={securityPolicy.keyRotationInterval}
                  onChange={(e) => updateSecurityPolicy({ keyRotationInterval: parseInt(e.target.value) })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Rate Limit (requests/minute)
                </label>
                <input
                  type="number"
                  value={securityPolicy.rateLimit}
                  onChange={(e) => updateSecurityPolicy({ rateLimit: parseInt(e.target.value) })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4">API Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  API Endpoint
                </label>
                <input
                  type="text"
                  defaultValue="https://api.clipvault.com/v1"
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  API Key
                </label>
                <div className="flex space-x-2">
                  <input
                    type={showApiKey ? 'text' : 'password'}
                    defaultValue="cv_live_sk_1234567890abcdef"
                    className="flex-1 bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                    readOnly
                  />
                  <button
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="p-2 text-gray-400 hover:text-white transition-colors"
                  >
                    {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Monitoring Tab */}
      {activeTab === 'monitoring' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 text-center">
              <div className="text-3xl font-bold text-blue-500 mb-2">{securityMetrics.last24Hours || 0}</div>
              <div className="text-sm text-gray-400">Events (24h)</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 text-center">
              <div className="text-3xl font-bold text-purple-500 mb-2">{securityMetrics.blockedIPs || 0}</div>
              <div className="text-sm text-gray-400">Blocked IPs</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 text-center">
              <div className="text-3xl font-bold text-green-500 mb-2">99.9%</div>
              <div className="text-sm text-gray-400">Uptime</div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4">Real-time Security Status</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Encryption Status</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-green-500 font-medium">Active</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Threat Detection</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-green-500 font-medium">Monitoring</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Access Control</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-green-500 font-medium">Enforced</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Audit Logging</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-green-500 font-medium">Recording</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Security Events Tab */}
      {activeTab === 'events' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold text-white">Recent Security Events</h3>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setSecurityEvents(securityManager.getSecurityEvents())}
                className="flex items-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </button>
              <button
                onClick={clearSecurityEvents}
                className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                <span>Clear</span>
              </button>
            </div>
          </div>

          <div className="space-y-3">
            {securityEvents.slice(0, 20).map(event => (
              <div key={event.id} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className={`w-3 h-3 rounded-full mt-1 ${
                      event.blocked ? 'bg-red-500' : 'bg-green-500'
                    }`}></div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="text-white font-medium">{event.description}</h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(event.severity)} bg-gray-900`}>
                          {event.severity}
                        </span>
                        {event.blocked && (
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-900 text-red-300">
                            Blocked
                          </span>
                        )}
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-400 mb-2">
                        <div>
                          <span className="font-medium">Source:</span> {event.source}
                        </div>
                        <div>
                          <span className="font-medium">IP:</span> {event.ipAddress}
                        </div>
                        <div>
                          <span className="font-medium">Time:</span> {formatTimestamp(event.timestamp)}
                        </div>
                      </div>
                      {event.details && Object.keys(event.details).length > 0 && (
                        <div className="text-xs text-gray-500 bg-gray-900 rounded p-2">
                          <pre>{JSON.stringify(event.details, null, 2)}</pre>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {securityEvents.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-400">No security events recorded yet.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}