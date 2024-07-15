from novelai import Metadata, Resolution, Sampler, NAIClient
from novelai.types import Image
from novelai.exceptions import ConcurrentError
from random import randint, choices
import httpx, asyncio


def determine_resolution(
    image_size: str | list[int], random_option: dict = {}
) -> tuple[int]:
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
        case "WALLPAPER_PORTRAIT":
            return Resolution.WALLPAPER_PORTRAIT.value
        case "WALLPAPER_LANDSCAPE":
            return Resolution.WALLPAPER_LANDSCAPE.value
        case "RANDOM":
            return random_resolution(
                random_option.get("random_list", None),
                random_option.get("weight", None),
            )
        case _:
            return check_custom_resolution(image_size)


def random_resolution(
    random_list: list | None = None, weight: list[float] | None = None
) -> tuple[int]:
    if random_list == None:
        random_list = ["NORMAL_PORTRAIT", "NORMAL_LANDSCAPE", "NORMAL_SQUARE"]
    if weight == None:
        weight = [1.0, 1.0, 1.0]
    if "RANDOM" in random_list:
        raise ValueError('"RANDOM" cannot be in the "random_list"')
    if len(random_list) != len(weight):
        raise ValueError(
            'list "random_list" length does not match list "weight" length'
        )
    res = choices(random_list, weight)[0]
    return determine_resolution(res)


def check_custom_resolution(image_size: list[int]) -> tuple[int]:
    if isinstance(image_size, list) and len(image_size) == 2:
        for element in image_size:
            if not isinstance(element, int):
                raise TypeError("'image_size' TypeError!")
        return tuple(image_size)
    raise TypeError("'image_size' TypeError!")


def determine_Sampler(sampler: str) -> Sampler:
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


class Novelai:

    def __init__(
        self,
        client,
        image_size,
        sampler,
        steps,
        sema,
        dyn,
        scale,
        cfg_rescale,
        n_sample,
        seed,
        qualityToggle,
        random_res_option,
    ) -> None:
        self.client: NAIClient = client
        self._image_size: str | list[int] = image_size
        self.sampler: Sampler = sampler
        self.steps: int = steps
        self.sema: bool = sema
        self.dyn: bool = dyn
        self.scale: float = scale
        self.cfg_rescale: float = cfg_rescale
        self.n_sample: int = n_sample
        self.seed: int = seed
        self.qualityToggle:bool = qualityToggle
        self.random_res_option: dict | None = random_res_option

    @staticmethod
    async def builder(config: dict):
        """
        创建Novelai对象的工厂函数
        """
        proxy = config.get("proxy", {}).get("host", None)
        account: dict = config.get("account")
        username: str = account.get("username")
        password: str = account.get("password")
        client: NAIClient = NAIClient(username, password, proxy=proxy)
        await client.init()
        option: dict = config.get("option",{})
        qualityToggle:bool = config.get("qualityToggle",True)
        random_res_option = option.get("random_res", None)
        image_size: str = option.get("image_size", "RANDOM")
        sampler: Sampler = determine_Sampler(option.get("sampler", "k_euler"))
        steps: int = option.get("steps", 28)
        sema: bool = option.get("SMEA", False)
        dyn: bool = option.get("DYN", False)
        scale: float = option.get("cfg_scale", 6)
        cfg_rescale: float = option.get("cfg_rescale", 0)
        n_sample: int = option.get("n_samples", 1)
        seed: int = option.get("seed", 0)
        return Novelai(
            client,
            image_size,
            sampler,
            steps,
            sema,
            dyn,
            scale,
            cfg_rescale,
            n_sample,
            seed,
            qualityToggle,
            random_res_option,
        )

    async def gen_image(self, prompt: str, negative_prompt: str = ""):
        scale = determine_resolution(self._image_size)
        seed = self.seed
        if seed == 0:
            seed = randint(1, 999999999)
        metadata = Metadata(
            prompt=prompt,
            negative_prompt=negative_prompt,
            qualityToggle=self.qualityToggle,
            width=scale[0],
            height=scale[1],
            seed=seed,
            n_samples=self.n_sample,
            steps=self.steps,
            scale=self.scale,
            cfg_rescale=self.cfg_rescale,
            sampler=self.sampler,
            sm=self.sema,
            sm_dyn=self.dyn,
        )
        return await self._gen_with_retry(metadata)
    

    @property
    def image_size(self)->tuple[int]:
        if self._image_size == "RANDOM":
            return "RANDOM"
        return determine_resolution(self._image_size)


    async def _gen_with_retry(self, metadata, retry=3) -> list[Image]:
        while retry >= 0:
            try:
                images = await self.client.generate_image(metadata)
                return images
            except (httpx.RemoteProtocolError, httpx.ConnectError) as e:
                if retry > 0:
                    print("Connect failed\nretry in:" + str(retry))
                    retry -= 1
                    asyncio.sleep(1)
                else:
                    raise e
            except ConcurrentError as e:
                if retry > 0:
                    print("ConcurrentError!\nretry in:" + str(retry))
                    retry -= 1
                    asyncio.sleep(10)
                else:
                    raise e
            except Exception as e:
                raise e
