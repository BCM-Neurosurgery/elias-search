import React, { useEffect, useState } from "react";
import TaskSelector from "./TaskSelector";
import PatientSelector from "./PatientSelector";
import BrainRegionSelector from "./DateTimeRangeSelector";
import DateTimeRangeSelector from "./DateTimeRangeSelector";
import DaysOfStaySelector from "./DaysOfStaySelector";
import TimeOfWeekSelector from "./TimeOfWeekSelector";

type TimeSlot = {
    day: string; // Sunday, Monday, ...
    hour: number; // 0 - 23
}

export default function QueryForm() {
    // set hooks
    const [selectedTasks, setSelectedTasks] = useState<string[]>([]);
    const [allTasks, setAllTasks] = useState<boolean>(true);
    const [excludeStim, setExcludeStim] = useState<boolean>(true);
    const [patients, setPatients] = useState<string[]>([]);
    const [selectedPatients, setSelectedPatients] = useState<string[]>([]);
    const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
    const [fromDateTime, setFromDateTime] = useState<string | null>(null);
    const [toDateTime, setToDateTime] = useState<string | null>(null);
    const [selectedDaysOfStay, setSelectedDaysOfStay] = useState<number[]>([]);
    const [selectedTimesOfWeek, setSelectedTimesOfWeek] = useState<TimeSlot[]>([]); // grid state - design TBD

    // fetch patients on mount
    useEffect(() => {
        const fetchPatients = async () => {
            try {
                const response = await fetch("/api/query/patients", {
                    credentials: "include",
                });
                const data = await response.json();
                console.log("Fetched patients:", data);

                setPatients(data.patients || []);
                setSelectedPatients(data.patients || []); // Select all by default
            } catch (err) {
                console.error("Error fetching patients:", err)
            }
        };

        fetchPatients();
    }, []);

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
            const response = await fetch("/api/query/patients", {
                method: "GET",
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
            <TaskSelector 
                value={selectedTasks} 
                onChange={setSelectedTasks} 
                allTasks={allTasks}
                setAllTasks={setAllTasks}
                excludeStim={excludeStim}
                setExcludeStim={setExcludeStim}
            />
            <PatientSelector 
                patients={patients}
                value={selectedPatients} 
                onChange={setSelectedPatients} 
            />
            {/* <BrainRegionSelector value={selectedRegions} onChange={setSelectedRegions} /> */}
            <DateTimeRangeSelector
                fromDateTime={fromDateTime}
                toDateTime={toDateTime}
                onFromChange={setFromDateTime}
                onToChange={setToDateTime}
            />
            <DaysOfStaySelector 
                maxDay={10}
                selectedDays={selectedDaysOfStay} 
                onChange={setSelectedDaysOfStay} 
            />
            <TimeOfWeekSelector 
                selectedSlots={selectedTimesOfWeek} 
                onChange={setSelectedTimesOfWeek} 
            />
            <button
                onClick={handleSubmit}
                className="mt-4 bg-blue-600 text-white px-4 py-2 rounded"
            >
                Run Query
            </button>

        </div>
    )
}