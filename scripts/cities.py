"""
Built-in city database for paipan_engine.
Includes all cities referenced in Case 001-006 plus common global cities.
Format: {name (zh/en): (latitude, longitude, timezone)}
"""

CITIES = {
    # 中国
    "北京": (39.9042, 116.4074, "Asia/Shanghai"),
    "上海": (31.2304, 121.4737, "Asia/Shanghai"),
    "广州": (23.1291, 113.2644, "Asia/Shanghai"),
    "深圳": (22.5431, 114.0579, "Asia/Shanghai"),
    "杭州": (30.2741, 120.1551, "Asia/Shanghai"),
    "温州": (27.9943, 120.6993, "Asia/Shanghai"),
    "南京": (32.0603, 118.7969, "Asia/Shanghai"),
    "芜湖": (31.3526, 118.4331, "Asia/Shanghai"),
    "成都": (30.5728, 104.0668, "Asia/Shanghai"),
    "武汉": (30.5928, 114.3055, "Asia/Shanghai"),
    "重庆": (29.5630, 106.5516, "Asia/Shanghai"),
    "西安": (34.3416, 108.9398, "Asia/Shanghai"),
    "呼和浩特": (40.8414, 111.7519, "Asia/Shanghai"),
    "哈尔滨": (45.8038, 126.5349, "Asia/Shanghai"),
    "昆明": (25.0389, 102.7183, "Asia/Shanghai"),
    "厦门": (24.4798, 118.0894, "Asia/Shanghai"),
    "青岛": (36.0671, 120.3826, "Asia/Shanghai"),
    "天津": (39.3434, 117.3616, "Asia/Shanghai"),
    "苏州": (31.2990, 120.5853, "Asia/Shanghai"),
    "绍兴": (30.0023, 120.5810, "Asia/Shanghai"),
    "宁波": (29.8683, 121.5440, "Asia/Shanghai"),
    "无锡": (31.4912, 120.3119, "Asia/Shanghai"),
    "长沙": (28.2278, 112.9388, "Asia/Shanghai"),
    "郑州": (34.7472, 113.6253, "Asia/Shanghai"),
    "济南": (36.6512, 117.1201, "Asia/Shanghai"),
    "合肥": (31.8206, 117.2272, "Asia/Shanghai"),
    "淄博": (36.7906, 118.0479, "Asia/Shanghai"),
    "运城": (35.0264, 110.9647, "Asia/Shanghai"),

    # 港澳台
    "香港": (22.3193, 114.1694, "Asia/Hong_Kong"),
    "澳门": (22.1987, 113.5439, "Asia/Macau"),
    "台北": (25.0330, 121.5654, "Asia/Taipei"),

    # 亚洲
    "东京": (35.6762, 139.6503, "Asia/Tokyo"),
    "Tokyo": (35.6762, 139.6503, "Asia/Tokyo"),
    "首尔": (37.5665, 126.9780, "Asia/Seoul"),
    "Seoul": (37.5665, 126.9780, "Asia/Seoul"),
    "新加坡": (1.3521, 103.8198, "Asia/Singapore"),
    "Singapore": (1.3521, 103.8198, "Asia/Singapore"),
    "吉隆坡": (3.1390, 101.6869, "Asia/Kuala_Lumpur"),
    "曼谷": (13.7563, 100.5018, "Asia/Bangkok"),
    "Bangkok": (13.7563, 100.5018, "Asia/Bangkok"),
    "雅加达": (-6.2088, 106.8456, "Asia/Jakarta"),
    "孟买": (19.0760, 72.8777, "Asia/Kolkata"),
    "Mumbai": (19.0760, 72.8777, "Asia/Kolkata"),
    "迪拜": (25.2048, 55.2708, "Asia/Dubai"),
    "Dubai": (25.2048, 55.2708, "Asia/Dubai"),

    # 欧洲
    "伦敦": (51.5074, -0.1278, "Europe/London"),
    "London": (51.5074, -0.1278, "Europe/London"),
    "巴黎": (48.8566, 2.3522, "Europe/Paris"),
    "Paris": (48.8566, 2.3522, "Europe/Paris"),
    "柏林": (52.5200, 13.4050, "Europe/Berlin"),
    "Berlin": (52.5200, 13.4050, "Europe/Berlin"),
    "阿姆斯特丹": (52.3676, 4.9041, "Europe/Amsterdam"),
    "苏黎世": (47.3769, 8.5417, "Europe/Zurich"),
    "莫斯科": (55.7558, 37.6173, "Europe/Moscow"),
    "罗马": (41.9028, 12.4964, "Europe/Rome"),

    # 北美
    "纽约": (40.7128, -74.0060, "America/New_York"),
    "New York": (40.7128, -74.0060, "America/New_York"),
    "洛杉矶": (34.0522, -118.2437, "America/Los_Angeles"),
    "Los Angeles": (34.0522, -118.2437, "America/Los_Angeles"),
    "旧金山": (37.7749, -122.4194, "America/Los_Angeles"),
    "San Francisco": (37.7749, -122.4194, "America/Los_Angeles"),
    "芝加哥": (41.8781, -87.6298, "America/Chicago"),
    "温哥华": (49.2827, -123.1207, "America/Vancouver"),
    "多伦多": (43.6532, -79.3832, "America/Toronto"),

    # 大洋洲
    "悉尼": (-33.8688, 151.2093, "Australia/Sydney"),
    "Sydney": (-33.8688, 151.2093, "Australia/Sydney"),
    "墨尔本": (-37.8136, 144.9631, "Australia/Melbourne"),
    "奥克兰": (-36.8485, 174.7633, "Pacific/Auckland"),
}


def lookup_city(name):
    """Look up city by name (Chinese or English). Returns (lat, lon, tz) or None."""
    if name in CITIES:
        return CITIES[name]
    # Try case-insensitive for English
    for city, coords in CITIES.items():
        if city.lower() == name.lower():
            return coords
    return None
