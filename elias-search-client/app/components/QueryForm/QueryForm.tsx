import React, { useEffect, useState } from "react";
import { v4 as uuidv4 } from 'uuid';
import TaskSelector from "./TaskSelector";
import PatientSelector from "./PatientSelector";
// import BrainRegionSelector from "./DateTimeRangeSelector";
import DateTimeRangeSelector from "./DateTimeRangeSelector";
import DaysOfStaySelector from "./DaysOfStaySelector";
import TimeOfWeekSelector from "./TimeOfWeekSelector";
import ModeSelector from "./ModeSelector";
import Spinner from '../Spinner';

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
    const [allData, setAllData] = useState<boolean>(true);
    const [allTasks, setAllTasks] = useState<boolean>(true);
    const [excludeStim, setExcludeStim] = useState<boolean>(true);
    const [patients, setPatients] = useState<string[]>([]);
    const [selectedPatients, setSelectedPatients] = useState<string[]>([]);
    // const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
    const [fromDateTime, setFromDateTime] = useState<string | null>(null);
    const [toDateTime, setToDateTime] = useState<string | null>(null);
    const [selectedDaysOfStay, setSelectedDaysOfStay] = useState<number[]>([]);
    const [selectedTimesOfWeek, setSelectedTimesOfWeek] = useState<TimeSlot[]>([]); 
    const [mode, setMode] = useState<"datalake" | "stitched">("datalake");

    const [formLoading, setFormLoading] = useState(true);
    const [queryLoading, setQueryLoading] = useState(false);
    const [queryStatus, setQueryStatus] = useState<string | null>(null);
    const [progress, setProgress] = useState<{ current: number, total: number} | null>(null);

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
            } finally {
                setFormLoading(false);
            }
        };
        fetchFormdata();
    }, []);

    const handleSubmit = async () => {
        const session_id = uuidv4();
        setQueryLoading(true);
        setQueryStatus("Starting...");
        setProgress(null);

        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
        const wsBase = `${wsScheme}://${window.location.host}`;
        const ws = new WebSocket(`${wsBase}/ws/query/${session_id}`);

        ws.onmessage = (event) => {
            const message = event.data;

            if (message.startsWith("Processed")) {
                const match = message.match(/Processed (\d+)\/(\d+)/i);
                if (match) {
                    const current = parseInt(match[1]);
                    const total = parseInt(match[2]);
                    setProgress({ current, total });
                }
            } else {
                setQueryStatus(message);
            }
        }

        const payload = {
            selectedTasks,
            selectedPatients,
            allData,
            allTasks,
            excludeStim,
            // selectedRegions,
            fromDateTime,
            toDateTime,
            selectedDaysOfStay,
            selectedTimesOfWeek,
            mode
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
        } finally {
            setQueryLoading(false);
            ws.close();
        }
    };

      if (formLoading) {
        return (
            <div className="p-8 text-center">
                <Spinner />
                <p className="mt-4 text-gray-700 dark:text-gray-300">Loading form...</p>
            </div>
        );
    }

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
                allData={allData}
                setAllData={setAllData}
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
            <ModeSelector mode={mode} setMode={setMode} />
            <button
                onClick={handleSubmit}
                className={`mt-4 bg-blue-600 text-white px-4 py-2 rounded ${queryLoading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'}`}
                disabled={queryLoading}
            >
                {queryLoading ? (
                    <span className="flex items-center">
                        <svg className="animate-spin h-5 w-5 mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z" />
                        </svg>
                        Running...
                    </span>
                ) : 'Run Query'}
            </button>
            {queryLoading && (
                <div className="mt-4 text-sm text-gray-700 dark:text-gray-300">
                    {queryStatus?.startsWith("filtering") ? (
                        <p className="italic animate-pulse">{queryStatus}</p>
                    ) : progress ? (
                        <div>
                            <p>{`Processing row ${progress.current} of ${progress.total}`}</p>
                            <div className="w-full bg-gray-300 dark:bg-gray-800 rounded h-2 mt-1">
                                <div
                                className="bg-blue-600 h-2 rounded"
                                style={{ width: `${(progress.current / progress.total) * 100}%`}}
                                />
                            </div>
                        </div>
                    ) : null}
                </div>
            )}
        </div>
    )
}