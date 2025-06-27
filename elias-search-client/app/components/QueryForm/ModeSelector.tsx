import React from "react"

interface ModeSelectorProps {
    mode: "datalake" | "stitched";
    setMode: (mode: "datalake" | "stitched") => void;
}

export default function ModeSelector({ mode, setMode }: ModeSelectorProps) {
    const isDatalake = mode === "datalake";

    return (
        <div className="flex items-center justify-center mb-4">
            <div className="relative inline-flex">
                <span
                    className={`px-4 py-2 rounded-1-full border ${
                        isDatalake ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-700"
                        } cursor-pointer`}
                    onClick={() => setMode("datalake")}
                >
                    Datalake
                </span>
                <span
                    className={`px-4 py-2 rounded-1-full border ${
                        !isDatalake ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-700"
                        } cursor-pointer`}
                    onClick={() => setMode("stitched")}
                >
                    Stitched
                </span>
            </div>
        </div>
    )
}