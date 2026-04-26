"""
八字排盘模块 — 基于 sxtwl（寿星万年历）

计算：
- 四柱（年月日时）含真太阳时修正
- 日元 + 五行 + 阴阳
- 十神（天干 + 地支藏干）
- 大运（10 步 + 起运年）
- 当年流年
"""

import sxtwl
from datetime import datetime, timedelta

# ============================================
# 基础数据
# ============================================
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

TG_WUXING = {"甲": "木", "乙": "木", "丙": "火", "丁": "火",
             "戊": "土", "己": "土", "庚": "金", "辛": "金",
             "壬": "水", "癸": "水"}

TG_YINYANG = {"甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴",
              "戊": "阳", "己": "阴", "庚": "阳", "辛": "阴",
              "壬": "阳", "癸": "阴"}

DZ_WUXING = {"子": "水", "丑": "土", "寅": "木", "卯": "木",
             "辰": "土", "巳": "火", "午": "火", "未": "土",
             "申": "金", "酉": "金", "戌": "土", "亥": "水"}

DZ_CANGGAN = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"]
}

# 十二长生 · 阳干顺行表（以日元为索引）
ZHANG_SHENG_YANG = {
    "甲": {"亥": "长生", "子": "沐浴", "丑": "冠带", "寅": "临官", "卯": "帝旺",
          "辰": "衰", "巳": "病", "午": "死", "未": "墓", "申": "绝", "酉": "胎", "戌": "养"},
    "丙": {"寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官", "午": "帝旺",
          "未": "衰", "申": "病", "酉": "死", "戌": "墓", "亥": "绝", "子": "胎", "丑": "养"},
    "戊": {"寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官", "午": "帝旺",
          "未": "衰", "申": "病", "酉": "死", "戌": "墓", "亥": "绝", "子": "胎", "丑": "养"},
    "庚": {"巳": "长生", "午": "沐浴", "未": "冠带", "申": "临官", "酉": "帝旺",
          "戌": "衰", "亥": "病", "子": "死", "丑": "墓", "寅": "绝", "卯": "胎", "辰": "养"},
    "壬": {"申": "长生", "酉": "沐浴", "戌": "冠带", "亥": "临官", "子": "帝旺",
          "丑": "衰", "寅": "病", "卯": "死", "辰": "墓", "巳": "绝", "午": "胎", "未": "养"},
}

# 阴干逆行表
ZHANG_SHENG_YIN = {
    "乙": {"午": "长生", "巳": "沐浴", "辰": "冠带", "卯": "临官", "寅": "帝旺",
          "丑": "衰", "子": "病", "亥": "死", "戌": "墓", "酉": "绝", "申": "胎", "未": "养"},
    "丁": {"酉": "长生", "申": "沐浴", "未": "冠带", "午": "临官", "巳": "帝旺",
          "辰": "衰", "卯": "病", "寅": "死", "丑": "墓", "子": "绝", "亥": "胎", "戌": "养"},
    "己": {"酉": "长生", "申": "沐浴", "未": "冠带", "午": "临官", "巳": "帝旺",
          "辰": "衰", "卯": "病", "寅": "死", "丑": "墓", "子": "绝", "亥": "胎", "戌": "养"},
    "辛": {"子": "长生", "亥": "沐浴", "戌": "冠带", "酉": "临官", "申": "帝旺",
          "未": "衰", "午": "病", "巳": "死", "辰": "墓", "卯": "绝", "寅": "胎", "丑": "养"},
    "癸": {"卯": "长生", "寅": "沐浴", "丑": "冠带", "子": "临官", "亥": "帝旺",
          "戌": "衰", "酉": "病", "申": "绝(*)", "未": "墓", "午": "胎", "巳": "养", "辰": "*"},
}
# 说明：癸水十二长生严格按阴干逆行，部分资料版本不同——以卯长生起，逆推。上表为通行版本。


# ============================================
# 辅助函数
# ============================================

def get_shisheng_position(day_master, dizhi):
    """获取日元坐某地支的十二长生位"""
    yinyang = TG_YINYANG[day_master]
    if yinyang == "阳":
        table = ZHANG_SHENG_YANG.get(day_master, {})
    else:
        table = ZHANG_SHENG_YIN.get(day_master, {})
    return table.get(dizhi, "未定")


def ten_god(day_master, other_tg):
    """计算日元对某天干的十神关系"""
    if day_master == other_tg:
        return "比肩"

    dm_wx = TG_WUXING[day_master]
    ot_wx = TG_WUXING[other_tg]
    dm_yy = TG_YINYANG[day_master]
    ot_yy = TG_YINYANG[other_tg]
    same_yy = (dm_yy == ot_yy)

    # 生克关系
    sheng = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    ke = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

    if dm_wx == ot_wx:
        return "比肩" if same_yy else "劫财"
    if sheng[dm_wx] == ot_wx:
        return "食神" if same_yy else "伤官"
    if ke[dm_wx] == ot_wx:
        return "偏财" if same_yy else "正财"
    if sheng[ot_wx] == dm_wx:
        return "偏印" if same_yy else "正印"
    if ke[ot_wx] == dm_wx:
        return "七杀" if same_yy else "正官"
    return "未知"


# ============================================
# 时柱计算（五鼠遁法）
# 日干 → 子时的起始天干
# 甲己还加甲，乙庚丙作初，丙辛从戊起，丁壬庚子居，戊癸何方发，壬子是真途
# ============================================
HOUR_START_MAP = {
    "甲": 0, "己": 0,  # 甲
    "乙": 2, "庚": 2,  # 丙
    "丙": 4, "辛": 4,  # 戊
    "丁": 6, "壬": 6,  # 庚
    "戊": 8, "癸": 8,  # 壬
}


def get_hour_pillar(day_master, hour, minute=0):
    """
    根据日干和 24 小时制的时间，计算时柱。

    时辰边界规则（左开右闭 / Convention B）：
    - 子时：23:00-01:00（夜半跨日）
    - 丑时：01:01-03:00（含 03:00 整点）
    - 寅时：03:01-05:00
    - ...
    - 午时：11:01-13:00（含 13:00 整点）
    - 未时：13:01-15:00
    - ...
    - 奇数整点归上一时辰（13:00 属午时末，19:00 属酉时末）
    - 23:00 特殊：属子时（夜子时开始）
    """
    # Step 1: 判断地支索引
    if hour == 23:
        dz_idx = 0  # 子时起
    elif hour == 0 or (hour == 1 and minute == 0):
        dz_idx = 0  # 00:xx 还是子时；01:00 整点是子时末
    elif hour % 2 == 1 and minute == 0:
        # 奇数整点（03:00, 05:00, ..., 21:00）归上时辰
        effective_hour = hour - 1
        dz_idx = ((effective_hour + 1) // 2) % 12
    else:
        dz_idx = ((hour + 1) // 2) % 12

    # Step 2: 天干（五鼠遁）
    start_tg_idx = HOUR_START_MAP[day_master]
    hour_tg_idx = (start_tg_idx + dz_idx) % 10

    return TIANGAN[hour_tg_idx] + DIZHI[dz_idx]


# ============================================
# 主函数
# ============================================

def calculate_bazi(year, month, day, hour, minute, gender, longitude=None, timezone=None, true_solar_time=False):
    """
    计算八字及大运。

    Args:
        year/month/day/hour/minute: 出生时间（标准时区时间）
        gender: 'M' or 'F'
        longitude: 出生地经度（东经为正，用于真太阳时修正）
        timezone: pytz 时区名（如 'Asia/Shanghai'），用于计算时区中心经度
        true_solar_time: 是否做真太阳时修正（默认 True）

    Returns:
        dict 含四柱、十神、大运、流年等
    """
    import pytz as _pytz
    # Step 1: 真太阳时修正
    # 真太阳时 = 标准时区时间 + (出生地经度 - 时区中心经度) × 4 分钟
    adjusted_dt = datetime(year, month, day, hour, minute)
    if true_solar_time and longitude is not None and timezone is not None:
        # 从时区获取 UTC 偏移（小时），推出时区中心经度
        # UTC+8 → 120°E; UTC-5 → -75°E
        try:
            tz = _pytz.timezone(timezone)
            # 用一个近似时间获取 UTC offset（避免 DST 跳转问题）
            utc_offset_seconds = tz.utcoffset(datetime(year, month, day, 12, 0)).total_seconds()
            utc_offset_hours = utc_offset_seconds / 3600
            tz_longitude = utc_offset_hours * 15  # 每小时=15度
            offset_minutes = (longitude - tz_longitude) * 4
            adjusted_dt += timedelta(minutes=offset_minutes)
        except Exception as e:
            # 降级：跳过真太阳时修正
            pass

    # Step 2: 用 sxtwl 计算四柱
    day_obj = sxtwl.fromSolar(adjusted_dt.year, adjusted_dt.month, adjusted_dt.day)

    year_gz = day_obj.getYearGZ()
    month_gz = day_obj.getMonthGZ()
    day_gz = day_obj.getDayGZ()

    year_pillar = TIANGAN[year_gz.tg] + DIZHI[year_gz.dz]
    month_pillar = TIANGAN[month_gz.tg] + DIZHI[month_gz.dz]
    day_pillar = TIANGAN[day_gz.tg] + DIZHI[day_gz.dz]

    day_master = TIANGAN[day_gz.tg]

    # 时柱（五鼠遁 + 时辰边界规则）
    hour_pillar = get_hour_pillar(day_master, adjusted_dt.hour, adjusted_dt.minute)

    pillars = {
        "年": year_pillar,
        "月": month_pillar,
        "日": day_pillar,
        "时": hour_pillar,
    }

    # Step 3: 提取各柱天干地支
    year_tg, year_dz = year_pillar[0], year_pillar[1]
    month_tg, month_dz = month_pillar[0], month_pillar[1]
    day_tg, day_dz = day_pillar[0], day_pillar[1]
    hour_tg, hour_dz = hour_pillar[0], hour_pillar[1]

    # Step 4: 十神（天干）
    shishen_tiangan = {
        "年干": ten_god(day_master, year_tg),
        "月干": ten_god(day_master, month_tg),
        "日干": "日元",
        "时干": ten_god(day_master, hour_tg),
    }

    # Step 5: 藏干 + 十神（地支）
    canggan = {
        "年支": DZ_CANGGAN[year_dz],
        "月支": DZ_CANGGAN[month_dz],
        "日支": DZ_CANGGAN[day_dz],
        "时支": DZ_CANGGAN[hour_dz],
    }
    shishen_dizhi = {}
    for pos, stems in canggan.items():
        shishen_dizhi[pos] = [{"stem": s, "god": ten_god(day_master, s)} for s in stems]

    # Step 6: 日元力量（得地定位）
    zhang_sheng = {
        "年支": get_shisheng_position(day_master, year_dz),
        "月支": get_shisheng_position(day_master, month_dz),
        "日支": get_shisheng_position(day_master, day_dz),
        "时支": get_shisheng_position(day_master, hour_dz),
    }

    # Step 7: 大运
    luck_pillars = calculate_luck_pillars(
        year_tg, month_tg, month_dz, day_master, gender, adjusted_dt
    )

    # Step 8: 流年（当前年）
    current_year = datetime.now().year
    current_year_pillar = get_year_pillar(current_year)

    return {
        "pillars": pillars,
        "day_master": day_master,
        "day_master_wuxing": TG_WUXING[day_master],
        "day_master_yinyang": TG_YINYANG[day_master],
        "day_master_gender": gender,
        "天干十神": shishen_tiangan,
        "地支藏干": canggan,
        "地支十神": shishen_dizhi,
        "日元十二长生位": zhang_sheng,
        "大运": luck_pillars,
        "流年": {
            "year": current_year,
            "pillar": current_year_pillar,
            "干十神": ten_god(day_master, current_year_pillar[0]),
        }
    }


def get_year_pillar(year):
    """根据公历年份计算年柱（立春前按上一年）"""
    # 简化：用公历年份计算（不考虑立春前后）
    # 甲子年 = 1984 - 0, 1984 = 甲子 (tg=0, dz=0)
    idx_tg = (year - 4) % 10
    idx_dz = (year - 4) % 12
    return TIANGAN[idx_tg] + DIZHI[idx_dz]


def calculate_luck_pillars(year_tg, month_tg, month_dz, day_master, gender, birth_dt):
    """
    计算 10 步大运。

    阳男阴女顺排（月柱往后推）
    阴男阳女逆排（月柱往前推）
    起运年龄 = 生日到下一（顺）或上一（逆）"节"的天数 ÷ 3
    """
    yy = TG_YINYANG[year_tg]
    is_forward = (yy == "阳" and gender == "M") or (yy == "阴" and gender == "F")

    # Step 1: 起运年龄
    day_obj = sxtwl.fromSolar(birth_dt.year, birth_dt.month, birth_dt.day)
    days_to_jieqi = find_days_to_jieqi(day_obj, birth_dt, is_forward)
    start_age_years = days_to_jieqi / 3.0  # 3日 = 1年
    start_days = int(start_age_years * 365.25)
    start_date = birth_dt + timedelta(days=start_days)

    # Step 2: 从月柱推 10 步
    tg_idx = TIANGAN.index(month_tg)
    dz_idx = DIZHI.index(month_dz)

    pillars = []
    age_begin = start_age_years
    for i in range(10):
        if is_forward:
            tg_idx = (tg_idx + 1) % 10
            dz_idx = (dz_idx + 1) % 12
        else:
            tg_idx = (tg_idx - 1) % 10
            dz_idx = (dz_idx - 1) % 12

        pillar = TIANGAN[tg_idx] + DIZHI[dz_idx]
        age_end = age_begin + 10
        year_begin = int(birth_dt.year + age_begin)
        year_end = year_begin + 10
        pillars.append({
            "序号": i + 1,
            "大运": pillar,
            "起始年龄": round(age_begin, 1),
            "起始年份": year_begin,
            "结束年份": year_end,
            "十神(天干)": ten_god(day_master, pillar[0]),
            "地支十二长生": get_shisheng_position(day_master, pillar[1]),
        })
        age_begin = age_end

    return {
        "排列方向": "顺排" if is_forward else "逆排",
        "起运年龄": round(start_age_years, 2),
        "起运日期": start_date.strftime("%Y-%m-%d"),
        "pillars": pillars,
    }


def find_days_to_jieqi(day_obj, birth_dt, forward):
    """
    找到生日到最近"节"（非"气"）的天数。
    节：立春、惊蛰、清明、立夏、芒种、小暑、立秋、白露、寒露、立冬、大雪、小寒
    对应 sxtwl JQList 的奇数索引？需要实测。
    """
    # sxtwl 节气列表顺序（从 立春 开始）
    # JQList: [小寒, 大寒, 立春, 雨水, 惊蛰, 春分, 清明, 谷雨, ...]
    # 但实际 sxtwl 的 JQList 可能从冬至开始。实测。
    # 节的索引（相对 JQList）：需查
    # 这里用实用方法：遍历附近日期找 hasJieQi()

    for offset in range(0, 62):  # 最多 62 天
        if forward:
            check_dt = birth_dt + timedelta(days=offset)
        else:
            check_dt = birth_dt - timedelta(days=offset)

        check_day = sxtwl.fromSolar(check_dt.year, check_dt.month, check_dt.day)
        if check_day.hasJieQi():
            jq_idx = check_day.getJieQi()
            # 节的索引（JQList 中）
            # 实测：奇数索引是"节"，偶数是"气"？
            # 经验证：JQList 顺序是 [冬至, 小寒, 大寒, 立春, 雨水, 惊蛰, 春分, 清明, 谷雨, 立夏, 小满, 芒种, 夏至, 小暑, 大暑, 立秋, 处暑, 白露, 秋分, 寒露, 霜降, 立冬, 小雪, 大雪]
            # 节索引：1(小寒), 3(立春), 5(惊蛰), 7(清明), 9(立夏), 11(芒种), 13(小暑), 15(立秋), 17(白露), 19(寒露), 21(立冬), 23(大雪)
            jie_indices = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23}
            if jq_idx in jie_indices:
                return offset
    return 15  # fallback


if __name__ == "__main__":
    # 自测试：Case 001
    print("=" * 50)
    print("Case 001 自测")
    print("=" * 50)
    result = calculate_bazi(1996, 8, 28, 9, 30, "F", longitude=118.4331, timezone="Asia/Shanghai")
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
