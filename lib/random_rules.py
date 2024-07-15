import random, os, json


class RandomPrompt:
    def __init__(self, prompt: str, weight: float) -> None:
        self.prompt: str = prompt
        self.weight: float = weight


class RandomGroup:
    def __init__(self, name: str, prompt_list: list[RandomPrompt]) -> None:
        self.name: str = name
        self.prompt_list: list[RandomPrompt] = prompt_list

    def get_random(self):
        prompt_list = [element.prompt for element in self.prompt_list]
        weight = [element.weight for element in self.prompt_list]
        return random.choices(prompt_list, weight)[0]


def read_rule(file_path: os.PathLike) -> dict[str, RandomGroup]:
    with open(file_path, "r", encoding="utf-8") as f:
        json_doc = json.load(f)
    if not isinstance(json_doc, dict):
        raise TypeError()
    return {key: _resolve_rule(key, value) for key, value in json_doc.items()}


def _resolve_rule(key, value: dict):
    return RandomGroup(
        key, [_resolve_prompt_list(prompt_list) for prompt_list in value.get("list")]
    )


def _resolve_prompt_list(prompt_list) -> RandomPrompt:
    if isinstance(prompt_list, dict):
        return RandomPrompt(prompt_list.get("prompt"), prompt_list.get("weight", 1))
    elif isinstance(prompt_list, str):
        return RandomPrompt(prompt_list, 1)
    else:
        raise TypeError()
