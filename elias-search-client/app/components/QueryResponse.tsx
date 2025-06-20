interface QueryResponseProps {
  result: any[];
  payload: any;
}

export default function QueryResponse({ result, payload} : QueryResponseProps) {
    if (!result) {
        return <p className="text-gray-600 dark:text-gray-300">No data found for your query.</p>
    }

    const headers = Object.keys(result[0] || {});

    const handleDownloadCSV = () => {
        alert("Download CSV not yet implemented");
    };

    const handleDownloadQuery = () => {
        alert("Download query not yet implemented");
    };

    return (
        <div className="p-4 border rounded shadow-sm bg-white dark:bg-gray-900 dark:border-gray-700">
            <div className="space-x-4">
                {JSON.stringify(result)}
            </div>
            <div className="space-x-4">
                <button onClick={handleDownloadQuery} className="text-blue-600 dark:text-blue-400 underline text-sm">
                    Download Query
                </button>
                <button onClick={handleDownloadCSV} className="text-blue-600 dark:text-blue-400 underline text-sm">
                    Download Table as CSV
                </button>
            </div>
        </div>
    );
}