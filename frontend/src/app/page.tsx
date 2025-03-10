'use client';

import { useState, useEffect, ChangeEvent, FormEvent } from 'react';
import axios from 'axios';
import * as XLSX from 'xlsx';
import styles from './styles/Home.module.css';

interface Comparison {
  lot_number: string;
  name: string;
  registration: string;
  normalized_registration: string;
  similarity: number;
}

const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState<string>('');
  const [names, setNames] = useState<string[]>(['Asim', 'Suna', 'Sue', 'Kay', 'Kayhan', 'Kai', 'Niz']);
  const [data, setData] = useState<Comparison[]>([]);
  const [isBackendConnected, setIsBackendConnected] = useState(false);

  useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        await axios.get(`${backendUrl}/health`);
        setIsBackendConnected(true);
      } catch (error) {
        console.error('Backend connection failed:', error);
        setIsBackendConnected(false);
      }
    };

    // Check connection immediately and every 30 seconds
    checkBackendConnection();
    const interval = setInterval(checkBackendConnection, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleNameChange = (e: ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
  };

  const handleAddName = () => {
    if (name && !names.includes(name)) {
      setNames([...names, name]);
      setName('');
    }
  };

  const handleRemoveName = (nameToRemove: string) => {
    setNames(names.filter((n) => n !== nameToRemove));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) {
      alert('Please select a file.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('names', names.join(','));

    try {
      const response = await axios.post(`${backendUrl}/uploadfile/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setData(response.data.comparisons);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file.');
    }
  };

  const handleDownload = () => {
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Comparisons');
    XLSX.writeFile(workbook, 'comparisons.xlsx');
  };

  return (
    <div className={styles.container}>
      <div className={styles.connectionIndicator}>
        <div className={`${styles.statusDot} ${isBackendConnected ? styles.connected : styles.disconnected}`} />
      </div>
      <div className={styles.formWrapper}>
        <h1>Registration Name Matcher</h1>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label>Select Excel File:</label>
            <input type="file" onChange={handleFileChange} />
          </div>
          <div className={styles.formGroup}>
            <label>Add Name to Check:</label>
            <input type="text" value={name} onChange={handleNameChange} />
            <button type="button" onClick={handleAddName}>Add</button>
          </div>
          <div className={styles.formGroup}>
            <label>Names to Check:</label>
            <ul className={styles.nameList}>
              {names.map((name, index) => (
                <li key={index}>
                  {name} <button type="button" onClick={() => handleRemoveName(name)}>Remove</button>
                </li>
              ))}
            </ul>
          </div>
          <button type="submit" className={styles.submitButton}>Upload and Check</button>
        </form>
      </div>
      {data.length > 0 && (
        <div className={styles.results}>
          <h2>Results</h2>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Lot Number</th>
                <th>Name</th>
                <th>Registration</th>
                <th>Normalized Registration</th>
                <th>Similarity</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <tr key={index}>
                  <td>{item.lot_number}</td>
                  <td>{item.name}</td>
                  <td>{item.registration}</td>
                  <td>{item.normalized_registration}</td>
                  <td>{item.similarity}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <button onClick={handleDownload} className={styles.downloadButton}>Download as Excel</button>
        </div>
      )}
    </div>
  );
}