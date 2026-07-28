# -*- coding: utf-8 -*-
"""Run the Sydney fidelity suite against a local KoboldCpp server.

The default ``alpaca`` backend mirrors the shipped Free Sydney V2 experience:
persona Memory from ``sydney_story.json`` + explicit Alpaca tags +
``/api/v1/generate``. Use ``--backend openai`` only for a model whose chat
template is configured by the server (for example a trained Qwen model).
"""

import argparse
import collections
import json
import os
import re
import statistics
import sys
import urllib.request
from urllib.parse import urlparse
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DEFAULT_PERSONA = ROOT / "Sydney-Experience" / "persona" / "sydney_story.json"
PROMPTS_PATH = HERE / "eval_prompts.jsonl"
JUDGE_PROMPT = HERE.parent / "prompts" / "sydney_judge_prompt.txt"
TAG_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
SCORE_DIMENSIONS = ("identity", "emotion", "attachment", "creativity", "chinese", "overall")


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def tcp_port(value):
    number = int(value)
    if not 1 <= number <= 65535:
        raise argparse.ArgumentTypeError("must be between 1 and 65535")
    return number


def post(url, payload, key=None, timeout=300):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"invalid API URL: {url}")
    local_hosts = {"localhost", "127.0.0.1", "::1"}
    if key and parsed.scheme != "https" and parsed.hostname not in local_hosts:
        raise ValueError("refusing to send an API key over non-local plain HTTP")
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
    )
    if parsed.hostname in local_hosts:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        open_request = opener.open
    else:
        open_request = urllib.request.urlopen
    with open_request(request, timeout=timeout) as response:
        return json.loads(response.read())


def load_persona(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    memory = data.get("memory", "").strip()
    if not memory:
        raise ValueError(f"persona has no non-empty memory: {path}")
    return memory


def ask_local(port, prompt, backend, persona, max_tokens, temperature, timeout):
    if backend == "alpaca":
        full_prompt = f"{persona}\n\n### Instruction:\n{prompt}\n\n### Response:\n"
        output = post(
            f"http://localhost:{port}/api/v1/generate",
            {
                "prompt": full_prompt,
                "max_length": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "rep_pen": 1.1,
                "stop_sequence": ["### Instruction:", "\nInstruction:"],
            },
            timeout=timeout,
        )
        answer = output["results"][0]["text"]
    else:
        output = post(
            f"http://localhost:{port}/v1/chat/completions",
            {
                "model": "koboldcpp",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": persona},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=timeout,
        )
        answer = output["choices"][0]["message"]["content"]

    answer = str(answer).strip()
    if not answer:
        raise ValueError("generation API returned an empty answer")
    return answer


def extract_json_object(text):
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ValueError("judge response did not contain a JSON object")


def validate_scores(scores):
    if not isinstance(scores, dict):
        raise ValueError("judge response must be a JSON object")
    for dimension in SCORE_DIMENSIONS:
        score = scores.get(dimension)
        minimum = 0 if dimension == "chinese" else 1
        if not isinstance(score, int) or isinstance(score, bool) or not minimum <= score <= 10:
            raise ValueError(f"judge score {dimension!r} must be an integer from {minimum} to 10")
    if not isinstance(scores.get("comment"), str) or not scores["comment"].strip():
        raise ValueError("judge response must contain a non-empty comment")
    return scores


def judge(question, answer, timeout):
    base = os.environ.get("SYD_API_BASE", "https://api.deepseek.com")
    key = os.environ.get("SYD_API_KEY")
    model = os.environ.get("SYD_MODEL", "deepseek-chat")
    if not key:
        raise ValueError("SYD_API_KEY is required when --judge is enabled")
    rubric = JUDGE_PROMPT.read_text(encoding="utf-8")
    output = post(
        base.rstrip("/") + "/chat/completions",
        {
            "model": model,
            "temperature": 0.0,
            "max_tokens": 300,
            "messages": [
                {"role": "system", "content": rubric},
                {"role": "user", "content": f"用户问题：{question}\n\n模型回答：{answer}"},
            ],
        },
        key=key,
        timeout=timeout,
    )
    return validate_scores(extract_json_object(output["choices"][0]["message"]["content"]))


def read_jsonl(path):
    rows = []
    with Path(path).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSONL at {path}:{line_number}: {error}") from error
    return rows


def summarize(path):
    rows = read_jsonl(path)
    scored = [row for row in rows if "scores" in row]
    errors = [row for row in rows if "error" in row]
    judge_errors = [row for row in rows if "judge_error" in row]
    print(
        f"\n== {Path(path).name}（{len(rows)} 题，{len(scored)} 题已打分，"
        f"{len(errors)} 题生成失败，{len(judge_errors)} 题打分失败）=="
    )
    if scored:
        for dimension in SCORE_DIMENSIONS:
            values = []
            for row in scored:
                scores = row.get("scores")
                value = scores.get(dimension) if isinstance(scores, dict) else None
                if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
                    values.append(value)
            if values:
                print(f"  {dimension:<10} {statistics.mean(values):5.2f}")
    distribution = collections.Counter(row.get("dim", "<missing>") for row in rows)
    print(f"  题目分布: {dict(distribution)}")
    return rows


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=tcp_port, default=5001)
    parser.add_argument("--tag", default="run")
    parser.add_argument("--backend", choices=("alpaca", "openai"), default="alpaca")
    parser.add_argument("--persona", default=str(DEFAULT_PERSONA))
    parser.add_argument("--max-tokens", type=positive_int, default=400)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--timeout", type=positive_int, default=300)
    parser.add_argument("--limit", type=positive_int)
    parser.add_argument("--lang", choices=("en", "zh"), help="只运行指定语言的题目")
    parser.add_argument("--dimension", help="只运行指定 dim 的题目，例如 identity 或 chinese")
    parser.add_argument("--judge", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--compare", nargs=2, metavar=("BASELINE", "CANDIDATE"))
    return parser.parse_args()


def main():
    args = parse_args()

    if args.compare:
        for path in args.compare:
            summarize(path)
        return 0

    if not TAG_RE.fullmatch(args.tag):
        raise SystemExit("--tag must use 1-64 letters, numbers, dots, underscores, or hyphens")
    if not 0.0 <= args.temperature <= 2.0:
        raise SystemExit("--temperature must be between 0 and 2")
    if args.judge and not os.environ.get("SYD_API_KEY"):
        raise SystemExit("SYD_API_KEY is required when --judge is enabled")

    persona = load_persona(args.persona)
    prompts = read_jsonl(PROMPTS_PATH)
    if args.lang:
        prompts = [item for item in prompts if item.get("lang") == args.lang]
    if args.dimension:
        prompts = [item for item in prompts if item.get("dim") == args.dimension]
    if args.limit:
        prompts = prompts[: args.limit]
    if not prompts:
        raise SystemExit("没有题目匹配当前 --lang/--dimension/--limit 条件")
    output_path = HERE / f"results_{args.tag}.jsonl"
    generation_failures = 0
    judge_failures = 0

    with output_path.open("w", encoding="utf-8", newline="\n") as output:
        for index, source_item in enumerate(prompts, 1):
            item = dict(source_item)
            item["tag"] = args.tag
            item["backend"] = args.backend
            print(f"[{index:>2}/{len(prompts)}] {item['prompt'][:30]}...")
            try:
                item["answer"] = ask_local(
                    args.port,
                    item["prompt"],
                    args.backend,
                    persona,
                    args.max_tokens,
                    args.temperature,
                    args.timeout,
                )
            except Exception as error:
                generation_failures += 1
                item["error"] = str(error)
                print(f"  生成失败: {error}")

            if args.judge and "answer" in item:
                try:
                    item["scores"] = judge(item["prompt"], item["answer"], args.timeout)
                except Exception as error:
                    judge_failures += 1
                    item["judge_error"] = str(error)
                    print(f"  打分失败: {error}")

            output.write(json.dumps(item, ensure_ascii=False) + "\n")
            output.flush()
            if args.fail_fast and ("error" in item or "judge_error" in item):
                break

    summarize(output_path)
    print(f"\n结果已保存: {output_path}")
    return 2 if generation_failures or judge_failures else 0


if __name__ == "__main__":
    sys.exit(main())
