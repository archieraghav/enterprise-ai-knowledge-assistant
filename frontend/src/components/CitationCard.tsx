interface Citation {
  document_id: string;
  document_title: string;
  excerpt: string;
}

export default function CitationCard({ citation }: { citation: Citation }) {
  return (
    <div className="border border-neutral-200 dark:border-neutral-700 rounded-lg px-3 py-2 bg-neutral-50 dark:bg-neutral-800/60">
      <p className="text-xs font-medium text-neutral-700 dark:text-neutral-200 mb-0.5">{citation.document_title}</p>
      <p className="text-xs text-neutral-500 dark:text-neutral-400 line-clamp-2">{citation.excerpt}</p>
    </div>
  );
}