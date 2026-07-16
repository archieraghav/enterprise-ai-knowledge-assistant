import { useState, useRef, type DragEvent, type ChangeEvent } from "react";

interface UploadZoneProps {
  onFileSelected: (file: File) => void;
  isUploading: boolean;
}

export default function UploadZone({ onFileSelected, isUploading }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) onFileSelected(file);
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelected(file);
    e.target.value = "";
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition ${
        isDragging ? "border-slate-900 bg-slate-50" : "border-slate-300 hover:border-slate-400"
      }`}
    >
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={handleFileInputChange}
        accept=".pdf,.docx,.pptx,.txt,.csv,.xlsx,.xls,.png,.jpg,.jpeg,.eml"
      />
      {isUploading ? (
        <p className="text-slate-500 text-sm">Uploading...</p>
      ) : (
        <>
          <p className="text-slate-700 font-medium mb-1">
            Drag & drop a file here, or click to browse
          </p>
          <p className="text-slate-400 text-xs">
            PDF, DOCX, PPTX, TXT, CSV, Excel, images, or email files
          </p>
        </>
      )}
    </div>
  );
}