from pathlib import Path
import argparse
import uuid

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

folder = Path(__file__)
tradfri_config = str(folder.cwd() / 'tradfri_standalone_psk.conf')

parser = argparse.ArgumentParser()
parser.add_argument(
    "host", metavar="IP", type=str, help="IP Address of your Tradfri Gateway"
)
parser.add_argument(
    "-K", "--key", dest="key", required=False, help="Key found on Tradfri Gateway"
)
args = parser.parse_args()
if args.host not in load_json(tradfri_config) and args.key is None:
    key = input().strip()
    if len(key) != 16:
        raise PytradfriError('Invalid key length')
    else:
        args.key = key


class TradFri:
    def __init__(self):
        self.conf = load_json(tradfri_config)
        self.host = self.conf.get("host")
        self.identity = self.conf.get("identity")
        self.psk = self.conf.get("key")

    async def get_tradfri_devices(self):
        try:
            api_factory = await APIFactory.init(host=self.host, psk_id=self.identity, psk=self.psk)
        except KeyError:
            self.identity = uuid.uuid4().hex
            api_factory = await APIFactory.init(host=self.host, psk_id=self.identity)
            try:
                self.psk = await api_factory.generate_psk(self.psk)
                print("Generated PSK: ", self.psk)

                self.conf[args.host] = {"identity": self.identity, "key": self.psk}
                save_json(tradfri_config, self.conf)
            except AttributeError:
                raise PytradfriError(
                    "Please provide the 'Security Code' on the "
                    "back of your Tradfri gateway using the "
                    "-K flag."
                )
        api = api_factory.request
        gateway = Gateway()
        devices_command = gateway.get_devices()
        devices_commands = await api(devices_command)
        devices = await api(devices_commands)
        lights = [dev for dev in devices if dev.has_light_control]
        return lights

    @staticmethod
    def dim_percentage():
        max_dim = 254
        dim_step = max_dim / 100
        return dim_step

    def color_switcher(self, input_color: str):
        color_dict = {'blue': '6c83ba', 'yellow': 'ebb63e', 'orange': 'e78834', 'white': 'f5faf6',
                      'green': 'a9d62b'}
        for color, hex_color in color_dict.items():
            if input_color == color:
                return hex_color

    async def switch_light(self, lights: list, name: str, status: str, dimmer: int, colour: str):
        lights_status = {index: [lamp.name, lamp.light_control.lights[0].state] for index, lamp in enumerate(lights)}
        req_color = self.color_switcher(colour)
        for i, lamp in lights_status.items():
            if name == lamp[0]:
                index = i
                api_factory = await APIFactory.init(host=self.host, psk_id=self.identity, psk=self.psk)
                api = api_factory.request
                await api(lights[index].light_control.set_dimmer(int(dimmer * self.dim_percentage())))
                await api(lights[index].light_control.set_hex_color(req_color))





