import React, { useEffect, useState } from 'react';
import DataTable from './components/DataTable';

interface DataRow {
  region: string;
  datetime: string;
  usage_mw: number;
}

function App() {
  const [data, setData] = useState<DataRow[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/data")
      .then(res => res.json())
      .then(setData)
      .catch(err => console.error("Error fetching data:", err));
  }, []);

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Energy Usage Dashboard</h1>
      <DataTable data={data} />
    </div>
  );
}

export default App;
