from src.plugins.chunithm.lib.chunithm_best_30 import generate
import asyncio
from src.plugins.chunithm.lib.request_client import get_player_info,generate_best_30_data
# asyncio.run(generate({"username":"ddaayy"}))
code,data = asyncio.run(generate_best_30_data("1826356872"))
# print(data)