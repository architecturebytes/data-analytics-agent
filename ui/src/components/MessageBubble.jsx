import AnalyticsRenderer from "./AnalyticsRenderer";

export default function MessageBubble({ msg, isUser }) {
  return (
    <div className={`flex mb-4 ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`
          max-w-[80%] p-4 rounded-lg shadow-md
          ${isUser ? "bg-blue-600 text-white" : "bg-gray-700 border border-gray-600 text-gray-100"}
        `}
      >
        <p className="mb-2 whitespace-pre-line">{msg.content}</p>

        {msg.type === "analytics" && msg.visualization?.chart_type !== "none" && (
          <div className="mt-4">
            <AnalyticsRenderer
              visualization={msg.visualization}
              data={msg.data}
            />
          </div>
        )}

        {msg.raw_sql && (
          <div className="mt-4">
            <p className="text-xs font-semibold mb-1 text-gray-400">Generated SQL</p>
            <pre className="bg-gray-900 text-gray-300 p-3 rounded-lg text-xs whitespace-pre-wrap">
              <code>{msg.raw_sql}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
