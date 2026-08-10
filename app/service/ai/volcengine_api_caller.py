"""
volcengine_api_caller.py
    用于调用火山API
"""

import requests
from app.models.ai import Model, CodeInsightExaminer
from app.service.ai import ChatCompletionRequest


def volcengine_api_caller(model: Model, message, message_list: list = None):
    url = model.model_ark_url
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {model.model_ark_key}"
    }

    data = ChatCompletionRequest(
        model=model,
        message=message,
        messages_list=message_list,
    )
    # print(data)
    response = requests.post(url, headers=headers, data=data)
    return response


if __name__ == '__main__':
    requests = volcengine_api_caller(CodeInsightExaminer(), "归并排序，简单")

    with open("test.txt", "w", encoding="utf-8") as f:
        f.write(requests.text)
        print(requests.text)



