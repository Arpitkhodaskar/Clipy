import React from 'react';
import { User, Wifi, WifiOff, Clock, Shield, LogOut } from 'lucide-react';
import type { User as UserType, SyncStatus } from '../types';

interface HeaderProps {
  user: UserType | null;
  onLogout: () => void;
  syncStatus: SyncStatus;
  offlineQueue: number;
}

export function Header({ user, onLogout, syncStatus, offlineQueue }: HeaderProps) {
  const getSyncIcon = () => {
    switch (syncStatus) {
      case 'connected':
        return <Wifi className="w-5 h-5 text-green-500" />;
      case 'connecting':
        return <Clock className="w-5 h-5 text-yellow-500 animate-spin" />;
      case 'offline':
        return <WifiOff className="w-5 h-5 text-red-500" />;
      default:
        return <Wifi className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Shield className="w-8 h-8 text-blue-500" />
            <h1 className="text-2xl font-bold text-white">ClipVault</h1>
          </div>
          <span className="text-sm text-gray-400">Enterprise Security</span>
        </div>

        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            {getSyncIcon()}
            <span className="text-sm text-gray-300 capitalize">{syncStatus}</span>
            {offlineQueue > 0 && (
              <span className="bg-yellow-600 text-xs px-2 py-1 rounded-full">
                {offlineQueue} queued
              </span>
            )}
          </div>

          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <User className="w-5 h-5 text-gray-400" />
              <span className="text-sm text-gray-300">{user?.email}</span>
            </div>
            <button
              onClick={onLogout}
              className="flex items-center space-x-1 text-gray-400 hover:text-white transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}