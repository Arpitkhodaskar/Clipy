import { useState } from 'react';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { ClipboardManager } from './components/ClipboardManager';
import { DeviceManager } from './components/DeviceManager';
import { SecuritySettings } from './components/SecuritySettings';
import { AuditLogs } from './components/AuditLogs';
import { AuthModal } from './components/AuthModal';
import { useAuth } from './hooks/useAuth';
import { useClipboard } from './hooks/useClipboard';
import { CheckCircle } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const { user, isAuthenticated, isLoading, error, login, logout, register } = useAuth();
  const { syncStatus, offlineQueue } = useClipboard();

  // Debug logging
  console.log('🔧 App State:', { 
    isLoading, 
    isAuthenticated, 
    hasUser: !!user, 
    error,
    syncStatus 
  });

  if (isLoading) {
    console.log('⏳ App: Showing loading screen');
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading ClipVault...</p>
          <p className="text-gray-500 text-xs mt-2">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    console.log('🔐 App: Showing auth modal');
    return <AuthModal onLogin={login} onRegister={register} authError={error} />;
  }

  console.log('✅ App: Showing main dashboard');
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header 
        user={user} 
        onLogout={logout}
        syncStatus={syncStatus}
        offlineQueue={offlineQueue}
      />
      
      {/* Backend Connected Status Banner */}
      <div className="bg-blue-900 border-b border-blue-700 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-5 h-5 text-blue-500" />
            <div>
              <p className="text-blue-200 font-medium">Backend Connected</p>
              <p className="text-blue-100 text-sm">
                Connected to ClipVault backend API with Firebase & Redis. Status: {syncStatus}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="flex">
        <nav className="w-64 bg-gray-800 min-h-screen p-4">
          <div className="space-y-2">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: '📊' },
              { id: 'clipboard', label: 'Clipboard', icon: '📋' },
              { id: 'devices', label: 'Devices', icon: '📱' },
              { id: 'security', label: 'Security', icon: '🔒' },
              { id: 'audit', label: 'Audit Logs', icon: '📜' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeTab === tab.id 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <span className="mr-3">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </nav>

        <main className="flex-1 p-6">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'clipboard' && <ClipboardManager />}
          {activeTab === 'devices' && <DeviceManager />}
          {activeTab === 'security' && <SecuritySettings />}
          {activeTab === 'audit' && <AuditLogs />}
        </main>
      </div>
    </div>
  );
}

export default App;