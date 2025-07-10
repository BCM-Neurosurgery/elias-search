"use client"
import { useEffect } from "react";
import Select, { type MultiValue, StylesConfig } from "react-select";
import { useTheme } from 'next-themes';

interface OptionType {
  value: string;
  label: string;
}

interface TaskSelectorProps {
    value: string[]; // selected task values
    taskList: OptionType[]; // full list of tasks
    onChange: (selected: string[]) => void;
    allTasks: boolean;
    setAllTasks: (val: boolean) => void;
    excludeStim: boolean;
    setExcludeStim: (val: boolean) => void;
    allData: boolean;
    setAllData: (val: boolean) => void;
}

export default function TaskSelector({
  value, taskList, onChange, 
  allTasks, setAllTasks, 
  excludeStim, setExcludeStim,
  allData, setAllData
}: TaskSelectorProps) {
  const handleSelectChange = (selectedOptions: MultiValue<OptionType>) => {
    onChange(selectedOptions.map((opt: OptionType) => opt.value));
  };

  const selectedOptions = taskList.filter((opt) => value.includes(opt.value));

  // set checkboxes appropriatelya cc to hierarchy
  useEffect(() => {
    if (allData) {
      setAllTasks(true);
      setExcludeStim(false);
    }
  }, [allData]);

  // Automatically uncheck Exclude STIM if ALl Tasks is unchecked
  useEffect(() => {
    if (!allTasks && excludeStim) {
      setExcludeStim(false);
    }
  }, [allTasks, excludeStim, setExcludeStim]);

  const { resolvedTheme } = useTheme(); // will be 'dark' or 'light'

  const isDark = resolvedTheme === 'dark';

  const selectStyles: StylesConfig<OptionType, true> = {
    control: (base, state) => ({
      ...base,
      backgroundColor: isDark ? '#1f2937' : '#ffffff', // gray-800 or white
      borderColor: state.isFocused
        ? isDark ? '#3b82f6' : '#60a5fa' // blue-500/400
        : isDark ? '#4b5563' : '#d1d5db', // gray-600 or gray-300
      color: isDark ? '#ffffff' : '#111827',
      boxShadow: state.isFocused
        ? isDark
          ? '0 0 0 2px #3b82f6'
          : '0 0 0 2px #60a5fa'
        : 'none',
      '&:hover': {
        borderColor: isDark ? '#6b7280' : '#9ca3af', // gray-500/400
      },
    }),
    menu: (base) => ({
      ...base,
      backgroundColor: isDark ? '#1f2937' : '#ffffff',
      color: isDark ? '#ffffff' : '#111827',
    }),
    option: (base, state) => ({
      ...base,
      backgroundColor: state.isSelected
        ? isDark ? '#2563eb' : '#3b82f6' // blue-600/500
        : state.isFocused
        ? isDark ? '#374151' : '#f3f4f6' // gray-700 or gray-100
        : isDark ? '#1f2937' : '#ffffff',
      color: state.isSelected
        ? '#ffffff'
        : isDark ? '#d1d5db' : '#111827',
      cursor: 'pointer',
    }),
    multiValue: (base) => ({
      ...base,
      backgroundColor: isDark ? '#374151' : '#e5e7eb', // gray-700 or gray-200
    }),
    multiValueLabel: (base) => ({
      ...base,
      color: isDark ? '#f9fafb' : '#111827', // gray-50 or gray-900
    }),
    multiValueRemove: (base) => ({
      ...base,
      color: isDark ? '#9ca3af' : '#4b5563',
      ':hover': {
        backgroundColor: isDark ? '#4b5563' : '#d1d5db',
        color: isDark ? '#ffffff' : '#111827',
      },
    }),
  };

  return (
    <div className="mb-4 p-4 border rounded bg-white dark:bg-gray-800 dark:border-gray-700">
      <h3 className="text-md font-bold mb-2 text-gray-900 dark:text-gray-100">Select Tasks</h3>

      <div className="flex flex-wrap items-center space-x-4 mb-3">
        <label className="flex items-center space-x-1 text-gray-800 dark:text-gray-200">
          <input
            type="checkbox"
            checked={allData}
            onChange={(e) => setAllData(e.target.checked)}
          />
          <span>All Data</span>
        </label>

        <label className="flex items-center space-x-1 text-gray-800 dark:text-gray-200">
          <input
            type="checkbox"
            checked={allTasks}
            onChange={(e) => setAllTasks(e.target.checked)}
            disabled={allData}
          />
          <span>All Tasks</span>
        </label>

        <label className="flex items-center space-x-1 text-gray-800 dark:text-gray-200">
          <input
            type="checkbox"
            checked={excludeStim}
            onChange={(e) => setExcludeStim(e.target.checked)}
            disabled={!allTasks || allData}
          />
          <span>Exclude Stim</span>
        </label>
      </div>

      <div className={!allTasks && !allData ? "" : "opacity-50 pointer-events-none"}>
        <Select
          isMulti
          options={taskList}
          value={selectedOptions}
          onChange={handleSelectChange}
          placeholder="Type to include tasks"
          className="w-full"
          styles={selectStyles}
        />
      </div>
    </div>
  );
}
