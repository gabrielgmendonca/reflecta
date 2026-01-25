import { useState } from 'react';
import { Link, Check } from 'lucide-react';

export function ShareButton() {
  const [copied, setCopied] = useState(false);

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy link:', err);
    }
  };

  return (
    <button
      onClick={handleShare}
      className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
    >
      {copied ? (
        <>
          <Check className="w-4 h-4 text-green-500" />
          <span className="text-sm font-medium text-green-600">Copied!</span>
        </>
      ) : (
        <>
          <Link className="w-4 h-4" />
          <span className="text-sm font-medium">Share</span>
        </>
      )}
    </button>
  );
}
