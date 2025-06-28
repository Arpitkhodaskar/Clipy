import { useState, useEffect, useCallback } from 'react';
import { apiRequest } from '../lib/api';
import type { SyncStatus, ClipboardItem } from '../types';

export function useClipboard() {
  const [clipboardItems, setClipboardItems] = useState<ClipboardItem[]>([]);
  const [syncStatus, setSyncStatus] = useState<SyncStatus>('connected');
  const [offlineQueue, setOfflineQueue] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  // Load clipboard items from backend
  const fetchClipboardItems = useCallback(async (limit = 50, offset = 0) => {
    try {
      setIsLoading(true);
      setSyncStatus('syncing');
      
      // 🌐 SHARED MODE: Get clipboard items from ALL users
      const items = await apiRequest(`/api/clipboard/?limit=${limit}&offset=${offset}&shared=true`);
      setClipboardItems(items);
      setSyncStatus('connected');
      return items;
    } catch (error) {
      console.error('Failed to load clipboard items:', error);
      setSyncStatus('offline');
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load items on mount
  useEffect(() => {
    console.log('📋 useClipboard: Component mounted, fetching clipboard items...');
    fetchClipboardItems().catch(error => {
      console.error('📋 useClipboard: Failed to fetch initial items:', error);
    });
  }, [fetchClipboardItems]);

  const captureClipboard = useCallback(async (text: string) => {
    try {
      setSyncStatus('syncing');
      const item = await apiRequest('/api/clipboard/', {
        method: 'POST',
        body: JSON.stringify({
          content: text,
          content_type: 'text',
          domain: window.location.hostname,
          metadata: { source: 'manual' }
        })
      });
      
      // Add to local state
      setClipboardItems(prev => [item, ...prev]);
      setSyncStatus('connected');
      return item;
    } catch (error) {
      console.error('Failed to capture clipboard:', error);
      setSyncStatus('offline');
      throw error;
    }
  }, []);

  const copyToClipboard = useCallback(async (item: ClipboardItem) => {
    try {
      await navigator.clipboard.writeText(item.content);
      return true;
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      return false;
    }
  }, []);

  const searchClipboard = useCallback(async (query: string) => {
    try {
      setSyncStatus('syncing');
      const results = await apiRequest(`/api/clipboard/search/${encodeURIComponent(query)}`);
      setSyncStatus('connected');
      return results;
    } catch (error) {
      console.error('Search failed:', error);
      setSyncStatus('offline');
      throw error;
    }
  }, []);

  return {
    clipboardItems,
    syncStatus,
    offlineQueue,
    isLoading,
    fetchClipboardItems,
    captureClipboard,
    copyToClipboard,
    searchClipboard
  };
}