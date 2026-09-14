"""
Catalog of FreeSurfer region labels used by the brain-region query filter.

The ``area_fs_vox`` attribute of ``emu24.schema.AreaFsVox`` holds the FreeSurfer
label of the voxel a macro contact sits in, taken from an ``aparc+aseg``
segmentation. Those labels come from two sources:

* ``aseg`` subcortical/volumetric labels, e.g. ``Left-Hippocampus``.
* ``aparc`` Desikan-Killiany cortical labels, e.g. ``ctx-lh-middletemporal``.

This module enumerates both so the query form can offer the full set of regions
without needing to scan the database first, and so a selection made in the
browser can be expanded into every spelling the database may hold.

Label spellings are not perfectly stable across FreeSurfer versions. Entries
deprecated in FreeSurfer 7 are written with a trailing ``*`` in
``FreeSurferColorLUT.txt`` (``Left-Thalamus-Proper*``), and a few were renamed
outright (``Left-Thalamus-Proper`` -> ``Left-Thalamus``). Both real spellings
appear in existing electrode CSVs, so every canonical value carries the list of
variants that should match it.
"""

# Group names, ordered the way the form should display them.
GROUP_SUBCORTICAL = "Subcortical"
GROUP_CORTICAL = "Cortical"
GROUP_WHITE_MATTER = "White matter"
GROUP_CEREBELLUM = "Cerebellum & brainstem"
GROUP_VENTRICLES = "Ventricles & CSF"
GROUP_OTHER = "Other"
GROUP_UNLOCALIZED = "Unlocalized"

GROUP_ORDER = [
    GROUP_SUBCORTICAL,
    GROUP_CORTICAL,
    GROUP_WHITE_MATTER,
    GROUP_CEREBELLUM,
    GROUP_VENTRICLES,
    GROUP_OTHER,
    GROUP_UNLOCALIZED,
]

# Desikan-Killiany cortical parcels, emitted per hemisphere as ctx-lh-* / ctx-rh-*.
_CORTICAL_PARCELS = [
    ("bankssts", "Banks of superior temporal sulcus"),
    ("caudalanteriorcingulate", "Caudal anterior cingulate"),
    ("caudalmiddlefrontal", "Caudal middle frontal gyrus"),
    ("corpuscallosum", "Corpus callosum (cortical label)"),
    ("cuneus", "Cuneus"),
    ("entorhinal", "Entorhinal cortex"),
    ("frontalpole", "Frontal pole"),
    ("fusiform", "Fusiform gyrus"),
    ("inferiorparietal", "Inferior parietal cortex"),
    ("inferiortemporal", "Inferior temporal gyrus"),
    ("insula", "Insula"),
    ("isthmuscingulate", "Isthmus of cingulate"),
    ("lateraloccipital", "Lateral occipital cortex"),
    ("lateralorbitofrontal", "Lateral orbitofrontal cortex"),
    ("lingual", "Lingual gyrus"),
    ("medialorbitofrontal", "Medial orbitofrontal cortex"),
    ("middletemporal", "Middle temporal gyrus"),
    ("paracentral", "Paracentral lobule"),
    ("parahippocampal", "Parahippocampal gyrus"),
    ("parsopercularis", "Pars opercularis"),
    ("parsorbitalis", "Pars orbitalis"),
    ("parstriangularis", "Pars triangularis"),
    ("pericalcarine", "Pericalcarine cortex"),
    ("postcentral", "Postcentral gyrus"),
    ("posteriorcingulate", "Posterior cingulate"),
    ("precentral", "Precentral gyrus"),
    ("precuneus", "Precuneus"),
    ("rostralanteriorcingulate", "Rostral anterior cingulate"),
    ("rostralmiddlefrontal", "Rostral middle frontal gyrus"),
    ("superiorfrontal", "Superior frontal gyrus"),
    ("superiorparietal", "Superior parietal cortex"),
    ("superiortemporal", "Superior temporal gyrus"),
    ("supramarginal", "Supramarginal gyrus"),
    ("temporalpole", "Temporal pole"),
    ("transversetemporal", "Transverse temporal gyrus"),
    ("unknown", "Unknown (cortical)"),
]

# aseg labels that exist once per hemisphere, emitted as Left-* / Right-*.
# (suffix, display name, group, extra variants for the Left/Right form)
_LATERAL_ASEG = [
    ("Accumbens-area", "Nucleus accumbens", GROUP_SUBCORTICAL, ()),
    ("Amygdala", "Amygdala", GROUP_SUBCORTICAL, ()),
    ("Caudate", "Caudate", GROUP_SUBCORTICAL, ()),
    ("Cerebellum-Cortex", "Cerebellar cortex", GROUP_CEREBELLUM, ()),
    ("Cerebellum-White-Matter", "Cerebellar white matter", GROUP_CEREBELLUM, ()),
    ("Cerebral-Cortex", "Cerebral cortex (unparcellated)", GROUP_CORTICAL, ()),
    ("Cerebral-White-Matter", "Cerebral white matter", GROUP_WHITE_MATTER, ()),
    ("choroid-plexus", "Choroid plexus", GROUP_OTHER, ()),
    ("Hippocampus", "Hippocampus", GROUP_SUBCORTICAL, ()),
    ("Inf-Lat-Vent", "Inferior lateral ventricle", GROUP_VENTRICLES, ()),
    ("Lateral-Ventricle", "Lateral ventricle", GROUP_VENTRICLES, ()),
    ("Pallidum", "Pallidum", GROUP_SUBCORTICAL, ()),
    ("Putamen", "Putamen", GROUP_SUBCORTICAL, ()),
    ("Substancia-Nigra", "Substantia nigra", GROUP_SUBCORTICAL, ()),
    ("Thalamus-Proper", "Thalamus", GROUP_SUBCORTICAL, ("Thalamus",)),
    ("undetermined", "Undetermined", GROUP_OTHER, ()),
    ("VentralDC", "Ventral diencephalon", GROUP_SUBCORTICAL, ()),
    ("vessel", "Vessel", GROUP_OTHER, ()),
    ("WM-hypointensities", "White matter hypointensities", GROUP_WHITE_MATTER, ()),
    ("non-WM-hypointensities", "Non-white-matter hypointensities", GROUP_OTHER, ()),
]

# aseg labels with no hemisphere of their own.
# (label, display name, group)
_MIDLINE_ASEG = [
    ("3rd-Ventricle", "Third ventricle", GROUP_VENTRICLES),
    ("4th-Ventricle", "Fourth ventricle", GROUP_VENTRICLES),
    ("5th-Ventricle", "Fifth ventricle", GROUP_VENTRICLES),
    ("Brain-Stem", "Brainstem", GROUP_CEREBELLUM),
    ("CC_Anterior", "Corpus callosum, anterior", GROUP_WHITE_MATTER),
    ("CC_Central", "Corpus callosum, central", GROUP_WHITE_MATTER),
    ("CC_Mid_Anterior", "Corpus callosum, mid-anterior", GROUP_WHITE_MATTER),
    ("CC_Mid_Posterior", "Corpus callosum, mid-posterior", GROUP_WHITE_MATTER),
    ("CC_Posterior", "Corpus callosum, posterior", GROUP_WHITE_MATTER),
    ("CSF", "CSF", GROUP_VENTRICLES),
    ("Optic-Chiasm", "Optic chiasm", GROUP_OTHER),
    ("WM-hypointensities", "White matter hypointensities", GROUP_WHITE_MATTER),
    ("non-WM-hypointensities", "Non-white-matter hypointensities", GROUP_OTHER),
]

# Values that mean "this contact was not assigned a brain region".
_UNLOCALIZED = [
    ("Unknown", "Unknown / outside segmentation", GROUP_UNLOCALIZED),
    ("NA", "Not localized", GROUP_UNLOCALIZED),
]

LEFT = "Left"
RIGHT = "Right"

_HEMI_PREFIX = {LEFT: ("Left-", "ctx-lh-"), RIGHT: ("Right-", "ctx-rh-")}


def _entry(value, label, group, hemisphere=None, variants=()):
    """Build one catalog entry, always accepting the deprecated ``*`` spelling."""
    all_variants = [value]
    for variant in variants:
        if variant not in all_variants:
            all_variants.append(variant)
    # FreeSurfer 7 marks deprecated LUT names with a trailing asterisk.
    all_variants += [f"{v}*" for v in list(all_variants)]
    return {
        "value": value,
        "label": label,
        "group": group,
        "hemisphere": hemisphere,
        "variants": all_variants,
    }


def _build_catalog():
    entries = []

    for hemi in (LEFT, RIGHT):
        aseg_prefix, ctx_prefix = _HEMI_PREFIX[hemi]

        for suffix, name, group, extra in _LATERAL_ASEG:
            entries.append(_entry(
                f"{aseg_prefix}{suffix}", name, group, hemi,
                variants=tuple(f"{aseg_prefix}{e}" for e in extra),
            ))

        for parcel, name in _CORTICAL_PARCELS:
            entries.append(_entry(f"{ctx_prefix}{parcel}", name, GROUP_CORTICAL, hemi))

    for value, name, group in _MIDLINE_ASEG:
        entries.append(_entry(value, name, group))

    for value, name, group in _UNLOCALIZED:
        entries.append(_entry(value, name, group))

    return entries


REGION_CATALOG = _build_catalog()

# Every spelling we know about -> the catalog value it belongs to.
_VARIANT_TO_VALUE = {
    variant: entry["value"]
    for entry in REGION_CATALOG
    for variant in entry["variants"]
}

_VALUE_TO_ENTRY = {entry["value"]: entry for entry in REGION_CATALOG}


def canonical_value(raw_label):
    """Map a raw ``area_fs_vox`` string onto its catalog value.

    Returns ``None`` for labels the catalog does not know, so callers can decide
    whether to surface them as extra options.
    """
    if raw_label is None:
        return None
    label = str(raw_label).strip()
    if not label:
        return None
    return _VARIANT_TO_VALUE.get(label)


def expand_values(values):
    """Expand selected catalog values into every spelling to match in the database.

    Unknown values are passed through unchanged so a region discovered in the
    database but missing from the catalog still filters correctly.
    """
    expanded = []
    for value in values or []:
        entry = _VALUE_TO_ENTRY.get(value)
        candidates = entry["variants"] if entry else [value]
        for candidate in candidates:
            if candidate not in expanded:
                expanded.append(candidate)
    return expanded


def form_options(extra_labels=()):
    """Catalog entries shaped for the query form, plus any unrecognized labels.

    ``extra_labels`` are raw ``area_fs_vox`` values observed in the database.
    Anything not already covered by the catalog is appended to the "Other" group
    so the form never silently hides a region that real data contains.
    """
    options = [
        {
            "value": entry["value"],
            "label": entry["label"],
            "group": entry["group"],
            "hemisphere": entry["hemisphere"],
        }
        for entry in REGION_CATALOG
    ]
    seen = {option["value"] for option in options}

    for raw in extra_labels or []:
        if canonical_value(raw) is not None:
            continue
        label = str(raw).strip()
        if not label or label in seen:
            continue
        seen.add(label)
        options.append({
            "value": label,
            "label": label,
            "group": GROUP_OTHER,
            "hemisphere": None,
        })

    return options
