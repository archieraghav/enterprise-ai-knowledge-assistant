import { BrowserRouter, Routes, Route, Navigate, Link } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./pages/Login";
import RegisterPage from "./pages/Register";
import DocumentsPage from "./pages/Documents";
import ChatPage from "./pages/Chat";
import AdminPage from "./pages/Admin";
import { motion } from "framer-motion";
import { MessageSquare, FileText, BarChart3, ArrowRight } from "lucide-react";
import Header from "./components/Header";
import Footer from "./components/Footer";
import BackgroundGlow from "./components/BackgroundGlow";

function HomePage() {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const features = [
    {
      icon: MessageSquare,
      title: "Ask Anything",
      description: "Chat with your documents using natural language, powered by RAG.",
      to: "/chat",
      color: "from-brand-500 to-brand-600",
    },
    {
      icon: FileText,
      title: "Document Library",
      description: "Upload, organize, and manage every company document in one place.",
      to: "/documents",
      color: "from-violet-500 to-violet-600",
    },
    {
      icon: BarChart3,
      title: "Admin Insights",
      description: "Track usage, feedback, and knowledge base health at a glance.",
      to: "/admin",
      color: "from-emerald-500 to-emerald-600",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col relative">
      <BackgroundGlow />
      <Header />

      <main className="flex-1">
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="max-w-4xl mx-auto px-4 sm:px-6 pt-14 sm:pt-20 pb-16 sm:pb-20 text-center"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="inline-flex items-center gap-2 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-full px-4 py-1.5 text-xs font-medium text-neutral-600 dark:text-neutral-300 mb-6 shadow-sm"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Signed in as {user?.email}
          </motion.div>

          <h1 className="text-3xl sm:text-5xl font-semibold text-neutral-900 dark:text-white tracking-tight mb-4 leading-tight">
            Your company's knowledge,
            <br />
            <span className="bg-gradient-to-r from-brand-600 to-violet-600 dark:from-brand-400 dark:to-violet-400 bg-clip-text text-transparent">
              one conversation away
            </span>
          </h1>

          <p className="text-neutral-500 dark:text-neutral-400 text-base sm:text-lg max-w-xl mx-auto mb-10">
            Upload documents, ask questions in plain English, and get grounded
            answers with real citations — every time.
          </p>

          <Link to="/chat">
            <motion.span
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="inline-flex items-center gap-2 bg-neutral-900 dark:bg-white text-white dark:text-neutral-900 rounded-xl px-6 py-3.5 font-medium shadow-lg shadow-neutral-900/10 cursor-pointer"
            >
              Start chatting
              <ArrowRight size={18} />
            </motion.span>
          </Link>
        </motion.section>

        <div className="max-w-5xl mx-auto px-4 sm:px-6 pb-20 sm:pb-24 grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-5">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.2 + i * 0.1 }}
            >
              <Link to={feature.to}>
                <motion.div
                  whileHover={{ y: -4 }}
                  transition={{ duration: 0.2 }}
                  className="card p-6 h-full cursor-pointer group"
                >
                  <div
                    className={`h-11 w-11 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 shadow-sm`}
                  >
                    <feature.icon className="text-white" size={20} />
                  </div>
                  <h3 className="font-semibold text-neutral-900 dark:text-white mb-1.5 flex items-center gap-1.5">
                    {feature.title}
                    <ArrowRight
                      size={14}
                      className="text-neutral-300 dark:text-neutral-600 group-hover:text-neutral-500 dark:group-hover:text-neutral-400 group-hover:translate-x-0.5 transition-all"
                    />
                  </h3>
                  <p className="text-sm text-neutral-500 dark:text-neutral-400 leading-relaxed">{feature.description}</p>
                </motion.div>
              </Link>
            </motion.div>
          ))}
        </div>
      </main>

      <Footer />
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
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;