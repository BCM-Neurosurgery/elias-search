import { useEffect } from "react";
import Select, { type MultiValue } from "react-select";

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
          className="w-full text-black dark:text-white"
          classNamePrefix="react-select"
        />
      </div>
    </div>
  );
}
