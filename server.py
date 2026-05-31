#!/usr/bin/env python3
"""NBTI Backend API - Entry Point

This module bootstraps the Flask app from the nbti package and provides
backward-compatible imports for existing tests.
"""

import os
import sys
import logging

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nbti.app import create_app
from nbti.config import (
    load_config, save_config, find_profile, find_profile_for_phase,
    get_model_for_phase, _migrate_old_config, DEFAULT_CONFIG, DEFAULT_PROFILES,
    CONFIG_FILE, get_api_key
)
from nbti.conversation import store, ConversationStore
from nbti.llm import (
    build_thinking_params, build_response_format, get_chat_completions_url,
    stream_generator, build_assess_schema, build_result_schema
)
from nbti.utils import (
    normalize_answer_question, normalize_options, parse_json_answer,
    parse_answer_meta, extract_scene_summary, count_questions,
    expected_next_question, inject_question_control, is_complete_assess,
    check_easter_egg, trim_history, next_dimension_for_question,
    commit_answer_to_history
)
from nbti.prompts import get_prompt_presets

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/api_calls.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)

    import socket
    ipv6_addr = None
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.connect(("2001:4860:4860::8888", 80))
        ipv6_addr = s.getsockname()[0]
        s.close()
    except:
        pass

    print("NBTI Backend API v2.0")
    print(f"  API: http://[::1]:8081/api")
    print(f"  Health: http://[::1]:8081/api/health")
    if ipv6_addr:
        print(f"  IPv6: http://[{ipv6_addr}]:8081/api")
    print(f"  Config: http://[::1]:8081/api/config")
    print(f"  Static files: python frontend_server.py 8080")

    app.run(host='127.0.0.1', port=8081, debug=False, threaded=True)
