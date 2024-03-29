'''Heler functions'''

import requests
import json

ARTHUR_SHIELD_URL = None
ARTHUR_SHIELD_API_URL = None
ARTHUR_SHIELD_API_KEY = None


def setup_env(base_url, api_key): 
    global ARTHUR_SHIELD_URL, ARTHUR_SHIELD_API_URL, ARTHUR_SHIELD_API_KEY

    ARTHUR_SHIELD_URL = base_url
    ARTHUR_SHIELD_API_URL = f"{ARTHUR_SHIELD_URL}/api/v2"
    ARTHUR_SHIELD_API_KEY = api_key

    return f"Setup against: {ARTHUR_SHIELD_API_URL}"

def create_task(task_name): 
    print(ARTHUR_SHIELD_API_URL)
    r = requests.post(
        f'{ARTHUR_SHIELD_API_URL}/task',
        headers ={
            'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
            'Content-type':'application/json' 
        },
        json = {"name":task_name},
        verify=False
    )

    if r.status_code == 200: 
        return json.loads(r.text)
    else: 
        err = f"Unable to create task with status {r.status_code}:{r.text}"
        raise Exception(err)


def get_task(task_id): 
    r = requests.get(
        f'{ARTHUR_SHIELD_API_URL}/tasks/{task_id}',
        headers ={
            'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
            'Content-type':'application/json' 
        },
        verify=False
    )

    resp = json.loads(r.text)
    return resp


def create_task_rule(task_id, rule_config):
    r = requests.post(
        f'{ARTHUR_SHIELD_API_URL}/tasks/{task_id}/rules',
        headers ={
            'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
            'Content-type':'application/json' 
        },
        json = rule_config,
        verify=False
    )

    if r.status_code == 200: 
        return json.loads(r.text)
    else: 
        err = f"Unable to create task rule with status {r.status_code}:{r.text}"
        raise Exception(err)


def archive_task_rule(task_id, rule_id): 
    print(task_id, rule_id)
    r = requests.delete(
        f'{ARTHUR_SHIELD_API_URL}/tasks/{task_id}/rules/{rule_id}',
        headers ={
            'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
            'Content-type':'application/json' 
        },
        verify=False
    )

    if r.status_code == 204: 
        return r.text
    else: 
        err = f"Unable to archive task rule with status {r.status_code}:{r.text}"
        raise Exception(err)


def archive_task(task_id): 
    r = requests.delete(
        f'{ARTHUR_SHIELD_API_URL}/tasks/{task_id}',
        headers ={
            'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
            'Content-type':'application/json' 
        },
        verify=False
    )

    if r.status_code == 200: 
        return json.loads(r.text)
    else: 
        err = f"Unable to archive task with status {r.status_code}:{r.text}"
        raise Exception(err)


def get_default_rules(): 
    r = requests.post(
        f'{ARTHUR_SHIELD_API_URL}/rules/search?sort=desc&page_size=250&page=0',
        headers ={
            'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
            'Content-type':'application/json' 
        },
        json= {
            "rule_scopes": ["default"]
        },
        verify=False
    )

    if r.status_code == 200: 
        return json.loads(r.text)
    else: 
        err = f"Unable to archive task with status {r.status_code}:{r.text}"
        raise Exception(err)


def load_rules_config_file(path): 
    with open(path, 'r') as f:
        dataset = json.load(f)
    return dataset


def task_prompt_validation(prompt, convo_id, task_id): 
    r = requests.post(
        f'{ARTHUR_SHIELD_API_URL}/tasks/{task_id}/validate_prompt',
        headers ={
            'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
            'Content-type':'application/json' 
        },
        json = {
            "prompt": prompt,
            "conversation_id": convo_id
        },
        verify=False
    ) 

    resp = json.loads(r.text)
    return resp


def update_task_rule(task_id, rule_id, enable):
    if enable:
        body = {"enabled": True}
    else:
        body = {"enabled": False}

    r = requests.patch(
        f'{ARTHUR_SHIELD_API_URL}/tasks/{task_id}/rules/{rule_id}',
        headers ={
            'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
            'Content-type':'application/json'
        },
        verify=False,
        json=body
    )

    if r.status_code == 200:
        return "Success"
    else:
        err = f"Unable to archive task rule with status {r.status_code}:{r.text}"
        raise Exception(err)