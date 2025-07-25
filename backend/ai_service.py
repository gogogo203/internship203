import json
import re
import time
import requests
from .config import ZHIPU_API_KEY


class ZhipuAI:
    """智谱AI服务类"""
    
    def __init__(self, zhipu_api_key: str, timeout: int = 60):
        self.zhipu_api_key = zhipu_api_key
        self.model_name = "glm-4-flash"
        self.temperature = 0.7
        self.max_tokens = 1000
        self.timeout = timeout
    
    def call(self, prompt: str) -> str:
        """调用智谱AI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.zhipu_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "你是专业出题助手"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "do_sample": True,
                "stream": False
            }
            
            response = requests.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise ValueError(f"HTTP请求失败，状态码: {response.status_code}, 响应: {response.text}")
            
            result = response.json()
            
            if "error" in result:
                raise ValueError(f"智谱API返回错误: {result['error']}")
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"智谱API响应格式错误: {result}")
                
        except requests.exceptions.RequestException as e:
            raise ValueError(f"网络请求错误: {str(e)}")
        except Exception as e:
            raise ValueError(f"调用智谱API时出错: {str(e)}")


def generate_mcq_from_text(text_content, num_questions=5, max_retries=3):
    """从文本生成选择题，带重试机制"""
    if not text_content or not isinstance(text_content, str) or len(text_content.strip()) < 50:
        print("文本内容不足，无法生成题目")
        return []

    # 限制文本长度，避免API调用失败
    if len(text_content) > 3000:
        text_content = text_content[:3000] + "..."

    # 准备提示词
    user_content = f"""
你是一个专业教育助手，请根据下面的文档内容生成 {num_questions} 道有挑战性的选择题，要有一定难度不能很简单。
每题必须有4个选项，选项描述中不要含有ABCD字样，且只有一个正确答案。
请用 JSON 格式返回，格式如下：
[
    {{
        "question": "问题文本",
        "options": ["选项A", "选项B", "选项C", "选项D"],
        "answer": "A"
    }},
    ...
]

文档内容：
{text_content}
"""

    for attempt in range(max_retries):
        try:
            # 检查API密钥
            if not ZHIPU_API_KEY:
                print("错误: 未设置ZHIPU_API_KEY环境变量")
                return []
                
            print(f"第 {attempt + 1} 次尝试调用智谱AI...")
            
            # 创建智谱AI实例
            zhipu_ai = ZhipuAI(
                zhipu_api_key=ZHIPU_API_KEY,
                timeout=60
            )
            
            # 调用API
            raw_content = zhipu_ai.call(user_content)
            
            if not raw_content:
                print("API响应内容为空")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return []
            
            print(f"API响应: {raw_content[:200]}...")  # 打印前200个字符
            
            # 提取json部分
            match = re.search(r"```json(.*?)```", raw_content, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
            else:
                json_str = raw_content.strip()

            quiz_list = json.loads(json_str)
            
            # 验证题目格式并安全处理选项
            validated_quiz = []
            for q in quiz_list:
                if not isinstance(q, dict):
                    continue
                
                if "question" not in q or "options" not in q or "answer" not in q:
                    continue
                
                options = q.get("options", [])
                if not isinstance(options, list) or len(options) != 4:
                    continue
                
                # 确保answer字段格式正确
                answer = q.get("answer", "A").upper()
                if answer not in ["A", "B", "C", "D"]:
                    answer = "A"  # 默认值
                
                validated_quiz.append({
                    "question": q["question"],
                    "options": options,
                    "correct_answer": answer
                })
            
            if validated_quiz:
                print(f"成功生成 {len(validated_quiz)} 道题目")
                return validated_quiz
            else:
                print(f"第 {attempt + 1} 次尝试：生成的题目格式不正确")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return []
                
        except json.JSONDecodeError as e:
            print(f"第 {attempt + 1} 次尝试失败: JSON解析错误: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
        except Exception as e:
            print(f"第 {attempt + 1} 次尝试失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
    
    print(f"生成题目失败: 已重试 {max_retries} 次")
    return []


def test_ai_service():
    """测试AI服务是否正常工作"""
    test_text = "人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。"
    try:
        result = generate_mcq_from_text(test_text, 2)
        print(f"测试结果: {result}")
        return len(result) > 0
    except Exception as e:
        print(f"测试失败: {e}")
        return False


if __name__ == "__main__":
    test_ai_service()