import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import UploadZone from "../components/UploadZone";
import { listDocuments, uploadDocument, deleteDocument, type DocumentItem } from "../lib/api";

const STATUS_STYLES: Record<string, string> = {
  indexed: "bg-green-100 text-green-700",
  processing: "bg-amber-100 text-amber-700",
  uploaded: "bg-slate-100 text-slate-700",
  failed: "bg-red-100 text-red-700",
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
    <div className="min-h-screen bg-slate-50 px-4 py-10">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-semibold text-slate-900">Document Library</h1>
          <Link to="/" className="text-sm text-slate-500 hover:underline">
            ← Back home
          </Link>
        </div>

        <div className="mb-8">
          <UploadZone onFileSelected={handleFileSelected} isUploading={isUploading} />
        </div>

        {error && <p className="text-sm text-red-600 mb-4">{error}</p>}

        {isLoading ? (
          <p className="text-slate-500 text-sm">Loading documents...</p>
        ) : documents.length === 0 ? (
          <p className="text-slate-500 text-sm">No documents uploaded yet.</p>
        ) : (
          <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
            {documents.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between px-5 py-4">
                <div>
                  <p className="text-sm font-medium text-slate-900">{doc.title}</p>
                  <p className="text-xs text-slate-400 uppercase">{doc.file_type}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span
                    className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                      STATUS_STYLES[doc.status] || "bg-slate-100 text-slate-700"
                    }`}
                  >
                    {doc.status}
                  </span>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="text-xs text-slate-400 hover:text-red-600 transition"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}