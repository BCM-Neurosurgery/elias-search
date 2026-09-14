"""Tests for the brain-region query filter.

These run without the real DataJoint/MySQL deployment: Django is pointed at a
throwaway SQLite database whose tables use the same names and columns as the
DataJoint schema, and synthetic electrode/recording rows are inserted directly.

Run from the ``elias-search-server`` directory:

    python -m unittest discover tests
"""
import os
import sys
import types
import unittest

SERVER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SERVER_DIR)

import django
from django.conf import settings

# The real settings module pulls in MySQL, CORS and DataJoint configuration that
# a test run has no use for, so configure a minimal project instead.
if not settings.configured:
    settings.configure(
        DEBUG=True,
        INSTALLED_APPS=["es_server"],
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
            "neural_data": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
        },
        DATABASE_ROUTERS=["es_server.database_router.NeuralDataRouter"],
        CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}},
        USE_TZ=True,
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    )

# query.py reads recording durations out of Blackrock files at result-formatting
# time. Only the filtering half is under test here, so stub the reader out rather
# than requiring the private package to be installed.
if "pyNsXStitch" not in sys.modules:
    pynsx = types.ModuleType("pyNsXStitch")
    helpers = types.ModuleType("pyNsXStitch.helpers")
    helpers.get_nsx_start_timestamp = lambda *a, **kw: 0
    helpers.get_nsx_duration = lambda *a, **kw: 0
    pynsx.helpers = helpers
    sys.modules["pyNsXStitch"] = pynsx
    sys.modules["pyNsXStitch.helpers"] = helpers

django.setup()

from django.db import connections  # noqa: E402

from es_server import brain_regions  # noqa: E402
from es_server.models import AreaFsVox, NSPChunks, StitchedChunks  # noqa: E402
from es_server.query import QueryBuilder  # noqa: E402


# Every distinct Area_fs value found across the electrode exports of 11 real
# patients. The catalog has to cover all of them, including the deprecated
# "Left-Thalamus-Proper*" spelling FreeSurfer 7 emits.
OBSERVED_LABELS = [
    "CSF",
    "Left-Amygdala",
    "Left-Cerebral-White-Matter",
    "Left-Hippocampus",
    "Left-Putamen",
    "Left-Thalamus-Proper",
    "Left-Thalamus-Proper*",
    "Left-VentralDC",
    "NA",
    "Right-Amygdala",
    "Right-Cerebral-White-Matter",
    "Right-Hippocampus",
    "Right-Thalamus-Proper",
    "Right-Thalamus-Proper*",
    "Unknown",
    "ctx-lh-fusiform",
    "ctx-lh-insula",
    "ctx-lh-isthmuscingulate",
    "ctx-lh-lateralorbitofrontal",
    "ctx-lh-lingual",
    "ctx-lh-medialorbitofrontal",
    "ctx-lh-middletemporal",
    "ctx-lh-parahippocampal",
    "ctx-lh-parstriangularis",
    "ctx-lh-precentral",
    "ctx-lh-precuneus",
    "ctx-lh-rostralanteriorcingulate",
    "ctx-lh-rostralmiddlefrontal",
    "ctx-lh-superiorfrontal",
    "ctx-lh-superiortemporal",
    "ctx-lh-supramarginal",
    "ctx-lh-temporalpole",
    "ctx-lh-transversetemporal",
    "ctx-rh-inferiortemporal",
    "ctx-rh-insula",
    "ctx-rh-lateralorbitofrontal",
    "ctx-rh-medialorbitofrontal",
    "ctx-rh-middletemporal",
    "ctx-rh-parahippocampal",
    "ctx-rh-parsopercularis",
    "ctx-rh-parstriangularis",
    "ctx-rh-posteriorcingulate",
    "ctx-rh-rostralanteriorcingulate",
    "ctx-rh-rostralmiddlefrontal",
    "ctx-rh-superiorfrontal",
    "ctx-rh-superiortemporal",
    "ctx-rh-transversetemporal",
]


class BrainRegionCatalogTests(unittest.TestCase):
    def test_catalog_covers_every_observed_label(self):
        uncovered = [
            label for label in OBSERVED_LABELS
            if brain_regions.canonical_value(label) is None
        ]
        self.assertEqual(uncovered, [])

    def test_deprecated_spelling_maps_to_same_region(self):
        self.assertEqual(
            brain_regions.canonical_value("Left-Thalamus-Proper*"),
            brain_regions.canonical_value("Left-Thalamus-Proper"),
        )

    def test_renamed_thalamus_maps_to_same_region(self):
        # FreeSurfer 7 dropped the "-Proper" suffix
        self.assertEqual(
            brain_regions.canonical_value("Right-Thalamus"),
            "Right-Thalamus-Proper",
        )

    def test_expand_covers_every_spelling_of_a_selection(self):
        expanded = brain_regions.expand_values(["Left-Thalamus-Proper"])
        for spelling in ("Left-Thalamus-Proper", "Left-Thalamus-Proper*", "Left-Thalamus"):
            self.assertIn(spelling, expanded)

    def test_expand_passes_unknown_values_through(self):
        self.assertEqual(brain_regions.expand_values(["Made-Up-Label"]), ["Made-Up-Label"])

    def test_unrecognized_label_is_offered_rather_than_hidden(self):
        options = brain_regions.form_options(extra_labels=["Left-Hippocampus", "Brand-New-Area"])
        values = [option["value"] for option in options]
        self.assertIn("Brand-New-Area", values)
        # a label already covered must not be duplicated as a raw option
        self.assertEqual(values.count("Left-Hippocampus"), 1)

    def test_options_are_hemisphere_tagged(self):
        by_value = {option["value"]: option for option in brain_regions.form_options()}
        self.assertEqual(by_value["Left-Hippocampus"]["hemisphere"], "Left")
        self.assertEqual(by_value["ctx-rh-insula"]["hemisphere"], "Right")
        # midline structures belong to neither hemisphere
        self.assertIsNone(by_value["Brain-Stem"]["hemisphere"])


# Synthetic cohort: patient -> the regions its contacts were localized to.
COHORT = {
    1: ["Left-Amygdala", "Left-Hippocampus", "Left-Cerebral-White-Matter"],
    2: ["ctx-rh-superiortemporal", "Right-Thalamus-Proper*", "Unknown"],
    3: ["ctx-lh-middletemporal", "ctx-lh-insula"],
    4: ["Right-Amygdala", "NA"],
}

# Patient 5 has recordings but no electrode localization at all.
PATIENTS_WITH_RECORDINGS = [1, 2, 3, 4, 5]

ADMISSION_ID = 1


def _sql(statement, params=()):
    with connections["neural_data"].cursor() as cursor:
        cursor.execute(statement, params)


def _create_tables():
    # Column lists mirror the DataJoint tables; note there is no surrogate "id"
    # column, so a query that needs one would fail here just as it would in MySQL.
    _sql("DROP TABLE IF EXISTS area_fs_vox")
    _sql("""
        CREATE TABLE area_fs_vox (
            patient_id INTEGER, admission_id INTEGER, config_id INTEGER,
            probe_id INTEGER, electrode_id INTEGER, area_fs_vox VARCHAR(64)
        )
    """)
    _sql("DROP TABLE IF EXISTS __n_s_p_chunks")
    _sql("""
        CREATE TABLE __n_s_p_chunks (
            patient_id INTEGER, admission_id INTEGER, toc_id INTEGER,
            chunk_id INTEGER, nsp_id INTEGER, file VARCHAR(256),
            absolute_time VARCHAR(256), nev_file BLOB, ns3_file BLOB, ns5_file BLOB
        )
    """)
    _sql("DROP TABLE IF EXISTS __stitched_chunks")
    _sql("""
        CREATE TABLE __stitched_chunks (
            patient_id INTEGER, admission_id INTEGER, toc_id INTEGER,
            start_chunk INTEGER, nsp_id INTEGER, start_tid INTEGER, emu_id INTEGER,
            stop_chunk INTEGER, stop_tid INTEGER, start_filename VARCHAR(256),
            stop_filename VARCHAR(256), nev_file BLOB, ns5_file BLOB, ns3_file BLOB
        )
    """)


def _seed():
    for patient_id, regions in COHORT.items():
        for electrode_id, region in enumerate(regions):
            _sql(
                "INSERT INTO area_fs_vox VALUES (%s, %s, %s, %s, %s, %s)",
                (patient_id, ADMISSION_ID, 0, 0, electrode_id, region),
            )

    for patient_id in PATIENTS_WITH_RECORDINGS:
        for chunk_id in range(2):
            _sql(
                "INSERT INTO __n_s_p_chunks "
                "(patient_id, admission_id, toc_id, chunk_id, nsp_id, file, absolute_time) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (patient_id, ADMISSION_ID, 0, chunk_id, 1,
                 f"p{patient_id}_c{chunk_id}", "2025-01-01 12:00:00.000000"),
            )
            _sql(
                "INSERT INTO __stitched_chunks "
                "(patient_id, admission_id, toc_id, start_chunk, nsp_id, start_tid, "
                "emu_id, stop_chunk, stop_tid) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (patient_id, ADMISSION_ID, 0, chunk_id, 1, chunk_id, 100 + patient_id,
                 chunk_id, chunk_id),
            )


def _payload(**overrides):
    data = {"mode": "datalake", "allRegions": True, "selectedRegions": []}
    data.update(overrides)
    return data


class RegionFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _create_tables()
        _seed()

    def matched_patients(self, data, model=NSPChunks):
        qb = QueryBuilder(data)
        qb._region_query()
        return sorted(set(
            model.objects.filter(qb.filter).values_list("patient_id", flat=True)
        ))

    def test_default_keeps_every_patient(self):
        self.assertEqual(
            self.matched_patients(_payload()),
            PATIENTS_WITH_RECORDINGS,
        )

    def test_single_region_keeps_only_implanted_patients(self):
        self.assertEqual(
            self.matched_patients(_payload(
                allRegions=False, selectedRegions=["Left-Amygdala"])),
            [1],
        )

    def test_multiple_regions_are_an_or(self):
        self.assertEqual(
            self.matched_patients(_payload(
                allRegions=False,
                selectedRegions=["Left-Amygdala", "ctx-lh-insula"])),
            [1, 3],
        )

    def test_region_selection_matches_deprecated_spelling_in_database(self):
        # patient 2's thalamic contact is stored as "Right-Thalamus-Proper*"
        self.assertEqual(
            self.matched_patients(_payload(
                allRegions=False, selectedRegions=["Right-Thalamus-Proper"])),
            [2],
        )

    def test_region_nobody_was_implanted_in_returns_nothing(self):
        self.assertEqual(
            self.matched_patients(_payload(
                allRegions=False, selectedRegions=["ctx-lh-cuneus"])),
            [],
        )

    def test_empty_selection_returns_nothing(self):
        # regions explicitly narrowed to none must not fall back to everything
        self.assertEqual(
            self.matched_patients(_payload(allRegions=False, selectedRegions=[])),
            [],
        )

    def test_patient_without_localization_is_excluded(self):
        # patient 5 has recordings but no area_fs_vox rows
        matched = self.matched_patients(_payload(
            allRegions=False, selectedRegions=["Left-Hippocampus", "Right-Amygdala"]))
        self.assertNotIn(5, matched)
        self.assertEqual(matched, [1, 4])

    def test_filter_applies_in_stitched_mode(self):
        self.assertEqual(
            self.matched_patients(
                _payload(mode="stitched", allRegions=False,
                         selectedRegions=["ctx-rh-superiortemporal"]),
                model=StitchedChunks,
            ),
            [2],
        )

    def test_waterfall_runs_the_region_step(self):
        data = _payload(allRegions=False, selectedRegions=["Left-Amygdala"])
        qb = QueryBuilder(data)
        qb._region_query()
        expected = str(qb.filter)

        qb2 = QueryBuilder(data)
        qb2._patient_query = lambda: qb2.filter
        qb2._task_query_dl = lambda: qb2.filter
        qb2._stay_day_query_dl = lambda: qb2.filter
        qb2._weektime_query_dl = lambda: qb2.filter
        qb2._timerange_query_dl = lambda: qb2.filter
        qb2.waterfall_query()
        self.assertIn(expected, str(qb2.filter))

    def test_missing_localization_table_does_not_break_the_query(self):
        _sql("ALTER TABLE area_fs_vox RENAME TO area_fs_vox_hidden")
        try:
            # every patient comes back rather than the query failing outright
            self.assertEqual(
                self.matched_patients(_payload(
                    allRegions=False, selectedRegions=["Left-Amygdala"])),
                PATIENTS_WITH_RECORDINGS,
            )
        finally:
            _sql("ALTER TABLE area_fs_vox_hidden RENAME TO area_fs_vox")


if __name__ == "__main__":
    unittest.main()
