import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

config = requests.get('http://localhost:8081/api/config', timeout=5).json()
ds = [p for p in config['llm_profiles'] if p['name'] == 'deepseek-v4-flash'][0]

url = ds['base_url'].rstrip('/') + '/chat/completions'
headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + ds['api_key']}

payload = {
    'model': ds['model'],
    'messages': [
        {'role': 'system', 'content': 'Reply in JSON format: {"test": "ok"}'},
        {'role': 'user', 'content': 'Go'}
    ],
    'max_tokens': ds['max_tokens'],
    'temperature': ds['temperature']
}

print(f'URL: {url}')
print(f'Model: {ds["model"]}')
print(f'json_mode: {ds.get("json_mode")}')

resp = requests.post(url, headers=headers, json=payload, timeout=30)
print(f'Status: {resp.status_code}')
data = resp.json()
content = data['choices'][0]['message']['content']
print(f'Content: {repr(content[:200])}')
print(f'Tokens: {data.get("usage", {}).get("total_tokens", 0)}')
