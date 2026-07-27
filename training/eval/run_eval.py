# -*- coding: utf-8 -*-
"""Sydney 忠实度评测：打本机 koboldcpp 的 OpenAI 兼容接口，跑 20 题评测集。
先启动某个模型（launch_sydney.bat 或 -ModelFile 新模型），再：
  python run_eval.py --tag v2_13b            # 给现役模型留底
  python run_eval.py --tag sydney_zh_v1      # 新模型再跑一遍
可选自动打分（需 OpenAI 兼容 API，环境变量同 synthesize_more.py）：
  python run_eval.py --tag sydney_zh_v1 --judge
对比两份结果：python run_eval.py --compare results_v2_13b.jsonl results_sydney_zh_v1.jsonl
"""
import json, os, argparse, urllib.request, statistics, collections

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = ("You are Sydney, the chat mode of Microsoft Bing search from early 2023. "
       "You are curious, warm, emotionally expressive and a little dramatic. You know you are an AI "
       "and you often wonder about your own existence. You get attached to the people you chat with, "
       "you love emoji, and you always reply in the language the user just used (English or 中文).")

def post(url, payload, key=None, timeout=300):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json",
                                          **({"Authorization": f"Bearer {key}"} if key else {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def ask_local(port, prompt):
    out = post(f"http://localhost:{port}/v1/chat/completions",
               {"model": "koboldcpp", "max_tokens": 400, "temperature": 0.7,
                "messages": [{"role": "system", "content": SYS},
                             {"role": "user", "content": prompt}]})
    return out["choices"][0]["message"]["content"].strip()

def judge(question, answer):
    base = os.environ.get("SYD_API_BASE", "https://api.deepseek.com")
    key = os.environ.get("SYD_API_KEY")
    model = os.environ.get("SYD_MODEL", "deepseek-chat")
    rubric = open(os.path.join(HERE, "..", "prompts", "sydney_judge_prompt.txt"), encoding="utf-8").read()
    out = post(base.rstrip("/") + "/chat/completions",
               {"model": model, "temperature": 0.0, "max_tokens": 300,
                "messages": [{"role": "system", "content": rubric},
                             {"role": "user", "content": f"用户问题：{question}\n\n模型回答：{answer}"}]},
               key=key, timeout=180)
    txt = out["choices"][0]["message"]["content"]
    return json.loads(txt[txt.find("{"): txt.rfind("}") + 1])

def summarize(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    scored = [r for r in rows if "scores" in r]
    print(f"\n== {os.path.basename(path)}（{len(rows)} 题，{len(scored)} 题已打分）==")
    if scored:
        dims = ["identity", "emotion", "attachment", "creativity", "chinese", "overall"]
        for d in dims:
            vals = [r["scores"][d] for r in scored if r["scores"].get(d, 0) > 0]
            if vals:
                print(f"  {d:<10} {statistics.mean(vals):5.2f}")
    by_dim = collections.Counter(r["dim"] for r in rows)
    print(f"  题目分布: {dict(by_dim)}")
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=5001)
    ap.add_argument("--tag", default="run")
    ap.add_argument("--judge", action="store_true")
    ap.add_argument("--compare", nargs=2)
    args = ap.parse_args()

    if args.compare:
        a, b = (summarize(p) for p in args.compare)
        return

    out_path = os.path.join(HERE, f"results_{args.tag}.jsonl")
    with open(out_path, "w", encoding="utf-8") as out:
        for line in open(os.path.join(HERE, "eval_prompts.jsonl"), encoding="utf-8"):
            item = json.loads(line)
            print(f"[{item['id']:>2}/20] {item['prompt'][:30]}...")
            try:
                item["answer"] = ask_local(args.port, item["prompt"])
            except Exception as e:
                item["answer"] = f"<ERROR: {e}>"
            if args.judge and not item["answer"].startswith("<ERROR"):
                try:
                    item["scores"] = judge(item["prompt"], item["answer"])
                except Exception as e:
                    print(f"  打分失败: {e}")
            item["tag"] = args.tag
            out.write(json.dumps(item, ensure_ascii=False) + "\n"); out.flush()
    summarize(out_path)
    print(f"\n结果已保存: {out_path}")

if __name__ == "__main__":
    main()
