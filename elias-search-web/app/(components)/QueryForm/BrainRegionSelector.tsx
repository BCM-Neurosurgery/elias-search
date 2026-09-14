"use client"
import { useMemo, useState } from "react";
import CollapsibleSection from "../CollapsibleSection";

export interface RegionOption {
    value: string; // FreeSurfer label, e.g. "Left-Hippocampus"
    label: string; // readable name, e.g. "Hippocampus"
    group: string; // "Subcortical", "Cortical", ...
    hemisphere: string | null; // "Left", "Right", or null for midline labels
}

interface BrainRegionSelectorProps {
    regions: RegionOption[]; // full list of selectable regions
    value: string[]; // selected FreeSurfer labels
    onChange: (selected: string[]) => void;
    allRegions: boolean;
    setAllRegions: (val: boolean) => void;
    defaultCollapsed?: boolean;
}

// keep groups in a stable anatomical order regardless of catalog ordering
const GROUP_ORDER = [
    "Subcortical",
    "Cortical",
    "White matter",
    "Cerebellum & brainstem",
    "Ventricles & CSF",
    "Other",
    "Unlocalized",
];

const HEMISPHERES = ["Both", "Left", "Right"] as const;
type Hemisphere = (typeof HEMISPHERES)[number];

export default function BrainRegionSelector({
    regions,
    value,
    onChange,
    allRegions,
    setAllRegions,
    defaultCollapsed = true,
}: BrainRegionSelectorProps) {
    const [search, setSearch] = useState("");
    const [hemisphere, setHemisphere] = useState<Hemisphere>("Both");

    const selected = useMemo(() => new Set(value), [value]);

    // regions left after the search box and hemisphere toggle, grouped for display
    const visibleGroups = useMemo(() => {
        const term = search.trim().toLowerCase();

        const matches = regions.filter((region) => {
            // midline labels have no hemisphere, so they stay visible either way
            if (hemisphere !== "Both" && region.hemisphere && region.hemisphere !== hemisphere) {
                return false;
            }
            if (!term) return true;
            return (
                region.label.toLowerCase().includes(term) ||
                region.value.toLowerCase().includes(term)
            );
        });

        const byGroup = new Map<string, RegionOption[]>();
        for (const region of matches) {
            const group = byGroup.get(region.group) ?? [];
            group.push(region);
            byGroup.set(region.group, group);
        }

        const rank = (group: string) => {
            const index = GROUP_ORDER.indexOf(group);
            return index === -1 ? GROUP_ORDER.length : index;
        };

        return Array.from(byGroup.entries())
            .sort(([a], [b]) => rank(a) - rank(b) || a.localeCompare(b))
            .map(([group, options]) => ({
                group,
                options: options.sort(
                    (a, b) =>
                        a.label.localeCompare(b.label) ||
                        (a.hemisphere ?? "").localeCompare(b.hemisphere ?? "")
                ),
            }));
    }, [regions, search, hemisphere]);

    const visibleValues = useMemo(
        () => visibleGroups.flatMap(({ options }) => options.map((o) => o.value)),
        [visibleGroups]
    );

    const toggleRegion = (region: string) => {
        if (selected.has(region)) {
            onChange(value.filter((r) => r !== region));
        } else {
            onChange([...value, region]);
        }
    };

    // add or remove a whole group at once, respecting the current search/hemisphere
    const toggleGroup = (options: RegionOption[]) => {
        const groupValues = options.map((o) => o.value);
        const allInGroupSelected = groupValues.every((v) => selected.has(v));
        if (allInGroupSelected) {
            onChange(value.filter((v) => !groupValues.includes(v)));
        } else {
            onChange([...value, ...groupValues.filter((v) => !selected.has(v))]);
        }
    };

    const selectAllVisible = () => {
        onChange([...value, ...visibleValues.filter((v) => !selected.has(v))]);
    };

    const clearSelection = () => onChange([]);

    const disabled = allRegions;

    return (
        <CollapsibleSection title="Select Brain Regions" defaultCollapsed={defaultCollapsed}>
            <label className="flex items-center space-x-1 mb-3 text-gray-800 dark:text-gray-200">
                <input
                    type="checkbox"
                    checked={allRegions}
                    onChange={(e) => setAllRegions(e.target.checked)}
                />
                <span>All Brain Regions</span>
            </label>

            <div className={disabled ? "opacity-50 pointer-events-none" : ""}>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    Keeps recordings from patients with at least one electrode contact in any
                    selected region.
                </p>

                <div className="flex flex-wrap items-center gap-2 mb-3">
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search regions"
                        className="flex-1 min-w-[12rem] px-2 py-1 border rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                    />

                    <div className="flex rounded border border-gray-300 dark:border-gray-600 overflow-hidden">
                        {HEMISPHERES.map((hemi) => (
                            <button
                                key={hemi}
                                onClick={() => setHemisphere(hemi)}
                                className={`px-2 py-1 text-sm transition-colors duration-150 ${
                                    hemisphere === hemi
                                        ? "bg-blue-600 text-white"
                                        : "bg-white text-gray-800 dark:bg-gray-800 dark:text-gray-200"
                                }`}
                            >
                                {hemi}
                            </button>
                        ))}
                    </div>

                    <button
                        onClick={selectAllVisible}
                        className="text-sm text-blue-600 dark:text-blue-400 underline focus:outline-none"
                    >
                        Select Shown
                    </button>
                    <button
                        onClick={clearSelection}
                        className="text-sm text-blue-600 dark:text-blue-400 underline focus:outline-none"
                    >
                        Select None
                    </button>
                </div>

                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {value.length} region{value.length === 1 ? "" : "s"} selected
                </p>

                <div className="max-h-96 overflow-y-auto pr-1">
                    {visibleGroups.length === 0 && (
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            No regions match this search.
                        </p>
                    )}

                    {visibleGroups.map(({ group, options }) => {
                        const allInGroupSelected = options.every((o) => selected.has(o.value));
                        return (
                            <div key={group} className="mb-4">
                                <div className="flex justify-between items-center mb-2">
                                    <h4 className="text-sm font-bold text-gray-900 dark:text-gray-100">
                                        {group}
                                    </h4>
                                    <button
                                        onClick={() => toggleGroup(options)}
                                        className="text-xs text-blue-600 dark:text-blue-400 underline focus:outline-none"
                                    >
                                        {allInGroupSelected ? "Clear Group" : "Select Group"}
                                    </button>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    {options.map((region) => {
                                        const isSelected = selected.has(region.value);
                                        return (
                                            <button
                                                key={region.value}
                                                title={region.value}
                                                onClick={() => toggleRegion(region.value)}
                                                className={`px-2 py-1 rounded border text-sm transition-colors duration-150 ${
                                                    isSelected
                                                        ? "bg-blue-600 text-white border-blue-600"
                                                        : "bg-white text-gray-800 border-gray-300 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600"
                                                }`}
                                            >
                                                {region.label}
                                                {region.hemisphere && (
                                                    <span
                                                        className={`ml-1 ${
                                                            isSelected
                                                                ? "text-blue-100"
                                                                : "text-gray-500 dark:text-gray-400"
                                                        }`}
                                                    >
                                                        ({region.hemisphere === "Left" ? "L" : "R"})
                                                    </span>
                                                )}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </CollapsibleSection>
    );
}
