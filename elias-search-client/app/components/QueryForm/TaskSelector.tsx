import { useEffect } from "react";
import Select, { type MultiValue } from "react-select";

interface OptionType {
  value: string;
  label: string;
}

interface TaskSelectorProps {
    value: string[]; // selected task values
    onChange: (selected: string[]) => void;
    allTasks: boolean;
    setAllTasks: (val: boolean) => void;
    excludeStim: boolean;
    setExcludeStim: (val: boolean) => void;
}

// task option list
const taskOptions: OptionType[] = [
    { value: "resting", label: "Resting"},
    { value: "catdi", label: "CAT-DI"},
    { value: "abcd", label: "ABCD"},
    { value: "rgb", label: "RGB"},
    { value: "gonogo_jumble", label: "GoNoGo Jumble"},
    { value: "gonogo_complex", label: "GoNoGo Complex"},
    { value: "gonogo_simple", label: "GoNoGo Simple"},
    { value: "math", label: "Math"},
    { value: "dot_estimation", label: "Dot Estimation"},
    { value: "og_pacman", label: "OG Pac-Man"},
    { value: "mst", label: "MST"},
    { value: "pep", label: "PEP"},
    { value: "ad_sweeps", label: "AD Sweeps"},
    { value: "prt", label: "PRT"},
    { value: "tnt", label: "TNT"},
    { value: "at", label: "AT"},
    { value: "esso", label: "ESSO"},
    { value: "urge", label: "Urge"},
    { value: "convo", label: "Convo"},
    { value: "podcast", label: "Podcast"},
    { value: "wof_recdec", label: "WoF/RecDec"},
    { value: "driving", label: "Driving"},
    { value: "dialogue", label: "Dialogue"},
    { value: "pacman", label: "Pac-Man"},
    { value: "fluency", label: "Fluency"},
    { value: "music", label: "Music"}
]

export default function TaskSelector({
  value, onChange, allTasks,
  setAllTasks, excludeStim, setExcludeStim,
}: TaskSelectorProps) {
  const handleSelectChange = (selectedOptions: MultiValue<OptionType>) => {
    onChange(selectedOptions.map((opt: OptionType) => opt.value));
  };

  const selectedOptions = taskOptions.filter((opt) => value.includes(opt.value));

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
          options={taskOptions}
          value={selectedOptions}
          onChange={handleSelectChange}
          placeholder="Type to include tasks"
        />
      )}
    </div>
  );
}
