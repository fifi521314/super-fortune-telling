#!/usr/bin/env python3
"""
paipan_engine.py · 八字 + 占星双轨排盘引擎 CLI

Usage:
  python paipan_engine.py --date 1996-08-28 --time 09:30 --city 芜湖 --gender F
  python paipan_engine.py --date 1996-08-28 --time 09:30 --lat 31.35 --lon 118.43 --tz Asia/Shanghai --gender F [--true-solar-time]

Output: JSON 到 stdout
"""

import argparse
import json
import sys
import os

# 确保能找到同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bazi import calculate_bazi
from astrology import calculate_astrology
from cities import lookup_city


def main():
    parser = argparse.ArgumentParser(
        description="双轨排盘引擎：八字（子平+盲派增强）+ 占星（Tompkins 心理占星）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--date", required=True, help="出生日期 YYYY-MM-DD")
    parser.add_argument("--time", required=True, help="出生时间 HH:MM (24h)")
    parser.add_argument("--gender", required=True, choices=["M", "F"], help="性别")

    # 地点：要么指定城市，要么给 lat/lon/tz
    parser.add_argument("--city", help="出生城市（中文名，内置城市表查找）")
    parser.add_argument("--lat", type=float, help="出生地纬度（北纬正）")
    parser.add_argument("--lon", type=float, help="出生地经度（东经正）")
    parser.add_argument("--tz", help="时区名（如 Asia/Shanghai）")

    parser.add_argument("--true-solar-time", action="store_true",
                        help="八字启用真太阳时修正（默认不启用；占星始终使用标准时间 + 经纬度精确计算）")
    parser.add_argument("--bazi-only", action="store_true", help="仅输出八字")
    parser.add_argument("--astrology-only", action="store_true", help="仅输出占星")
    parser.add_argument("--pretty", action="store_true", help="格式化 JSON 输出")

    args = parser.parse_args()

    # 解析日期时间
    try:
        y, m, d = map(int, args.date.split("-"))
        h, mi = map(int, args.time.split(":"))
    except ValueError:
        print(json.dumps({"error": "日期/时间格式错误。期望 YYYY-MM-DD HH:MM"}, ensure_ascii=False))
        sys.exit(1)

    # 解析地点
    if args.city:
        coords = lookup_city(args.city)
        if coords is None:
            print(json.dumps({"error": f"城市未找到: {args.city}。请用 --lat/--lon/--tz 手动指定。"}, ensure_ascii=False))
            sys.exit(1)
        lat, lon, tz = coords
    elif args.lat is not None and args.lon is not None and args.tz:
        lat, lon, tz = args.lat, args.lon, args.tz
    else:
        print(json.dumps({"error": "必须指定 --city 或 (--lat + --lon + --tz)"}, ensure_ascii=False))
        sys.exit(1)

    # 构造输出
    output = {
        "input": {
            "date": args.date,
            "time": args.time,
            "city": args.city,
            "lat": lat,
            "lon": lon,
            "tz": tz,
            "gender": args.gender,
            "true_solar_time": args.true_solar_time,
        }
    }

    # 八字
    if not args.astrology_only:
        try:
            bazi_result = calculate_bazi(
                y, m, d, h, mi, args.gender,
                longitude=lon, timezone=tz,
                true_solar_time=args.true_solar_time,
            )
            output["bazi"] = bazi_result
        except Exception as e:
            output["bazi_error"] = str(e)

    # 占星
    if not args.bazi_only:
        try:
            astro_result = calculate_astrology(y, m, d, h, mi, lat, lon, tz)
            output["astrology"] = astro_result
        except Exception as e:
            output["astrology_error"] = str(e)

    # 输出
    indent = 2 if args.pretty else None
    print(json.dumps(output, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
