import React, { useEffect, useState } from "react";
import TaskSelector from "./TaskSelector";
import PatientSelector from "./PatientSelector";
// import BrainRegionSelector from "./DateTimeRangeSelector";
import DateTimeRangeSelector from "./DateTimeRangeSelector";
import DaysOfStaySelector from "./DaysOfStaySelector";
import TimeOfWeekSelector from "./TimeOfWeekSelector";

type TimeSlot = {
    day: string; // Sunday, Monday, ...
    hour: number; // 0 - 23
}

interface OptionType {
  value: string;
  label: string;
}

interface QueryFormProps {
    onResult: (data: { result: any; query: any }) => void;
}

export default function QueryForm({ onResult } : QueryFormProps) {
    // set hooks
    const [taskList, setTaskList] = useState<OptionType[]>([]);
    const [selectedTasks, setSelectedTasks] = useState<string[]>([]);
    const [allTasks, setAllTasks] = useState<boolean>(true);
    const [excludeStim, setExcludeStim] = useState<boolean>(true);
    const [patients, setPatients] = useState<string[]>([]);
    const [selectedPatients, setSelectedPatients] = useState<string[]>([]);
    // const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
    const [fromDateTime, setFromDateTime] = useState<string | null>(null);
    const [toDateTime, setToDateTime] = useState<string | null>(null);
    const [selectedDaysOfStay, setSelectedDaysOfStay] = useState<number[]>([]);
    const [selectedTimesOfWeek, setSelectedTimesOfWeek] = useState<TimeSlot[]>([]); // grid state - design TBD

    // fetch patients on mount
    useEffect(() => {
        const fetchFormdata = async () => {
            try {
                const response = await fetch("/api/query/formdata", {
                    method: "GET",
                    credentials: "include",
                });
                const data = await response.json();
                console.log("Fetched patients:", data);

                setPatients(data.patients || []);
                const taskOptions = (data.tasks || []).map((task: string) => ({value: task, label: task}))
                setTaskList(taskOptions);
            } catch (err) {
                console.error("Error fetching patients:", err)
            }
        };
        fetchFormdata();
    }, []);

    const handleSubmit = async () => {
        const payload = {
            selectedTasks,
            selectedPatients,
            allTasks,
            excludeStim,
            // selectedRegions,
            fromDateTime,
            toDateTime,
            selectedDaysOfStay,
            selectedTimesOfWeek,
        }
        
        console.log("Submitting query with payload:", payload);

        try {
            const response = await fetch("/api/query/db", {
                method: "POST",
                headers: {"Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            console.log("Query results:", data);
            onResult({ result: data, query: payload });
        } catch (err) {
            console.error("Error submitting query:", err);
            onResult({ result: err, query: payload });
        }
    };

    return (
        <div className="p-4 border rounded shadow bg-white dark:bg-gray-900 dark:border-gray-700">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Query Form</h2>
            <TaskSelector 
                value={selectedTasks} 
                taskList={taskList}
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
            {/* <DateTimeRangeSelector
                fromDateTime={fromDateTime}
                toDateTime={toDateTime}
                onFromChange={setFromDateTime}
                onToChange={setToDateTime}
            /> */}
            {/* <DaysOfStaySelector 
                maxDay={10}
                selectedDays={selectedDaysOfStay} 
                onChange={setSelectedDaysOfStay} 
            /> */}
            {/* <TimeOfWeekSelector 
                selectedSlots={selectedTimesOfWeek} 
                onChange={setSelectedTimesOfWeek} 
            /> */}
            <button
                onClick={handleSubmit}
                className="mt-4 bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded"
            >
                Run Query
            </button>

        </div>
    )
}