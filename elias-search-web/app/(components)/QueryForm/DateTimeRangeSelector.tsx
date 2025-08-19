"use client"
import React, { useEffect, useState } from "react";
import CollapsibleSection from "../CollapsibleSection";

interface DateTimeRangeSelectorProps {
    fromDateTime: string | null;
    toDateTime: string | null;
    onFromChange: (val: string | null) => void;
    onToChange: (val: string | null) => void;
    defaultCollapsed?: boolean;
}

function formatReadableDate(value: string | null): string {
    if (!value) return "Unbounded";
    const d = new Date(value);
    return d.toLocaleString();
}

export default function DateTimeRangeSelector({
    fromDateTime, toDateTime, onFromChange, onToChange, defaultCollapsed = false
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
        <CollapsibleSection title="Select Date Range" defaultCollapsed={defaultCollapsed}>
            <div className="flex flex-col space-y-4">
                {/* FROM */}
                <div>
                    <label className="text-sm font-medium flex justify-between items-center text-gray-800 dark:text-gray-100">
                        <span>
                            From:{" "}
                            <span className="font-normal text-gray-600 dark:text-gray-300">
                                {formatReadableDate(fromDateTime)}
                            </span>
                        </span>
                        {fromDateTime && (
                            <button
                                type="button"
                                className="text-sm text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-300"
                                onClick={() => onFromChange(null)}
                            >
                                Clear
                            </button>
                        )}
                    </label>
                    <input
                        type="datetime-local"
                        value={fromDateTime || ""}
                        onChange={(e) =>
                            onFromChange(e.target.value ? e.target.value : null)
                        }
                        className="border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                    />
                </div>
    
                {/* TO */}
                <div>
                    <label className="text-sm font-medium flex justify-between items-center text-gray-800 dark:text-gray-100">
                        <span>
                            To:{" "}
                            <span className="font-normal text-gray-600 dark:text-gray-300">
                                {formatReadableDate(toDateTime)}
                            </span>
                        </span>
                        {toDateTime && (
                            <button
                                type="button"
                                className="text-sm text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-300"
                                onClick={() => onToChange(null)}
                            >
                                Clear
                            </button>
                        )}
                    </label>
                    <input
                        type="datetime-local"
                        value={toDateTime || ""}
                        onChange={(e) =>
                            onToChange(e.target.value ? e.target.value : null)
                        }
                        className="border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                    />
                </div>
            </div>
    
            {error && (
                <div className="text-red-600 dark:text-red-400 mt-2">{error}</div>
            )}
        </CollapsibleSection>
    );
    
}