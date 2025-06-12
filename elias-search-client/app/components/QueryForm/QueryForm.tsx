import React, { useState } from "react";
import TaskSelector from "./TaskSelector";
import PatientSelector from "./PatientSelector";
import BrainRegionSelector from "./DateTimeRangeSelector";
import DateTimeRangeSelector from "./DateTimeRangeSelector";
import DaysOfStaySelector from "./DaysOfStaySelector";
import TimeOfWeekSelector from "./TimeOfWeekSelector";

export default function QueryForm() {
    // set hooks
    const [selectedTasks, setSelectedTasks] = useState<string[]>([]);
    const [selectedPatients, setSelectedPatients] = useState<string[]>([]);
    const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
    const [fromDateTime, setFromDateTime] = useState<Date | null>(null);
    const [toDateTime, setToDateTime] = useState<Date | null>(null);
    const [selectedDaysOfStay, setSelectedDaysOfStay] = useState<number[]>([]);
    const [selectedTimesOfWeek, setSelectedTimesOfWeek] = useState<any>([]); // grid state - design TBD

    const handleSubmit = async () => {
        const payload = {
            selectedTasks,
            selectedPatients,
            selectedRegions,
            fromDateTime,
            toDateTime,
            selectedDaysOfStay,
            selectedTimesOfWeek,
        }
        
        console.log("Submitting query with payload:", payload);

        try {
            const response = await fetch("http://elias.bcms.bcm.edu/api/query", {
                method: "POST",
                headers: {"Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            console.log("Query results:", data);
        } catch (err) {
            console.error("Error submitting query:", err);
        }
    };

    return (
        <div className="p-4 border rounded shadow bg-white">
            <h2 className="text-x1 font-bold mb-4">Query Form</h2>
            <TaskSelector value={selectedTasks} onChange={setSelectedTasks} />
            <PatientSelector value={selectedPatients} onChange={setSelectedPatients} />
            <BrainRegionSelector value={selectedRegions} onChange={setSelectedRegions} />
            <DateTimeRangeSelector
                fromDateTime={fromDateTime}
                toDateTime={toDateTime}
                onFromChange={setFromDateTime}
                onToChange={setToDateTime}
            />
            <DaysOfStaySelector value={selectedDaysOfStay} onChange={setSelectedDaysOfStay} />
            <TimeOfWeekSelector value={selectedTimesOfWeek} onChange={setSelectedTimesOfWeek} />
            <button
                onClick={handleSubmit}
                className="mt-4 bg-blue-600 text-white px-4 py-2 rounded"
            >
                Run Query
            </button>

        </div>
    )
}