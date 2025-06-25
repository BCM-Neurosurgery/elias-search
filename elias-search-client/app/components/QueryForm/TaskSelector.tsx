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
}

export default function TaskSelector({
  value, taskList, onChange, allTasks,
  setAllTasks, excludeStim, setExcludeStim,
}: TaskSelectorProps) {
  const handleSelectChange = (selectedOptions: MultiValue<OptionType>) => {
    onChange(selectedOptions.map((opt: OptionType) => opt.value));
  };

  const selectedOptions = taskList.filter((opt) => value.includes(opt.value));

  // Automatically uncheck Exclude STIM if ALl Tasks is unchecked
  useEffect(() => {
    if (!allTasks && excludeStim) {
      setExcludeStim(false);
    }
  }, [allTasks, excludeStim, setExcludeStim]);

  return (
    <div className="mb-4 p-4 border rounded">
      <h3 className="text-md font-bold mb-2">Select Tasks</h3>

      <div className="flex items-center space-x-4 mb-2">
        <label className="flex items-center space-x-1">
          <input
            type="checkbox"
            checked={allTasks}
            onChange={(e) => setAllTasks(e.target.checked)}
          />
          <span>All Tasks</span>
        </label>

        <label className="flex items-center space-x-1">
          <input
            type="checkbox"
            checked={excludeStim}
            onChange={(e) => setExcludeStim(e.target.checked)}
            disabled={!allTasks}
          />
          <span>Exclude Stim</span>
        </label>
      </div>

      {!allTasks && (
        <Select
          isMulti
          options={taskList}
          value={selectedOptions}
          onChange={handleSelectChange}
          placeholder="Type to include tasks"
        />
      )}
    </div>
  );
}
