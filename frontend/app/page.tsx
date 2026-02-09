export default function HomePage() {
  return (
    <div className="container mx-auto flex min-h-screen items-center justify-center py-10">
      <div className="text-center">
        <h1 className="text-3xl font-bold">Todo Management App</h1>
        <p className="mt-2">Simple todo application</p>
        <div className="mt-4 space-x-4">
          <a href="/signup" className="text-blue-500 hover:underline">Sign Up</a>
          <a href="/signin" className="text-blue-500 hover:underline">Sign In</a>
        </div>
      </div>
    </div>
  );
}