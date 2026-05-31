"""NBTI Flask app factory with all routes registered"""

import os
import uuid
import logging
import requests
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS

from nbti.config import (
    load_config, save_config, find_profile_for_phase, find_profile,
    get_model_for_phase, _migrate_old_config, DEFAULT_CONFIG, CONFIG_FILE
)
from nbti.conversation import store
from nbti.llm import (
    build_thinking_params, build_response_format, get_chat_completions_url,
    stream_generator
)
from nbti.utils import (
    normalize_answer_question, parse_answer_meta, normalize_options,
    expected_next_question, inject_question_control, is_complete_assess,
    commit_answer_to_history, extract_scene_summary
)

logger = logging.getLogger(__name__)

STATIC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app():
    app = Flask(__name__)
    CORS(app)

    # ---- Health check ----
    @app.route('/api/health', methods=['GET'])
    def health():
        config = load_config()
        return jsonify({
            "status": "ok",
            "profiles": len(config.get("llm_profiles", [])),
            "active_preset": config.get("active_preset", ""),
            "version": "2.0.0"
        })

    # ---- Chat endpoints ----
    @app.route('/api/chat', methods=['POST'])
    def chat():
        data = request.json
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', '')
        config = load_config()

        use_stream = request.args.get('stream') == '1'
        logger.info(f"[CHAT] id={conversation_id} | msg={message[:50]}... | stream={use_stream}")

        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            store.save_history(conversation_id, [])

        history = store.get_history(conversation_id)
        expected_q = None

        if message in ['开始测试', '开始'] or not history:
            phase = 'init'
            expected_q = 1
            system_prompt = config['prompt_init']
        elif '[PHASE:RESULT]' in message or '[CAN_CONCLUDE:true]' in message:
            phase = 'result'
            system_prompt = config['prompt_result']
            eggs = config.get('easter_eggs', {})
            for key in ['schrodinger', 'hexagon', 'buddha', 'double', 'mouthpiece']:
                system_prompt = system_prompt.replace('{' + f'easter_{key}' + '}', str(eggs.get(key, 1)))
        else:
            phase = 'assess'
            expected_q = expected_next_question(history)
            system_prompt = config['prompt_assess']
            scenes = store.get_scenes(conversation_id)
            if scenes:
                scenes_text = '\n'.join([f"- {s}" for s in scenes])
                system_prompt = system_prompt.replace('{previous_scenes}', scenes_text)
            else:
                system_prompt = system_prompt.replace('{previous_scenes}', '（暂无，你是第一题）')
            min_q = int(config.get("min_questions", 20))
            max_q = int(config.get("max_questions", 25))
            system_prompt = system_prompt.replace('{min_questions}', str(min_q))
            system_prompt = system_prompt.replace('{min_questions_minus_1}', str(min_q - 1))
            system_prompt = system_prompt.replace('{max_questions}', str(max_q))

        if phase in ['init', 'assess']:
            system_prompt = inject_question_control(system_prompt, expected_q)

        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            if msg.get("role") != "system":
                messages.append(msg)
        messages.append({"role": "user", "content": message})

        profile = find_profile_for_phase(config, phase)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {profile['api_key']}"
        }

        payload = {
            "model": profile['model'],
            "messages": messages,
            "temperature": profile.get('temperature', 0.9),
            "max_tokens": profile.get('max_tokens', 2000)
        }
        if expected_q:
            payload['_expected_q'] = expected_q

        thinking_params = build_thinking_params(profile)
        payload.update(thinking_params)
        rf = build_response_format(profile, phase)
        if rf:
            payload.update(rf)

        logger.info(f"[CHAT] call LLM | phase={phase} | q={expected_q} | profile={profile.get('name')} | model={profile['model']}")

        if use_stream:
            return Response(
                stream_generator(profile, payload, conversation_id, history, message, phase, save_history=True, config=config),
                mimetype='text/event-stream',
                headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
            )
        else:
            try:
                response = requests.post(
                    get_chat_completions_url(profile),
                    headers=headers,
                    json={k: v for k, v in payload.items() if not k.startswith('_')},
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()
                    answer = result['choices'][0]['message']['content']
                    answer = normalize_answer_question(answer, expected_q, config)
                    tokens_used = result.get('usage', {}).get('total_tokens', 0)
                    meta = parse_answer_meta(answer)
                    logger.info(f"[CHAT] OK | Q={meta['q']} | tokens={tokens_used}")
                    commit_answer_to_history(conversation_id, message, answer, phase)
                    return jsonify({"answer": answer, "conversation_id": conversation_id, "tokens_used": tokens_used})
                else:
                    logger.error(f"[CHAT] API error {response.status_code}")
                    return jsonify({"error": f"API error: {response.status_code}", "detail": response.text, "conversation_id": conversation_id}), 500
            except Exception as e:
                logger.error(f"[CHAT] Exception: {e}")
                return jsonify({"error": str(e), "conversation_id": conversation_id}), 500

    @app.route('/api/chat/preload', methods=['POST'])
    def preload():
        data = request.json
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', '')
        config = load_config()

        use_stream = request.args.get('stream') == '1'
        logger.info(f"[PRELOAD] id={conversation_id} | msg={message[:50]}...")

        history = list(store.get_history(conversation_id))
        expected_q = None

        if '[PHASE:RESULT]' in message or '[CAN_CONCLUDE:true]' in message:
            phase = 'result'
            system_prompt = config['prompt_result']
            eggs = config.get('easter_eggs', {})
            for key in ['schrodinger', 'hexagon', 'buddha', 'double', 'mouthpiece']:
                system_prompt = system_prompt.replace('{' + f'easter_{key}' + '}', str(eggs.get(key, 1)))
        else:
            phase = 'assess'
            expected_q = expected_next_question(history)
            system_prompt = config['prompt_assess']
            scenes = store.get_scenes(conversation_id)
            if scenes:
                scenes_text = '\n'.join([f"- {s}" for s in scenes])
                system_prompt = system_prompt.replace('{previous_scenes}', scenes_text)
            else:
                system_prompt = system_prompt.replace('{previous_scenes}', '（暂无，你是第一题）')
            min_q = int(config.get("min_questions", 20))
            max_q = int(config.get("max_questions", 25))
            system_prompt = system_prompt.replace('{min_questions}', str(min_q))
            system_prompt = system_prompt.replace('{min_questions_minus_1}', str(min_q - 1))
            system_prompt = system_prompt.replace('{max_questions}', str(max_q))

        if phase == 'assess':
            system_prompt = inject_question_control(system_prompt, expected_q)

        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            if msg.get("role") != "system":
                messages.append(msg)
        messages.append({"role": "user", "content": message})

        profile = find_profile_for_phase(config, phase)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {profile['api_key']}"
        }

        payload = {
            "model": profile['model'],
            "messages": messages,
            "temperature": profile.get('temperature', 0.9),
            "max_tokens": profile.get('max_tokens', 2000)
        }
        if expected_q:
            payload['_expected_q'] = expected_q

        thinking_params = build_thinking_params(profile)
        payload.update(thinking_params)
        rf = build_response_format(profile, phase)
        if rf:
            payload.update(rf)

        if use_stream:
            return Response(
                stream_generator(profile, payload, conversation_id, config=config),
                mimetype='text/event-stream',
                headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
            )
        else:
            try:
                response = requests.post(
                    get_chat_completions_url(profile),
                    headers=headers,
                    json={k: v for k, v in payload.items() if not k.startswith('_')},
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()
                    answer = result['choices'][0]['message']['content']
                    answer = normalize_answer_question(answer, expected_q, config)
                    tokens_used = result.get('usage', {}).get('total_tokens', 0)
                    meta = parse_answer_meta(answer)
                    logger.info(f"[PRELOAD] OK | Q={meta['q']} | tokens={tokens_used}")
                    if conversation_id and message:
                        if meta.get('phase') == 'ASSESS' and not is_complete_assess(answer, expected_q):
                            logger.warning(f"[PRELOAD] Discard incomplete draft")
                        else:
                            store.save_preload_draft(conversation_id, message, answer, tokens_used)
                    return jsonify({"answer": answer, "tokens_used": tokens_used})
                else:
                    logger.error(f"[PRELOAD] API error {response.status_code}")
                    return jsonify({"error": f"API error: {response.status_code}", "detail": response.text}), 500
            except Exception as e:
                logger.error(f"[PRELOAD] Exception: {e}")
                return jsonify({"error": str(e)}), 500

    @app.route('/api/chat/preload/commit', methods=['POST'])
    def commit_preload():
        data = request.json
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', '')

        if not conversation_id or not message:
            return jsonify({"error": "Missing conversation_id or message"}), 400

        draft = store.get_preload_draft(conversation_id, message)
        if not draft:
            return jsonify({"error": "Preload draft not found or expired", "conversation_id": conversation_id}), 404

        answer = draft.get('answer', '')
        tokens_used = draft.get('tokens_used', 0)
        history = store.get_history(conversation_id)
        meta = parse_answer_meta(answer)
        expected_q = expected_next_question(history)
        if meta.get('phase') == 'ASSESS' and not is_complete_assess(answer, expected_q):
            logger.warning(f"[PRELOAD_COMMIT] Reject incomplete draft | q={expected_q} | Q={meta.get('q')}")
            return jsonify({"error": "Preload draft incomplete or expired", "conversation_id": conversation_id}), 409

        answer_phase = 'result' if meta.get('phase') == 'RESULT' else 'assess'
        commit_answer_to_history(conversation_id, message, answer, answer_phase)
        store.clear_preloads(conversation_id)

        logger.info(f"[PRELOAD_COMMIT] OK | Q={meta['q']} | phase={meta['phase']}")
        return jsonify({"answer": answer, "conversation_id": conversation_id, "tokens_used": tokens_used, "committed": True})

    @app.route('/api/chat/stream', methods=['POST'])
    def chat_stream():
        from werkzeug.datastructures import MultiDict
        request.args = MultiDict([('stream', '1')])
        return chat()

    @app.route('/api/chat/preload/stream', methods=['POST'])
    def preload_stream():
        from werkzeug.datastructures import MultiDict
        request.args = MultiDict([('stream', '1')])
        return preload()

    # ---- Config endpoints ----
    @app.route('/api/config', methods=['GET'])
    def get_config():
        config = load_config()
        return jsonify(config)

    @app.route('/api/config', methods=['POST'])
    def update_config():
        config = request.json
        config = _migrate_old_config(config)
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        save_config(config)
        logger.info(f"[CONFIG] Updated")
        return jsonify({"success": True})

    @app.route('/api/config/test-connection', methods=['POST'])
    def test_connection():
        data = request.json
        if not data:
            return jsonify({"error": "Missing profile data"}), 400

        base_url = data.get('base_url', '')
        api_key = data.get('api_key', '')
        model = data.get('model', '')
        vendor = data.get('vendor', '')

        if not base_url or not api_key:
            return jsonify({"error": "Missing base_url or api_key"}), 400

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 1
        }

        try:
            test_profile = {"base_url": base_url, "vendor": vendor}
            resp = requests.post(
                get_chat_completions_url(test_profile),
                headers=headers, json=payload, timeout=15
            )
            if resp.status_code == 200:
                result = resp.json()
                model_used = result.get('model', model)
                return jsonify({"success": True, "model": model_used, "message": f"Connected! Model: {model_used}"})
            elif resp.status_code in (401, 403):
                return jsonify({"success": False, "error": f"Auth failed ({resp.status_code})"}), 200
            else:
                return jsonify({"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}), 200
        except requests.exceptions.Timeout:
            return jsonify({"success": False, "error": "Timeout (15s)"}), 200
        except requests.exceptions.ConnectionError:
            return jsonify({"success": False, "error": "Cannot connect to server"}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 200

    @app.route('/api/config/reset', methods=['POST'])
    def reset_config():
        save_config(DEFAULT_CONFIG)
        logger.info("[CONFIG] Reset to defaults")
        return jsonify({"success": True})

    # ---- Stats endpoint ----
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        conv_dir = store.base_dir
        total = 0
        if os.path.exists(conv_dir):
            total = len([f for f in os.listdir(conv_dir) if f.endswith('.json')])
        config = load_config()
        return jsonify({
            "total_conversations": total,
            "active_preset": config.get("active_preset", ""),
            "profiles_count": len(config.get("llm_profiles", []))
        })

    return app
