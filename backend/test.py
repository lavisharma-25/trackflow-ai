import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    timeout=120,
    max_retries=0,
)

try:
    response = client.chat.completions.create(
        model="deepseek-ai/deepseek-v4.1-flash",
        messages=[
            {
                "role": "user",
                "content": "Say hi in one sentence."
            }
        ],
        max_tokens=100,
        temperature=0,
    )

    print(response.choices[0].message.content)

except Exception as e:
    print(type(e).__name__)
    print(e)


# import os
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI

# load_dotenv()

# api_key = os.getenv("NVIDIA_API_KEY")
# model = os.getenv("NVIDIA_MODEL")
# base_url = os.getenv("NVIDIA_BASE_URL")

# print("API key loaded:", bool(api_key))
# print("Model:", model)
# print("Base URL:", base_url)

# llm = ChatOpenAI(
#     model=model,
#     api_key=api_key,
#     base_url=base_url,
#     temperature=0.0,
#     max_tokens=100,
#     max_retries=2,
# )

# response = llm.invoke("hi")
# print(response.content)