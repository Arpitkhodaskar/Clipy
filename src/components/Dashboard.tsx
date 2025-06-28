import { Shield, Users, Clipboard, AlertTriangle, Wifi, RefreshCw } from 'lucide-react';
import { useDevices } from '../hooks/useDevices';
import { useAuditLogs } from '../hooks/useAuditLogs';
import { useDashboard } from '../hooks/useDashboard';

export function Dashboard() {
  const { stats: deviceStats, fetchDevices } = useDevices();
  const { auditLogs, fetchAuditLogs } = useAuditLogs();
  const { stats, isLoading, refreshStats } = useDashboard();

  // Get recent activity from audit logs
  const recentActivity = auditLogs.slice(0, 5).map(log => ({
    time: new Date(log.timestamp).toLocaleString(),
    action: log.action,
    device: log.device,
    status: log.status
  }));

  const handleRefresh = () => {
    fetchDevices();
    fetchAuditLogs();
    refreshStats();
  };

  // Use device stats from useDevices hook or fallback to dashboard stats
  const effectiveStats = {
    ...stats,
    activeDevices: deviceStats.online || stats.activeDevices
  };

  const statsConfig = [
    { label: 'Active Devices', value: effectiveStats.activeDevices.toString(), icon: Users, color: 'text-blue-500' },
    { label: 'Clipboard Syncs', value: effectiveStats.clipboardSyncs.toString(), icon: Clipboard, color: 'text-green-500' },
    { label: 'Security Events', value: effectiveStats.securityEvents.toString(), icon: AlertTriangle, color: 'text-yellow-500' },
    { label: 'Data Encrypted', value: effectiveStats.dataEncrypted, icon: Shield, color: 'text-purple-500' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Security Dashboard</h2>
          <p className="text-gray-400">Monitor your organization's clipboard security in real-time</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isLoading}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsConfig.map((stat, index) => (
          <div key={index} className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">{stat.label}</p>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
              </div>
              <stat.icon className={`w-8 h-8 ${stat.color}`} />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-semibold text-white mb-4">Encryption Status</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">AES-256 Encryption</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-green-500 font-medium">Active</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">RSA-2048 Key Exchange</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-green-500 font-medium">Secured</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Hash Chain Integrity</span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-green-500 font-medium">Verified</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Domain Whitelist</span>
              <span className="text-blue-500 font-medium">Active</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-semibold text-white mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {recentActivity.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-400">No recent activity</p>
              </div>
            ) : (
              recentActivity.map((activity, index) => (
                <div key={index} className="flex items-center justify-between py-2 hover:bg-gray-700 rounded px-2 transition-colors">
                  <div className="flex-1">
                    <p className="text-sm text-white">{activity.action}</p>
                    <p className="text-xs text-gray-400">{activity.device} • {activity.time}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    activity.status === 'success' ? 'bg-green-900 text-green-300' :
                    activity.status === 'warning' ? 'bg-yellow-900 text-yellow-300' :
                    activity.status === 'error' ? 'bg-red-900 text-red-300' :
                    'bg-blue-900 text-blue-300'
                  }`}>
                    {activity.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-semibold text-white mb-4">Security Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-gray-900 rounded-lg">
            <div className="text-3xl font-bold text-green-500 mb-2">{effectiveStats.uptime}%</div>
            <div className="text-sm text-gray-400">Uptime</div>
            <div className="text-xs text-gray-500 mt-1">System availability</div>
          </div>
          <div className="text-center p-4 bg-gray-900 rounded-lg">
            <div className="text-3xl font-bold text-blue-500 mb-2">{effectiveStats.avgSyncTime}s</div>
            <div className="text-sm text-gray-400">Avg Sync Time</div>
            <div className="text-xs text-gray-500 mt-1">Real-time encryption</div>
          </div>
          <div className="text-center p-4 bg-gray-900 rounded-lg">
            <div className="text-3xl font-bold text-red-500 mb-2">{effectiveStats.threatsBlocked}</div>
            <div className="text-sm text-gray-400">Threats Blocked</div>
            <div className="text-xs text-gray-500 mt-1">Security incidents</div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-900 to-purple-900 rounded-lg p-6 border border-blue-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold text-white mb-2">System Status</h3>
            <p className="text-blue-200">All systems operational and secure</p>
          </div>
          <div className="flex items-center space-x-2">
            <Wifi className="w-6 h-6 text-green-400" />
            <span className="text-green-400 font-medium">Connected</span>
          </div>
        </div>
      </div>
    </div>
  );
}