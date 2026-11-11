"""Derive native lifecycle facts from the preserved RPC stream, including timeouts."""


def initial_observation(mode):
    return {'goal_mode':mode, 'native_turn_count':0, 'completed_native_turn_count':0,
            'client_turn_start_count':0, 'manual_resumes':0,
            'completed_tool_commands':0, 'file_change_events':0,
            'goal_confirmed_active':False, 'goal_confirmed_absent':False,
            'last_observed_goal':None}


def _observe_native_turn(state, method, params):
    thread_id = state.get('thread_id')
    if not thread_id or params.get('threadId') != thread_id:
        return
    current_turn = state.get('native_turn_id')
    if method == 'error':
        turn_id = params.get('turnId')
        if (isinstance(turn_id, str) and turn_id and current_turn in (None, turn_id) and
                params.get('willRetry') is False and isinstance(params.get('error'), dict) and
                state.get('native_turn_status') != 'completed'):
            state['native_turn_failure'] = {'kind': 'native-provider-error', 'turn_id': turn_id}
        return
    if method not in ('turn/started', 'turn/completed'):
        return
    turn = params.get('turn')
    if not isinstance(turn, dict) or not isinstance(turn.get('id'), str) or not turn['id']:
        return
    turn_id = turn['id']
    if method == 'turn/started':
        if turn_id != current_turn:
            previous = state.get('native_turn_failure') or {}
            if previous.get('turn_id') != turn_id:
                state.pop('native_turn_failure', None)
            state['native_turn_id'] = turn_id
            state['native_turn_status'] = 'started'
        return
    if current_turn not in (None, turn_id):
        return
    status = turn.get('status')
    state['native_turn_id'] = turn_id
    state['native_turn_status'] = status
    if status == 'failed':
        state['native_turn_failure'] = {'kind': 'native-turn-failed', 'turn_id': turn_id}
    elif status == 'completed':
        state.pop('native_turn_failure', None)


def observe(state, event):
    if event.get('type') == 'thread.started':
        state['thread_id']=event['thread_id']
    elif event.get('type') == 'native.goal.confirmed':
        state['goal_confirmed_active'] = event['goal']['status']=='active'
        state['last_observed_goal'] = event['goal']
    elif event.get('type') == 'native.goal.absent':
        state['goal_confirmed_absent'] = True
    elif event.get('type') == 'rpc.event':
        message = event.get('message',{}); method=message.get('method')
        if event.get('direction') == 'send':
            if method=='turn/start': state['client_turn_start_count'] += 1
            if method=='thread/resume': raise ValueError('External resume is forbidden')
        elif event.get('direction') == 'receive':
            params=message.get('params') or {}
            if state.get('thread_id') and params.get('threadId') not in (None,state['thread_id']):
                return
            _observe_native_turn(state, method, params)
            if method=='turn/started': state['native_turn_count'] += 1
            elif method=='turn/completed': state['completed_native_turn_count'] += 1
            elif method=='thread/goal/updated': state['last_observed_goal']=params.get('goal')
            elif method=='item/completed':
                item=params.get('item') or {}
                if item.get('type')=='commandExecution': state['completed_tool_commands'] += 1
                elif item.get('type')=='fileChange': state['file_change_events'] += 1
