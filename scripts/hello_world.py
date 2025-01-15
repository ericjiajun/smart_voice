#!/bin/env python3
'''
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''

import requests
import json
import re


# 设置API密钥和URL
API_KEY = "sk-e21f5ece451f4d82aa0313847bf0fb53"
API_URL ="https://api.deepseek.com/v1/chat/completions"
# 设置请求头。字典：映射
headers_for_deepseek_api = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
# 初始化对话历史
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant."}
]

# 天气 API 配置
SENIVERSE_API_KEY = "SScYkkf5_T_47E6IX"  # 心知天气 API 密钥
SENIVERSE_API_URL = "https://api.seniverse.com/v3/weather/now.json"

# 从用户输入中提取城市名称
def extract_city(user_input):
    # 匹配中国城市名称（可以根据需要扩展）
    cities = ["北京", "上海", "广州", "深圳", "成都", "杭州", "武汉", "南京", "重庆", "西安", "苏州", "无锡", "昆山"]
    for city in cities:
        if city in user_input:
            return city
    return None

## 获取当前天气（气温和降水情况）
def get_current_weather(city):
    params = {
        "key": SENIVERSE_API_KEY,
        "location": city,
        "language": "zh-Hans",
        "unit": "c"  # 使用摄氏度
    }
    response = requests.get(SENIVERSE_API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    weather_info = data["results"][0]["now"]
    return {

        "temperature": weather_info["temperature"],  # 气温
        "text": weather_info["text"]  # 天气状况（如“晴”、“雨”等）
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
    global conversation_history
    try:
        # 检查用户输入是否为“汇报你的状态”
        if user_input.strip() == "汇报你的状态":
            return "好的，已开机，目前电量100%，汽车无故障，可以开始工作。"
        # 检查用户输入是否包含“天气”关键词
        if "天气" in user_input:
            city = extract_city(user_input)  # 提取城市名称
            if city:
                weather = get_current_weather(city)
                return f"当前{city}的天气状况是{weather['text']}，气温是{weather['temperature']}摄氏度。"
            else:
                return "请换一个中国城市，例如：今天北京的天气怎么样？"
         # 将用户输入添加到对话历史
        conversation_history.append({"role": "user", "content": user_input})
        # 创建请求体
        #data = create_chat_prompt(user_input)
        # 调用 DeepSeek API
        data = {
            "model": "deepseek-chat",
            "messages": conversation_history,  # 传递完整的对话历史
            "max_tokens": 150,
            "temperature": 0.7
        }
        # 发送POST请求
        response: requests.Response = requests.post(API_URL, headers=headers_for_deepseek_api, json=data)
        response.raise_for_status()  # 检查HTTP错误,抛出异常，预案try

        # 解析响应
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            assistant_reply = result["choices"][0]["message"]["content"].strip()
            # 将模型回复添加到对话历史
            conversation_history.append({"role": "assistant", "content": assistant_reply})
            return assistant_reply
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
