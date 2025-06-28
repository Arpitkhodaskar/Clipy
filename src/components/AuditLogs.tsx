import { useState } from 'react';
import { Search, Download, Filter, Shield, AlertTriangle, Info, CheckCircle, RefreshCw } from 'lucide-react';
import { useAuditLogs } from '../hooks/useAuditLogs';

export function AuditLogs() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const { auditLogs, stats, isLoading, error, fetchAuditLogs } = useAuditLogs();

  const handleSearch = () => {
    fetchAuditLogs(50, 0, statusFilter !== 'all' ? statusFilter : undefined, searchTerm || undefined);
  };

  const handleRefresh = () => {
    fetchAuditLogs(50, 0, statusFilter !== 'all' ? statusFilter : undefined, searchTerm || undefined);
  };

  const exportAuditData = () => {
    const data = {
      auditLogs,
      stats,
      exportDate: new Date().toISOString(),
      filters: { searchTerm, statusFilter }
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `clipvault-audit-logs-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <Shield className="w-4 h-4 text-red-500" />;
      case 'info':
        return <Info className="w-4 h-4 text-blue-500" />;
      default:
        return <Info className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "px-2 py-1 rounded-full text-xs font-medium";
    switch (status) {
      case 'success':
        return `${baseClasses} bg-green-900 text-green-300`;
      case 'warning':
        return `${baseClasses} bg-yellow-900 text-yellow-300`;
      case 'error':
        return `${baseClasses} bg-red-900 text-red-300`;
      case 'info':
        return `${baseClasses} bg-blue-900 text-blue-300`;
      default:
        return `${baseClasses} bg-gray-900 text-gray-300`;
    }
  };

  const filteredLogs = auditLogs.filter(log => {
    const matchesSearch = log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         log.device.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || log.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (isLoading && auditLogs.length === 0) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading audit logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Audit Logs</h2>
          <p className="text-gray-400">Monitor all security events and activities</p>
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
            onClick={exportAuditData}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-900 border border-red-700 rounded-lg p-4">
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-500">{stats.total_events}</div>
            <div className="text-sm text-gray-400">Total Events</div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-500">{stats.success_rate.toFixed(1)}%</div>
            <div className="text-sm text-gray-400">Success Rate</div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-500">{stats.security_events}</div>
            <div className="text-sm text-gray-400">Security Events</div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-500">{stats.failed_attempts}</div>
            <div className="text-sm text-gray-400">Failed Attempts</div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-500">{stats.last_24h}</div>
            <div className="text-sm text-gray-400">Last 24h</div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full bg-gray-900 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-white focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            >
              <option value="all">All Status</option>
              <option value="success">Success</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
              <option value="info">Info</option>
            </select>
          </div>
          <button
            onClick={handleSearch}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Search
          </button>
        </div>
      </div>

      {/* Audit Logs List */}
      <div className="space-y-4">
        {filteredLogs.length === 0 ? (
          <div className="bg-gray-800 rounded-lg p-8 border border-gray-700 text-center">
            <p className="text-gray-400 mb-4">No audit logs found</p>
            <p className="text-sm text-gray-500">Try adjusting your search criteria or refresh the logs</p>
          </div>
        ) : (
          filteredLogs.map(log => (
            <div key={log.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  {getStatusIcon(log.status)}
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-white">{log.action}</h3>
                      <span className={getStatusBadge(log.status)}>{log.status.toUpperCase()}</span>
                    </div>
                    <div className="text-sm text-gray-400 space-y-1">
                      <div className="flex items-center space-x-4">
                        <span><span className="font-medium">User:</span> {log.user}</span>
                        <span>•</span>
                        <span><span className="font-medium">Device:</span> {log.device}</span>
                        <span>•</span>
                        <span><span className="font-medium">IP:</span> {log.ip_address}</span>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span><span className="font-medium">Time:</span> {formatTimestamp(log.timestamp)}</span>
                        {log.hash_chain && (
                          <>
                            <span>•</span>
                            <span><span className="font-medium">Hash Chain:</span> {log.hash_chain.substring(0, 12)}...</span>
                          </>
                        )}
                      </div>
                    </div>
                    <p className="text-gray-300 mt-2">{log.details}</p>
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