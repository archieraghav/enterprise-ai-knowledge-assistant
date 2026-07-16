import { BrowserRouter, Routes, Route, Navigate, Link} from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./pages/Login";
import RegisterPage from "./pages/Register";
import DocumentsPage from "./pages/Documents";
import ChatPage from "./pages/Chat";
import AdminPage from "./pages/Admin";

function HomePage() {
  const { isAuthenticated, user, logout } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-sm border border-slate-200 p-8">
        <h1 className="text-2xl font-semibold text-slate-900 mb-2">
          Enterprise AI Knowledge Assistant
        </h1>
        <p className="text-slate-500 mb-6">
          Ask questions about your company documents, powered by RAG.
        </p>

        <div className="space-y-3">
          <p className="text-slate-700">
            Signed in as <span className="font-medium">{user?.email}</span>
          </p>
          <Link
            to="/chat"
            className="block w-full text-center bg-slate-900 text-white rounded-lg py-2.5 font-medium hover:bg-slate-800 transition"
          >
            Open Chat
          </Link>
          <Link
            to="/documents"
            className="block w-full text-center border border-slate-300 text-slate-700 rounded-lg py-2.5 font-medium hover:bg-slate-50 transition"
          >
            View Document Library
          </Link>
          <Link
            to="/admin"
            className="block w-full text-center border border-slate-300 text-slate-700 rounded-lg py-2.5 font-medium hover:bg-slate-50 transition"
          >
            Admin Dashboard
          </Link>
          <button
            onClick={logout}
            className="w-full border border-slate-300 text-slate-700 rounded-lg py-2.5 font-medium hover:bg-slate-50 transition"
          >
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;