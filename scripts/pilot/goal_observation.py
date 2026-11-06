"""Derive native lifecycle facts from the preserved RPC stream, including timeouts."""


def initial_observation(mode):
    return {'goal_mode':mode, 'native_turn_count':0, 'completed_native_turn_count':0,
            'client_turn_start_count':0, 'manual_resumes':0,
            'completed_tool_commands':0, 'file_change_events':0,
            'goal_confirmed_active':False, 'goal_confirmed_absent':False,
            'last_observed_goal':None}


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
            if method=='turn/started': state['native_turn_count'] += 1
            elif method=='turn/completed': state['completed_native_turn_count'] += 1
            elif method=='thread/goal/updated': state['last_observed_goal']=params.get('goal')
            elif method=='item/completed':
                item=params.get('item') or {}
                if item.get('type')=='commandExecution': state['completed_tool_commands'] += 1
                elif item.get('type')=='fileChange': state['file_change_events'] += 1
