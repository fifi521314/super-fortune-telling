# Scripts · 排盘引擎

## paipan_engine.py

双轨排盘引擎：**八字（子平+盲派增强）+ 西洋占星（Tompkins 心理占星）**。

### 依赖

- Python 3.9+
- `sxtwl`（八字真太阳时、四柱、节气）
- `pyswisseph`（Swiss Ephemeris，占星天文计算）
- `pytz`（时区处理）

依赖已装在 `scripts/venv/`。激活：`source scripts/venv/bin/activate`

### 用法

**方式 A · 内置城市**：
```bash
python scripts/paipan_engine.py \
  --date 1996-08-28 --time 09:30 \
  --city 芜湖 \
  --gender F \
  --pretty
```

**方式 B · 手动指定经纬度时区**：
```bash
python scripts/paipan_engine.py \
  --date 1996-08-28 --time 09:30 \
  --lat 31.3526 --lon 118.4331 --tz Asia/Shanghai \
  --gender F
```

**选项**：
- `--true-solar-time`：八字启用真太阳时修正（默认不启用）
- `--bazi-only`：仅输出八字
- `--astrology-only`：仅输出占星
- `--pretty`：格式化 JSON

### 输出格式

```json
{
  "input": { "date", "time", "city", "lat", "lon", "tz", "gender", ... },
  "bazi": {
    "pillars": { "年", "月", "日", "时" },
    "day_master": "丁",
    "day_master_wuxing": "火",
    "day_master_yinyang": "阴",
    "天干十神": { ... },
    "地支藏干": { ... },
    "地支十神": { ... },
    "日元十二长生位": { ... },
    "大运": {
      "排列方向": "顺排|逆排",
      "起运年龄": 7.0,
      "起运日期": "...",
      "pillars": [ {"序号", "大运", "十神(天干)", "起始年份", ...} × 10 ]
    },
    "流年": { "year", "pillar", "干十神" }
  },
  "astrology": {
    "planets": { "Sun", "Moon", "Mercury", ... × 10 } // 每颗含 sign_zh, sign_degree, house, retrograde
    "angles": { "ASC", "MC", "IC", "DSC" },
    "house_cusps": { "1", "2", ..., "12" },
    "aspects": [ {"planet1", "planet2", "type", "type_zh", "orb", "actual"} ],
    "configurations": [ {"type": "Stellium|T-Square|Grand Trine|Yod", ...} ]
  }
}
```

---

## 在 Skill 中的调用

八字 subagent / 占星 subagent 可以用 Bash 工具直接调用：

```python
result = subprocess.run([
    "python", "scripts/paipan_engine.py",
    "--date", birth_date, "--time", birth_time,
    "--city", city, "--gender", gender,
], capture_output=True, text=True)
data = json.loads(result.stdout)
```

---

## 已验证案例

6 案例八字四柱 **100% 正确**：

| Case | 四柱 | 状态 |
|---|---|---|
| 001 | 丙子 丙申 丁酉 乙巳 | ✅ |
| 002 | 己亥 癸酉 癸亥 戊午 | ✅ |
| 003 | 丙子 甲午 戊戌 庚申 | ✅ |
| 004 | 丁丑 丙午 辛丑 戊子 | ✅ |
| 005 | 庚辰 庚辰 戊戌 乙卯 | ✅ |
| 006 | 戊辰 戊午 丙午 戊戌 | ✅ |

占星部分每案例都识别出行星、相位、配置；对精确出生地的案例（001/003/004/006）宫位匹配度高；对出生地标注"待确认"的 Case 005，建议用精确坐标重算。

---

## 技术决策

### 真太阳时修正默认**关闭**（中国大陆案例）

理由：
- 现代用户输入的时间通常是**当地标准时间**（e.g., 北京时间 19:02）
- 多数传统八字师傅不做真太阳时修正
- 若原数据已经过真太阳时修正（如某些专业软件输出），再修正会错
- 需要时可用 `--true-solar-time` 开启

### 🌍 海外 / 跨时区案例的硬约定

**`--time` 必须是"出生地当地时间"**——不是北京时间、不是 UTC。

**`--tz` 必须是"出生地时区"**（`America/Los_Angeles` / `Europe/London` / `Asia/Tokyo` / `Asia/Dubai` 等）。

海外名人例 · Steve Jobs（1955-02-24 07:15 San Francisco 男）：
```bash
python scripts/paipan_engine.py \
  --date 1955-02-24 --time 07:15 \
  --city 旧金山 --gender M \
  --true-solar-time
```

**为什么海外特别需要 `--true-solar-time`**（真太阳时修正）：

| 出生地 | 经度 | 时区中心 | 偏差（分钟）|
|---|---|---|---|
| 旧金山 | -122.42° | -120° (PST) | **-9.7** |
| 纽约 | -74.00° | -75° (EST) | +4.0 |
| 伦敦 | -0.13° | 0° (GMT) | -0.5（几乎忽略）|
| 迪拜 | +55.27° | +60° (GST) | **-18.9** |
| 东京 | +139.65° | +135° (JST) | +18.6 |

偏差分钟会影响**时辰归属**——07:00、09:00、13:00、19:00 这类边界附近尤甚。海外未修正可能得到错误的时柱。

**夏令时（DST）**：pytz 自动处理历史 DST 规则（包括 1950s 起的美国 DST 历史数据）。

**时区中心经度怎么推导**：paipan 内部从 pytz 的 UTC offset 算（UTC+8 → 120°、UTC-5 → -75°、UTC+0 → 0°），不需要用户手填。

**关键提醒**：
- 公众人物的生辰数据若来自 astro.com 或 astro-databank，注意确认是**出生地当地时间**还是已转 UTC
- 中国大陆八字没有真太阳时修正是主流；海外排盘**必须修正**才符合传统

### 时辰边界：左开右闭（Convention B）

- 午时：11:00-13:00（**包含 13:00 整点**）
- 未时：13:01-15:00
- 戌时：19:01-21:00
- 奇数整点归上一时辰（除 23:00 特殊归子时）

理由：与多数中文八字软件一致（Case 002 的 13:00 → 午时 戊午 能正确匹配）。

### 占星默认 Placidus 宫位

Whole Sign 作为对照体系可后续扩展。

---

## 维护提醒

- 依赖版本锁定在 `scripts/venv/` 中
- `scripts/cities.py` 内置 50+ 城市；扩展新城市直接编辑该文件
- 若要支持新的占星相位（如七分相 51.4°）修改 `astrology.py` 的 `ASPECTS` 列表
- 若要支持其他排盘体系（紫微、七政四余等），另起 module，不改本引擎
