'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { getBackendUrl } from '@/utils/environment';
import styles from '../styles/StatusPage.module.css';

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

// Define a type for cell values that can be properly serialized
type CellValue = string | number | boolean | null;

interface TableData {
  columns: string[];
  rows: CellValue[][];
}

export default function StatusPage() {
  const [statusData, setStatusData] = useState<StatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreatingData, setIsCreatingData] = useState(false);
  const [apiUrl, setApiUrl] = useState<string>('');
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tableData, setTableData] = useState<TableData | null>(null);
  const [isLoadingTableData, setIsLoadingTableData] = useState(false);
  
  const fetchStatus = async () => {
    try {
      setLoading(true);
      const backendUrl = getBackendUrl();
      setApiUrl(backendUrl); // Store the API URL
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
  
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  const createDummyData = async () => {
    try {
      setIsCreatingData(true);
      const backendUrl = getBackendUrl();
      await axios.post(`${backendUrl}/create-dummy-data`);
      // Refresh status after creating data
      await fetchStatus();
      alert('Dummy data created successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      alert(`Failed to create dummy data: ${errorMessage}`);
    } finally {
      setIsCreatingData(false);
    }
  };
  
  const viewTableData = async (tableName: string) => {
    try {
      setIsLoadingTableData(true);
      setSelectedTable(tableName);
      const backendUrl = getBackendUrl();
      const response = await axios.get<TableData>(`${backendUrl}/table-data/${tableName}`);
      setTableData(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      alert(`Failed to load table data: ${errorMessage}`);
      setSelectedTable(null);
    } finally {
      setIsLoadingTableData(false);
    }
  };
  
  const closeModal = () => {
    setSelectedTable(null);
    setTableData(null);
  };
  
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  return (
    <div className={styles.statusPage}>
      <div className={styles.header}>
        <h1 className={styles.title}>System Status</h1>
      </div>
      
      {error && (
        <div className="bg-red-100 p-4 rounded-lg border border-red-300 text-red-800 mb-6">
          {error}
        </div>
      )}
      
      {/* API Status */}
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>API</h2>
        <div className="mb-4">
          <div className={styles.statusIndicator}>
            <div className={`${styles.statusDot} ${statusData?.api.status === 'online' ? styles.statusDotOnline : styles.statusDotOffline}`}></div>
            <span className={styles.statusLabel}>Status: {statusData?.api.status}</span>
          </div>
          <div className="text-black mb-1">Version: {statusData?.api.version}</div>
          <div className="text-black mb-1">Environment: {statusData?.api.environment}</div>
          <div className="text-black mt-3 font-medium">API Location:</div>
          <div className={styles.codeBlock}>{apiUrl}</div>
        </div>
      </div>
      
      {/* Database Status */}
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Database</h2>
        <div className="mb-4">
          <div className={styles.statusIndicator}>
            <div className={`${styles.statusDot} ${statusData?.database.connected ? styles.statusDotOnline : styles.statusDotOffline}`}></div>
            <span className={styles.statusLabel}>Connection: {statusData?.database.connected ? 'Connected' : 'Disconnected'}</span>
          </div>
          
          {statusData?.database.error && (
            <div className="bg-red-100 p-3 rounded mb-4 text-red-800 border border-red-300">
              {statusData.database.error}
            </div>
          )}
          
          <button 
            className={styles.button}
            onClick={createDummyData}
            disabled={isCreatingData}
          >
            {isCreatingData ? 'Creating...' : 'Create Dummy Data'}
          </button>
          
          {statusData?.database.tables && statusData.database.tables.length > 0 ? (
            <div className="mt-6">
              <h3 className="text-black text-lg font-medium mb-2">Tables</h3>
              <div className="overflow-x-auto">
                <table className={styles.table}>
                  <thead className={styles.tableHeader}>
                    <tr>
                      <th className={styles.tableHeaderCell}>Table Name</th>
                      <th className={styles.tableHeaderCell}>Records</th>
                      <th className={styles.tableHeaderCell}>Columns</th>
                      <th className={styles.tableHeaderCell}>Primary Key</th>
                      <th className={styles.tableHeaderCell}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {statusData.database.tables.map((table) => (
                      <tr key={table.name} className={styles.tableRow}>
                        <td className={styles.tableCell}>{table.name}</td>
                        <td className={styles.tableCell}>{table.record_count}</td>
                        <td className={styles.tableCell}>{table.column_count}</td>
                        <td className={styles.tableCell}>
                          {table.has_primary_key ? (
                            <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">Yes</span>
                          ) : (
                            <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium">No</span>
                          )}
                        </td>
                        <td className={styles.tableCell}>
                          <button 
                            onClick={() => viewTableData(table.name)}
                            className={styles.viewButton}
                            disabled={table.record_count === 0}
                          >
                            View Data
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="text-black italic">No tables found</div>
          )}
        </div>
      </div>
      
      {/* Table Data Modal */}
      {selectedTable && (
        <div className={styles.modalOverlay} onClick={closeModal}>
          <div className={styles.modal} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h3 className={styles.modalTitle}>Table: {selectedTable}</h3>
              <button className={styles.closeButton} onClick={closeModal}>×</button>
            </div>
            <div className={styles.modalBody}>
              {isLoadingTableData ? (
                <div className="flex justify-center items-center h-40">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
                </div>
              ) : tableData ? (
                <div className="overflow-x-auto max-h-96">
                  <table className={styles.dataTable}>
                    <thead>
                      <tr>
                        {tableData.columns.map((column, idx) => (
                          <th key={idx} className={styles.dataTableHeaderCell}>{column}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {tableData.rows.map((row, rowIdx) => (
                        <tr key={rowIdx} className={styles.dataTableRow}>
                          {row.map((cell, cellIdx) => (
                            <td key={cellIdx} className={styles.dataTableCell}>
                              {cell === null ? <span className="text-gray-400">NULL</span> : String(cell)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p>No data available</p>
              )}
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.button} onClick={closeModal}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}