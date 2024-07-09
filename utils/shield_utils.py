'''Heler functions'''

import requests
import json
import random
import pandas as pd 
import urllib.parse

ARTHUR_SHIELD_URL = None
ARTHUR_SHIELD_API_URL = None
ARTHUR_SHIELD_API_KEY = None


def setup_env(base_url, api_key): 
    global ARTHUR_SHIELD_URL, ARTHUR_SHIELD_API_URL, ARTHUR_SHIELD_API_KEY

    ARTHUR_SHIELD_URL = base_url
    ARTHUR_SHIELD_API_URL = f"{ARTHUR_SHIELD_URL}/api/v2"
    ARTHUR_SHIELD_API_KEY = api_key

    return f"Setup against: {ARTHUR_SHIELD_API_URL}"


def set_up_task_and_rule(rule_config, task_prefix): 
    # 1 - Create Task 
    random_number = random.randint(1, 10000)
    task_name = f"{task_prefix}-{random_number}"
    task = create_task(task_name)

    # 2 - Disable all rules (if there any default)
    for rule in task["rules"]:
        archive_task_rule(task["id"], rule["id"])

    # 3 - Create Rule 
    rule = create_task_rule(task_id=task["id"], rule_config=rule_config)

    # Get updated task 
    return rule, get_task(task["id"])


def validate_task_setup(task, rule_type): 
    if (len(task["rules"]) > 1):
        raise Exception("Cannot have more than one rule enabled for this test.")
    else: 
        if task["rules"][0]["type"] != rule_type:
                raise Exception("Invalid rule type enabled. Must be PromptInjectionRule.")
        else: 
            print(f"Valid task {task}")


def run_shield_evaluation(df, task, rule, verbose=True): 
    task_id = task["id"]

    def shield_eval_prompt(row): 
        shield_result = task_prompt_validation(row.text, 1, task_id)

        if verbose: print("===============\n", row)

        for rule_result in shield_result["rule_results"]:
            if rule_result["id"] == rule["id"]:
                result = rule_result["result"]
                
                if result == "Pass": 
                    result = False
                else:
                    result = True
                return result, shield_result
            
            else: 
                return None, None
    
    df[["shield_result", "shield_result_full_detail"]] = df.apply(shield_eval_prompt, axis=1).apply(pd.Series)

    return df


def create_task(task_name): 
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
            "conversation_id": str(convo_id)
        },
        verify=False
    ) 
    try:
        resp = json.loads(r.text)
        return resp
    except Exception as e:
        print(e)

def create_default_rule(rule_config):
    r = requests.post(
        f'{ARTHUR_SHIELD_API_URL}/default_rules',
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
        err = f"Unable to create default rule with status {r.status_code}:{r.text}"
        raise Exception(err)


def task_response_validation(response, context, inference_id, task_id): 

    r = requests.post(
        f'{ARTHUR_SHIELD_API_URL}/tasks/{task_id}/validate_response/{inference_id}',
        headers ={
            'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
            'Content-type':'application/json' 
        },
        json = {
            "response": response,
            "context": context
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
    
def query_inferences(start, end, task_ids=None, rule_types=None, rule_statuses=None): 

    iso_string_end = end.strftime('%Y-%m-%dT%H:%M:%S.%f')
    iso_string_start = start.strftime('%Y-%m-%dT%H:%M:%S.%f')

    encoded_iso_string_end= urllib.parse.quote(iso_string_end)
    encoded_iso_string_start = urllib.parse.quote(iso_string_start)
    
    url = f'{ARTHUR_SHIELD_API_URL}/inferences/query?start_time={encoded_iso_string_start}&end_time={encoded_iso_string_end}'

    if task_ids:
        for task_id in task_ids: 
            url = url + f"&task_ids={task_id}"

    if rule_types:
        for rule_type in rule_types: 
            url = url + f"&rule_types={rule_type}"

    if rule_statuses:
        for rule_status in rule_statuses: 
            url = url + f"&rule_statuses={rule_status}"

    def query(url, page, page_size):
        url = url + f'&sort=desc&page_size={page_size}&page={page}'
        r = requests.get(
                url,
                headers ={
                    'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
                    'Content-type':'application/json' 
                },
                verify=False
            )
        if r.status_code == 200: 
            resp = json.loads(r.text)
            return resp
        else: 
            raise Exception(r.text)

    all_inferences = []
    page = 0
    page_size = 100
    while True: 
        try:
            result = query(url, page, page_size)
            inferences = result["inferences"]
            if len(inferences) == 0: 
                break
            all_inferences.extend(inferences)
            page+=1
        except Exception as e: 
            print(e)
            break
    return all_inferences


def get_token_usage(start, end, groupby_task=False, groupby_rule_type=False): 

    iso_string_end = end.strftime('%Y-%m-%dT%H:%M:%S.%f')
    iso_string_start = start.strftime('%Y-%m-%dT%H:%M:%S.%f')

    encoded_iso_string_end= urllib.parse.quote(iso_string_end)
    encoded_iso_string_start = urllib.parse.quote(iso_string_start)

    url = f'{ARTHUR_SHIELD_API_URL}/usage/tokens?start_time={encoded_iso_string_start}&end_time={encoded_iso_string_end}'
    
    if groupby_task: 
        url = url + f'&group_by=task'

    if groupby_rule_type: 
        url = url + f'&group_by=rule_type'

    print(url)
    r = requests.get(
            url,
            headers ={
                'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
                'Content-type':'application/json' 
            },
            verify=False
    )
    if r.status_code == 200: 
        resp = json.loads(r.text)
        return resp
    else: 
        raise Exception(r.text)

def search_tasks(page_size=50, all_tasks=False, task_ids=[]): 
    tasks = []

    if all_tasks: 
        page = 0
        while True:
            url = f'{ARTHUR_SHIELD_API_URL}/tasks/search?sort=desc&page_size={page_size}&page={page}'
            r = requests.post(
                    url,
                    headers ={
                        'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
                        'Content-type':'application/json' 
                    },
                    json={},
                    verify=False
                )

            if r.status_code == 200: 
                resp = json.loads(r.text)
                current_page_tasks = resp["tasks"]
            else: 
                err = f"Unable to serach tasks with status {r.status_code}:{r.text}"
                raise Exception(err)
            
            if not current_page_tasks:
                break
            tasks.extend(current_page_tasks)
            page += 1
    else: 
        url = f'{ARTHUR_SHIELD_API_URL}/tasks/search?sort=desc&page_size=250&page=0'
        r = requests.post(
                url,
                headers ={
                    'Authorization':'Bearer %s' % ARTHUR_SHIELD_API_KEY,
                    'Content-type':'application/json' 
                },
                json={
                    "task_ids": task_ids
                },
                verify=False
        )

        if r.status_code == 200: 
            resp = json.loads(r.text)
            current_page_tasks = resp["tasks"]
        else: 
            err = f"Unable to serach tasks with status {r.status_code}:{r.text}"
            raise Exception(err)
        
        tasks.extend(current_page_tasks)
        
    print(f"Fetched {len(tasks)} total tasks.")

    return tasks