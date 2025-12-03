export default function LoadingDots() {
  return (
    <div className="flex gap-1 items-center">
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-100"></div>
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-200"></div>
    </div>
  );
}
