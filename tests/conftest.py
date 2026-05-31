import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def make_minimal_config(min_q=20, max_q=25):
    return {
        "llm_profiles": [
            {
                "name": "test",
                "vendor": "openai",
                "model": "gpt-test",
                "api_key": "sk-test",
                "base_url": "https://test.example.com",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        ],
        "active_profile": "test",
        "phase_profiles": {"init": "test", "assess": "test", "result": "test"},
        "active_preset": "default",
        "prompt_presets": {
            "default": {
                "prompt_init": "test init prompt",
                "prompt_assess": "test assess prompt {previous_scenes} {min_questions} {min_questions_minus_1} {max_questions}",
                "prompt_result": "test result prompt"
            }
        },
        "min_questions": min_q,
        "max_questions": max_q,
        "easter_egg_enabled": True,
        "easter_eggs": {
            "schrodinger": 1,
            "hexagon": 3,
            "buddha": 3,
            "double": 3,
            "mouthpiece": 5
        },
        "prompt_init": "test init prompt",
        "prompt_assess": "test assess prompt {previous_scenes} {min_questions} {min_questions_minus_1} {max_questions}",
        "prompt_result": "test result prompt"
    }
