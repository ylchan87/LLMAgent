from LLMAgent.ToolRegistry import ToolRegistry
from typing import Annotated

registry = ToolRegistry("ToolBox")

#@registry.register_func
def random_number_generator(
        seed: Annotated[int, 'The random seed used by the generator', True],
        range: Annotated[tuple[int, int], 'The range of the generated numbers', True],
) -> int:
    """
    Generates a random number x, s.t. range[0] <= x < range[1]
    """
    if not isinstance(seed, int):
        raise TypeError("Seed must be an integer")
    if not isinstance(range, tuple):
        raise TypeError("Range must be a tuple")
    if not isinstance(range[0], int) or not isinstance(range[1], int):
        raise TypeError("Range must be a tuple of integers")

    import random
    return random.Random(seed).randint(*range)

#@registry.register_func
def get_weather(
        city_name: Annotated[str, 'The name of the city to be queried', True],
) -> str:
    """
    Get the current weather for `city_name`
    """

    if not isinstance(city_name, str):
        raise TypeError("City name must be a string")

    key_selection = {
        "current_condition": ["temp_C", "FeelsLikeC", "humidity", "weatherDesc", "observation_time"],
    }
    import requests
    try:
        resp = requests.get(f"https://wttr.in/{city_name}?format=j1")
        resp.raise_for_status()
        resp = resp.json()
        ret = {k: {_v: resp[k][0][_v] for _v in v} for k, v in key_selection.items()}
    except:
        import traceback
        ret = "Error encountered while fetching weather data!\n" + traceback.format_exc()

    return str(ret)

@registry.register_func
def is_holiday(
    month: Annotated[int, 'Month of the date', True],
    day  : Annotated[int, 'Day of the date'  , True],
) -> bool:
    """
    Check if date is a holiday
    """
    return day%10 == 1

@registry.register_func
def check_current_date(
) -> bool:
    """
    Return the current year, month and day
    """
    reply = {
        "year" : 2000,
        "month" : 5,
        "day" : 10
    }
    return reply

if __name__=="__main__":
    #registry.register_func(get_weather)
    #print(registry.dispatch_func("get_weather", {"city_name": "beijing"}))

    print(registry.get_tool_descriptions())