from lib import *
import asyncio,tomllib,tqdm,json,os


async def gen(nai_cli:Novelai,prompt,negative_prompt):
    images = await nai_cli.gen_image(prompt,negative_prompt)
    for image in images:
        name = f"{image.metadata.width}x{image.metadata.height}_{image.metadata.prompt[:45]}_{image.metadata.seed}.png"
        image.save("./output",name)

async def main():
    with open("./config.toml","rb") as f:
        config = tomllib.load(f)
    novelai = await Novelai.builder(config)
    prompt_conf:dict = config.get("prompt")
    prompt_raw = prompt_conf.get("prompt","")
    negative_prompt = prompt_conf.get("negative_prompt","")
    random_conf:dict = config.get("random",None)
    if random_conf:
        rules_file_path = random_conf.get("rules_file")
        rules = read_rule(rules_file_path)
    else:
        rules = {}
    repeat = prompt_conf.get("repeat",1)
    combinations_conf:dict = config.get("combinations",None)
    if combinations_conf:
        combinations_list = combinations_conf.get("list")
        max_length = combinations_conf.get("max")
        min_length = combinations_conf.get("min")
    if os.path.exists("./crash_dump"):
        print("检测到崩溃记录，正在读取断点进度")
        with open("./crash_dump","rb") as f:
            prompt_list = json.load(f)
        os.remove("./crash_dump")
    else:
        prompt_list = []
        for i in range(0,repeat):
            prompt = convert_prompt(prompt_raw,rules)
            if combinations_conf:
                prompt_list.extend(prompt_combinations(combinations_list,prompt,min_length=min_length,max_length=max_length))
            else:
                prompt_list.extend([prompt])
    try:
        for index,prompt in enumerate(tqdm.tqdm(prompt_list)):
            await gen(novelai,prompt,negative_prompt)
    except Exception as e:
        crash_dump = prompt_list[index:]
        with open("crash_dump","w",encoding="utf8") as f:
            json.dump(crash_dump,f)
        raise e
    
if __name__ == "__main__":
    asyncio.run(main())