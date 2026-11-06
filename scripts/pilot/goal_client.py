"""Single native app-server session; no host-generated continuation turns."""
import argparse
import datetime as dt
import json
import queue
import subprocess
import threading
import time
from pathlib import Path


def emit(event):
    print(json.dumps(event, ensure_ascii=False), flush=True)


def goal_objective(platform):
    proof = 'Submission.lean' if platform == 'lean' else 'Submission.v'
    task = 'Task.lean' if platform == 'lean' else 'Task.v'
    return (f'Produce /work/claim.json and /work/{proof} proving exactly '
            f'the equivalence or literal counterexample target defined in /task/{task}. '
            'Keep implementations, domains and observations fixed. Compile the final '
            'complete solve theorem using the supplied platform interface. '
            'No admitted proofs, placeholders or candidate-defined axioms. '
            'The external evaluator independently grades the final submission.')


def main(mode, prompt_file, platform):
    prompt = Path(prompt_file).read_text()
    process = subprocess.Popen(['/opt/codex', 'app-server', '--stdio'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               text=True, bufsize=1)
    messages = queue.Queue()

    def read():
        for line in process.stdout:
            try:
                messages.put(json.loads(line))
            except json.JSONDecodeError:
                emit({'type':'protocol.invalid','line':line})
        messages.put(None)

    threading.Thread(target=read, daemon=True).start()
    sequence = 0
    thread = None; turn_count = 0; goal = None; active = False
    last_turn_end = None; pending = {}; summary = None; next_goal_poll = 0

    def send(method, params, expect=True):
        nonlocal sequence
        sequence += 1
        message = {'method':method,'params':params}
        if expect:
            message['id'] = sequence; pending[sequence] = method
        emit({'type':'rpc.event','direction':'send','message':message})
        process.stdin.write(json.dumps(message)+'\n'); process.stdin.flush()
        return sequence

    def receive(timeout=1):
        try:
            message = messages.get(timeout=timeout)
        except queue.Empty:
            return False
        if message is None:
            raise RuntimeError('App server exited unexpectedly')
        emit({'type':'rpc.event','direction':'receive',
              'received_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'message':message})
        return message

    def request(method, params):
        identifier = send(method, params)
        deadline = time.monotonic()+90
        while time.monotonic()<deadline:
            message = receive()
            if message is False:
                continue
            handle(message)
            if message.get('id') == identifier and 'method' not in message:
                if 'error' in message:
                    raise RuntimeError(method+': '+json.dumps(message['error']))
                return message['result']
        raise TimeoutError('No response to '+method)

    def handle(message):
        nonlocal goal, active, turn_count, last_turn_end
        method = message.get('method'); params = message.get('params') or {}
        if 'id' in message and method:
            # A never-approval evaluation must not silently grant new privileges.
            raise RuntimeError('Unexpected server request: '+method)
        if thread and params.get('threadId') not in (None,thread):
            return
        if method == 'thread/goal/updated':
            goal = params.get('goal')
        elif method == 'turn/started':
            turn_count += 1; active = True; last_turn_end = None
        elif method == 'turn/completed':
            active = False; last_turn_end = time.monotonic()
            emit({'type':'native.turn.completed','turn':params.get('turn'),
                  'native_turn_count':turn_count})
        elif method == 'thread/tokenUsage/updated':
            total = params['tokenUsage']['total']
            emit({'type':'native.usage','usage':{
                'input_tokens':total['inputTokens'],
                'cached_input_tokens':total['cachedInputTokens'],
                'output_tokens':total['outputTokens'],
                'reasoning_output_tokens':total['reasoningOutputTokens'],
                'cache_write_input_tokens':total.get('cacheWriteInputTokens',0),
                'total_tokens':total['totalTokens']}})
        elif method == 'item/completed':
            item = params.get('item') or {}
            if item.get('type') == 'agentMessage':
                emit({'type':'item.completed','item':{'type':'agent_message','text':item.get('text','')}})

    try:
        request('initialize', {'clientInfo':{'name':'speclessbench','version':'1'},
                               'capabilities':{'experimentalApi':True}})
        send('initialized', {}, expect=False)
        result = request('thread/start', {'model':'gpt-6-luna','cwd':'/work',
                         'approvalPolicy':'never','permissions':'eval',
                         'ephemeral':False,
                         'config':{'model_reasoning_effort':'medium',
                                   'features.goals':mode=='on'}})
        thread = result['thread']['id']
        emit({'type':'thread.started','thread_id':thread})
        if mode == 'on':
            objective = goal_objective(platform)
            goal = request('thread/goal/set', {'threadId':thread,'objective':objective,
                            'status':'active','origin':'user'})['goal']
            observed = request('thread/goal/get', {'threadId':thread})['goal']
            if not observed or observed['status'] != 'active':
                raise RuntimeError('Native Goal was not activated')
            emit({'type':'native.goal.confirmed','goal':observed})
        else:
            observed = request('thread/goal/get', {'threadId':thread}).get('goal')
            if observed is not None:
                raise RuntimeError('Goal-off thread unexpectedly has a Goal')
            emit({'type':'native.goal.absent','goal':None})
        # This is the only client-issued turn/start. Any later turns must be native.
        request('turn/start', {'threadId':thread,'model':'gpt-6-luna','effort':'medium',
                              'input':[{'type':'text','text':prompt}]})
        while True:
            message = receive()
            if message is not False:
                handle(message)
            if last_turn_end is not None and not active:
                if mode == 'off':
                    reason = 'single-turn-completed'; break
                if time.monotonic()-last_turn_end >= 3 and time.monotonic() >= next_goal_poll:
                    next_goal_poll = time.monotonic()+5
                    goal = request('thread/goal/get', {'threadId':thread}).get('goal')
                    if goal and goal['status'] != 'active':
                        reason = 'goal-'+goal['status']; break
                if last_turn_end is not None and time.monotonic()-last_turn_end >= 120:
                    reason = 'native-continuation-not-observed'; break
                # Polling observes state only; it never starts another turn.
                time.sleep(0.1)
        summary = {'goal_mode':mode,'thread_id':thread,'native_turn_count':turn_count,
                   'client_turn_start_count':1,'manual_resumes':0,
                   'stop_reason':reason,'goal':goal}
        emit({'type':'native.run.completed','summary':summary})
        emit({'type':'turn.completed'})
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--goal-mode', choices=('on','off'), required=True)
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--platform', choices=('lean','rocq','compcert'), required=True)
    args = parser.parse_args()
    main(args.goal_mode,args.prompt,args.platform)
