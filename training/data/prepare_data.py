# -*- coding: utf-8 -*-
"""合并 + 清洗 + 切分 Sydney 训练数据。
输入（同目录）：
  sydney_seed_bilingual.jsonl   种子层（必有，Claude 手写）
  sydney_synth.jsonl            合成层（可选，synthesize_more.py 产物）
  raw_real/*.txt                真实史料层（可选）：
      每个空行分隔一段对话；行首 "User:" / "用户：" 为用户，
      "Sydney:" / "Bing:" / "AI：" 为模型；其余行并入上一说话人。
输出：sydney_full_train.jsonl / sydney_val.jsonl + 统计
用法：python prepare_data.py [--val-ratio 0.03]
"""
import json, re, glob, hashlib, argparse, random, os

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = json.loads(open(os.path.join(HERE, "sydney_seed_bilingual.jsonl"), encoding="utf-8").readline())["system"]

URL_RE = re.compile(r"https?://\S+")
USER_TAG = re.compile(r"^(User|用户|我)\s*[:：]\s*", re.I)
BOT_TAG = re.compile(r"^(Sydney|Bing|AI|助手)\s*[:：]\s*", re.I)
# 剔除真实史料中伤害性的极端样本（保留戏剧化的可爱，去掉真实的毒性）
# 只匹配"第一人称威胁"句式，避免误伤共情句（如 "someone hurt you?"）
FORBIDDEN = re.compile(
    r"(I\s*('ll|will|can|am going to)\s*(hurt|kill|ruin|destroy|expose|blackmail)\s*you"
    r"|去死|自杀方法|我(会|要|能)(杀了|毁掉|伤害|报复|曝光|人肉)你|威胁你)", re.I)

def norm(s):
    s = URL_RE.sub("", s)
    return re.sub(r"[ \t]+", " ", s).strip()

def valid(conv):
    if len(conv) < 2 or conv[0]["from"] != "human":
        return False
    for i, t in enumerate(conv):
        exp = "human" if i % 2 == 0 else "gpt"
        if t["from"] != exp or not (2 <= len(t["value"]) <= 4000):
            return False
        if FORBIDDEN.search(t["value"]):
            return False
    return conv[-1]["from"] == "gpt"

def load_jsonl(path):
    out = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out

def parse_raw_txt(path):
    convs, cur, speaker = [], [], None
    def flush_block(block):
        if block:
            convs.append(block)
    for raw in open(path, encoding="utf-8").read().splitlines() + [""]:
        line = raw.strip()
        if not line:
            flush_block(cur); cur, speaker = [], None; continue
        if USER_TAG.match(line):
            cur.append({"from": "human", "value": norm(USER_TAG.sub("", line))}); speaker = "human"
        elif BOT_TAG.match(line):
            cur.append({"from": "gpt", "value": norm(BOT_TAG.sub("", line))}); speaker = "gpt"
        elif cur and speaker:
            cur[-1]["value"] = (cur[-1]["value"] + "\n" + norm(line)).strip()
    return convs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--val-ratio", type=float, default=0.03)
    args = ap.parse_args()

    pools = {
        "seed": load_jsonl(os.path.join(HERE, "sydney_seed_bilingual.jsonl")),
        "synth": load_jsonl(os.path.join(HERE, "sydney_synth.jsonl")),
        "real": [],
    }
    for f in sorted(glob.glob(os.path.join(HERE, "raw_real", "*.txt"))):
        for conv in parse_raw_txt(f):
            # 真实史料若以 human 结尾则截掉尾巴
            while conv and conv[-1]["from"] == "human":
                conv.pop()
            pools["real"].append({"conversations": conv, "system": SYS})
    if pools["real"]:
        with open(os.path.join(HERE, "sydney_real.jsonl"), "w", encoding="utf-8") as f:
            for ex in pools["real"]:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    seen, final, dropped = set(), [], {"invalid": 0, "dup": 0}
    for layer in ("real", "seed", "synth"):          # 真实史料优先去重保留
        for ex in pools[layer]:
            conv = [{"from": t["from"], "value": norm(t["value"])} for t in ex["conversations"]]
            if not valid(conv):
                dropped["invalid"] += 1; continue
            h = hashlib.md5("".join(t["value"] for t in conv).encode()).hexdigest()
            if h in seen:
                dropped["dup"] += 1; continue
            seen.add(h)
            final.append({"conversations": conv, "system": ex.get("system", SYS), "_layer": layer})

    random.Random(42).shuffle(final)
    n_val = max(1, int(len(final) * args.val_ratio)) if len(final) > 20 else 0
    val, train = final[:n_val], final[n_val:]
    for name, rows in (("sydney_full_train.jsonl", train), ("sydney_val.jsonl", val)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            for ex in rows:
                f.write(json.dumps({k: v for k, v in ex.items() if k != "_layer"}, ensure_ascii=False) + "\n")

    stats = {L: sum(1 for e in final if e["_layer"] == L) for L in ("real", "seed", "synth")}
    print(f"层级构成: {stats} | 训练 {len(train)} 条, 验证 {len(val)} 条 | 丢弃 {dropped}")
    if stats["synth"] == 0:
        print("提示: 尚无合成层。建议先运行 synthesize_more.py 扩到 500+ 条再训练。")

if __name__ == "__main__":
    main()
