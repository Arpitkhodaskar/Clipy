import { useState, useEffect, useCallback } from 'react';
import { apiRequest } from '../lib/api';

interface AuditLog {
  id: string;
  timestamp: string;
  action: string;
  user: string;
  device: string;
  status: 'success' | 'warning' | 'error' | 'info';
  ip_address: string;
  details: string;
  hash_chain?: string;
  metadata?: Record<string, any>;
}

interface AuditStats {
  total_events: number;
  success_rate: number;
  security_events: number;
  failed_attempts: number;
  last_24h: number;
}

export function useAuditLogs() {
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [stats, setStats] = useState<AuditStats>({
    total_events: 0,
    success_rate: 0,
    security_events: 0,
    failed_attempts: 0,
    last_24h: 0
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch audit logs from backend
  const fetchAuditLogs = useCallback(async (
    limit = 50,
    offset = 0,
    statusFilter?: string,
    search?: string
  ) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
        ...(statusFilter && statusFilter !== 'all' && { status_filter: statusFilter }),
        ...(search && { search })
      });
      
      const logsData = await apiRequest(`/api/audit/?${params}`);
      const statsData = await apiRequest('/api/audit/stats');
      
      setAuditLogs(logsData);
      setStats(statsData);
      
      console.log('✅ Audit logs loaded from backend:', logsData);
    } catch (error) {
      console.error('❌ Failed to load audit logs:', error);
      setError('Failed to load audit logs');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load audit logs on mount
  useEffect(() => {
    console.log('📜 useAuditLogs: Component mounted, fetching audit logs...');
    fetchAuditLogs();
  }, [fetchAuditLogs]);

  const createAuditLog = useCallback(async (
    action: string,
    details: string,
    status = 'success',
    device?: string
  ) => {
    try {
      await apiRequest('/api/audit/', {
        method: 'POST',
        body: JSON.stringify({ action, details, status, device })
      });
      
      // Refresh audit logs
      await fetchAuditLogs();
    } catch (error) {
      console.error('Failed to create audit log:', error);
      setError('Failed to create audit log');
      throw error;
    }
  }, [fetchAuditLogs]);

  const searchLogs = useCallback(async (searchTerm: string, statusFilter?: string) => {
    await fetchAuditLogs(50, 0, statusFilter, searchTerm);
  }, [fetchAuditLogs]);

  const filterByStatus = useCallback(async (statusFilter: string) => {
    await fetchAuditLogs(50, 0, statusFilter);
  }, [fetchAuditLogs]);

  return {
    auditLogs,
    stats,
    isLoading,
    error,
    fetchAuditLogs,
    createAuditLog,
    searchLogs,
    filterByStatus
  };
}
