import obspython as obs
from flask import Flask    
from flask import Response                                                     
import threading
import datetime
import json
import socket


host_name = "localhost"
port = 0
ports = {"8000":False,"8001":False,"8002":False,"8003":False,"8004":False,"8005":False}
app = Flask(__name__)

@app.route("/")
def root():
    time = datetime.datetime.now().strftime("%H:%M:%S")
    return f"{[time]} obs is running on {host_name}:{port}"

@app.route('/source/<source_type>/all')
def get_all_source_by_type(source_type):
    '''
        @param source_type: 0 | OBS_SOURCE_TYPE_INPUT for inputs
                            1 | OBS_SOURCE_TYPE_FILTER for filters
                            2 | OBS_SOURCE_TYPE_TRANSITION for transitions
                            3 | OBS_SOURCE_TYPE_SCENE for scenes
    '''
    try:
        sources = obs.obs_enum_sources()
        counter = 0
        result_dict = {}
        for s in sources:
            name = obs.obs_source_get_name(s)
            src_type = obs.obs_source_get_type(s)
            curr_state = obs.obs_source_active(s)
            
            result_dict[counter] = {'name':name, 'type':src_type, 'active':curr_state}
            counter+=1
        
        obs.source_list_release(sources)
        return Response(json.dumps(result_dict, indent=2), status=200)
    
    except Exception as e:
        return Response(f"[ERROR] exception {e}", status=500)

@app.route('/toggle/visibility/<source_name>/<state>')
def toggle_visibility_by_name(source_name, state):
    '''
        @param source_name: name of the source in string
        @param state: True | False
    '''
    try:
        current_scene = obs.obs_scene_from_source(obs.obs_frontend_get_current_scene())
        scene_item = obs.obs_scene_find_source_recursive(current_scene, source_name)
        _result = obs.obs_sceneitem_set_visible(scene_item, eval(state))
        result = f"[{source_name}] toggled to [{obs.obs_sceneitem_visible(scene_item)}]"
        return Response(result, status=200)
    except Exception as e:
        return Response(f"[ERROR] exception {e}", status=500)

@app.route('/toggle/visibility/all/<state>')
def toggle_visibility_all(state):
    '''
        @param state: True | False
    '''
    try:
        current_scene = obs.obs_scene_from_source(obs.obs_frontend_get_current_scene())
        sources = obs.obs_enum_sources()
        counter = 0
        result_dict = {}
        for s in sources:
            name = obs.obs_source_get_name(s)
            src_type = obs.obs_source_get_type(s)
            curr_state = obs.obs_source_active(s)
            if src_type==0 and curr_state != eval(state):
                scene_item = obs.obs_scene_find_source_recursive(current_scene, name)
                _result = obs.obs_sceneitem_set_visible(scene_item, eval(state))
                result_dict[name] = obs.obs_sceneitem_visible(scene_item)
                counter+=1
        
        obs.source_list_release(sources)
        result_dict['TOTAL_TOGGLED'] = counter
        return Response(json.dumps(result_dict, indent=2), status=200)
    
    except Exception as e:
        return Response(f"[ERROR] exception {e}", status=500)


@app.route('/record/<action>')
def recording(action):
    '''
        @param action: start | stop | pause
    '''
    try:
        is_recording = obs.obs_frontend_recording_active()
        is_paused = obs.obs_frontend_recording_paused()
        
        if action == 'start' and not is_recording:
            obs.obs_frontend_recording_start()
        elif action == 'pause' and is_recording:
            obs.obs_frontend_recording_pause(not is_paused)
        elif action == 'stop' and is_recording:
            obs.obs_frontend_recording_stop()
                    
        return Response(f"{action} complete", status=200)
    
    except Exception as e:
        return Response(f"[ERROR] exception {e}", status=500)


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def btn_pressed(props, prop):
    global port
    print(f"Button pressed, starting server on {host_name}:{port}")
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False), daemon = True).start()

def script_properties():
    global ports
    props = obs.obs_properties_create()
    list_property = obs.obs_properties_add_list(props, "port", "select a port",
                        obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_INT)

    for p in ports:
        obs.obs_property_list_add_int(list_property, f"{p} | in_use: {ports[p]}", int(p))
  
    btn = obs.obs_properties_add_button(props, "button", "start server", btn_pressed)
    return props

def script_update(settings):
  global port
  port = obs.obs_data_get_int(settings, "port")
  
def script_load(settings):
    global ports
    for p in ports:
        ports[p] = is_port_in_use(p)