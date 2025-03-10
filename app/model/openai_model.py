import openai
import requests
import simplejson
import time

from openai import OpenAI
from model import Model
from utils import LOG


class OpenAIModel(Model):
    def __init__(self, model: str, api_key: str, api_base: str = 'https://openai.api2d.net',headers=None):
        self.model = model
        if headers:
            self.client =  OpenAI(default_headers=headers, base_url=api_base, api_key=api_key)
        else:
            self.client =  OpenAI(base_url=api_base, api_key=api_key)

    def make_request(self, prompt):
        attempts = 0
        while attempts < 3:
            try:
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role":"system","content": Model.MODEL_ROLE_TRANSLATE_PROMPT},
                        {"role": "user", "content": prompt}
                    ]
                )
                translation = response.choices[0].message.content.strip()
                
                return translation, True
            except openai.RateLimitError:
                attempts += 1
                if attempts < 3:
                    LOG.warning("Rate limit reached. Waiting for 60 seconds before retrying.")
                    time.sleep(60)
                else:
                    raise Exception("Rate limit reached. Maximum attempts exceeded.")
            except requests.exceptions.RequestException as e:
                raise Exception(f"请求异常：{e}")
            except requests.exceptions.Timeout as e:
                raise Exception(f"请求超时：{e}")
            except simplejson.errors.JSONDecodeError as e:
                raise Exception("Error: response is not valid JSON format.")
            except Exception as e:
                raise Exception(f"发生了未知错误：{e}")
        return "", False
