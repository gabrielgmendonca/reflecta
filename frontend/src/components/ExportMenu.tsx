import { Download, FileJson, FileSpreadsheet, FileText } from 'lucide-react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { api } from '../api/client';

interface ExportMenuProps {
  slug: string;
}

export function ExportMenu({ slug }: ExportMenuProps) {
  const handleExport = (format: 'json' | 'csv' | 'pdf') => {
    let url: string;
    switch (format) {
      case 'json':
        url = api.exportJSON(slug);
        break;
      case 'csv':
        url = api.exportCSV(slug);
        break;
      case 'pdf':
        url = api.exportPDF(slug);
        break;
    }
    window.open(url, '_blank');
  };

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
          <Download className="w-4 h-4" />
          <span className="text-sm font-medium">Export</span>
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="min-w-[160px] bg-white rounded-lg shadow-lg border border-gray-200 p-1 z-50"
          sideOffset={5}
        >
          <DropdownMenu.Item
            className="flex items-center gap-2 px-3 py-2 text-sm cursor-pointer rounded-md hover:bg-gray-100 outline-none"
            onClick={() => handleExport('json')}
          >
            <FileJson className="w-4 h-4 text-indigo-500" />
            Export as JSON
          </DropdownMenu.Item>
          <DropdownMenu.Item
            className="flex items-center gap-2 px-3 py-2 text-sm cursor-pointer rounded-md hover:bg-gray-100 outline-none"
            onClick={() => handleExport('csv')}
          >
            <FileSpreadsheet className="w-4 h-4 text-green-500" />
            Export as CSV
          </DropdownMenu.Item>
          <DropdownMenu.Item
            className="flex items-center gap-2 px-3 py-2 text-sm cursor-pointer rounded-md hover:bg-gray-100 outline-none"
            onClick={() => handleExport('pdf')}
          >
            <FileText className="w-4 h-4 text-red-500" />
            Export as PDF
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
