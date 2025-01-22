import os
from openai import AsyncOpenAI as OpenAI
# from openai import RateLimitError
import asyncio

base_url = os.environ.get('LLM_API_BASE', "https://api.siliconflow.cn/v1")
token = os.environ.get('LLM_API_KEY', "sk-lgxwkhjdoveiamcyisjlidpmviprzidzjrwbawrnoflyhvma")

if not base_url and not token:
    raise ValueError("LLM_API_BASE or LLM_API_KEY must be set")
elif base_url and not token:
    client = OpenAI(base_url=base_url, api_key="not_use")
elif not base_url and token:
    client = OpenAI(api_key=token)
else:
    client = OpenAI(api_key=token, base_url=base_url)

concurrent_number = os.environ.get('LLM_CONCURRENT_NUMBER', 1)
semaphore = asyncio.Semaphore(int(concurrent_number))


async def openai_llm(messages: list, model: str, logger=None, **kwargs) -> str:
    resp = ''
    await semaphore.acquire()
    if logger:
        logger.debug(f'messages:\n {messages}')
        logger.debug(f'model: {model}')
        logger.debug(f'kwargs:\n {kwargs}')

    try:
        response = await client.chat.completions.create(messages=messages, model=model, **kwargs)
        resp = response.choices[0].message.content
    except Exception as e:
        if logger:
            logger.warning(e)
        else:
            print(e)
    finally:
        semaphore.release()

    if logger and resp:
        logger.debug(f'result:\n {response.choices[0]}')
        logger.debug(f'usage:\n {response.usage}')
    return resp
