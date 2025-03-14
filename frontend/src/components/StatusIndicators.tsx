import { useState, useEffect } from 'react';
import axios from 'axios';
import { getBackendUrl } from '@/utils/environment';

export default function StatusIndicators() {
  const [apiConnected, setApiConnected] = useState(false);
  const [dbConnected, setDbConnected] = useState(false);
  
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const backendUrl = getBackendUrl();
        const response = await axios.get(`${backendUrl}/status`);
        setApiConnected(true);
        setDbConnected(response.data.database.connected);
      } catch {
        setApiConnected(false);
        setDbConnected(false);
      }
    };
    
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="flex space-x-2 items-center">
      <div className="flex items-center">
        <div className={`w-2 h-2 rounded-full mr-1 ${apiConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
        <span className="text-xs text-gray-600">API</span>
      </div>
      <div className="flex items-center">
        <div className={`w-2 h-2 rounded-full mr-1 ${dbConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
        <span className="text-xs text-gray-600">DB</span>
      </div>
    </div>
  );
}