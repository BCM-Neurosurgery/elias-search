"use client"
import React, { useState } from "react";
import { ChevronDownIcon, ChevronRightIcon } from "@heroicons/react/24/outline";

interface CollapsibleSectionProps {
    title: string;
    children: React.ReactNode;
    defaultCollapsed?: boolean;
}

export default function CollapsibleSection({ title, children, defaultCollapsed = false }: CollapsibleSectionProps) {
    const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

    return (
        <div className="mb-4 border rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800">
            <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="w-full p-4 text-left flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
                <h3 className="text-md font-bold text-gray-800 dark:text-gray-100">
                    {title}
                </h3>
                {isCollapsed ? (
                    <ChevronRightIcon className="h-5 w-5 text-gray-500" />
                ) : (
                    <ChevronDownIcon className="h-5 w-5 text-gray-500" />
                )}
            </button>
            
            {!isCollapsed && (
                <div className="px-4 pb-4">
                    {children}
                </div>
            )}
        </div>
    );
}
