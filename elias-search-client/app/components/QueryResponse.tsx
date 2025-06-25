import {
    useReactTable,
    getCoreRowModel,
    flexRender,
    createColumnHelper,
} from '@tanstack/react-table';
import { useMemo, useState } from 'react';


interface QueryResponseProps {
  result: Record<string, any[]>;
  payload: any;
}

function formatColumnDictToRows(result: Record<string, any[]>): any[] {
  const keys = Object.keys(result);
  const numRows = result[keys[0]]?.length ?? 0;
  return Array.from({ length: numRows }, (_, i) => {
    const row: any = {};
    keys.forEach((key) => {
      row[key] = result[key][i];
    });
    return row;
  });
}

export default function QueryResponse({ result, payload }: QueryResponseProps) {
  if (!result || Object.keys(result).length === 0) {
    return <p className="text-gray-600 dark:text-gray-300">No data found for your query.</p>;
  }

  const data = useMemo(() => formatColumnDictToRows(result), [result]);

  const columns = useMemo(() => {
    const keys = Object.keys(result);
    return keys.map((key) => ({
      accessorKey: key,
      header: key,
      cell: (info: any) => info.getValue(),
    }));
  }, [result]);

  const [pageIndex, setPageIndex] = useState(0);
  const [excludeDatalake, setExcludeDatalake] = useState(false);
  const pageSize = 50;
  const filteredData = excludeDatalake ? data.filter(row => row.source !== "datalake") : data;
  const pagedData = filteredData.slice(pageIndex * pageSize, (pageIndex + 1) * pageSize);
  const pageCount = Math.ceil(filteredData.length / pageSize);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    state: {
      pagination: {
        pageIndex,
        pageSize,
      },
    },
    manualPagination: true,
    pageCount,
  });
  
 

  const handleDownloadCSV = () => {
    const csv = [Object.keys(result).join(","),
  ...filteredData.map(row => Object.values(row).join(","))
].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "query_results.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="p-4 border rounded shadow-sm bg-white dark:bg-gray-900 dark:border-gray-700">
        <label className="inline-flex items-center space-x-2">
            <input
            type="checkbox"
            checked={excludeDatalake}
            onChange={(e) => {setPageIndex(0); setExcludeDatalake(e.target.checked)}}
            className="form-checkbox"
            />
        <span className="text-sm text-gray-800 dark:text-gray-200">Exclude Datalake Entries</span>
        </label>
      <div className="overflow-x-auto">
        <table className="min-w-full table-auto border-collapse">
          <thead>
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th key={header.id} className="border px-4 py-2 bg-gray-100 dark:bg-gray-800">
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {pagedData.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {Object.keys(result).map((key, colIndex) => (
                  <td key={colIndex} className="border px-4 py-1 text-sm">
                    {row[key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center mt-4">
        <div className="space-x-2">
          <button
            onClick={() => setPageIndex(Math.max(0, pageIndex - 1))}
            disabled={pageIndex === 0}
            className="px-2 py-1 border rounded"
          >
            Previous
          </button>
          <button
            onClick={() => setPageIndex(Math.min(pageCount - 1, pageIndex + 1))}
            disabled={pageIndex >= pageCount - 1}
            className="px-2 py-1 border rounded"
          >
            Next
          </button>
        </div>

        <div>
          <button
            onClick={handleDownloadCSV}
            className="text-blue-600 dark:text-blue-400 underline text-sm"
          >
            Download Table as CSV
          </button>
        </div>
      </div>
    </div>
  );
}