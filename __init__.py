import asyncio,toml,itertools
import random

import novelai
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

def determine_resolution(image_size):
    if not image_size:  # 检查image_size是否为空
        random_number = random.randint(1, 6)
        if random_number in {1, 2, 3, 4}:
            return Resolution.NORMAL_PORTRAIT
        elif random_number == 5:
            return Resolution.NORMAL_LANDSCAPE
        else:  # 当random_number为6时
            return Resolution.NORMAL_SQUARE
    else:
        if image_size == "NORMAL_PORTRAIT":
            return Resolution.NORMAL_PORTRAIT
        elif image_size == "NORMAL_LANDSCAPE":
            return Resolution.NORMAL_LANDSCAPE
        elif image_size == "NORMAL_SQUARE":
            return Resolution.NORMAL_SQUARE
        else:
            return Resolution.NORMAL_PORTRAIT
        return image_size

def determine_Sampler(sampler):
    if not sampler:  # 检查image_size是否为空
        return novelai.Sampler.EULER
    else:
        if sampler == "k_euler":
            return novelai.Sampler.EULER
        elif sampler == "k_euler_ancestral":
            return novelai.Sampler.EULER_ANC
        elif sampler == "k_dpmpp_2s_ancestral":
            return novelai.Sampler.DPM2S_ANC
        elif sampler == "ddim":
            return novelai.Sampler.DDIM
        elif sampler == "k_dpmpp_2m":
            return novelai.Sampler.DPM2M
        elif sampler == "k_dpmpp_sde":
            return novelai.Sampler.DPMSDE
async def main():
    async def init():
        client = NAIClient(username, password, proxy=proxy)
        await client.init(timeout=1000)
        return client

    async def gen(prompt,negative_prompt,image_size,seed,sampler,steps,SMEA,DYN,cfg_scale,cfg_rescale):
        metadata = Metadata(
            prompt= prompt,
            negative_prompt = negative_prompt,
            model = Model.V3,
            action = Action.GENERATE,
            sampler = sampler,
            steps = steps,
            sm = SMEA,
            sm_dyn = DYN,
            scale = cfg_scale,
            cfg_rescale = cfg_rescale,
            res_preset = image_size,
            n_samples=1,
            )
        if seed != 0:
            metadata.seed = seed
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
    const_steps = config['option']['steps']
    const_sampler = determine_Sampler(config['option']['sampler'])
    const_SMEA = config['option']['SMEA']
    const_DYN = config['option']['DYN']
    if const_DYN:
        const_SMEA = True
    const_cfg_scale = config['option']['cfg_scale']
    const_cfg_rescale = config['option']['cfg_rescale']
    const_seed = config['option']['seed']
    const_image_size = determine_resolution(config['option']['image_size'])

    list = prompt_combinations(prompt_list,const_positive_prompt,3,1)
    for prompt in list:
        await gen(prompt,const_negative_prompt,const_image_size,const_seed,const_sampler,const_steps,
                  const_SMEA,const_DYN,const_cfg_scale,const_cfg_rescale)

asyncio.run(main())