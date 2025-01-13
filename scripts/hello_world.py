#!/bin/env python3
'''
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''

import requests
import json

# 设置API密钥和URL
API_KEY = "sk-e21f5ece451f4d82aa0313847bf0fb53"
API_URL = "https://api.deepseek.com/v1/chat/completions"

# 设置请求头。字典：映射
headers_for_deepseek_api = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 设置请求体
def create_chat_prompt(user_input):
    return {
        "model": "deepseek-chat",  # 假设的模型名称
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},  # 系统提示system prompt
            {"role": "user", "content": user_input}  # 用户输入
        ],
        "max_tokens": 150,  # 控制生成的最大长度
        "temperature": 0.7  # 控制生成文本的随机性
    }

# 调用API实现对话
def chat_with_deepseek(user_input):
    try:
        # 创建请求体
        data = create_chat_prompt(user_input)

        # 发送POST请求
        response: requests.Response = requests.post(API_URL, headers=headers_for_deepseek_api, json=data)
        response.raise_for_status()  # 检查HTTP错误,抛出异常，预案try

        # 解析响应
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            return "No response generated."
    except requests.exceptions.RequestException as e:   #除非，捕获
        return f"An error occurred: {e}"

# 示例对话
if __name__ == "__main__":
    while True:
        user_input = input("You: ")  # 获取用户输入
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat...")
            break
        response :str = chat_with_deepseek(user_input)  # 调用API
        print(f"DeepSeek: {response}")
