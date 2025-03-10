'use client';

import { useState, ChangeEvent, FormEvent } from 'react';
import axios from 'axios';
import * as XLSX from 'xlsx';

interface Comparison {
  lot_number: string;
  name: string;
  registration: string;
  normalized_registration: string;
  similarity: number;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [names, setNames] = useState<string>('Asim,Suna,Sue,Kay,Kayhan,Kai,Niz');
  const [threshold, setThreshold] = useState<number>(80);
  const [data, setData] = useState<Comparison[]>([]);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleNamesChange = (e: ChangeEvent<HTMLInputElement>) => {
    setNames(e.target.value);
  };

  const handleThresholdChange = (e: ChangeEvent<HTMLInputElement>) => {
    setThreshold(Number(e.target.value));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) {
      alert('Please select a file.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('names', names);
    formData.append('threshold', threshold.toString());

    try {
      const response = await axios.post('http://127.0.0.1:8000/uploadfile/', formData, {
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
    <div>
      <h1>Registration Name Matcher</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Select Excel File:</label>
          <input type="file" onChange={handleFileChange} />
        </div>
        <div>
          <label>Names to Check (comma-separated):</label>
          <input type="text" value={names} onChange={handleNamesChange} />
        </div>
        <div>
          <label>Similarity Threshold:</label>
          <input type="number" value={threshold} onChange={handleThresholdChange} />
        </div>
        <button type="submit">Upload and Check</button>
      </form>
      {data.length > 0 && (
        <div>
          <h2>Results</h2>
          <table>
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
          <button onClick={handleDownload}>Download as Excel</button>
        </div>
      )}
    </div>
  );
}