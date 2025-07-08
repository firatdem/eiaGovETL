import React, { useEffect, useState } from 'react';
import DataTable from './components/DataTable';
import UsageChart from './components/UsageChart';


interface DataRow {
  region: string;
  datetime: string;
  usage_mw: number;
}

function App() {
  const [data, setData] = useState<DataRow[]>([]);
  const [regionOptions, setRegionOptions] = useState<string[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string>("");

  const fetchData = (region = "") => {
    const url = region
      ? `http://localhost:8000/api/data?region=${encodeURIComponent(region)}`
      : `http://localhost:8000/api/data`;
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .catch(err => console.error("Error fetching data:", err));
  };

  // Initial data fetch and region list
useEffect(() => {
  fetchData();

  fetch("http://localhost:8000/api/regions")
    .then(res => res.json())
    .then(setRegionOptions)
    .catch(err => console.error("Error fetching regions:", err));
}, []);


return (
  <div style={{ padding: '2rem' }}>
    <h1>Energy Usage Dashboard</h1>

    <div style={{ marginBottom: '1rem' }}>
      <label htmlFor="region-select">Select Region: </label>
      <select
        id="region-select"
        value={selectedRegion}
        onChange={(e) => {
          const selected = e.target.value;
          setSelectedRegion(selected);
          fetchData(selected);
        }}
      >
        <option value="">All Regions</option>
        {regionOptions.map(region => (
          <option key={region} value={region}>
            {region}
          </option>
        ))}
      </select>
    </div>

    {/* Usage Chart */}
    <div style={{ marginBottom: '2rem' }}>
      <UsageChart data={data} />
    </div>

    {/* Data Table */}
    <DataTable data={data} />
  </div>
);

}

export default App;
