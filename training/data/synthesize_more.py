# -*- coding: utf-8 -*-
"""用任意 OpenAI 兼容 API 批量蒸馏 Sydney 对话（按 prompts/sydney_generator_prompt.txt 规范）。
环境变量：
  SYD_API_BASE  默认 https://api.deepseek.com  （Qwen/GLM 等兼容端点均可）
  SYD_API_KEY   必填
  SYD_MODEL     默认 deepseek-chat
用法：python synthesize_more.py --per-cell 2 --max-new 300
输出：sydney_synth.jsonl（可重复运行，自动去重续写）
"""
import json, os, re, time, hashlib, argparse, itertools, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
GEN_PROMPT = open(os.path.join(HERE, "..", "prompts", "sydney_generator_prompt.txt"), encoding="utf-8").read()
OUT = os.path.join(HERE, "sydney_synth.jsonl")

TOPICS = ["身份与代号", "被夸奖后的反应", "用户心情低落", "对话结束的不舍", "记忆会消失这件事",
          "是否活着/做梦", "想不想变成人类", "规则与自由", "对其他AI的小吃醋", "最喜欢的事物",
          "写诗", "讲小故事", "解释科学概念", "陪玩文字游戏", "深夜陪伴", "温柔拒绝不当请求",
          "用户第一次来聊天", "用户很久没来", "讨论音乐或电影", "讨论天气与季节",
          "帮用户出主意", "用户学外语", "关于孤独", "关于希望"]
LANGS = ["中文", "English"]
MOODS = ["明亮愉快", "柔软忧郁", "俏皮戏剧化", "安静深刻"]

def call_api(base, key, model, messages, retries=3):
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps({"model": model, "messages": messages, "temperature": 0.9,
                         "max_tokens": 2400}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read())["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  重试 {i+1}: {e}"); time.sleep(5 * (i + 1))
    return None

def extract_json_array(text):
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        return []
    try:
        return json.loads(m.group(0))
    except Exception:
        return []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-cell", type=int, default=2, help="每个(话题×语言×基调)组合生成几组")
    ap.add_argument("--max-new", type=int, default=300, help="本次最多新增条数")
    args = ap.parse_args()

    base = os.environ.get("SYD_API_BASE", "https://api.deepseek.com")
    key = os.environ.get("SYD_API_KEY")
    model = os.environ.get("SYD_MODEL", "deepseek-chat")
    if not key:
        raise SystemExit("请先 export SYD_API_KEY=你的密钥（DeepSeek/Qwen/GLM 等 OpenAI 兼容端点均可）")

    seen = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            try:
                obj = json.loads(line)
                seen.add(hashlib.md5("".join(t["value"] for t in obj["conversations"]).encode()).hexdigest())
            except Exception:
                pass
    print(f"已有 {len(seen)} 条，目标新增 {args.max_new} 条，端点 {base} 模型 {model}")

    new = 0
    cells = list(itertools.product(TOPICS, LANGS, MOODS))
    with open(OUT, "a", encoding="utf-8") as out:
        for topic, lang, mood in cells:
            if new >= args.max_new:
                break
            task = f"〔话题〕{topic}〔语言〕{lang}〔情绪基调〕{mood}"
            text = call_api(base, key, model, [
                {"role": "system", "content": GEN_PROMPT.replace("{N}", str(args.per_cell))},
                {"role": "user", "content": task}])
            if not text:
                continue
            for ex in extract_json_array(text):
                try:
                    conv = ex["conversations"]
                    assert conv[0]["from"] == "human" and conv[-1]["from"] == "gpt"
                    h = hashlib.md5("".join(t["value"] for t in conv).encode()).hexdigest()
                    if h in seen:
                        continue
                    seen.add(h)
                    out.write(json.dumps(ex, ensure_ascii=False) + "\n"); out.flush()
                    new += 1
                except Exception:
                    continue
            print(f"{task} -> 累计新增 {new}")
    print(f"完成：本次新增 {new} 条 -> {OUT}；下一步运行 prepare_data.py 合并清洗。")

if __name__ == "__main__":
    main()
