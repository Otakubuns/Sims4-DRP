import time
from functools import wraps
from os.path import expanduser
from time import mktime

import rpc
import services
import sims4.reload
from game_services import GameServiceManager, service_manager
from sims.funds import FamilyFunds
from sims4.service_manager import Service

# DRP Variables
client_id = '971558123531804742'
rpc_sims = rpc.DiscordIpcClient.for_platform(client_id)
start_time = mktime(time.localtime())


def inject(target_function, new_function):
    @wraps(target_function)
    def _inject(*args, **kwargs):
        return new_function(target_function, *args, **kwargs)

    return _inject


def inject_to(target_object, target_function_name):
    def _inject_to(new_function):
        target_function = getattr(target_object, target_function_name)
        setattr(target_object, target_function_name, inject(target_function, new_function))
        return new_function

    return _inject_to


# Global service variable
with sims4.reload.protected(globals()):
    _my_custom_service = None


def get_my_custom_service():
    return service_manager.my_custom_service


#### FOR DEBUG ####
path = expanduser('~/Documents/Electronic Arts/The Sims 4/Mods/TESTING/DRP.txt')


class MyCustomService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Setting Presence to current household, income & world
    def on_zone_load(self, *args, **kwargs):
        SetActivity(GetWorldName(), GetWorldKey(GetWorldName()), GetWorldName(),
                    f"{GetHouseholdName()} | §{GetHouseholdFunds()}")

    def stop(self, *args, **kwargs):
        global _my_custom_service
        _my_custom_service = None


@inject_to(GameServiceManager, 'start_services')
def start_services(original, self, *args, **kwargs):
    global _my_custom_service
    try:
        if _my_custom_service is None:
            _my_custom_service = MyCustomService()
            self.register_service(_my_custom_service, is_init_critical=False)
    except:
        pass

    original(self, *args, **kwargs)


@inject_to(services, 'on_enter_main_menu')
def inject_zone_loading(original):
    original()
    SetActivity("Main Menu", "menu", "Browsing the menu", "")


@inject_to(FamilyFunds, 'send_money_update')
def update_household_funds(original, self, *args, **kwargs):
    original(self, *args, **kwargs)
    SetActivity(GetWorldName(), GetWorldKey(GetWorldName()), GetWorldName(),
                f"{GetHouseholdName()} | §{GetHouseholdFunds()}")


# Discord RPC Functions
def SetActivity(largeimagetext, largeimagekey, details, state=""):
    try:
        if state != "":
            activity = {
                "details": details,
                "state": state,
                "timestamps": {
                    "start": start_time
                },
                "assets": {
                    "large_image": largeimagekey,
                    "large_text": largeimagetext
                }
            }
        else:
            activity = {
                "details": details,
                "timestamps": {
                    "start": start_time
                },
                "assets": {
                    "large_image": largeimagekey,
                    "large_text": largeimagetext
                }
            }
        rpc_sims.set_activity(activity)
    except:
        pass


def GetHouseholdName():
    return services.active_household().name


def GetHouseholdFunds():
    return f"{services.active_household().funds.money:,}"


def GetWorldName():
    return services.get_persistence_service().get_neighborhood_proto_buf_from_zone_id(services.current_zone_id()).name


def GetWorldKey(world_name):
    world_key = world_name.replace(' ', '_')
    world_key = world_key.replace('.', '_')
    world_key = world_key.replace('-', '_')
    world_key = world_key.lower()
    return world_key
