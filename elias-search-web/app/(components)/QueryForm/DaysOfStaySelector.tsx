"use client"
import React, { useEffect, useRef, useState } from "react";

interface DaysOfStaySelectorProps {
    maxDay: number; // the maximum day of stay (n)
    selectedDays: number[];
    onChange: (days: number[]) => void;
}

export default function DaysOfStaySelector({ maxDay, selectedDays, onChange }: DaysOfStaySelectorProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [mode, setMode] = useState<"add" | "remove" | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    const allSelected = selectedDays.length === maxDay
    const days = Array.from({ length: maxDay }, (_, i) => i + 1);

    // day toggle
    const toggleDay = (day: number, action: "add" | "remove") => {
        if (action === "add" && !selectedDays.includes(day)) {
            onChange([...selectedDays, day]);
        } else if (action == "remove" && selectedDays.includes(day)) {
            onChange(selectedDays.filter((d: number) => d !== day));
        }
    };

    const toggleAll = () => {
        if (allSelected) {
            onChange([]);
        } else {
            onChange(days); // Select all
        }
    }

    // functionality when press down on day
    const handleMouseDown = (day: number) => {
        const isSelected = selectedDays.includes(day);
        const newMode = isSelected ? "remove" : "add";
        setMode(newMode);
        setIsDragging(true);
        toggleDay(day, newMode);
    };

    const handleMouseUp = () => {
        setIsDragging(false);
        setMode(null);
    }

    const handleMouseEnter = (day : number) => {
        if (isDragging && mode) {
            toggleDay(day, mode)
        }
    }

    // clean on mouse release outside component
    useEffect(() => {
        const handleGlobalMouseUp = () => {
            setIsDragging(false);
            setMode(null);
        };
        
        window.addEventListener("mouseup", handleGlobalMouseUp);
        return () => window.removeEventListener("mouseup", handleGlobalMouseUp);
    }, []);

    return (
        <div className="mb-4 p-4 border rounded" ref={containerRef}>
            <div className="flex justify-between items-center mb-2">
                <h3 className="text-md font-bold">Select Days of Stay</h3>
                <button
                    onClick={toggleAll}
                    className="text-sm text-blue-600 underline"
                >
                    {allSelected ? "Select None" : "Select All"}
                </button>
            </div>

            <div className="inline-flex select-none border border-solid border-gray-400 rounded overflow-hidden">
                {days.map((day, idx) => {
                    const isSelected = selectedDays.includes(day);
                    const isLast = idx === days.length - 1;

                    return (
                    <div
                        key={day}
                        onMouseDown={() => handleMouseDown(day)}
                        onMouseEnter={() => handleMouseEnter(day)}
                        className={`w-10 h-10 flex items-center justify-center cursor-pointer
                            ${isSelected ? "bg-blue-600 text-white" : "bg-white text-gray-800"}
                            ${!isLast ? "border-r border-dashed border-gray-600" : ""}
                        `}
                    >
                        {day}
                    </div>
                    );
                })}
            </div>
        </div>
    )
}