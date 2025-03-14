'use client';

import { useState, useEffect, ChangeEvent, FormEvent, useMemo } from 'react';
import axios from 'axios';
import * as XLSX from 'xlsx';
import Cookies from 'js-cookie';
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getSortedRowModel,
  getPaginationRowModel,
  SortingState,
  PaginationState,
} from '@tanstack/react-table';
import styles from './styles/Home.module.css';
import { COOKIE_KEYS } from '@/constants/cookies';
import { getCookieOptions } from '@/utils/cookieConfig';
import StatusIndicators from '@/components/StatusIndicators';

interface Comparison {
  lot_number: string;
  name: string;
  registration: string;
  normalized_registration: string;
  similarity: number;
  // reserve_price?: string;
  // current_price?: string;
  // end_time?: string;
  // lot_url?: string;
}

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState<string>('');
  const [names, setNames] = useState<string[]>([]);
  const [data, setData] = useState<Comparison[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const [selectedName, setSelectedName] = useState<string>('All');
  const [auctionId, setAuctionId] = useState<string>('');

  // Load names from cookie on component mount
  useEffect(() => {
    const savedNames = Cookies.get(COOKIE_KEYS.REGISTRATION_NAMES);
    if (savedNames) {
      try {
        const parsedNames = JSON.parse(savedNames);
        setNames(Array.isArray(parsedNames) ? parsedNames : []);
      } catch (error) {
        console.error('Error parsing saved names:', error);
        setNames([]);
      }
    }
  }, []);

  // Save names to cookie whenever they change
  useEffect(() => {
    const isDev = process.env.NODE_ENV === 'development';
    Cookies.set(
      COOKIE_KEYS.REGISTRATION_NAMES, 
      JSON.stringify(names),
      getCookieOptions(isDev)
    );
  }, [names]);

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

    if (names.length === 0) {
      alert('Please add at least one name to check.');
      return;
    }

    setIsLoading(true);
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
      if (axios.isAxiosError(error)) {
        console.error('Axios error:', error.response?.data);
      } else {
        console.error('Error uploading file:', error);
      }
      alert('Error uploading file.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Comparisons');
    XLSX.writeFile(workbook, 'comparisons.xlsx');
  };

  const handlePageSizeChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setPagination(prev => ({
      ...prev,
      pageSize: Number(e.target.value),
    }));
  };

  const handleNameFilterChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setSelectedName(e.target.value);
  };

  const handleAuctionIdChange = (e: ChangeEvent<HTMLInputElement>) => {
    setAuctionId(e.target.value);
  };

  const handleScrape = async () => {
    if (!auctionId) {
      alert('Please enter an auction ID.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.get(`${backendUrl}/scrape/${auctionId}`, {
        params: { names: names.join(',') }
      });
      const auctionData = response.data.comparisons;
      console.log('Scraped data:', auctionData); // Debug message
      setData(auctionData.map((item: Comparison) => ({
        lot_number: item.lot_number,
        name: item.name,
        registration: item.registration,
        normalized_registration: item.normalized_registration,
        similarity: item.similarity
        // ,
        // reserve_price: item.reserve_price,
        // current_price: item.current_price,
        // end_time: item.end_time,
        // lot_url: item.lot_url,
      })));
    } catch (error) {
      console.error('Error scraping auction data:', error);
      alert('Error scraping auction data.');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredData = useMemo(() => {
    if (selectedName === 'All') {
      return data;
    }
    return data.filter(item => item.name === selectedName);
  }, [data, selectedName]);

  const columnHelper = createColumnHelper<Comparison>();

  const columns = useMemo(() => [
    columnHelper.accessor('lot_number', {
      header: 'Lot Number',
      cell: info => info.getValue(),
    }),
    columnHelper.accessor('name', {
      header: 'Name',
      cell: info => info.getValue(),
    }),
    columnHelper.accessor('registration', {
      header: 'Registration',
      cell: info => (
        <span className={styles.registration}>
          {info.getValue()}
        </span>
      ),
    }),
    columnHelper.accessor('normalized_registration', {
      header: 'Normalized Registration',
      cell: info => info.getValue(),
    }),
    columnHelper.accessor('similarity', {
      header: 'Similarity',
      cell: info => info.getValue(),
    }),
  ], [columnHelper]);

  const table = useReactTable({
    data: filteredData,
    columns,
    state: {
      sorting,
      pagination,
    },
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  return (
    <div className={styles.container}>
      <StatusIndicators />
      <div className={styles.formWrapper}>
        <h1 className={styles.mainTitle}>Registration Name Matcher</h1>
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
          <button 
            type="submit" 
            className={styles.submitButton}
            disabled={isLoading}
          >
            {isLoading ? (
              <span className={styles.loadingWrapper}>
                <span className={styles.loadingSpinner}></span>
                Processing...
              </span>
            ) : (
              'Upload and Check'
            )}
          </button>
        </form>
        <div className={styles.formGroup}>
          <label>Enter Auction ID to Scrape:</label>
          <input type="text" value={auctionId} onChange={handleAuctionIdChange} />
          <button type="button" onClick={handleScrape}>Scrape</button>
        </div>
      </div>
      {data.length > 0 && (
        <div className={styles.results}>
          <h2 className={styles.resultsTitle}>Results</h2>
          <div className={styles.tableContainer}>
            <div className={styles.tableControls}>
              <label>
                Show 
                <select value={pagination.pageSize} onChange={handlePageSizeChange}>
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
                entries
              </label>
              <label>
                Filter by Name
                <select value={selectedName} onChange={handleNameFilterChange}>
                  <option value="All">All</option>
                  {names.map((name, index) => (
                    <option key={index} value={name}>{name}</option>
                  ))}
                </select>
              </label>
            </div>
            <table className={styles.table}>
              <thead>
                {table.getHeaderGroups().map(headerGroup => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map(header => (
                      <th
                        key={header.id}
                        onClick={header.column.getToggleSortingHandler()}
                        style={{ cursor: 'pointer' }}
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                        {
                          {
                            asc: ' 🔼',
                            desc: ' 🔽',
                          }[header.column.getIsSorted() as string] ?? null
                        }
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map(row => (
                  <tr key={row.id}>
                    {row.getVisibleCells().map(cell => (
                      <td key={cell.id} className="field-name data-text">
                        <a href="#">{flexRender(cell.column.columnDef.cell, cell.getContext())}</a>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            <div className={styles.pagination}>
              <div className={styles.entriesCount}>
                {`Entries returned: ${data.length}`}
              </div>
              <button
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
              >
                &lt;
              </button>
              <span>
                Page{' '}
                <strong>
                  {table.getState().pagination.pageIndex + 1} of{' '}
                  {table.getPageCount()}
                </strong>{' '}
              </span>
              <button
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
              >
                &gt;
              </button>
            </div>
          </div>
          <button onClick={handleDownload} className={styles.downloadButton}>
            Download as Excel
          </button>
        </div>
      )}
    </div>
  );
}