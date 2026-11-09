export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-[80vh] items-center justify-center">
      <div className="w-full max-w-md">{children}</div>
    </div>
  );
}