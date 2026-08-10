import json
from typing import List, Union, Dict, Optional
from app.models.ai import Model


def build_messages_list(model: Model, message, messages_list: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
    """构建消息列表"""
    if messages_list is None:
        if type(message) is str:
            return [
                {"role": "system", "content": model.model_prompt},
                {"role": "user", "content": message}
            ]
        elif type(message) is list:
            return [
                {"role": "system", "content": model.model_prompt},
                *message
            ]
        else:
            raise TypeError("message必须是str或list")
    else:
        messages_list.append({"role": "user", "content": message})
        return messages_list


def build_request_data(
        model: Model,
        messages_list: List[Dict[str, str]],
        stream: Optional[bool] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        logit_bias: Optional[Dict[str, float]] = None
) -> Dict[str, Union[str, List[Dict[str, str]], bool, int, float, Dict[str, float]]]:
    """构建请求数据"""
    return {
        "model": model.model_ark_id,
        "messages": messages_list,
        "stream": stream,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
        "logit_bias": logit_bias
    }


def filter_none_values(data: Dict) -> Dict:
    """过滤字典中的空值"""
    return {k: v for k, v in data.items() if v is not None}


def serialize_to_json(data: Dict) -> str:
    """将字典序列化为 JSON 字符串"""
    try:
        return json.dumps(data, ensure_ascii=False)
    except TypeError as e:
        raise ValueError(f"Failed to serialize data to JSON: {e}")


def ChatCompletionRequest(
        model: Model,
        message,
        messages_list: Optional[List[Dict[str, str]]] = None,
        stream: Optional[bool] = None,
        max_tokens: Optional[int] = None
) -> str:
    """主函数，负责调用各个函数，并将结果返回"""
    messages_list = build_messages_list(model, message, messages_list)
    request_data = build_request_data(
        model, messages_list, stream, max_tokens,
        model.temperature, model.top_p,
        model.frequency_penalty, model.presence_penalty,
        model.logit_bias
    )
    clean_data = filter_none_values(request_data)
    return serialize_to_json(clean_data)

