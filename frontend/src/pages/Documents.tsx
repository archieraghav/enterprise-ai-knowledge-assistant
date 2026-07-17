import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import Header from "../components/Header";
import Footer from "../components/Footer";
import BackgroundGlow from "../components/BackgroundGlow";
import UploadZone from "../components/UploadZone";
import { listDocuments, uploadDocument, deleteDocument, type DocumentItem } from "../lib/api";

const STATUS_STYLES: Record<string, string> = {
  indexed: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400",
  processing: "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-400",
  uploaded: "bg-neutral-100 text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-400",
};

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDocuments = useCallback(async () => {
    try {
      const data = await listDocuments();
      setDocuments(data.items);
    } catch {
      setError("Failed to load documents.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleFileSelected = async (file: File) => {
    setIsUploading(true);
    setError(null);
    try {
      await uploadDocument(file);
      await loadDocuments();
    } catch (err: any) {
      const message = err?.response?.data?.error || "Upload failed.";
      setError(message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    try {
      await deleteDocument(documentId);
      setDocuments((prev) => prev.filter((d) => d.id !== documentId));
    } catch {
      setError("Failed to delete document.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col relative">
      <BackgroundGlow />
      <Header />

      <main className="flex-1 px-4 sm:px-6 py-8 sm:py-10">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="max-w-2xl mx-auto"
        >
          <h1 className="text-xl sm:text-2xl font-semibold text-neutral-900 dark:text-white mb-6">Document Library</h1>

          <div className="mb-8">
            <UploadZone onFileSelected={handleFileSelected} isUploading={isUploading} />
          </div>

          {error && <p className="text-sm text-red-600 dark:text-red-400 mb-4">{error}</p>}

          {isLoading ? (
            <p className="text-neutral-500 dark:text-neutral-400 text-sm">Loading documents...</p>
          ) : documents.length === 0 ? (
            <p className="text-neutral-500 dark:text-neutral-400 text-sm">No documents uploaded yet.</p>
          ) : (
            <div className="card divide-y divide-neutral-100 dark:divide-neutral-800">
              {documents.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between gap-3 px-4 sm:px-5 py-4">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-neutral-900 dark:text-white truncate">{doc.title}</p>
                    <p className="text-xs text-neutral-400 dark:text-neutral-500 uppercase">{doc.file_type}</p>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span
                      className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                        STATUS_STYLES[doc.status] || "bg-neutral-100 text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300"
                      }`}
                    >
                      {doc.status}
                    </span>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="text-xs text-neutral-400 dark:text-neutral-500 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </main>

      <Footer />
    </div>
  );
}