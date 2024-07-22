import itertools,re,os
from .random_rules import RandomGroup


def prompt_combinations(
    prompt_list: list[str], prompt: str, min_length: int, max_length: int,mode:str="forward"
) -> list[str]:
    res = []
    if max_length < min_length:
        raise RuntimeError("min_length bigger than max_length")
    for length in range(min_length, max_length + 1):
        temp = [
            ",".join(element) for element in itertools.permutations(prompt_list, length)
        ]
        match mode:
            case "forward":
                res.extend([f"{element},{prompt}" for element in temp])
            case "behind":
                res.extend([f"{prompt},{element}" for element in temp])
            case _:
                res.extend([f"{element},{prompt}" for element in temp])
    return res


def convert_prompt(prompt:str,rules:dict[str, RandomGroup]):
    pattern = re.compile(r"<(.*?)>")
    for match_obj in pattern.finditer(prompt):
        try:
            random_group = rules[match_obj.group(1)]
            prompt = prompt.replace(match_obj.group(0),random_group.get_random())
        except KeyError as e: 
            print(f"Random group:{match_obj.group(1)} is notfound!")
            prompt = prompt.replace(match_obj.group(0),"")
    return prompt

