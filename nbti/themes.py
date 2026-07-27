"""NBTI 多主题定义模块"""

THEMES = {
    "workplace": {
        "id": "workplace",
        "name": "职场人格",
        "description": "经典职场人格测试，16种职场角色定位",
        "icon": "💼",
        "dimensions": [
            {"key": "nb", "positive": "N(能动)", "negative": "S(稳态)"},
            {"key": "bh", "positive": "B(边界)", "negative": "H(合群)"},
            {"key": "tf", "positive": "T(理性)", "negative": "F(感性)"},
            {"key": "ip", "positive": "I(强执行)", "negative": "P(灵活)"}
        ],
        "personality_types": [
            {"code": "NBTI", "name": "卷王", "oneline": "996是福报，加班是修行"},
            {"code": "NBTP", "name": "棋手", "oneline": "所有人都是我棋盘上的棋子"},
            {"code": "NBFI", "name": "独狼", "oneline": "给我一个需求，还你一个奇迹，别烦我"},
            {"code": "NBFP", "name": "浪子", "oneline": "四海为家，简历比冒险小说精彩"},
            {"code": "NHTI", "name": "霸总", "oneline": "我不是在PUA你，我是为你好"},
            {"code": "NHTP", "name": "教练", "oneline": "我不上赛场，我培养冠军"},
            {"code": "NHFI", "name": "护犊子", "oneline": "天塌了我顶着，动我的人试试"},
            {"code": "NHFP", "name": "气氛组", "oneline": "公司没我早散伙了"},
            {"code": "SBTI", "name": "工蚁", "oneline": "不声不响，但所有灯都是我开的"},
            {"code": "SBTP", "name": "人形计算器", "oneline": "别跟我谈感情，谈数据"},
            {"code": "SBFI", "name": "螺丝钉", "oneline": "最无聊的岗位，最不可替代的人"},
            {"code": "SBFP", "name": "扫地僧", "oneline": "你以为我是青铜，其实我是王者"},
            {"code": "SHTI", "name": "大管家", "oneline": "诸葛亮都没我会统筹"},
            {"code": "SHTP", "name": "质检警察", "oneline": "99.9%就是不及格"},
            {"code": "SHFI", "name": "居委会大妈", "oneline": "有矛盾？来，坐下聊"},
            {"code": "SHFP", "name": "职场空气", "oneline": "我在，但好像又不在"}
        ],
        "easter_eggs": {
            "schrodinger": "薛定谔的打工人",
            "hexagon": "六边形战士",
            "buddha": "职场活佛",
            "double": "职场双面人",
            "mouthpiece": "互联网嘴替"
        }
    },
    "animal": {
        "id": "animal",
        "name": "动物系人格",
        "description": "你是哪种动物？揭秘你的野性人格",
        "icon": "🐾",
        "dimensions": [
            {"key": "nb", "positive": "N(猎食者)", "negative": "S(食草者)"},
            {"key": "bh", "positive": "B(独居)", "negative": "H(群居)"},
            {"key": "tf", "positive": "T(冷血)", "negative": "F(热血)"},
            {"key": "ip", "positive": "I(昼行)", "negative": "P(夜行)"}
        ],
        "personality_types": [
            {"code": "NBTI", "name": "东北虎", "oneline": "丛林之王，独来独往的顶级猎手"},
            {"code": "NBTP", "name": "狐狸", "oneline": "聪明狡黠，算无遗策的谋略家"},
            {"code": "NBFI", "name": "雪豹", "oneline": "高山隐士，一击致命的独行侠"},
            {"code": "NBFP", "name": "猎豹", "oneline": "速度之王，永远在追逐下一个目标"},
            {"code": "NHTI", "name": "狮王", "oneline": "草原霸主，威严不容置疑的领袖"},
            {"code": "NHTP", "name": "头狼", "oneline": "狼群之首，带领团队走向胜利"},
            {"code": "NHFI", "name": "棕熊", "oneline": "护崽狂魔，谁敢动我的人试试"},
            {"code": "NHFP", "name": "金毛", "oneline": "快乐小狗，团队的气氛担当"},
            {"code": "SBTI", "name": "工蜂", "oneline": "勤勤恳恳，蜂巢的无名英雄"},
            {"code": "SBTP", "name": "猫头鹰", "oneline": "夜视之眼，冷静精准的观察者"},
            {"code": "SBFI", "name": "树懒", "oneline": "慢活大师，与世无争的哲学家"},
            {"code": "SBFP", "name": "章鱼", "oneline": "伪装大师，深藏不露的智者"},
            {"code": "SHTI", "name": "大象", "oneline": "记忆超群，稳重可靠的族长"},
            {"code": "SHTP", "name": "黑猫", "oneline": "完美主义，细节决定一切"},
            {"code": "SHFI", "name": "海豚", "oneline": "治愈系天使，海里的心理医生"},
            {"code": "SHFP", "name": "水母", "oneline": "随波逐流，海洋里的透明精灵"}
        ],
        "easter_eggs": {
            "schrodinger": "薛定谔的猫",
            "hexagon": "凤凰",
            "buddha": "树懒佛",
            "double": "变色龙",
            "mouthpiece": "鹦鹉"
        }
    },
    "color": {
        "id": "color",
        "name": "色彩人格",
        "description": "你的灵魂是什么颜色？色彩心理学测试",
        "icon": "🎨",
        "dimensions": [
            {"key": "nb", "positive": "N(暖色)", "negative": "S(冷色)"},
            {"key": "bh", "positive": "B(纯色)", "negative": "H(混色)"},
            {"key": "tf", "positive": "T(深色)", "negative": "F(浅色)"},
            {"key": "ip", "positive": "I(亮色)", "negative": "P(暗色)"}
        ],
        "personality_types": [
            {"code": "NBTI", "name": "中国红", "oneline": "热情似火，天生的领导者"},
            {"code": "NBTP", "name": "皇家蓝", "oneline": "深邃睿智，运筹帷幄的策略家"},
            {"code": "NBFI", "name": "黑金", "oneline": "神秘高贵，不可触碰的存在"},
            {"code": "NBFP", "name": "橙红", "oneline": "活力四射，永远年轻永远热血"},
            {"code": "NHTI", "name": "酒红", "oneline": "成熟霸气，掌控全场的女王"},
            {"code": "NHTP", "name": "焦糖色", "oneline": "温暖治愈，人生导师般的存在"},
            {"code": "NHFI", "name": "珊瑚粉", "oneline": "温柔守护，治愈系小太阳"},
            {"code": "NHFP", "name": "柠檬黄", "oneline": "快乐源泉，走到哪亮到哪"},
            {"code": "SBTI", "name": "石灰白", "oneline": "默默奉献，最可靠的底色"},
            {"code": "SBTP", "name": "墨黑", "oneline": "理性深邃，数据就是一切"},
            {"code": "SBFI", "name": "奶茶色", "oneline": "温柔百搭，最舒服的存在"},
            {"code": "SBFP", "name": "雾霾蓝", "oneline": "文艺复古，有故事的颜色"},
            {"code": "SHTI", "name": "橄榄绿", "oneline": "沉稳务实，靠谱的代言人"},
            {"code": "SHTP", "name": "藏青", "oneline": "严谨细致，零容错的完美主义"},
            {"code": "SHFI", "name": "豆沙粉", "oneline": "善解人意，最好的倾听者"},
            {"code": "SHFP", "name": "米白", "oneline": "佛系随缘，存在感极低的小透明"}
        ],
        "easter_eggs": {
            "schrodinger": "透明色",
            "hexagon": "彩虹色",
            "buddha": "莫兰迪",
            "double": "镭射色",
            "mouthpiece": "弹幕色"
        }
    },
    "love": {
        "id": "love",
        "name": "恋爱人格",
        "description": "你在恋爱中是什么类型？揭秘你的爱情模式",
        "icon": "💕",
        "dimensions": [
            {"key": "nb", "positive": "N(主动)", "negative": "S(被动)"},
            {"key": "bh", "positive": "B(独立)", "negative": "H(依恋)"},
            {"key": "tf", "positive": "T(理性)", "negative": "F(感性)"},
            {"key": "ip", "positive": "I(承诺)", "negative": "P(随缘)"}
        ],
        "personality_types": [],
        "easter_eggs": {}
    },
    "social": {
        "id": "social",
        "name": "社交人格",
        "description": "你是社牛还是社恐？社交场合真实的你",
        "icon": "👥",
        "dimensions": [
            {"key": "nb", "positive": "N(外向)", "negative": "S(内向)"},
            {"key": "bh", "positive": "B(边界)", "negative": "H(共情)"},
            {"key": "tf", "positive": "T(逻辑)", "negative": "F(情绪)"},
            {"key": "ip", "positive": "I(主导)", "negative": "P(配合)"}
        ],
        "personality_types": [],
        "easter_eggs": {}
    },
    "mbti": {
        "id": "mbti",
        "name": "官方MBTI",
        "description": "经典16型人格测试，权威心理学视角",
        "icon": "🧠",
        "dimensions": [
            {"key": "nb", "positive": "E(外倾)", "negative": "I(内倾)"},
            {"key": "bh", "positive": "S(感觉)", "negative": "N(直觉)"},
            {"key": "tf", "positive": "T(思考)", "negative": "F(情感)"},
            {"key": "ip", "positive": "J(判断)", "negative": "P(感知)"}
        ],
        "personality_types": [],
        "easter_eggs": {}
    },
    "brainhol": {
        "id": "brainhol",
        "name": "脑洞人格",
        "description": "奇葩脑洞测试，你的脑回路有多清奇",
        "icon": "🤯",
        "dimensions": [
            {"key": "nb", "positive": "N(外星)", "negative": "S(地球)"},
            {"key": "bh", "positive": "B(深井冰)", "negative": "H(正常人)"},
            {"key": "tf", "positive": "T(神经病)", "negative": "F(精神病)"},
            {"key": "ip", "positive": "I(发病)", "negative": "P(潜伏期)"}
        ],
        "personality_types": [],
        "easter_eggs": {}
    }
}


def get_themes():
    """返回所有主题列表（精简版，不含完整prompt）"""
    return [
        {
            "id": theme["id"],
            "name": theme["name"],
            "description": theme["description"],
            "icon": theme["icon"]
        }
        for theme in THEMES.values()
    ]


def get_theme(theme_id):
    """根据theme_id获取完整主题配置"""
    return THEMES.get(theme_id, THEMES["workplace"])
