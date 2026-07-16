interface Citation {
    document_id: string;
    document_title: string;
    excerpt: string;
  }
  
  export default function CitationCard({ citation }: { citation: Citation }) {
    return (
      <div className="border border-slate-200 rounded-lg px-3 py-2 bg-slate-50">
        <p className="text-xs font-medium text-slate-700 mb-0.5">{citation.document_title}</p>
        <p className="text-xs text-slate-500 line-clamp-2">{citation.excerpt}</p>
      </div>
    );
  }