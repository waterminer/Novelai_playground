import asyncio,toml,itertools,tqdm
from novelai import NAIClient,Metadata,Model,Action,Resolution

with open("./config.toml",'r',encoding="utf-8") as f:
    config = toml.load(f)

username = config['account']['username']
password = config['account']['password']
prompt_conf = config['prompt']
try:
    proxy=config['proxy']['host']
except:
    proxy=None


def prompt_combinations(prompt_list:list[str],prompt:str,max_length:int,min_length:int)->list[str]:
    res = []
    if max_length<min_length: raise RuntimeError("min_length bigger than max_length")
    for length in range(min_length,max_length+1):
        temp = [",".join(element) for element in itertools.permutations(prompt_list, length)]
        res.extend([f"{element},{prompt}" for element in temp])
    return res

async def main():
    box = Resolution.NORMAL_PORTRAIT
    async def init():
        client = NAIClient(username, password, proxy=proxy)
        await client.init(timeout=1000)
        return client

    async def gen(prompt,negative_prompt):
        metadata = Metadata(
            prompt= prompt,
            negative_prompt = negative_prompt,
            model = Model.V3,
            action = Action.GENERATE,
            seed= 114514,
            res_preset=Resolution.NORMAL_PORTRAIT,
            n_samples=1,
            sm=False
            )
        print(f"prompt:{metadata.prompt}\nEstimated Anlas cost: {metadata.calculate_cost(is_opus=False)}")

        output = await client.generate_image(
            metadata, verbose=False, is_opus=False
        )
        for image in output:
            image.save("./output",f"{prompt}.png")

    client = await init()
    prompt_list = config['prompt']['list']
    const_positive_prompt = config['prompt']['const_positive_prompt']
    const_negative_prompt = config['prompt']['const_negative_prompt']
    list = prompt_combinations(prompt_list,const_positive_prompt,3,1)
    for prompt in tqdm(list):
        await gen(prompt,const_negative_prompt)

asyncio.run(main())