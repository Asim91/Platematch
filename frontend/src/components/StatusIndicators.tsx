import { useState, useEffect } from 'react';
import axios from 'axios';
import { getBackendUrl } from '@/utils/environment';
import styles from '../app/styles/StatusIndicator.module.css';

interface StatusData {
  api: {
    status: string;
  };
  database: {
    connected: boolean;
  };
}

export default function StatusIndicators() {
  const [apiConnected, setApiConnected] = useState(false);
  const [dbConnected, setDbConnected] = useState(false);
  
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const backendUrl = getBackendUrl();
        const response = await axios.get<StatusData>(`${backendUrl}/status`);
        setApiConnected(true);
        setDbConnected(response.data.database.connected);
      } catch {
        // We already handle errors by setting connection states to false
        setApiConnected(false);
        setDbConnected(false);
      }
    };
    
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className={styles.indicators}>
      <div className={styles.indicator}>
        <div className={`${styles.dot} ${apiConnected ? styles.connected : styles.disconnected}`}></div>
        <span className={styles.label}>API</span>
      </div>
      <div className={styles.indicator}>
        <div className={`${styles.dot} ${dbConnected ? styles.connected : styles.disconnected}`}></div>
        <span className={styles.label}>DB</span>
      </div>
    </div>
  );
}