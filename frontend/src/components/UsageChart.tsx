// src/components/UsageChart.tsx
import React from "react";
// ⚠️ Core Chart.js imports (for registration & types)
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend as ChartLegend,
} from "chart.js";
// ⚠️ React wrapper
import type { ChartOptions } from "chart.js";
import { Bar } from "react-chartjs-2";

// register the parts of Chart.js you’re going to use
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  ChartTooltip,
  ChartLegend
);

interface UsageChartProps {
  data: { region: string; datetime: string; usage_mw: number }[];
}

const UsageChart: React.FC<UsageChartProps> = ({ data }) => {
  // take the last 20 points, sorted by datetime
  const chartDataPoints = [...data]
    .sort((a, b) => new Date(a.datetime).getTime() - new Date(b.datetime).getTime())
    .slice(-20);

  const labels = chartDataPoints.map(d =>
    new Date(d.datetime).toLocaleDateString()
  );
  const values = chartDataPoints.map(d => d.usage_mw);

  const chartData = {
    labels,
    datasets: [
      {
        label: "Usage (MWh)",
        data: values,
        backgroundColor: "rgba(75,192,192,0.6)",
      },
    ],
  };

  const options: ChartOptions<"bar"> = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: "Usage (MWh) Over Time",
      },
      legend: { position: "top" },
      tooltip: { mode: "index", intersect: false },
    },
    scales: {
      x: { title: { display: true, text: "Date" } },
      y: { title: { display: true, text: "MWh" } },
    },
  };

  return (
    <div style={{ width: "100%", maxWidth: 800, margin: "0 auto" }}>
      <h2>Usage (MWh) Over Time</h2>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default UsageChart;
