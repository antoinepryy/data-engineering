# Plan: Enhanced Training DAGs for Module 2 (Airflow)

## Executive Summary

This plan proposes improving Module 2's training DAGs to better demonstrate real-world ETL patterns based on the POI (Points of Interest) ETL documentation. The goal is to create demo DAGs that teach tag mapping, deduplication, and aggregation concepts without requiring real API connections.

---

## Current State Analysis

### Existing DAGs

1. **01_demo_basic_dag.py** (300 lines)
   - Basic ETL pipeline: extract -> transform -> validate -> load
   - Demonstrates: XCom, PythonOperator, BashOperator, DummyOperator
   - Uses generic data (random record counts)
   - Good foundation but lacks domain-specific context

2. **02_demo_advanced_patterns.py** (427 lines)
   - Branching, TaskGroups, dynamic task simulation
   - Quality-based branching (high/medium/low)
   - Generic source processing (API, DATABASE, FILE)
   - Good patterns but not related to POI domain

### Key Gaps Identified

| Gap | Current State | Target State |
|-----|--------------|--------------|
| Domain context | Generic data | POI-like structures |
| Tag mapping | Not covered | Full demonstration |
| Deduplication | Not covered | Multi-strategy approach |
| Aggregation rules | Simple merge | 20+ rule types |
| Multi-source ETL | Simulated generically | Named sources (Apidae, Datatourisme, etc.) |
| Sourcing levels | Not covered | Priority-based processing |
| Educational content | Basic docstrings | Exercises + solutions |

---

## Proposed DAG Architecture

### New DAG Structure

```
dags/
├── 01_demo_basic_dag.py           # Keep (minor enhancements)
├── 02_demo_advanced_patterns.py   # Keep (minor enhancements)
├── 03_demo_poi_extraction.py      # NEW: Multi-source POI extraction
├── 04_demo_tag_mapping.py         # NEW: Tag equivalence system
├── 05_demo_deduplication.py       # NEW: Redundancy detection
├── 06_demo_aggregation.py         # NEW: Complex aggregation rules
├── utils/
│   ├── __init__.py
│   ├── poi_data_generator.py      # NEW: POI mock data generator
│   ├── tag_mapping_config.py      # NEW: Tag equivalence rules
│   └── aggregation_rules.py       # NEW: Aggregation rule definitions
└── data/
    ├── sample_poi_apidae.json     # NEW: Sample source data
    ├── sample_poi_datatourisme.json
    ├── sample_poi_tourinsoft.json
    └── tag_equivalences.csv       # NEW: Tag mapping reference
```

---

## Detailed DAG Specifications

### DAG 3: POI Multi-Source Extraction (`03_demo_poi_extraction.py`)

**Purpose:** Demonstrate extracting and normalizing data from multiple heterogeneous sources.

**Learning Objectives:**
- Multi-source extraction patterns
- Source-specific normalization
- TaskGroups for organizing parallel extractions
- POI data structure understanding

**Architecture:**
```
start
  |
  ├── [TaskGroup: extraction]
  │     ├── extract_apidae
  │     ├── extract_datatourisme
  │     ├── extract_tourinsoft
  │     └── extract_tripadvisor
  |
  ├── [TaskGroup: normalization]
  │     ├── normalize_apidae
  │     ├── normalize_datatourisme
  │     ├── normalize_tourinsoft
  │     └── normalize_tripadvisor
  |
  └── merge_sources -> validate_schema -> end
```

**Key Features:**
- Simulated API responses with realistic POI structures
- Source-specific field mappings (each source has different schemas)
- Schema validation against the target POI model
- XCom for passing data between tasks

**POI Data Structure (from documentation):**
```python
POI_SCHEMA = {
    "id": int,
    "closed": bool,
    "display": bool,
    "tags": List[str],
    "types": List[str],
    "age_limit": {"min_age": int, "max_age": int},
    "duration": {"average_duration": int, "min_duration": int, "max_duration": int},
    "group_size_limit": {"min_group_size": int, "max_group_size": int, "max_wheelchairs": int},
    "poi_name": {"fr": str, "en": str, ...},
    "addresses": List[AddressObject],
    "contacts": List[ContactObject],
    "descriptions": List[DescriptionObject],
    "geopoints": List[GeopointObject],
    "pictures": List[PictureObject],
    "products": List[ProductObject],
    "schedules": List[ScheduleObject],
    "sources": List[SourceObject],
    "ratings": RatingsObject
}
```

**Exercise Ideas:**
- Add a 5th source (e.g., Google Places)
- Implement retry logic for failed extractions
- Add data quality metrics per source

---

### DAG 4: Tag Mapping System (`04_demo_tag_mapping.py`)

**Purpose:** Demonstrate the tag equivalence system that translates source-specific tags into a unified nomenclature.

**Learning Objectives:**
- Understanding tag normalization
- Lookup table patterns
- Handling unmapped tags
- Branching based on mapping success

**Architecture:**
```
start
  |
  ├── load_tag_equivalences (from CSV)
  |
  ├── extract_source_tags
  |
  ├── [TaskGroup: mapping_pipeline]
  │     ├── identify_source_columns
  │     ├── add_source_name_column
  │     ├── rename_to_source_tag
  │     ├── concatenate_tag_datasets
  │     └── apply_equivalence_lookup
  |
  ├── check_unmapped_tags (BranchOperator)
  │     ├── all_mapped -> finalize_tags
  │     └── has_unmapped -> alert_unmapped -> manual_review -> finalize_tags
  |
  └── finalize_tags -> end
```

**Tag Equivalence Example (from documentation):**
```python
TAG_EQUIVALENCES = {
    ("Anglais", "langues_parlees"): "spoken_languages_en",
    ("Anglais", "langues_documentation"): "document_languages_en",
    ("Français", "langues_parlees"): "spoken_languages_fr",
    ("Piscine", "equipements"): "equipment_pool",
    ("Spa", "services"): "activities_aquatic_wellness_spa",
    # ... 200+ mappings
}
```

**Exercise Ideas:**
- Add a new source language mapping
- Implement fuzzy matching for typos
- Create a report of unmapped tags frequency

---

### DAG 5: Deduplication Pipeline (`05_demo_deduplication.py`)

**Purpose:** Demonstrate the multi-stage redundancy detection process.

**Learning Objectives:**
- Database lookup patterns
- Reference matching across sources
- Similarity measures (name, distance, address)
- Sourcing levels concept

**Architecture:**
```
start
  |
  ├── load_existing_database_refs
  |
  ├── [TaskGroup: db_matching]
  │     ├── match_by_source_reference
  │     ├── assign_sourcing_levels
  │     └── filter_high_sourcing (level > 1 = skip update)
  |
  ├── [TaskGroup: reference_matching]
  │     ├── identify_common_references
  │     └── link_by_shared_reference
  |
  ├── [TaskGroup: similarity_matching]
  │     ├── filter_poi_with_location
  │     ├── cartesian_by_department
  │     ├── name_similarity_filter
  │     ├── distance_calculation
  │     ├── check_distance_threshold
  │     │     ├── distance_lt_200m -> mark_duplicate
  │     │     ├── distance_lt_1km -> address_similarity_check
  │     │     └── distance_gt_1km -> mark_unique
  │     └── address_similarity_check -> mark_duplicate_or_unique
  |
  └── merge_dedup_results -> end
```

**Sourcing Levels (from documentation):**
```python
SOURCING_LEVELS = {
    3: "POI owner verified and customized - NEVER update from ETL",
    2: "External actor reported - DO NOT update from ETL",
    1: "Standard ETL data - Can be updated"
}
```

**Similarity Thresholds:**
- Name similarity: > 0.8 (Levenshtein ratio)
- Distance: < 200m = definite match, 200m-1km = needs address check
- Address similarity: > 0.7 for same zip code

**Exercise Ideas:**
- Tune similarity thresholds and observe impact
- Add phone number matching as additional signal
- Implement weighted scoring for multiple signals

---

### DAG 6: Aggregation Rules Engine (`06_demo_aggregation.py`)

**Purpose:** Demonstrate the 20+ different aggregation rules for merging POI attributes.

**Learning Objectives:**
- Complex aggregation patterns
- Rule-based data processing
- Handling conflicts between sources
- Building production-ready aggregation logic

**Architecture:**
```
start
  |
  ├── load_duplicates_groups
  |
  ├── [TaskGroup: simple_aggregations]
  │     ├── aggregate_closed (max value)
  │     ├── aggregate_display (min value)
  │     ├── aggregate_tags (union)
  │     └── aggregate_types (union)
  |
  ├── [TaskGroup: complex_object_aggregations]
  │     ├── aggregate_age_limit (min/max)
  │     ├── aggregate_duration (average)
  │     ├── aggregate_group_size (min/max)
  │     ├── aggregate_poi_name (first non-null per language)
  │     └── aggregate_ratings (union + sum)
  |
  ├── [TaskGroup: list_object_aggregations]
  │     ├── aggregate_addresses (complex merge by key)
  │     ├── aggregate_contacts (merge by name key)
  │     ├── aggregate_descriptions (merge by type key)
  │     ├── aggregate_geopoints (union)
  │     ├── aggregate_pictures (merge by url key)
  │     ├── aggregate_products (merge by name+currency key)
  │     ├── aggregate_schedules (complex - most complex!)
  │     └── aggregate_sources (union)
  |
  └── build_final_poi -> validate_output -> end
```

**Aggregation Rules Reference (from documentation):**

| Attribute | Rule | Example |
|-----------|------|---------|
| `closed` | MAX | [false, true] -> true |
| `display` | MIN | [true, false] -> false |
| `tags` | UNION | [["a"], ["b"]] -> ["a", "b"] |
| `age_limit.min_age` | MIN | [4, 18] -> 4 |
| `age_limit.max_age` | MAX | [50, 99] -> 99 |
| `duration.*` | AVERAGE | [120, 150] -> 135 |
| `poi_name.{lang}` | FIRST_NON_NULL | [null, "Name"] -> "Name" |
| `addresses.street_addresses` | UNION | Merge lists |
| `contacts` | MERGE_BY_KEY(first_name, last_name) | Complex merge |
| `pictures` | MERGE_BY_KEY(url) | Complex merge |
| `validity_period` | MIN start / MAX end | Date range expansion |

**Exercise Ideas:**
- Implement a custom aggregation rule
- Add conflict resolution logging
- Create aggregation statistics report

---

## Support Files Specifications

### `utils/poi_data_generator.py`

Generates realistic mock POI data for all four sources:

```python
class POIDataGenerator:
    """
    Generates mock POI data matching real source schemas.
    
    EDUCATIONAL NOTE:
    In production, each source has a unique schema. This generator
    simulates the heterogeneity learners will face in real ETL work.
    """
    
    SOURCES = ["apidae", "datatourisme", "tourinsoft", "tripadvisor"]
    
    def generate_apidae_poi(self) -> dict:
        """Apidae uses French field names and nested structures."""
        ...
    
    def generate_datatourisme_poi(self) -> dict:
        """Datatourisme follows a JSON-LD schema."""
        ...
    
    def generate_poi_with_duplicates(self, count: int) -> List[dict]:
        """Generates POIs with known duplicates for testing."""
        ...
```

### `utils/tag_mapping_config.py`

Contains the tag equivalence rules:

```python
# Tag equivalence mapping
# Format: (source_tag, source_column) -> internal_tag

TAG_EQUIVALENCES = {
    # Languages
    ("Anglais", "langues_parlees"): "spoken_languages_en",
    ("English", "languages"): "spoken_languages_en",
    ("Anglais", "langues_documentation"): "document_languages_en",
    
    # Activities
    ("Spa", "services"): "activities_aquatic_wellness_spa",
    ("Wellness", "amenities"): "activities_aquatic_wellness_spa",
    
    # Sites
    ("Château", "type_lieu"): "sites_monument_castle",
    ("Castle", "place_type"): "sites_monument_castle",
    
    # ... 200+ mappings for training
}

# Unmapped tag handling
UNMAPPED_TAG_STRATEGIES = {
    "ignore": "Skip unmapped tags (not recommended)",
    "alert": "Log warning and continue",
    "fail": "Raise error (strict mode)",
    "queue": "Add to manual review queue"
}
```

### `utils/aggregation_rules.py`

Defines all aggregation rules as configurable functions:

```python
from typing import Any, List, Callable
from enum import Enum

class AggregationStrategy(Enum):
    MIN = "min"
    MAX = "max"
    AVERAGE = "average"
    FIRST_NON_NULL = "first_non_null"
    UNION = "union"
    MERGE_BY_KEY = "merge_by_key"
    CUSTOM = "custom"

# Rule definitions
AGGREGATION_RULES = {
    "closed": {"strategy": AggregationStrategy.MAX},
    "display": {"strategy": AggregationStrategy.MIN},
    "tags": {"strategy": AggregationStrategy.UNION},
    "types": {"strategy": AggregationStrategy.UNION},
    "age_limit": {
        "min_age": {"strategy": AggregationStrategy.MIN},
        "max_age": {"strategy": AggregationStrategy.MAX}
    },
    "duration": {
        "average_duration": {"strategy": AggregationStrategy.AVERAGE},
        "min_duration": {"strategy": AggregationStrategy.AVERAGE},
        "max_duration": {"strategy": AggregationStrategy.AVERAGE}
    },
    "poi_name": {"strategy": AggregationStrategy.FIRST_NON_NULL},
    "contacts": {
        "strategy": AggregationStrategy.MERGE_BY_KEY,
        "key_fields": ["first_name", "last_name"],
        "union_fields": ["roles", "phones", "emails", "websites"]
    },
    # ... all 20+ rules
}

def apply_aggregation(values: List[Any], rule: dict) -> Any:
    """Apply aggregation rule to a list of values."""
    ...
```

### `data/sample_poi_*.json`

Sample POI data files for each source with realistic examples:

```json
// sample_poi_apidae.json
{
  "pois": [
    {
      "identifiant": "123456",
      "nom": {"libelleFr": "Château de Chambord"},
      "localisation": {
        "adresse": {"codePostal": "41250", "commune": "Chambord"}
      },
      "informations": {
        "languesParlees": ["Français", "Anglais", "Allemand"]
      }
    }
  ]
}
```

### `data/tag_equivalences.csv`

CSV file for tag mapping lookup:

```csv
source_tag,source_column,source,internal_tag
Anglais,langues_parlees,apidae,spoken_languages_en
English,languages,datatourisme,spoken_languages_en
Français,langues_parlees,apidae,spoken_languages_fr
Spa,services,apidae,activities_aquatic_wellness_spa
Wellness,amenities,tripadvisor,activities_aquatic_wellness_spa
```

---

## Educational Enhancements

### Inline Documentation

Each DAG will include extensive educational comments:

```python
# ============================================================================
# EDUCATIONAL SECTION: Understanding Tag Equivalence
# ============================================================================
#
# WHY TAG MAPPING?
# ----------------
# Different data sources use different vocabularies:
# - Apidae (French): "langues_parlees" = "Anglais"
# - Datatourisme (English): "languages" = "English"
# - TripAdvisor (Mixed): "spoken_language" = "en"
#
# All must map to our internal tag: "spoken_languages_en"
#
# THE CHALLENGE:
# - 4 sources x 50+ tag categories = 200+ mappings
# - New tags appear regularly
# - Typos and variations must be handled
#
# LEARNING EXERCISE:
# Try adding a new mapping for "Italien" -> "spoken_languages_it"
# See the tag_mapping_config.py file for the mapping dictionary.
# ============================================================================
```

### Exercise Files

Create `/formation-data-engineering/module-2-airflow/exercises/` with:

```
exercises/
├── README.md                    # Exercise overview
├── ex01_add_new_source/
│   ├── instructions.md
│   ├── starter_code.py
│   └── solution.py
├── ex02_custom_tag_mapping/
│   ├── instructions.md
│   ├── starter_code.py
│   └── solution.py
├── ex03_dedup_tuning/
│   ├── instructions.md
│   ├── test_data.json
│   └── solution.py
└── ex04_aggregation_rule/
    ├── instructions.md
    ├── starter_code.py
    └── solution.py
```

---

## Implementation Timeline (1 Week)

### Day 1-2: Foundation
- [ ] Create `utils/poi_data_generator.py`
- [ ] Create sample data files (`data/sample_poi_*.json`)
- [ ] Create `utils/tag_mapping_config.py`
- [ ] Create `data/tag_equivalences.csv`

### Day 3: DAG 3 - POI Extraction
- [ ] Implement `03_demo_poi_extraction.py`
- [ ] Add inline documentation
- [ ] Test with generated data

### Day 4: DAG 4 - Tag Mapping
- [ ] Implement `04_demo_tag_mapping.py`
- [ ] Add branching for unmapped tags
- [ ] Add inline documentation

### Day 5: DAG 5 - Deduplication
- [ ] Implement `05_demo_deduplication.py`
- [ ] Add similarity calculations
- [ ] Add sourcing level logic

### Day 6: DAG 6 - Aggregation
- [ ] Create `utils/aggregation_rules.py`
- [ ] Implement `06_demo_aggregation.py`
- [ ] Add all 20+ aggregation rules

### Day 7: Polish and Exercises
- [ ] Enhance existing DAGs (01, 02) with POI context
- [ ] Create exercise files
- [ ] Update module README
- [ ] Final testing

---

## Critical Files for Implementation

1. **`/Users/antoine/IdeaProjects/imagesimages/Documentation _ Processus ETL.md`**
   - Primary reference for POI structure and all aggregation rules
   - Contains the complete data schema to replicate

2. **`/Users/antoine/IdeaProjects/imagesimages/formation-data-engineering/module-2-airflow/dags/01_demo_basic_dag.py`**
   - Reference for coding style and Airflow patterns
   - Template for XCom usage and documentation

3. **`/Users/antoine/IdeaProjects/imagesimages/formation-data-engineering/module-2-airflow/dags/02_demo_advanced_patterns.py`**
   - Reference for TaskGroups and branching
   - Pattern to follow for complex DAG structure

4. **`/Users/antoine/IdeaProjects/imagesimages/formation-data-engineering/module-2-airflow/Dockerfile`**
   - May need pandas for similarity calculations (already included)
   - Check if additional packages needed (rapidfuzz for fuzzy matching)

5. **`/Users/antoine/IdeaProjects/imagesimages/formation-data-engineering/README.md`**
   - Overall project context
   - Exercise structure to follow

---

## Dependencies to Add (Dockerfile)

```dockerfile
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    psycopg2-binary \
    apache-airflow-providers-postgres \
    apache-airflow-providers-http \
    rapidfuzz \        # NEW: For fuzzy string matching
    geopy              # NEW: For distance calculations
```

---

## Success Criteria

1. **All 4 new DAGs run successfully** in the Docker environment
2. **Each DAG demonstrates at least 3 concepts** from the ETL documentation
3. **Inline documentation** explains the "why" not just the "how"
4. **Exercise files** allow learners to practice independently
5. **Sample data** is realistic and matches real-world complexity
6. **No real API connections** required - all data is simulated

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Complexity overwhelming learners | Progressive complexity: DAG 3 simple, DAG 6 complex |
| Sample data not realistic | Base on actual ETL documentation examples |
| Performance issues with cartesian joins | Use small datasets (10-50 POIs) for demo |
| Similarity calculations too slow | Pre-filter by department/zip code first |

---

## Next Steps After Implementation

1. Create corresponding slides for Module 2 training
2. Record video walkthrough of each DAG
3. Add automated tests for DAG validation
4. Consider integration with Module 3 (dbt) for downstream modeling
