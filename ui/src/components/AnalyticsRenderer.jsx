import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line,
  PieChart, Pie, Cell,
  Label
} from "recharts";

const COLORS = ["#3b82f6", "#22c55e", "#facc15", "#ef4444", "#a855f7"];

const formatLabel = (str) => {
    if (!str) return "";
    return str.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
};

export default function AnalyticsRenderer({ visualization, data }) {
  if (!data?.length) return null;

  switch (visualization.chart_type) {
    case "bar_chart":
      return (
        <div className="h-64 bg-gray-800 p-4 rounded-lg shadow-md border border-gray-700">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#4a4a4a" />
              <XAxis dataKey={visualization.x_axis} stroke="#ccc">
                <Label value={formatLabel(visualization.x_axis)} offset={-5} position="insideBottom" fill="#ccc" />
              </XAxis>
              <YAxis stroke="#ccc">
                <Label value={formatLabel(visualization.y_axis)} angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} fill="#ccc" />
              </YAxis>
              <Tooltip contentStyle={{ backgroundColor: '#333', borderColor: '#555', color: '#fff' }} itemStyle={{ color: '#fff' }} />
              <Bar dataKey={visualization.y_axis} fill="#8884d8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      );

    case "line_chart":
      return (
        <div className="h-64 bg-gray-800 p-4 rounded-lg shadow-md border border-gray-700">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#4a4a4a" />
              <XAxis dataKey={visualization.x_axis} stroke="#ccc">
                <Label value={formatLabel(visualization.x_axis)} offset={-5} position="insideBottom" fill="#ccc" />
              </XAxis>
              <YAxis stroke="#ccc">
                <Label value={formatLabel(visualization.y_axis)} angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} fill="#ccc" />
              </YAxis>
              <Tooltip contentStyle={{ backgroundColor: '#333', borderColor: '#555', color: '#fff' }} itemStyle={{ color: '#fff' }} />
              <Line
                type="monotone"
                dataKey={visualization.y_axis}
                stroke="#82ca9d"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      );

    case "pie_chart":
      return (
        <div className="h-64 bg-gray-800 p-4 rounded-lg shadow-md border border-gray-700">
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={data}
                dataKey={visualization.y_axis}
                nameKey={visualization.x_axis}
                outerRadius={80}
                label={(entry) => entry[visualization.x_axis]}
              >
                {data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#333', borderColor: '#555', color: '#fff' }} itemStyle={{ color: '#fff' }} formatter={(value, name) => [value, formatLabel(name)]} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      );

    case "table":
      return (
        <table className="min-w-full bg-gray-800 border border-gray-700 rounded shadow-md text-sm">
          <thead>
            <tr>
              {Object.keys(data[0]).map((k) => (
                <th key={k} className="p-2 border-b border-gray-600 bg-gray-700 text-left capitalize">
                  {k.replace(/_/g, " ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, r) => (
              <tr key={r}>
                {Object.values(row).map((v, c) => (
                  <td className="p-2 border-b border-gray-600" key={c}>{v}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      );

    default:
      return null;
  }
}