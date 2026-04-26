"""
占星排盘模块 — 基于 Swiss Ephemeris（pyswisseph）

计算：
- 10 行星的星座 + 度数 + 是否逆行
- 上升（ASC）+ MC + IC + DSC
- 宫位（Placidus 默认；Whole Sign 可选）
- 主要相位（合/对冲/刑/拱/六合 + 梅花）+ 容许度
- 配置扫描（Stellium / T-Square / Grand Trine / Kite / Yod）
"""

import swisseph as swe
import pytz
from datetime import datetime


# ============================================
# 基础常量
# ============================================

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGNS_ZH = ["白羊", "金牛", "双子", "巨蟹", "狮子", "处女",
            "天秤", "天蝎", "射手", "摩羯", "水瓶", "双鱼"]

PLANET_CODES = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}

PLANET_ZH = {
    "Sun": "太阳", "Moon": "月亮", "Mercury": "水星", "Venus": "金星",
    "Mars": "火星", "Jupiter": "木星", "Saturn": "土星",
    "Uranus": "天王", "Neptune": "海王", "Pluto": "冥王",
}

# 主要相位（容许度）
ASPECTS = [
    ("conjunction", 0, 8),      # 合相 0° (容许 8°)
    ("opposition", 180, 8),     # 对冲 180°
    ("square", 90, 8),          # 刑 90°
    ("trine", 120, 6),          # 三分 120° (六分容许略小)
    ("sextile", 60, 4),         # 六合 60°
    ("quincunx", 150, 3),       # 梅花 150°
]
ASPECT_ZH = {
    "conjunction": "合", "opposition": "冲",
    "square": "刑", "trine": "拱", "sextile": "六合", "quincunx": "梅花",
}


# ============================================
# 核心计算
# ============================================

def to_julian_day(year, month, day, hour, minute, timezone_name):
    """
    把本地时间转 Julian Day（UTC 基准）。
    """
    tz = pytz.timezone(timezone_name)
    local_dt = tz.localize(datetime(year, month, day, hour, minute))
    utc_dt = local_dt.astimezone(pytz.UTC)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                     utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0)
    return jd


def degree_to_sign(degree):
    """把 0-360° 转为 (星座名, 星座内度数 0-30°)"""
    degree = degree % 360
    sign_idx = int(degree // 30)
    sign_degree = degree % 30
    return SIGNS[sign_idx], SIGNS_ZH[sign_idx], round(sign_degree, 2)


def calc_planet(jd, planet_code, planet_name):
    """计算某颗行星在 JD 的位置"""
    # swe.calc_ut 返回 (longitude, latitude, distance, speed_long, speed_lat, speed_dist)
    result = swe.calc_ut(jd, planet_code)
    pos = result[0]
    longitude = pos[0]
    speed = pos[3]
    retrograde = speed < 0

    sign_en, sign_zh, sign_deg = degree_to_sign(longitude)

    return {
        "name_en": planet_name,
        "name_zh": PLANET_ZH[planet_name],
        "longitude": round(longitude, 4),
        "sign": sign_en,
        "sign_zh": sign_zh,
        "sign_degree": sign_deg,
        "retrograde": retrograde,
    }


def calc_houses(jd, lat, lon, system=b'P'):
    """
    计算宫位和四轴（ASC, MC, IC, DSC）。
    system: b'P' = Placidus (默认); b'W' = Whole Sign
    """
    houses, angles = swe.houses(jd, lat, lon, system)
    # houses: 12 个宫头黄经（从 1 宫起）
    # angles: [ASC, MC, ARMC, Vertex, ...] — angles[0]=ASC, angles[1]=MC

    asc_lon = angles[0]
    mc_lon = angles[1]
    ic_lon = (mc_lon + 180) % 360
    dsc_lon = (asc_lon + 180) % 360

    house_cusps = {}
    for i, cusp in enumerate(houses, start=1):
        sign_en, sign_zh, sign_deg = degree_to_sign(cusp)
        house_cusps[i] = {
            "longitude": round(cusp, 4),
            "sign": sign_en,
            "sign_zh": sign_zh,
            "sign_degree": sign_deg,
        }

    def _angle(lon):
        sign_en, sign_zh, sign_deg = degree_to_sign(lon)
        return {"longitude": round(lon, 4), "sign": sign_en, "sign_zh": sign_zh, "sign_degree": sign_deg}

    return {
        "house_cusps": house_cusps,
        "ASC": _angle(asc_lon),
        "MC": _angle(mc_lon),
        "IC": _angle(ic_lon),
        "DSC": _angle(dsc_lon),
    }


def planet_house(planet_lon, house_cusps):
    """判断行星落在哪一宫（Placidus）"""
    cusps = [house_cusps[i]["longitude"] for i in range(1, 13)]
    # 规则：宫 i = [cusp_i, cusp_{i+1})，需处理跨 0° 情况
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        if start < end:
            if start <= planet_lon < end:
                return i + 1
        else:
            # 跨 360°
            if planet_lon >= start or planet_lon < end:
                return i + 1
    return None


def detect_aspects(planets):
    """
    扫描所有行星 pair 之间的相位。
    planets: list of {"name_en", "longitude", ...}
    """
    aspects = []
    names = list(planets.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1_name, p2_name = names[i], names[j]
            p1 = planets[p1_name]
            p2 = planets[p2_name]
            diff = abs(p1["longitude"] - p2["longitude"])
            if diff > 180:
                diff = 360 - diff

            for asp_name, asp_angle, asp_orb in ASPECTS:
                if abs(diff - asp_angle) <= asp_orb:
                    aspects.append({
                        "planet1": p1_name,
                        "planet2": p2_name,
                        "type": asp_name,
                        "type_zh": ASPECT_ZH[asp_name],
                        "angle": asp_angle,
                        "orb": round(abs(diff - asp_angle), 2),
                        "actual": round(diff, 2),
                    })
                    break  # 一对行星只保留一种相位（按优先级）
    return aspects


def detect_configurations(planets, aspects):
    """
    检测结构配置：T-Square / Grand Trine / Stellium / Kite / Yod。
    """
    configs = []

    # Stellium：3+ 行星在同一星座
    sign_groups = {}
    for name, p in planets.items():
        sign_groups.setdefault(p["sign"], []).append(name)
    for sign, members in sign_groups.items():
        if len(members) >= 3:
            configs.append({
                "type": "Stellium",
                "sign": sign,
                "sign_zh": SIGNS_ZH[SIGNS.index(sign)],
                "planets": members,
                "count": len(members),
            })

    # T-Square / Grand Trine / Kite / Yod 需要基于 aspects 图检测
    # 简化：先实现 T-Square 和 Grand Trine

    # Build aspect lookup
    asp_map = {}
    for a in aspects:
        key = tuple(sorted([a["planet1"], a["planet2"]]))
        asp_map[key] = a["type"]

    names = list(planets.keys())
    n = len(names)

    # T-Square: A-B opposition, C-A square, C-B square
    for i in range(n):
        for j in range(i + 1, n):
            a, b = names[i], names[j]
            if asp_map.get(tuple(sorted([a, b]))) == "opposition":
                for c in names:
                    if c in (a, b):
                        continue
                    if (asp_map.get(tuple(sorted([a, c]))) == "square"
                        and asp_map.get(tuple(sorted([b, c]))) == "square"):
                        configs.append({
                            "type": "T-Square",
                            "apex": c,
                            "opposition_pair": [a, b],
                        })

    # Grand Trine: A-B trine, B-C trine, C-A trine
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                a, b, c = names[i], names[j], names[k]
                if (asp_map.get(tuple(sorted([a, b]))) == "trine"
                    and asp_map.get(tuple(sorted([b, c]))) == "trine"
                    and asp_map.get(tuple(sorted([a, c]))) == "trine"):
                    configs.append({
                        "type": "Grand Trine",
                        "planets": [a, b, c],
                    })

    # Yod: A-B sextile, A-C quincunx, B-C quincunx
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(n):
                if k in (i, j):
                    continue
                a, b, c = names[i], names[j], names[k]
                if (asp_map.get(tuple(sorted([a, b]))) == "sextile"
                    and asp_map.get(tuple(sorted([a, c]))) == "quincunx"
                    and asp_map.get(tuple(sorted([b, c]))) == "quincunx"):
                    # 避免重复（同一 yod 可能被 i,j 反向找到）
                    existing = any(
                        set(conf.get("sextile_pair", [])) == {a, b} and conf.get("apex") == c
                        for conf in configs if conf["type"] == "Yod"
                    )
                    if not existing:
                        configs.append({
                            "type": "Yod",
                            "apex": c,
                            "sextile_pair": [a, b],
                        })

    return configs


# ============================================
# Profection（希腊化年运）
# ============================================

# 传统守护星（Hellenistic rulerships）— 用于 LOTY 计算
TRADITIONAL_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# 12 宫主题
HOUSE_THEMES_ZH = {
    1: "自我 · 身份 · 外貌",
    2: "资源 · 价值 · 现金流",
    3: "沟通 · 学习 · 兄弟姐妹 · 短程",
    4: "家 · 根 · 情绪底盘 · 母亲",
    5: "创造 · 爱 · 子女 · 游戏",
    6: "日常 · 工作 · 身体 · 服务",
    7: "关系 · 伴侣 · 合作 · 敌手",
    8: "共享资源 · 性 · 死亡 · 转化",
    9: "信念 · 远方 · 高等教育 · 哲学",
    10: "事业 · 社会角色 · 父亲 · 权威",
    11: "社群 · 朋友 · 理想 · 未来",
    12: "潜意识 · 幕后 · 终结 · 灵性",
}


def calculate_profection(birth_year, birth_month, birth_day,
                         target_year=None, target_month=None, target_day=None,
                         house_cusps=None, planets=None):
    """
    计算 Profection（希腊化年运）。两种并存：
    - **Modern**：house = (completed_age % 12) + 1（age 0 → 1H）
    - **Hellenistic / Life Year**：life_year = completed_age + 1；house = ((life_year - 1) % 12) + 1
      LY1 (age 0-1) → 1H, LY13 (age 12) → 1H (第二轮)

    主流 Hellenistic 复兴派（Brennan, Demetra George）用 Life Year 系统。

    LOTY = 激活宫宫头星座的传统守护星。

    Args:
        birth_year/month/day: 出生日期
        target_year/month/day: 目标日期（默认 today）
        house_cusps: calc_houses() 的 house_cusps 字典
        planets: calc_planet() 的 planets 字典

    Returns:
        dict: 两种系统的 profection 信息
    """
    from datetime import date
    if target_year is None:
        today = date.today()
        target_year, target_month, target_day = today.year, today.month, today.day

    # 完整年龄（生日为边界）
    age = target_year - birth_year
    if (target_month, target_day) < (birth_month, birth_day):
        age -= 1

    # 两套系统
    modern_house = (age % 12) + 1
    life_year = age + 1
    hellenistic_house = ((life_year - 1) % 12) + 1  # LY1 → 1H

    def _house_info(house_num):
        info = {
            "house_num": house_num,
            "house_theme": HOUSE_THEMES_ZH[house_num],
        }
        if house_cusps and planets:
            cusp = house_cusps[house_num]
            sign = cusp["sign"]
            sign_zh = cusp["sign_zh"]
            loty_name = TRADITIONAL_RULERS[sign]
            loty_planet = planets[loty_name]
            info.update({
                "sign_on_cusp": sign,
                "sign_on_cusp_zh": sign_zh,
                "loty": loty_name,
                "loty_zh": PLANET_ZH[loty_name],
                "loty_natal_sign": loty_planet["sign_zh"],
                "loty_natal_degree": loty_planet["sign_degree"],
                "loty_natal_house": loty_planet["house"],
                "loty_retrograde": loty_planet["retrograde"],
            })
        return info

    return {
        "age_at_target": age,
        "life_year": life_year,
        "target_date": f"{target_year:04d}-{target_month:02d}-{target_day:02d}",
        "modern": _house_info(modern_house),
        "hellenistic": _house_info(hellenistic_house),
        "_note": "Modern: (age % 12) + 1 · Hellenistic (Brennan / Demetra George): Life Year = age + 1, house = ((LY - 1) % 12) + 1。两者结果在某些年一致，跨生日时会不同",
    }


# ============================================
# 主函数
# ============================================

def calculate_astrology(year, month, day, hour, minute, lat, lon, timezone_name):
    """
    计算完整本命盘。
    """
    jd = to_julian_day(year, month, day, hour, minute, timezone_name)

    # 10 行星
    planets = {}
    for name, code in PLANET_CODES.items():
        planets[name] = calc_planet(jd, code, name)

    # 宫位 + 四轴
    houses_data = calc_houses(jd, lat, lon)
    house_cusps = houses_data["house_cusps"]

    # 给每颗行星标记落宫
    for name, p in planets.items():
        p["house"] = planet_house(p["longitude"], house_cusps)

    # 相位
    aspects = detect_aspects(planets)

    # 配置
    configurations = detect_configurations(planets, aspects)

    # 当前 Profection（默认）
    profection_current = calculate_profection(
        year, month, day,
        house_cusps=house_cusps, planets=planets,
    )

    return {
        "planets": planets,
        "angles": {
            "ASC": houses_data["ASC"],
            "MC": houses_data["MC"],
            "IC": houses_data["IC"],
            "DSC": houses_data["DSC"],
        },
        "house_cusps": house_cusps,
        "aspects": aspects,
        "configurations": configurations,
        "profection_current_year": profection_current,
    }


if __name__ == "__main__":
    # 自测试：Case 001
    print("Case 001 · 1996-08-28 09:30 F 芜湖")
    print("=" * 60)
    result = calculate_astrology(1996, 8, 28, 9, 30, 31.3526, 118.4331, "Asia/Shanghai")

    print("\n行星：")
    for name, p in result["planets"].items():
        r = "(R)" if p["retrograde"] else ""
        print(f"  {p['name_zh']:4} {p['sign_zh']:3} {p['sign_degree']:>6.2f}°  H{p['house']}  {r}")

    print("\n四轴：")
    for ax_name, ax in result["angles"].items():
        print(f"  {ax_name:4} {ax['sign_zh']} {ax['sign_degree']}°")

    print(f"\n相位（{len(result['aspects'])} 条）：")
    for a in result["aspects"]:
        print(f"  {PLANET_ZH[a['planet1']]:4} {a['type_zh']:2} {PLANET_ZH[a['planet2']]:4}  orb {a['orb']:>5.2f}°")

    print(f"\n结构配置（{len(result['configurations'])} 个）：")
    for c in result["configurations"]:
        print(f"  {c}")
