#!/bin/env python3
'''
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''
import speech_recognition as sr
import threading
import time

import numpy as np
import pyttsx3
import requests
import os
import json
import re
#import pyaudio
import uuid
from gtts import gTTS
# 生成一个唯一的设备 ID
#cuidid= str(uuid.uuid4())




# 设置API密钥和URL
API_KEY = "sk-e21f5ece451f4d82aa0313847bf0fb53"
API_URL ="https://api.deepseek.com/v1/chat/completions"
# 设置请求头。字典：映射
headers_for_deepseek_api = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 初始化语音识别和语音合成
recognizer = sr.Recognizer()
engine = pyttsx3.init()

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

# 全局变量
voice_mode = False  # 是否启用语音交互模式

# 语音识别
def recognize_speech(timeout=10):
    with sr.Microphone() as source:
        print("请说话...")
        recognizer.adjust_for_ambient_noise(source)  # 调整环境噪音
        try:
            audio = recognizer.listen(source, timeout=timeout)  # 设置超时时间
        except sr.WaitTimeoutError:
            print("10 秒内未检测到语音输入，退出语音交互模式。")
            return None

    try:
        text = recognizer.recognize_sphinx(audio, language="zh-CN")
        print(f"你说：{text}")
        return text
    except sr.UnknownValueError:
        print("无法识别语音")
        return None
    except sr.RequestError as e:
        print(f"语音识别服务出错：{e}")
        return None

# 语音合成
'''
def speak(text):
    print(f"DeepSeek: {text}")
    engine.say(text)
    engine.runAndWait()
'''
# 百度 TTS API 配置
api_key = "HoMFvZPdu9AzOH4rLupDciNw"
secret_key = "Qc7pUqGEjjZOFg3fyq5fkUCSmCg9uVpJ"
token_url = f"https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"#记得加f
tts_url = "http://tsn.baidu.com/text2audio"

# 获取访问令牌
def get_token():
    response = requests.get(token_url)
    return response.json().get("access_token")

# 合成语音
def speak(text, language='zh'):
    print(f"DeepSeek: {text}")

    token = get_token()
    if not token:
        print("无法获取访问令牌。")
        return

    # 设置请求参数
    params = {
        "tex": text,
        "lan": language,
        "cuid": "my-app-v1.0",
        "ctp": 1,  # 客户端类型（Web 为 1）
        "tok": token,
        "per": 0,  # 语音角色（0 为普通女声）
    }

    # 发送请求并保存语音文件
    response = requests.post(tts_url, data=params)
     # 检查响应状态码
    if response.status_code == 200:
        # 检查内容类型是否为音频
        if response.headers["Content-Type"] == "audio/mp3":
            with open("output.mp3", "wb") as f:
                f.write(response.content)
            print("语音文件已生成。")
            os.system("mpg321 output.mp3")  # 播放语音
        else:
            print("语音合成失败，响应内容不是音频文件。")
            print("响应内容:", response.text)  # 打印错误信息
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print("响应内容:", response.text)  # 打印错误信息
        '''
    if response.headers["Content-Type"] == "audio/mp3":
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        os.system("mpg321 output.mp3")  # 播放语音
    else:
        print("语音合成失败。")
'''
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

# 语音交互模式
def voice_interaction():
    global voice_mode
    while voice_mode:
        user_input = recognize_speech(timeout=10)  # 设置 10 秒超时
        if user_input is None:
            # 10 秒内未检测到语音输入，退出语音交互模式
            voice_mode = False
            speak("10 秒内未检测到语音输入，已退出语音交互模式。")
            break

        # 退出语音交互模式
        if "关闭语音交互" in user_input:
            voice_mode = False
            speak("已关闭语音交互模式")
            break

        # 处理用户输入
        response = chat_with_deepseek(user_input)
        speak(response)
'''
# 启动语音交互模式
def start_voice_interaction():
    global voice_mode
    voice_mode = True
    threading.Thread(target=voice_interaction, daemon=True).start()
'''
# 主程序
if __name__ == "__main__":
    while True:
        if voice_mode:
            # 启动语音交互模式
            voice_interaction()
        else:
            # 文本交互模式
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "关闭语音交互"]:
                if voice_mode:
                    voice_mode = False
                    speak("已关闭语音交互模式")
                else:
                    print("Exiting chat...")
                    break

            # 开启语音交互模式
            if "开启语音交互" in user_input:
                #start_voice_interaction()
                #print("DeepSeek: 已开启语音交互模式")
                #continue
                voice_mode = True
                print("DeepSeek: 已开启语音交互模式")
                continue

            # 处理用户输入
            response = chat_with_deepseek(user_input)
            print(f"DeepSeek: {response}")
