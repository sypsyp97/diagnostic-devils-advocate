import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.output_parser import parse_json_response


def test_parse_json_response_returns_dict():
    parsed = parse_json_response('{"challenges":[{"claim":"x","counter_evidence":"y"}]}')
    assert parsed["challenges"][0]["claim"] == "x"


def test_parse_json_response_coerces_top_level_list_of_strings():
    parsed = parse_json_response('["CT angiogram","D-dimer"]')
    assert parsed["items"] == ["CT angiogram", "D-dimer"]


def test_parse_json_response_infers_container_key_for_da_items():
    parsed = parse_json_response(
        '[{"diagnosis":"Aortic dissection","why_dangerous":"High mortality","supporting_signs":"Pain radiating to back","rule_out_test":"CTA chest"}]'
    )
    assert parsed["must_not_miss"][0]["diagnosis"] == "Aortic dissection"

