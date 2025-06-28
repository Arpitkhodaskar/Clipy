import { useState } from 'react';
import { Copy, Lock, Eye, EyeOff, Plus, Download } from 'lucide-react';
import { useClipboard } from '../hooks/useClipboard';
import type { ClipboardItem } from '../types';

export function ClipboardManager() {
  const { clipboardItems, copyToClipboard, captureClipboard } = useClipboard();
  const [showContent, setShowContent] = useState<Record<string, boolean>>({});
  const [currentDomain] = useState(window.location.hostname || 'localhost');
  const [newClipboardText, setNewClipboardText] = useState('');
  const [isCapturing, setIsCapturing] = useState(false);

  const handleCopyToClipboard = async (item: ClipboardItem) => {
    try {
      const success = await copyToClipboard(item);
      if (success) {
        // Show success notification
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        notification.textContent = 'Copied to clipboard from shared storage!';
        document.body.appendChild(notification);
        
        setTimeout(() => {
          document.body.removeChild(notification);
        }, 3000);
      } else {
        throw new Error('Copy failed');
      }
    } catch (error) {
      // Show error notification
      const notification = document.createElement('div');
      notification.className = 'fixed top-4 right-4 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg z-50';
      notification.textContent = 'Access denied: Domain not whitelisted or decryption failed';
      document.body.appendChild(notification);
      
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 3000);
    }
  };

  const handleManualCapture = async () => {
    if (!newClipboardText.trim()) return;
    
    setIsCapturing(true);
    try {
      await captureClipboard(newClipboardText);
      setNewClipboardText('');
      
      // Show success notification
      const notification = document.createElement('div');
      notification.className = 'fixed top-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg z-50';
      notification.textContent = 'Added to shared clipboard!';
      document.body.appendChild(notification);
      
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 3000);
    } catch (error) {
      console.error('Failed to capture text:', error);
    } finally {
      setIsCapturing(false);
    }
  };

  const isCurrentDomainAllowed = (allowedDomain: string) => {
    const whitelist = getDomainWhitelist();
    return whitelist.includes(allowedDomain) || 
           whitelist.includes(currentDomain) || 
           whitelist.includes('*') ||
           allowedDomain === currentDomain;
  };

  const getDomainWhitelist = (): string[] => {
    try {
      const whitelist = localStorage.getItem('clipvault_domain_whitelist');
      return whitelist ? JSON.parse(whitelist) : ['localhost', '127.0.0.1'];
    } catch (error) {
      return ['localhost', '127.0.0.1'];
    }
  };

  const toggleContentVisibility = (id: string) => {
    setShowContent(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case 'password':
        return '🔑';
      case 'code':
        return '💻';
      default:
        return '📝';
    }
  };

  const formatTimestamp = (timestamp: Date | string) => {
    const now = new Date();
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  const exportClipboardData = () => {
    const data = {
      items: clipboardItems,
      exportDate: new Date().toISOString(),
      domain: currentDomain
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `clipvault-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Shared Clipboard</h2>
          <p className="text-gray-400">Access clipboard data from all users across all devices</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
            <p className="text-sm text-gray-400">Current Domain</p>
            <p className="text-green-500 font-medium">{currentDomain}</p>
          </div>
          <button
            onClick={exportClipboardData}
            className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
        </div>
      </div>

      <div className="bg-yellow-900 border border-yellow-700 rounded-lg p-4">
        <div className="flex items-center space-x-2">
          <Lock className="w-5 h-5 text-yellow-500" />
          <span className="text-yellow-200 font-medium">Security Notice</span>
        </div>
        <p className="text-yellow-100 text-sm mt-2">
          This is a shared clipboard where all users can see and copy content from any device.
          All clipboard data is encrypted and permanently stored - nothing gets deleted.
        </p>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-semibold text-white mb-4">Add to Shared Clipboard</h3>
        <div className="flex space-x-4">
          <textarea
            value={newClipboardText}
            onChange={(e) => setNewClipboardText(e.target.value)}
            placeholder="Enter text to add to the shared clipboard..."
            className="flex-1 bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none resize-none"
            rows={3}
          />
          <button
            onClick={handleManualCapture}
            disabled={!newClipboardText.trim() || isCapturing}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            {isCapturing ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Plus className="w-4 h-4" />
            )}
            <span>Add</span>
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {clipboardItems.length === 0 ? (
          <div className="bg-gray-800 rounded-lg p-8 border border-gray-700 text-center">
            <p className="text-gray-400 mb-4">No shared clipboard items yet</p>
            <p className="text-sm text-gray-500">
              Add some text above to get started with the shared clipboard
            </p>
          </div>
        ) : (
          clipboardItems.map(item => (
            <div key={item.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{getContentTypeIcon(item.content_type || item.contentType || 'text')}</span>
                  <div>
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-white font-medium capitalize">{item.content_type || item.contentType || 'text'}</span>
                      {(item.encrypted || item.metadata?.encrypted) && <Lock className="w-4 h-4 text-green-500" />}
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-400">
                      <span>{item.deviceName || item.metadata?.deviceName || 'Unknown Device'}</span>
                      <span>•</span>
                      <span>User: {item.user_id?.substring(0, 8) || 'Unknown'}...</span>
                      <span>•</span>
                      <span>{item.domain}</span>
                      <span>•</span>
                      <span>{formatTimestamp(item.created_at || item.timestamp || new Date())}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => toggleContentVisibility(item.id)}
                    className="p-2 text-gray-400 hover:text-white transition-colors"
                    title={showContent[item.id] ? 'Hide content' : 'Show content'}
                  >
                    {showContent[item.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={() => handleCopyToClipboard(item)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                      isCurrentDomainAllowed(item.domain)
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : 'bg-gray-700 text-gray-400 cursor-not-allowed'
                    }`}
                    disabled={!isCurrentDomainAllowed(item.domain)}
                  >
                    <Copy className="w-4 h-4" />
                    <span>Copy</span>
                  </button>
                </div>
              </div>

              <div className="bg-gray-900 rounded-lg p-4">
                <pre className="text-sm text-gray-300 whitespace-pre-wrap break-words">
                  {showContent[item.id] ? item.content : '••••••••••••••••••••••••••••••••'}
                </pre>
              </div>

              {!isCurrentDomainAllowed(item.domain) && (
                <div className="mt-3 flex items-center space-x-2 text-red-400 text-sm">
                  <Lock className="w-4 h-4" />
                  <span>Access restricted - domain not whitelisted</span>
                </div>
              )}

              {item.hash && (
                <div className="mt-3 text-xs text-gray-500">
                  <span className="font-medium">Hash:</span> {item.hash.substring(0, 16)}...
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}