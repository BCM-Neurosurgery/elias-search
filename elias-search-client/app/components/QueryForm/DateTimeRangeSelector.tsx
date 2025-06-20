import React, { useEffect, useState } from "react";

interface DateTimeRangeSelectorProps {
    fromDateTime: string | null;
    toDateTime: string | null;
    onFromChange: (val: string | null) => void;
    onToChange: (val: string | null) => void;
}

function formatReadableDate(value: string | null): string {
    if (!value) return "Unbounded";
    const d = new Date(value);
    return d.toLocaleString();
}

export default function DateTimeRangeSelector({
    fromDateTime, toDateTime, onFromChange, onToChange
} : DateTimeRangeSelectorProps) {
    // define error display hook
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Validate: if both set → from <= to
        if (fromDateTime && toDateTime && fromDateTime > toDateTime) {
            setError("Error: 'From' date must be before 'To' date.");
            return;
        }

        // Validate if any date is set → must be in the past
        const now = new Date().toISOString();

        if (fromDateTime && fromDateTime > now) {
            setError("Error: 'From' date must be in the past.");
            return
        }

        if (toDateTime && toDateTime > now) {
            setError("Error: 'To' date must be in the past.");
            return;
        }

        setError(null); // No error
    }, [fromDateTime, toDateTime]);

    return (
        <div className="mb-4 p-4 border rounded">
            <h3 className="text-md font-bold mb-2">Select Date Range</h3>

            <div className="flex flex-col space-y-2">
                {/* FROM */}
                <div>
                    <label className="text-sm font-medium flex justify-between items-center">
                        <span>From: <span className="font-normal text-gray-600">{formatReadableDate(fromDateTime)}</span></span>
                        {fromDateTime && (
                            <button
                                type="button"
                                className="text-sm text-blue-600 underline"
                                onClick={() => onFromChange(null)}
                            >
                                Clear
                            </button>
                        )}
                    </label>
                    <input
                        type="datetime-local"
                        value={fromDateTime || ""}
                        onChange={(e) => {
                            onFromChange(e.target.value ? e.target.value : null)
                        }}
                        className="border p-2 rounded"
                    />
                </div>
                {/* TO */}
                <div>
                    <label className="text-sm font-medium flex justify-between items-center">
                        <span>To: <span className="font-normal text-gray-600">{formatReadableDate(toDateTime)}</span></span>
                        {toDateTime && (
                            <button
                                type="button"
                                className="text-sm text-blue-600 underline"
                                onClick={() => onToChange(null)}
                            >
                                Clear
                            </button>
                        )}
                    </label>
                    <input
                        type="datetime-local"
                        value={toDateTime || ""}
                        onChange={(e) => {
                            onToChange(e.target.value ? e.target.value : null)
                        }}
                        className="border p-2 rounded"
                    />
                </div>
            </div>
            {error && <div className="text-red-600 mt-2">{error}</div>}
        </div>
    );
}