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
      className={`border-2 border-dashed rounded-xl p-8 sm:p-10 text-center cursor-pointer transition-colors ${
        isDragging
          ? "border-brand-500 bg-brand-50 dark:bg-brand-500/10"
          : "border-neutral-300 dark:border-neutral-700 hover:border-neutral-400 dark:hover:border-neutral-600"
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
        <p className="text-neutral-500 dark:text-neutral-400 text-sm">Uploading...</p>
      ) : (
        <>
          <p className="text-neutral-700 dark:text-neutral-200 font-medium mb-1 text-sm sm:text-base">
            Drag & drop a file here, or click to browse
          </p>
          <p className="text-neutral-400 dark:text-neutral-500 text-xs">
            PDF, DOCX, PPTX, TXT, CSV, Excel, images, or email files
          </p>
        </>
      )}
    </div>
  );
}