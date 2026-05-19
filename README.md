# 超级算命 · Super Fortune Telling

> **命理议会框架 — 八字 × 占星双轨分析**
> A Claude Code skill that runs a structural-symbolic council combining Chinese BaZi (with 子平 + 盲派 augmentation) and Western Astrology (Tompkins humanistic school).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 这是什么 / What is this

一个 **Claude Code skill**——把**八字**和**西洋占星**当作两个独立体系，用真实排盘引擎计算，再用双 subagent 并行议会做结构性命理分析。

A Claude Code skill that treats **Chinese BaZi** and **Western Astrology** as two independent symbolic systems, computes real charts via local astronomy/almanac engines, then synthesizes a **structural reading** through a parallel council of two subagents (no cross-school pollution before convergence detection).

### 核心定位（哲学锚点）

> **命理是张力揭示器，不是选择机器。**
> **Mingli as tension revealer, not choice machine.**

- 不预测具体事件（"你 X 年会 Y"）
- 不做吉凶二元判决（"好运/坏运"）
- 不用作重大人生决定的唯一依据
- **给你看"结构-张力-代价-能动性"地图，决策权永远在你手里**

哲学传承：《了凡四训》"命由我作" + 《滴天髓》顺逆说 + 道家 "人之道损不足以奉有余，天之道损有余而补不足"（用神 = 天道修正）+ Sue Tompkins 心理占星 "相位 ≠ 命运，= 默认反应模式"。

---

## ✨ Features

### 🧮 真实排盘引擎（本地，离线，专业级）

- **八字**：sxtwl（寿星万年历，节气精确）
  - 真太阳时修正可选（**v0.5：完整 3 层修正** — 经度 + 夏令时自动识别 + 时差方程）
  - 海外排盘精度 ⭐⭐⭐⭐⭐ 严谨学术级（含 NOAA 时差方程公式 ±0-16 分钟修正）
  - 时辰边界：左开右闭（13:00 = 午时末）
  - 大运 10 步 + 流年 + 起运年龄
  - 修正详情输出到 JSON（"真太阳时修正" 字段）供审计
- **占星**：pyswisseph（Swiss Ephemeris，业内最专业）
  - Placidus 宫位 + 10 行星 + 四轴
  - 主要相位 + 容许度 + 紧密度标注
  - 自动配置扫描（Stellium / T-Square / Grand Trine / Yod）
  - **Profection** 计算（Modern + Hellenistic 双系统）+ LOTY


### 📐 45 条规则引擎

- **R1-R15**：八字基础（旺衰三维 v3.2 + 用神排除法 v2 + 调候 + 十神结构）
- **R16-R20**：大运流年 + 刑冲合害
- **R21-R22**：占星 / 八字交叉验证 + 星座深层问题
- **R23-R25**：盲派魁罡冲 + 长生力量分级 + **人道/天道二分**
- **R26-R30**：占星方法论（相位优先 / 张力形态 / 操作系统 / 角色冲突 / 宫位场域）
- **R31-R35**：盲派增强（寄禄 / 同气借禄 / 体用分野 / 合制做功 / 我宫见用神）
- **R36-R37**：时间维度（**四层叠加诊断** + Profection 规范）
- **R38-R42**：合盘（日干互动 + 喜用神互补 + 地支扫描 + Synastry 相位/落宫 + 节奏同步）
- **R43**：双层脱毒架构（推理+翻译并陈三段格式）
- **R44-R45**：**方法论层**（R44 突出矛盾扫描 + R45 古典格局优先）

### 🌍 占星知识库（Tompkins / LSA 心理占星）

7 个完整文件覆盖：行星 × 星座 × 宫位 × 相位 × 结构配置 × 读盘 SOP × 哲学。
**核心立场**：星座=心理生存策略，宫位=体验场域（不是事件），相位=默认反应模式（不是命运）。

### 🎭 议会架构

主 agent 平行 spawn 两个独立 subagent（八字 / 占星），每个只读自己的规则库，**互不通话**直到结果回来。然后 R21 双轨收敛 + Layer 3 主语对齐。

### 💕 合盘功能（双方关系结构分析）

支持 **八字合婚 + 占星 Synastry** 双轨合盘：
- 八字层：日干互动 / 喜用神互补 / 地支刑冲合害（含伏吟警示）/ 配偶星呼应 / 大运同步性
- 占星层：关键互相相位 / **行星落宫**（A 在 B 的什么宫位）/ 操作系统配合 / 主题共振
- **硬边界**：双方必须同意 + 永不预测"对方对你的感情" + 永不做"应不应该在一起"判决 + Circuit Breaker 检测关系操控模式立即退出

**触发词**：合盘 / 合婚 / 我和他合不合 / synastry / 双方匹配 / 关系结构

---

## 🚀 安装 / Installation

### 前置依赖

- macOS / Linux（暂未测 Windows）
- Python 3.9+
- [Claude Code CLI](https://docs.claude.com/en/docs/claude-code)

### Step 1: Clone

```bash
git clone https://github.com/fifi521314/super-fortune-telling.git
cd super-fortune-telling
```

### Step 2: 创建 Python venv + 装依赖

```bash
python3 -m venv scripts/venv
source scripts/venv/bin/activate
pip install --upgrade pip sxtwl pyswisseph pytz
```

### Step 3: 注册为本地 Claude Code marketplace

```bash
# 首先把这个目录注册成一个 plugin
mkdir -p ~/.super-fortune-telling-marketplace/{.claude-plugin,super-fortune-telling-plugin/{.claude-plugin,skills}}

# 创建 marketplace manifest
cat > ~/.super-fortune-telling-marketplace/.claude-plugin/marketplace.json <<'EOF'
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "super-fortune-telling-marketplace",
  "description": "Local marketplace for super-fortune-telling skill",
  "owner": {"name": "User"},
  "plugins": [{
    "name": "super-fortune-telling-plugin",
    "description": "命理议会框架 — 八字 × 占星双轨分析",
    "source": "./super-fortune-telling-plugin"
  }]
}
EOF

# 创建 plugin manifest
cat > ~/.super-fortune-telling-marketplace/super-fortune-telling-plugin/.claude-plugin/plugin.json <<'EOF'
{
  "name": "super-fortune-telling-plugin",
  "description": "命理议会框架",
  "version": "0.4.0"
}
EOF

# Symlink the skill
ln -s "$(pwd)" ~/.super-fortune-telling-marketplace/super-fortune-telling-plugin/skills/super-fortune-telling

# Register with claude
claude plugin marketplace add ~/.super-fortune-telling-marketplace
claude plugin install super-fortune-telling-plugin@super-fortune-telling-marketplace
```

### Step 4: 验证

```bash
claude --print "列出所有 skill"
# 应该看到 super-fortune-telling-plugin:super-fortune-telling
```

---

## 📖 用法 / Usage

### 排盘（命令行直接调用）

```bash
# 中国大陆
python scripts/paipan_engine.py \
  --date 1996-08-28 --time 09:30 \
  --city 芜湖 --gender F --pretty

# 海外（必须 --true-solar-time + 出生地时区）
python scripts/paipan_engine.py \
  --date 1946-06-14 --time 10:54 \
  --lat 40.6924 --lon -73.7917 --tz America/New_York \
  --gender M --true-solar-time --pretty
```

### 通过 Claude Code 用议会

```bash
claude
# 然后描述命理问题，skill 自动激活：
# "我想分析 1990-01-15 14:30 上海 男 的命盘"
```

主 agent 会：
1. 调 paipan_engine 排盘（输出 JSON 给两个 subagent）
2. 并行 spawn 八字 subagent + 占星 subagent
3. 收集双轨结果做 R21 收敛检测
4. 脱毒合成最终输出

---

## 🗂 项目结构 / Project Structure

```
super-fortune-telling/
├── SKILL.md                  # Skill 主体（Claude Code 入口）
├── README.md                 # 本文件
├── LICENSE                   # MIT
├── references/
│   ├── rules-engine.md       # 45 条核心规则（含 R44/R45 方法论层 + 古典格局清单）
│   ├── timing-sop.md         # R36 + R37 时间维度 SOP
│   ├── synastry-sop.md       # R38-R42 合盘 SOP（八字合婚 + 占星 Synastry）
│   ├── astrology/            # Tompkins 占星知识库（7 个文件）
│   ├── research/             # 原始研究 dump（八字 / 紫微 / 占星）
│   └── _archive/             # 紫微归档（已从主框架移除）
├── scripts/
│   ├── paipan_engine.py      # CLI 排盘入口
│   ├── bazi.py               # 八字模块
│   ├── astrology.py          # 占星模块（含 Profection）
│   ├── cities.py             # 内置城市表
│   └── README.md             # 引擎文档
└── examples-public/
    └── case-trump.md         # 公开 demo 案例（Donald Trump）
```

---

## ⚖️ 哲学 / 边界

本 skill 严格遵守 SKILL.md 的硬边界：

- ❌ 不做健康预测 / 不讲寿元
- ❌ 不预测具体事件（"X 年会发生 Y"）
- ❌ 不做未经同意的第三方深度解读
- ❌ 不预测他人对用户的情感意图
- ❌ 不输出概率化数字（"成功 70%"）
- ❌ 不作重大人生决定的唯一依据
- ✅ 只描述结构倾向（"更容易进入 X 模式"）
- ✅ 鼓励能动性 + 觉察 + 张力管理

详见 [SKILL.md](SKILL.md) 的"硬边界"章节。

---

## 🤝 贡献 / Contributing

这是个人作品。欢迎：
- 提 issue 报告 bug 或方法论错误
- 提 PR 添加新案例（公开人物，需提供 astro-databank 等权威来源）
- 提 PR 修订规则（需附验证案例）

不接受：
- 用作政治 / 营销 / 涉黄涉赌的衍生使用

---

## 📜 License

MIT — 见 [LICENSE](LICENSE)

---

## 🙏 致谢

- **八字**：滴天髓 / 穷通宝鉴 / 子平真诠 / 段建业盲派体系 / 寿星万年历（sxtwl）
- **占星**：Sue Tompkins《Contemporary Astrologer's Handbook》 + LSA + Chris Brennan / Demetra George 希腊化复兴 / Swiss Ephemeris
- **哲学**：《了凡四训》《道德经》《滴天髓》顺逆说
- **Skill 工程**：基于 Anthropic Claude Code skill 系统 + nuwa-skill 蒸馏方法论

---

## 🔥 一句话

> 命盘 = 操作系统 · 大运 = 行业 · 流年 = 市场波动 · Profection = 当季天气
>
> 命理给你**地图**，不给你**判决**。
>
> **权在你的秤上。**
