# 运行说明

需要运行在python3.12.x版本  
推荐运行在python3.12.3，然后通过以下方式安装环境

```bash
pip install -r .
```

# 配置说明

## 账户配置

配置登录到novelai的账户，该项为必填项

### 范例

```toml
[account]
username = "登录账号"
password = "密码"
```

## 代理配置

### 范例

```toml
[proxy]
host = "主机地址"
```

## 可选项

配置图片生成选项

### 范例

```toml
[option]
image_size = "NORMAL_PORTRAIT"
...
...
```

### 详解

#### 配置项说明

|项目名|说明|默认值|
|---|---|---|
|image_size|设置图片尺寸|"RANDOM"|
|seed|生成种子，设定为0则为随机|0|
|steps|生成步数|28|
|sampler|采样器|"k_euler"|
|SMEA|是否开启SMEA，参数为布尔值|False|
|DYN|是否开启DYN，True开启，False关闭，开启DYN会自动开SMEA|False|
|cfg_scale|生成指导系数，范围0-10，步进0.1，越高越符合提示词|5|
|cfg_rescale|重调整生成指导，范围0-1，步进0.02|0|
|n_samples|每批图片生成数，注意，不同大小的图片支持的批量数不一样，详细请参考novelai|1|
|qualityToggle|提示词注入，开启则自动加入质量词|True|
|ucPreset|提示词注入等级，|0|

#### 设置图片尺寸说明

`image_size`允许用以下方式进行设置

```toml
image_size = "NORMAL_PORTRAIT" #设定为预设尺寸

image_size = [1920,1080] #设定为自定义尺寸
```

##### 支持的预设

|名称|尺寸(像素)|
|---|---|
|NORMAL_PORTRAIT|832X1216|
|NORMAL_LANDSCAPE|1216x832|
|NORMAL_SQUARE|1024x1024|
|LARGE_PORTRAIT|1024x1536|
|LARGE_LANDSCAPE|1536x1024|
|LARGE_SQUARE|1472x1472|
|SMALL_PORTRAIT|512x768|
|SMALL_LANDSCAPE|768x512|
|SMALL_SQUARE|640x640|
|WALLPAPER_PORTRAIT|1088x1920|
|WALLPAPER_LANDSCAPE|1920x1088|
|RANDOM|详情看下文介绍|

##### "RANDOM"预设说明

当你的`image_size`设定为`"RANDOM"`时，默认为从`NORMAL_PORTRAIT\NORMAL_LANDSCAPE\NORMAL_SQUARE`中随机抽选

如果需要更多自定义请看以下配置

```toml
[option.random_res]
random_list = ["NORMAL_PORTRAIT","[1920,1080]"] #随机项目列表
weight = [1.0,0.75] #每个项目的随机权重
```

random_list中的列表可选项与image_size一致，但是不能是"RANDOM"

weight的列表长度必须和random_list一致，也就是一一对应

#### 提示词注入

`ucPreset`可选项列表，具体请见[Novelai文档](https://docs.novelai.net/image/undesiredcontent.html)

- 0:Heavy
- 1:Light
- 2:Human Focus
- 3:None

## 提示词

### 范例

```toml
[prompt]
prompt = "提示词"
negative_prompt = "负面提示词"
#重复次数
repeat = 5 
```

## 排列组合列表

### 范例

```toml
#排列组合列表
[combinations]
max=3
min=1
list=[a,b,c]
mode="forward"
```

`mode`支持两种选项：

- "forward" 将组合结果放在提示词前面
- "behind" 将组合结果放在提示词末尾

默认为"forward"

## 随机提示词

将提示词部分替换成随机词组的功能

### 使用方式

若要使用随机提示词功能，请进行以下配置

```toml
[random]
rules_file="随机规则文件路径"
```

#### 使用范例

```toml
[prompt]
prompt="1girl,<hair_color>"
[random]
rules_file="./rules/example.json"
```

程序会识别输入的提示词中被`<尖括号>`包括的内容，并且从规则文件中读取对应键值的规则并替换，如案例所写，它的最终生成所用的提示词将可能是`1girl,blue hair`

### 规则文件

随机规则的编写可参考example文件，以下是详细说明

```json
{
    #标准写法
    "键值":{
        "list":[
            {"prompt":"被替换的结果1","weight":<权重>}，
            {"prompt":"被替换的结果2","weight":<权重>}，
            ...
        ]
    }
    #简化写法
    "键值":{
        "list":["被替换的结果1","被替换的结果2"]
    }
}
```

标准写法可以定义每一项替换的权重，倘若每一项的权重都相等，可以用简化写法
