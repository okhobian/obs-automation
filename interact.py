import obspython as obs
import math, time

print("=======================================================")

def get_modifiers(key_modifiers):
    if key_modifiers:
        shift = key_modifiers.get("shift")
        control = key_modifiers.get("control")
        alt = key_modifiers.get("alt")
        command = key_modifiers.get("command")
    else:
        shift = control = alt = command = 0
    modifiers = 0

    if shift:
        modifiers |= obs.INTERACT_SHIFT_KEY
    if control:
        modifiers |= obs.INTERACT_CONTROL_KEY
    if alt:
        modifiers |= obs.INTERACT_ALT_KEY
    if command:
        modifiers |= obs.INTERACT_COMMAND_KEY
    return modifiers

def send_mouse_move_to_browser(source_name, x=0, y=0, key_modifiers=None):
    source = obs.obs_get_source_by_name(source_name)
    event = obs.obs_mouse_event()
    event.modifiers = get_modifiers(key_modifiers)
    event.x = x
    event.y = y
    obs.obs_source_send_mouse_move(source, event, False)

def send_mouse_click_to_browser(source_name, x=0, y=0, mouse_up=False, click_count=1):
    source = obs.obs_get_source_by_name(source_name)
    event = obs.obs_mouse_event()
    event.x = x
    event.y = y
    button_type=obs.MOUSE_LEFT
    key_modifiers=None
    event.modifiers = get_modifiers(key_modifiers)
    obs.obs_source_send_mouse_click(source, event, button_type, mouse_up, click_count)

def send_key_click_to_browser(source_name, key_up):
    source = obs.obs_get_source_by_name(source_name)
    key = obs.obs_key_from_name("OBS_KEY_TAB")
    vk = obs.obs_key_to_virtual_key(key)
    event = obs.obs_key_event()
    event.native_vkey = vk
    event.modifiers = get_modifiers(None)
    event.native_modifiers = event.modifiers
    event.native_scancode = vk
    event.text = ""
    obs.obs_source_send_key_click(source, event, key_up)
    print("pressed")
    

def single_click(source_name, x, y):
    send_mouse_click_to_browser(source_name, x, y, mouse_up=False, click_count=1)
    send_mouse_click_to_browser(source_name, x, y, mouse_up=True, click_count=2)
    print(f"[] single clicked at {x}, {y} on source [{source_name}]")
    
def double_click(source_name, x, y):
    send_mouse_click_to_browser(source_name, x, y, mouse_up=False, click_count=2)
    send_mouse_click_to_browser(source_name, x, y, mouse_up=True, click_count=2)
    send_mouse_click_to_browser(source_name, x, y, mouse_up=False, click_count=1)
    send_mouse_click_to_browser(source_name, x, y, mouse_up=True, click_count=1)
    
    print(f"[] double clicked at {x}, {y} on source [{source_name}]")


