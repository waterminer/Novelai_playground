import asyncio,toml,itertools,tqdm,random,json,time,httpx
from novelai import NAIClient,Metadata,Model,Action,Resolution,Sampler
from novelai.exceptions import ConcurrentError
from os import path,remove

with open("./config.toml",'r',encoding="utf-8") as f:
    config = toml.load(f)

resume_list=None
if path.exists("./crash_dump"):
    with open("./crash_dump") as f:
        resume_list = json.load(f)
    remove("./crash_dump")

username = config['account']['username']
password = config['account']['password']
prompt_conf = config['prompt']
try:
    proxy=config['proxy']['host']
except:
    proxy=None

# 提示词排列组合函数
def prompt_combinations(prompt_list:list[str],prompt:str,min_length:int,max_length:int)->list[str]:
    res = []
    if max_length<min_length: raise RuntimeError("min_length bigger than max_length")
    for length in range(min_length,max_length+1):
        temp = [",".join(element) for element in itertools.permutations(prompt_list, length)]
        res.extend([f"{element},{prompt}" for element in temp])
    return res

# 按照传入参数确定图片尺寸，如果没输入则按用户自定义尺寸处理
def determine_resolution(image_size)->tuple[int]:
    match image_size:
        case "NORMAL_PORTRAIT":
            return Resolution.NORMAL_PORTRAIT.value
        case "NORMAL_LANDSCAPE":
            return Resolution.NORMAL_LANDSCAPE.value
        case "NORMAL_SQUARE":
            return Resolution.NORMAL_SQUARE.value
        case "LARGE_PORTRAIT":
            return Resolution.LARGE_PORTRAIT.value
        case "LARGE_LANDSCAPE":
            return Resolution.LARGE_LANDSCAPE.value
        case "LARGE_SQUARE":
            return Resolution.LARGE_SQUARE.value
        case "SMALL_PORTRAIT":
            return Resolution.SMALL_PORTRAIT.value
        case "SMALL_LANDSCAPE":
            return Resolution.SMALL_LANDSCAPE.value
        case "SMALL_SQUARE":
            return Resolution.SMALL_SQUARE.value
        case _:
            return check_custom_resolution(image_size)
        
def check_custom_resolution(image_size)->tuple[int]:
    if isinstance(image_size,list) and len(image_size)==2:
        for element in image_size:
            if not isinstance(element,int):
                raise ValueError("'image_size' value error!")
        return tuple(image_size)
    raise ValueError("'image_size' value error!")


def determine_Sampler(sampler):
    match sampler:
        case "k_euler":
            return Sampler.EULER
        case "k_euler_ancestral":
            return Sampler.EULER_ANC
        case "k_dpmpp_2s_ancestral":
            return Sampler.DPM2S_ANC
        case "ddim":
            return Sampler.DDIM
        case "k_dpmpp_2m":
            return Sampler.DPM2M
        case "k_dpmpp_sde":
            return Sampler.DPMSDE
        case _:
            return Sampler.EULER


def metadata_builder(prompt:str,negative_prompt:str)->Metadata:
    option = config["option"]
    image_size = determine_resolution(option["image_size"])
    sampler = determine_Sampler(option["sampler"])
    try:
        steps = option["steps"]
    except:
        steps = 28
    try:
        sema = option["SMEA"]
    except:
        sema = False
    try:
        dyn = option["DYN"]
    except:
        dyn = False
    try:
        scale = option["cfg_scale"]
    except:
        scale = 6
    try: 
        cfg_rescale = option["cfg_rescale"]
    except:
        cfg_rescale = 0
    try:
        n_samples = option["n_samples"]
    except:
        n_samples = 1
    return Metadata(
        prompt= prompt,
        negative_prompt = negative_prompt,
        model = Model.V3,
        action = Action.GENERATE,
        sampler = sampler,
        steps = steps,
        sm = sema,
        sm_dyn = dyn,
        scale = scale,
        cfg_rescale = cfg_rescale,
        width=image_size[0],
        height=image_size[1],
        n_samples=n_samples,
    )

async def main():
    async def init():
        client = NAIClient(username, password, proxy=proxy)
        await client.init(timeout=1000)
        return client

    async def gen(metadata:Metadata,retry:int=3):
        # print(f"prompt:{metadata.prompt}\nEstimated Anlas cost: {metadata.calculate_cost(is_opus=False)}")
        while retry >= 0:
            try:
                output = await client.generate_image(
                    metadata, verbose=False, is_opus=False
                )
                for image in output:
                    image.save("./output",f"{prompt}.png")
                return
            except httpx.RemoteProtocolError as e:
                if retry > 0:
                    print("failed retry in:"+str(retry))
                    retry -= 1
                    time.sleep(1)
                else:
                    raise e
            except httpx.ConnectError as e:
                if retry > 0:
                    print("failed retry in:"+str(retry))
                    retry -= 1
                    time.sleep(1)
                else:
                    raise e
            except ConcurrentError as e:
                time.sleep(10)
        raise Exception("Unknown Exception")

    client = await init()
    try:
        seed = config["option"]["seed"]
    except:
        seed = 0
    prompt_list = config['prompt']['list']
    const_positive_prompt = config['prompt']['const_positive_prompt']
    const_negative_prompt = config['prompt']['const_negative_prompt']
    min = config['prompt']['min_length']
    max = config['prompt']['max_length']
    if resume_list:
        print("检测到意外中断，会将从上次任务断点继续")
        list = resume_list
    else:
        list = prompt_combinations(prompt_list,const_positive_prompt,min,max)
    try:
        for index,prompt in enumerate(tqdm.tqdm(list)):
            metadata=metadata_builder(prompt,const_negative_prompt)
            if seed == 0:
                metadata.seed=random.randint(1,999999999)
            await gen(metadata)
    except Exception as e:
        crash = list[index:]
        with open("crash_dump","w",encoding="utf8") as f:
            json.dump(crash,f)
        raise e

asyncio.run(main())