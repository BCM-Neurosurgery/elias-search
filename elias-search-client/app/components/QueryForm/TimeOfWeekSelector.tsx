import React, { useEffect, useState } from "react";

type TimeSlot = {
    day: string; // Sunday, Monday, ...
    hour: number; // 0 - 23
}

interface TimeOfWeekSelectorProps {
    selectedSlots: TimeSlot[];
    onChange: (slots: TimeSlot[]) => void
}

const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const hours = Array.from({ length: 24}, (_, i) => i);

function slotKey(day: string, hour: number) {
    return `${day}-${hour}`;
}

export default function TimeOfWeekSelector({ selectedSlots, onChange }: TimeOfWeekSelectorProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [dragMode, setDragMode] = useState<"add" | "remove" | null>(null);

    const selectedMap = new Set(selectedSlots.map((s) => slotKey(s.day, s.hour)));

    const isSelected = (day: string, hour: number) =>
        selectedMap.has(slotKey(day, hour));

    const toggleSlot = (day: string, hour: number, mode: "add" | "remove") => {
        const key = slotKey(day, hour);
        const exists = selectedMap.has(key);

        if (mode === "add" && !exists) {
            onChange([...selectedSlots, { day, hour }]);
        } else if (mode === "remove" && exists) {
            onChange(selectedSlots.filter((s) => slotKey(s.day, s.hour) !== key));
        }
    };

    const handleMouseDown = (day: string, hour: number) => {
        const mode = isSelected(day, hour) ? "remove" : "add"
        setDragMode(mode);
        setIsDragging(true);
        toggleSlot(day, hour, mode);
    };

    const handleMouseEnter = (day: string, hour: number) => {
       if (isDragging && dragMode) {
            toggleSlot(day, hour, dragMode);
       } 
    };

    const handleMouseUp = () => {
        setIsDragging(false);
        setDragMode(null);
    };

    useEffect(() => {
        window.addEventListener("mouseup", handleMouseUp);
        return () => window.removeEventListener("mouseup", handleMouseUp);
    }, []);

    const handleSelectAll = () => {
        const all = daysOfWeek.flatMap((day) => 
            hours.map((hour) => ({ day, hour }))
        );
        onChange(all);
    };

    const handleClearAll = () => {
        onChange([]);
    }
    return (
    <div className="mb-4 p-4 border rounded">
        <div className="flex justify-between items-center mb-2">
            <h3 className="text-md font-bold">Select Time of Week</h3>
            <div className="space-x-4">
                <button onClick={handleSelectAll} className="text-sm text-blue-600 underline">Select All</button>
                <button onClick={handleClearAll} className="text-sm text-blue-600 underline">Clear All</button>
            </div>
        </div>

        <div className="overflow-auto">
            <div className="grid" style={{ gridTemplateColumns: `80px repeat(7, 1fr)` }}>
                {/* Day headers */}
                <div></div>
                {daysOfWeek.map((day) => (
                    <div key={day} className="text-center font-semibold border-b pb-1">
                        {day}
                    </div>
                ))}

                {/* Hour rows */}
                {hours.map((hour) => (
                    <React.Fragment key={hour}>
                        <div className="text-right pr-2 text-sm border-r">
                            {hour === 0 ? "12 AM" : hour < 12 ? `${hour} AM` : hour === 12 ? "12 PM" : `${hour - 12} PM`}
                        </div>

                        {daysOfWeek.map((day) => {
                            const selected = isSelected(day, hour);
                            return (
                                <div
                                    key={`${day}-${hour}`}
                                    onMouseDown={() => handleMouseDown(day, hour)}
                                    onMouseEnter={() => handleMouseEnter(day, hour)}
                                    className={`w-full h-8 border border-gray-300 cursor-pointer ${
                                        selected ? "bg-blue-600" : "bg-white"
                                    }`}
                                />
                            );
                        })}
                    </React.Fragment>

                ))}
            </div>
        </div>
    </div>
    );
}