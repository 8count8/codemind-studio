from typing import Optional, Union, Dict, List


class Model:
    """
    Model类用于表示一个模型，包含模型的基本信息和生成文本时的参数配置。

    属性:
        model_id (str): 模型的唯一标识符，默认为None。
        model_name (str): 模型的名称，默认为None。
        model_ark_id (str): 模型在ARK系统中的ID，默认为None。
        model_ark_url (str): 模型在ARK系统中的URL地址，默认为None。
        model_ark_key (str): 模型在ARK系统中的访问密钥，默认为None。
        model_prompt (str): 生成文本时的初始提示，默认为None。
        temperature (float): 控制生成文本的随机性，值越高生成的文本越随机，默认为1.0。
        top_p (float): 控制生成文本时的采样策略，值越小生成的文本越集中，默认为1.0。
        frequency_penalty (float): 控制生成文本时对重复词汇的惩罚，值越高越避免重复，默认为0.0。
        presence_penalty (float): 控制生成文本时对新词汇的奖励，值越高越倾向于使用新词汇，默认为0.0。
        stop (Optional[Union[str, List[str]]]): 生成文本时的停止条件，可以是字符串或字符串列表，默认为None。
        logit_bias (Optional[Dict[str, float]]): 控制生成文本时对特定词汇的偏好，键为词汇，值为偏好的权重，默认为None。
    """
    model_id: str = None
    model_name: str = None
    model_ark_id: str = None
    model_ark_url: str = None
    model_ark_key: str = None
    model_prompt: str = None
    temperature: float = None
    top_p: float = None
    frequency_penalty: float = None
    presence_penalty: float = None
    logit_bias: Optional[Dict[str, float]] = None
