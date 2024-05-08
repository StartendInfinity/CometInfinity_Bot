import asyncio
from src.plugins.chunithm.lib.chunithm_best_30 import generate_by_lx
# asyncio.run(generate({"username":"ddaayy"}))
code,data = asyncio.run(generate_by_lx("1826356872"))
code.show()
# print(data)