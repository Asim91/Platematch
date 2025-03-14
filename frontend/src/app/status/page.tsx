'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';  // Removed unused AxiosError import
import { getBackendUrl } from '@/utils/environment';

interface TableInfo {
  name: string;
  record_count: number;
  column_count: number;
  has_primary_key: boolean;
}

interface StatusData {
  api: {
    status: string;
    version: string;
    environment: string;
  };
  database: {
    connected: boolean;
    tables: TableInfo[];
    error?: string;
  };
}

export default function StatusPage() {
  const [statusData, setStatusData] = useState<StatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true);
        const backendUrl = getBackendUrl();
        const response = await axios.get<StatusData>(`${backendUrl}/status`);
        setStatusData(response.data);
        setError(null);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
        setError(`Failed to fetch status: ${errorMessage}`);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">System Status</h1>
        <div className="bg-red-100 p-4 rounded-lg border border-red-300 text-red-800">
          {error}
        </div>
      </div>
    );
  }
  
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">System Status</h1>
      
      {/* API Status */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-2">API</h2>
        <div className="bg-white shadow rounded-lg p-4">
          <div className="flex items-center mb-2">
            <div className={`w-3 h-3 rounded-full mr-2 ${statusData?.api.status === 'online' ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="font-medium">Status: {statusData?.api.status}</span>
          </div>
          <div className="text-gray-600">Version: {statusData?.api.version}</div>
          <div className="text-gray-600">Environment: {statusData?.api.environment}</div>
        </div>
      </div>
      
      {/* Database Status */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Database</h2>
        <div className="bg-white shadow rounded-lg p-4">
          <div className="flex items-center mb-4">
            <div className={`w-3 h-3 rounded-full mr-2 ${statusData?.database.connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="font-medium">Connection: {statusData?.database.connected ? 'Connected' : 'Disconnected'}</span>
          </div>
          
          {statusData?.database.error && (
            <div className="bg-red-100 p-3 rounded mb-4 text-red-800">
              {statusData.database.error}
            </div>
          )}
          
          {statusData?.database.tables && statusData.database.tables.length > 0 ? (
            <div>
              <h3 className="text-lg font-medium mb-2">Tables</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white">
                  <thead>
                    <tr>
                      <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Table Name
                      </th>
                      <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Records
                      </th>
                      <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Columns
                      </th>
                      <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Primary Key
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {statusData.database.tables.map((table) => (
                      <tr key={table.name}>
                        <td className="py-2 px-4 border-b border-gray-200">
                          {table.name}
                        </td>
                        <td className="py-2 px-4 border-b border-gray-200">
                          {table.record_count}
                        </td>
                        <td className="py-2 px-4 border-b border-gray-200">
                          {table.column_count}
                        </td>
                        <td className="py-2 px-4 border-b border-gray-200">
                          {table.has_primary_key ? (
                            <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">Yes</span>
                          ) : (
                            <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs">No</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="text-gray-500 italic">No tables found</div>
          )}
        </div>
      </div>
    </div>
  );
}