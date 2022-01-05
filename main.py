import asyncio

from src.TradFri import TradFri


async def main():
    light, mode, dimmer, colour = input("Select bulb and mode: ").split()
    tradfri = TradFri()
    # tradfri_config = await tradfri.tradfri_configuration()
    # print(tradfri_config)
    lights = await tradfri.get_tradfri_devices()
    # print(lights)
    # print({index: [lamp.name, lamp.light_control.lights[0].state] for index, lamp in enumerate(lights)})
    await tradfri.switch_light(lights, light, mode, int(dimmer), colour)

if __name__ == '__main__':
    asyncio.run(main())
