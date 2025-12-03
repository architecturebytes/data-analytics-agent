import React, { useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";

export default function AnalyticsDashboard() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const sendQuery = async () => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8080/chat", {
        message: query,
      });
      setResponse(res.data);
    } catch (err) {
      setResponse({
        type: "text",
        content: "Error communicating with backend: " + err.message,
      });
    }
    setLoading(false);
  };

  const renderVisualization = () => {
    if (!response || response.type !== "analytics") return null;

    const viz = response.visualization;
    const data = response.data || [];

    if (viz === "table") {
      return (
        <table className="analytics-table">
          <thead>
            <tr>
              {Object.keys(data[0] || {}).map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i}>
                {Object.keys(row).map((col) => (
                  <td key={col + i}>{row[col]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      );
    }

    if (viz === "bar_chart") {
      const firstKey = Object.keys(data[0] || {})[0];
      const secondKey = Object.keys(data[0] || {})[1];
      return (
        <BarChart width={650} height={350} data={data}>
          <XAxis dataKey={firstKey} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey={secondKey} />
        </BarChart>
      );
    }

    if (viz === "line_chart") {
      const firstKey = Object.keys(data[0] || {})[0];
      const secondKey = Object.keys(data[0] || {})[1];
      return (
        <LineChart width={650} height={350} data={data}>
          <XAxis dataKey={firstKey} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey={secondKey} />
        </LineChart>
      );
    }

    if (viz === "pie_chart") {
      const labelKey = Object.keys(data[0] || {})[0];
      const valueKey = Object.keys(data[0] || {})[1];
      return (
        <PieChart width={450} height={350}>
          <Pie
            data={data}
            dataKey={valueKey}
            nameKey={labelKey}
            cx="50%"
            cy="50%"
            outerRadius={120}
            label
          >
            {data.map((entry, idx) => (
              <Cell key={idx} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      );
    }

    return null;
  };

  return (
    <div className="dashboard-container">
      <h1>Retail Analytics Dashboard</h1>

      <div className="query-box">
        <textarea
          placeholder="Ask anything... e.g., 'Top 5 products by sales'"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        <button onClick={sendQuery} disabled={loading}>
          {loading ? "Loading..." : "Analyze"}
        </button>
      </div>

      <div className="response-section">
        {response && (
          <>
            <h2>Response</h2>
            <p>{response.content}</p>

            {renderVisualization()}

            {response.raw_sql && (
              <div className="sql-box">
                <h3>SQL Used</h3>
                <pre>{response.raw_sql}</pre>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
