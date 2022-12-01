import time
from functools import wraps
from os.path import expanduser
from time import mktime
import rpc
import services
import sims4.reload
from game_services import GameServiceManager, service_manager
from sims4.service_manager import Service
from world import lot

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

    def on_zone_load(self, *args, **kwargs):
        Household = services.active_household().name
        World = services.get_persistence_service().get_neighborhood_proto_buf_from_zone_id(
            services.current_zone_id()).name
        Lot = lot.Lot.get_lot_name(self=services.active_lot())

        try:
            # setup text for discord image
            world_key = World.replace(' ', '_')
            world_key = world_key.replace('.', '_')
            world_key = world_key.replace('-', '_')
            world_key = world_key.lower()

            # On successful lot load
            activity = {
                "state": f"{Household} Household",
                "details": f"{World}",
                "timestamps": {
                    "start": start_time
                },
                "assets": {
                    "large_image": f"{world_key}",
                    "large_text": f"{World}"
                }
            }
            rpc_sims.set_activity(activity)
        except:
            pass

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
    # Start RPC Initial Connection
    activity = {
        "details": "Browsing the menu",  # anything you like
        "timestamps": {
            "start": start_time
        },
        "assets": {
            "large_image": "menu",  # must match the image key
            "large_text": "Main Menu"
        }
    }
    rpc_sims.set_activity(activity)
