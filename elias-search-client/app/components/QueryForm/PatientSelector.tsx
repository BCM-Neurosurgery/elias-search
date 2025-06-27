interface PatientSelectorProps {
    patients: string[]; // Full list of patients
    value: string[]; // Selected patient IDs
    onChange: (selected: string[]) => void;
}


export default function PatientSelector(
    { patients, value, onChange }: PatientSelectorProps) {
    const allSelected = value.length === patients.length;

    // remove patient from current value list if already in it, otherwise add them
    const togglePatient = (patient: string) => {
        if (value.includes(patient)) {
            onChange(value.filter((p) => p !== patient));
        } else {
            onChange([...value, patient]);
        }
    };

    // toggle patients for all or none button
    const toggleSelectAll = () => {
        if (allSelected) {
            onChange([]); // Select none
        } else {
            onChange([...patients]); // Select all
        }
    };

    return (
        <div className="mb-4 p-4 border rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900">
            <div className="flex justify-between items-center mb-2">
                <h3 className="text-md font-bold text-gray-900 dark:text-gray-100">Select Patients</h3>
                <button
                onClick={toggleSelectAll}
                className="text-sm text-blue-600 dark:text-blue-400 underline focus:outline-none"
                >
                {allSelected ? "Select None" : "Select All"}
                </button>
            </div>
            <div className="flex flex-wrap gap-2">
                {patients.map((patient) => {
                const selected = value.includes(patient);
                return (
                    <button
                    key={patient}
                    onClick={() => togglePatient(patient)}
                    className={`px-2 py-1 rounded border transition-colors duration-150 ${
                        selected
                        ? "bg-blue-600 text-white border-blue-600"
                        : "bg-white text-gray-800 border-gray-300 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600"
                    }`}
                    >
                    {patient}
                    </button>
                );
                })}
            </div>
        </div>
    );
}