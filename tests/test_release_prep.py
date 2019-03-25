from unittest import TestCase

from release_prep import ReleasePreparation


# TODO create more test cases

class ReleasePrepTest(TestCase):
    def setUp(self):
        self.versions = {
            "last_update_date": "2019-02-05T11:03:57Z",
            "version_numbers": {
                "core": {
                    "biomaterial": {
                        "biomaterial_core": "7.0.5"
                    },
                    "file": {
                        "file_core": "5.2.5"
                    },
                    "process": {
                        "process_core": "9.0.3"
                    },
                    "project": {
                        "project_core": "7.0.5"
                    },
                    "protocol": {
                        "protocol_core": "5.2.5"
                    }
                },
                "module": {
                    "biomaterial": {
                        "cell_morphology": "6.1.6",
                        "death": "5.4.1",
                        "familial_relationship": "6.0.3",
                        "growth_conditions": "6.4.2",
                        "human_specific": "1.0.9",
                        "medical_history": "5.2.5",
                        "mouse_specific": "1.0.7",
                        "preservation_storage": "6.0.1",
                        "state_of_specimen": "5.2.7",
                        "timecourse": "2.0.1"
                    },
                    "ontology": {
                        "biological_macromolecule_ontology": "5.3.4",
                        "cell_cycle_ontology": "5.3.5",
                        "cell_type_ontology": "5.3.5",
                        "cellular_component_ontology": "1.0.4",
                        "development_stage_ontology": "5.3.5",
                        "disease_ontology": "5.3.7",
                        "enrichment_ontology": "1.2.5",
                        "ethnicity_ontology": "5.3.7",
                        "instrument_ontology": "5.3.5",
                        "length_unit_ontology": "5.3.4",
                        "library_amplification_ontology": "1.2.4",
                        "library_construction_ontology": "1.2.4",
                        "mass_unit_ontology": "5.3.4",
                        "microscopy_ontology": "1.0.4",
                        "organ_ontology": "5.3.7",
                        "organ_part_ontology": "5.3.4",
                        "process_type_ontology": "5.3.4",
                        "protocol_type_ontology": "5.3.4",
                        "sequencing_ontology": "1.1.4",
                        "species_ontology": "5.3.4",
                        "strain_ontology": "5.3.5",
                        "time_unit_ontology": "5.3.4"
                    },
                    "process": {
                        "purchased_reagents": "6.0.4",
                        "sequencing": {
                            "10x": "1.0.5",
                            "barcode": "5.2.6",
                            "insdc_experiment": "1.1.5",
                            "plate_based_sequencing": "1.0.6"
                        }
                    },
                    "project": {
                        "contact": "6.1.4",
                        "funder": "2.0.0",
                        "publication": "5.2.5"
                    },
                    "protocol": {
                        "channel": "2.0.1",
                        "target": "1.0.6"
                    }
                },
                "system": {
                    "license": "1.0.0",
                    "links": "1.1.5",
                    "provenance": "1.0.3"
                },
                "type": {
                    "biomaterial": {
                        "cell_line": "10.0.4",
                        "cell_suspension": "9.0.0",
                        "donor_organism": "14.0.3",
                        "imaged_specimen": "2.0.7",
                        "organoid": "10.0.2",
                        "specimen_from_organism": "7.0.3"
                    },
                    "file": {
                        "analysis_file": "5.3.6",
                        "image_file": "1.0.3",
                        "reference_file": "2.2.10",
                        "sequence_file": "7.0.2",
                        "supplementary_file": "1.1.8"
                    },
                    "process": {
                        "analysis": {
                            "analysis_process": "8.0.8"
                        },
                        "process": "6.0.7"
                    },
                    "project": {
                        "project": "11.0.0"
                    },
                    "protocol": {
                        "analysis": {
                            "analysis_protocol": "8.0.7"
                        },
                        "biomaterial_collection": {
                            "aggregate_generation_protocol": "2.0.0",
                            "collection_protocol": "8.2.11",
                            "differentiation_protocol": "1.3.3",
                            "dissociation_protocol": "5.0.8",
                            "enrichment_protocol": "2.2.9",
                            "ipsc_induction_protocol": "2.0.4"
                        },
                        "imaging": {
                            "imaging_preparation_protocol": "2.0.1",
                            "imaging_protocol": "11.0.9"
                        },
                        "protocol": "6.3.9",
                        "sequencing": {
                            "library_preparation_protocol": "4.4.6",
                            "sequencing_protocol": "9.0.11"
                        }
                    }
                }
            }
        }

    def test_expand_urls(self):
        base_path = 'json_schema_path'
        schema_path = 'json_schema_path/core/biomaterial/biomaterial_core.json'

        context = 'develop'
        release_prep = ReleasePreparation(context, self.versions)
        relative_schema_path = schema_path.replace(base_path + "/", "")
        relative_schema_path = relative_schema_path.replace(".json", "")

        schema_json = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "description": "Information about any biological material that was generated/used in the project including everything from a whole organism to subcellular components.",
            "additionalProperties": False,
            "required": ["biomaterial_id"],
            "title": "Biomaterial core",
            "name": "biomaterial_core",
            "type": "object",
            "properties": {
                "describedBy": {
                    "description": "The URL reference to the schema.",
                    "type": "string",
                    "pattern": "^(http|https)://schema.(.*?)humancellatlas.org/core/biomaterial/(([0-9]{1,}.[0-9]{1,}.[0-9]{1,})|([a-zA-Z]*?))/biomaterial_core"
                },
                "schema_version": {
                    "description": "The version number of the schema in major.minor.patch format.",
                    "type": "string",
                    "pattern": "^[0-9]{1,}.[0-9]{1,}.[0-9]{1,}$",
                    "example": "4.6.1"
                },
                "biomaterial_id": {
                    "description": "A unique ID for the biomaterial.",
                    "type": "string",
                    "user_friendly": "Biomaterial ID"
                }
            }
        }

        expanded_file_data = release_prep.expand_urls(relative_schema_path,
                                                      schema_json)

        expected = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "https://schema.dev.data.humancellatlas.org/core/biomaterial/7.0.5/biomaterial_core",
            "description": "Information about any biological material that was generated/used in the project including everything from a whole organism to subcellular components.",
            "additionalProperties": False,
            "required": ["biomaterial_id"],
            "title": "Biomaterial core",
            "name": "biomaterial_core",
            "type": "object",
            "properties": {
                "describedBy": {
                    "description": "The URL reference to the schema.",
                    "type": "string",
                    "pattern": "^(http|https)://schema.(.*?)humancellatlas.org/core/biomaterial/(([0-9]{1,}.[0-9]{1,}.[0-9]{1,})|([a-zA-Z]*?))/biomaterial_core"
                },
                "schema_version": {
                    "description": "The version number of the schema in major.minor.patch format.",
                    "type": "string",
                    "pattern": "^[0-9]{1,}.[0-9]{1,}.[0-9]{1,}$",
                    "example": "4.6.1"
                },
                "biomaterial_id": {
                    "description": "A unique ID for the biomaterial.",
                    "type": "string",
                    "user_friendly": "Biomaterial ID"
                }
            }
        }
        self.assertEqual(expanded_file_data, expected)
