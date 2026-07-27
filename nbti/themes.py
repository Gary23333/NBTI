"""NBTI 多主题定义模块"""

THEMES = {
    "workplace": {
        "id": "workplace",
        "name": "职场人格",
        "description": "经典职场人格测试，16种职场角色定位",
        "icon": "💼",
        "colors": {
            "primary": "#2563EB",
            "secondary": "#1E40AF",
            "accent": "#F59E0B"
        },
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
        },
        "scenes": [
            "加班修罗场：深夜改需求、周末被@、领导的夺命连环call",
            "团建社死现场：破冰游戏、才艺表演、敬酒环节",
            "办公室政治：站队、甩锅、抢功劳、茶水间八卦",
            "领导迷惑行为：画饼、PUA、朝令夕改、薛定谔的预算",
            "摸鱼与反摸鱼：带薪拉屎、假装忙、防窥膜文学",
            "年终大考：述职PPT、年终奖博弈、绩效考核"
        ]
    },
    "animal": {
        "id": "animal",
        "name": "动物系人格",
        "description": "你是哪种动物？揭秘你的野性人格",
        "icon": "🐾",
        "colors": {
            "primary": "#059669",
            "secondary": "#78350F",
            "accent": "#FBBF24"
        },
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
        },
        "scenes": [
            "丛林法则：领地争夺、食物链抉择、弱肉强食现场",
            "族群生活：头领竞选、带娃分工、群体迁徙",
            "捕猎时刻：伏击、追击、到嘴的猎物飞了",
            "求偶大赏：开屏斗艳、情歌对唱、相亲角混战",
            "生存危机：天敌逼近、寒冬断粮、栖息地被占",
            "日常摆烂：晒太阳、囤粮、冬眠前的最后狂欢"
        ]
    },
    "color": {
        "id": "color",
        "name": "色彩人格",
        "description": "你的灵魂是什么颜色？色彩心理学测试",
        "icon": "🎨",
        "colors": {
            "primary": "#8B5CF6",
            "secondary": "#EC4899",
            "accent": "#F59E0B"
        },
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
        },
        "scenes": [
            "情绪调色盘：今天的心情是什么颜色",
            "穿搭修罗场：衣柜爆炸、出门前两小时的纠结",
            "装修与审美：刷墙选色、软装搭配、审美battle",
            "高光与至暗：人生高光时刻的配色、深夜emo的底色",
            "滤镜人生：朋友圈精修vs原图直出",
            "本命色觉醒：第一眼就被击中的颜色"
        ]
    },
    "love": {
        "id": "love",
        "name": "恋爱人格",
        "description": "你在恋爱中是什么类型？揭秘你的爱情模式",
        "icon": "💕",
        "colors": {
            "primary": "#EC4899",
            "secondary": "#F43F5E",
            "accent": "#FDA4AF"
        },
        "dimensions": [
            {"key": "nb", "positive": "N(主动)", "negative": "S(被动)"},
            {"key": "bh", "positive": "B(独立)", "negative": "H(依恋)"},
            {"key": "tf", "positive": "T(理性)", "negative": "F(感性)"},
            {"key": "ip", "positive": "I(承诺)", "negative": "P(随缘)"}
        ],
        "personality_types": [
            {"code": "NBTI", "name": "爱情架构师", "oneline": "恋爱是项目管理，目标明确执行到位"},
            {"code": "NBTP", "name": "海王本王", "oneline": "万花丛中过，片叶不沾身"},
            {"code": "NBFI", "name": "忠犬骑士", "oneline": "爱你这件事，我单方面宣布终身有效"},
            {"code": "NBFP", "name": "浪漫游侠", "oneline": "爱你时全力以赴，缘尽时潇洒转身"},
            {"code": "NHTI", "name": "恋爱CEO", "oneline": "我们的五年规划我做好了，签字吧"},
            {"code": "NHTP", "name": "理智贴贴怪", "oneline": "嘴上说随缘，身体却很诚实地粘着你"},
            {"code": "NHFI", "name": "热恋永动机", "oneline": "对你的喜欢24小时营业，永不打烊"},
            {"code": "NHFP", "name": "恋爱脑本脑", "oneline": "上头是日常，理智已离家出走"},
            {"code": "SBTI", "name": "闷声守候者", "oneline": "不说爱，但余生都是你的Plan A"},
            {"code": "SBTP", "name": "爱情绝缘体", "oneline": "恋爱？哦，等我忙完这阵再说"},
            {"code": "SBFI", "name": "暗恋收藏家", "oneline": "把你放在心里最深处，谁也不告诉"},
            {"code": "SBFP", "name": "灵魂独行客", "oneline": "心动常有，行动全无"},
            {"code": "SHTI", "name": "温水伴侣", "oneline": "不浪漫但靠谱，爱都藏在细节里"},
            {"code": "SHTP", "name": "备胎转正委", "oneline": "你不找我我不找你，你找我我一直在"},
            {"code": "SHFI", "name": "望夫石", "oneline": "爱上了就是一辈子，等也是"},
            {"code": "SHFP", "name": "恋爱NPC", "oneline": "在别人的爱情故事里，我永远在待机"}
        ],
        "easter_eggs": {
            "schrodinger": "薛定谔的暧昧对象",
            "hexagon": "六边形恋人",
            "buddha": "单身活佛",
            "double": "恋爱双面胶",
            "mouthpiece": "全网恋爱嘴替"
        },
        "scenes": [
            "暧昧期拉扯：秒回与轮回、猜心思、谁先表白",
            "表白修罗场：当众表白、被拒现场、酒后吐真言",
            "相亲翻车：查户口式提问、照骗奔现、奇葩要求",
            "前任诈尸：深夜好友申请、婚礼请柬、旧物处理",
            "送命选择题：我和你妈掉水里、游戏和我谁重要",
            "恋爱日常：纪念日礼物、查手机、异地恋的视频通话"
        ]
    },
    "social": {
        "id": "social",
        "name": "社交人格",
        "description": "你是社牛还是社恐？社交场合真实的你",
        "icon": "👥",
        "colors": {
            "primary": "#F97316",
            "secondary": "#06B6D4",
            "accent": "#FBBF24"
        },
        "dimensions": [
            {"key": "nb", "positive": "N(外向)", "negative": "S(内向)"},
            {"key": "bh", "positive": "B(边界)", "negative": "H(共情)"},
            {"key": "tf", "positive": "T(逻辑)", "negative": "F(情绪)"},
            {"key": "ip", "positive": "I(主导)", "negative": "P(配合)"}
        ],
        "personality_types": [
            {"code": "NBTI", "name": "社交悍匪", "oneline": "组局我说了算，社恐都给我让道"},
            {"code": "NBTP", "name": "气氛操盘手", "oneline": "场子冷不了，但谁也别想指挥我"},
            {"code": "NBFI", "name": "聚会麦霸", "oneline": "KTV的麦在我手里，谁抢跟谁急"},
            {"code": "NBFP", "name": "快乐显眼包", "oneline": "有我在的地方，尴尬不存在"},
            {"code": "NHTI", "name": "社交导演", "oneline": "全场人际关系，我一手编排"},
            {"code": "NHTP", "name": "人形WiFi", "oneline": "走到哪连到哪，信号满格"},
            {"code": "NHFI", "name": "热场暖宝宝", "oneline": "所有人的情绪我都要照顾到"},
            {"code": "NHFP", "name": "捧场王", "oneline": "哈哈哈哈哈哈，你讲得真好"},
            {"code": "SBTI", "name": "高冷观察员", "oneline": "我不说话，但全场尽在掌握"},
            {"code": "SBTP", "name": "社交节能侠", "oneline": "能打字绝不语音，能线上绝不见面"},
            {"code": "SBFI", "name": "社恐leader", "oneline": "心里很慌，但场面必须撑住"},
            {"code": "SBFP", "name": "隐形听众", "oneline": "我在听，你们聊，别cue我"},
            {"code": "SHTI", "name": "幕后军师", "oneline": "饭局我不组，但去哪吃听我的"},
            {"code": "SHTP", "name": "树洞本洞", "oneline": "所有人的秘密都在我这，嘴比保险柜严"},
            {"code": "SHFI", "name": "温柔港湾", "oneline": "朋友有难第一个想到我"},
            {"code": "SHFP", "name": "人形抱枕", "oneline": "不说话，但抱着很安心"}
        ],
        "easter_eggs": {
            "schrodinger": "薛定谔的社牛",
            "hexagon": "社交六边形战士",
            "buddha": "社交活佛",
            "double": "线上社牛线下社恐",
            "mouthpiece": "聚会嘴替"
        },
        "scenes": [
            "社死现场：叫错名字、群发吐槽、电梯偶遇领导",
            "饭局生存：拼桌陌生人、敬酒词、AA算账",
            "群聊生态：抢红包手速、被@全员、潜水被点名",
            "被迫营业：婚礼上台发言、邻居尬聊、亲戚盘问",
            "同学聚会：凡尔赛大赏、怀旧杀、加微信修罗场",
            "社交充电与耗电：独处回血、营业额度耗尽"
        ]
    },
    "mbti": {
        "id": "mbti",
        "name": "官方MBTI",
        "description": "经典16型人格测试，权威心理学视角",
        "icon": "🧠",
        "colors": {
            "primary": "#6366F1",
            "secondary": "#8B5CF6",
            "accent": "#94A3B8"
        },
        "dimensions": [
            {"key": "nb", "positive": "E(外倾)", "negative": "I(内倾)"},
            {"key": "bh", "positive": "S(感觉)", "negative": "N(直觉)"},
            {"key": "tf", "positive": "T(思考)", "negative": "F(情感)"},
            {"key": "ip", "positive": "J(判断)", "negative": "P(感知)"}
        ],
        "personality_types": [
            {"code": "ISTJ", "name": "检查员", "oneline": "认真严谨、负责任的务实者"},
            {"code": "ISFJ", "name": "保护者", "oneline": "温暖体贴、忠于职守的守护者"},
            {"code": "INFJ", "name": "提倡者", "oneline": "富有洞察力、理想主义的引路人"},
            {"code": "INTJ", "name": "建筑师", "oneline": "独立思考、战略导向的规划者"},
            {"code": "ISTP", "name": "鉴赏家", "oneline": "冷静理性、擅长动手的实践者"},
            {"code": "ISFP", "name": "探险家", "oneline": "温和敏感、热爱艺术的体验者"},
            {"code": "INFP", "name": "调停者", "oneline": "理想主义、富同情心的梦想家"},
            {"code": "INTP", "name": "逻辑学家", "oneline": "思辨缜密、追求真理的思考者"},
            {"code": "ESTP", "name": "企业家", "oneline": "精力充沛、行动力强的冒险家"},
            {"code": "ESFP", "name": "表演者", "oneline": "热情外向、活在当下的娱乐者"},
            {"code": "ENFP", "name": "竞选者", "oneline": "充满热情、富有创造力的激励者"},
            {"code": "ENTP", "name": "辩论家", "oneline": "聪明好奇、喜欢挑战的创新者"},
            {"code": "ESTJ", "name": "总经理", "oneline": "务实高效、组织能力强的管理者"},
            {"code": "ESFJ", "name": "执政官", "oneline": "热心友善、善于合作的协调者"},
            {"code": "ENFJ", "name": "主人公", "oneline": "富有魅力、天生的领导者"},
            {"code": "ENTJ", "name": "指挥官", "oneline": "果断自信、战略眼光的领袖"}
        ],
        "easter_eggs": {
            "schrodinger": "薛定谔型人格",
            "hexagon": "全维度均衡型",
            "buddha": "超稳定型",
            "double": "双高反差型",
            "mouthpiece": "表达外化型"
        },
        "scenes": [
            "团队协作：项目分工、会议讨论、意见冲突时的处理",
            "计划与变化：周末安排被打乱、临时任务、截止日期",
            "决策时刻：重要选择、信息不足时的判断、权衡利弊",
            "情绪处理：朋友倾诉、他人崩溃、自己的压力出口",
            "能量来源：独处充电还是聚会回血、社交后的状态",
            "学习新知：偏好理论还是实操、接收新信息的方式"
        ]
    },
    "brainhol": {
        "id": "brainhol",
        "name": "脑洞人格",
        "description": "奇葩脑洞测试，你的脑回路有多清奇",
        "icon": "🤯",
        "colors": {
            "primary": "#A855F7",
            "secondary": "#22D3EE",
            "accent": "#FACC15"
        },
        "dimensions": [
            {"key": "nb", "positive": "N(外星)", "negative": "S(地球)"},
            {"key": "bh", "positive": "B(深井冰)", "negative": "H(正常人)"},
            {"key": "tf", "positive": "T(神经病)", "negative": "F(精神病)"},
            {"key": "ip", "positive": "I(发病)", "negative": "P(潜伏期)"}
        ],
        "personality_types": [
            {"code": "NBTI", "name": "星际病院院长", "oneline": "地球容不下我，我是来殖民笑点的"},
            {"code": "NBTP", "name": "宇宙抬杠机", "oneline": "和外星人都能抬杠，杠出银河系"},
            {"code": "NBFI", "name": "外星电波人", "oneline": "我的信号，人类接收不到"},
            {"code": "NBFP", "name": "银河gai溜子", "oneline": "在宇宙的街头巷尾瞎逛，到处惹事"},
            {"code": "NHTI", "name": "伪装地球人", "oneline": "潜伏十年，开口就暴露"},
            {"code": "NHTP", "name": "人形bug", "oneline": "出厂设置就有问题，懒得修了"},
            {"code": "NHFI", "name": "脑洞永动机", "oneline": "一秒三个离谱想法，全是发病现场"},
            {"code": "NHFP", "name": "抽象艺术家", "oneline": "没人懂我，包括我自己"},
            {"code": "SBTI", "name": "地球卧底", "oneline": "表面正常，档案厚得能出书"},
            {"code": "SBTP", "name": "潜伏期患者", "oneline": "看着正常，其实病得不轻，只是没到时候"},
            {"code": "SBFI", "name": "静默发病区", "oneline": "脑内世界大战，表面岁月静好"},
            {"code": "SBFP", "name": "地心脑洞仓", "oneline": "脑洞深埋地心，一挖一个喷涌"},
            {"code": "SHTI", "name": "正经胡说家", "oneline": "用最正经的脸，说最离谱的话"},
            {"code": "SHTP", "name": "伪正常之光", "oneline": "全病区最像正常人的病人"},
            {"code": "SHFI", "name": "深夜emo诗人", "oneline": "凌晨三点，我和宇宙对话"},
            {"code": "SHFP", "name": "透明病友", "oneline": "病得很安静，安静到没人发现"}
        ],
        "easter_eggs": {
            "schrodinger": "薛定谔的正常人",
            "hexagon": "六边形神经病",
            "buddha": "放空活佛",
            "double": "间歇性正常人",
            "mouthpiece": "互联网脑替"
        },
        "scenes": [
            "离谱假设：给你一亿但有奇葩条件、超能力二选一",
            "穿越乱流：穿到奇怪朝代、和动物互换身体一天",
            "规则怪谈：凌晨的电梯守则、不能回头的走廊",
            "荒诞生存：丧尸围城带三样东西、荒岛只剩WiFi",
            "灵魂拷问：如果明天不用上班、记忆能删除一段",
            "抽象日常：和Siri吵架、给蚊子写感谢信"
        ]
    },
    "money": {
        "id": "money",
        "name": "搞钱人格",
        "description": "你的财富观是哪种流派？揭秘你的搞钱体质",
        "icon": "💰",
        "colors": {
            "primary": "#F59E0B",
            "secondary": "#D97706",
            "accent": "#10B981"
        },
        "dimensions": [
            {"key": "nb", "positive": "N(狼性)", "negative": "S(稳守)"},
            {"key": "bh", "positive": "B(单干)", "negative": "H(抱团)"},
            {"key": "tf", "positive": "T(精算)", "negative": "F(感觉)"},
            {"key": "ip", "positive": "I(长线)", "negative": "P(短线)"}
        ],
        "personality_types": [
            {"code": "NBTI", "name": "复利孤狼", "oneline": "一个人一台电脑，闷声滚雪球"},
            {"code": "NBTP", "name": "量化赌徒", "oneline": "K线是我的战场，止损比谁都快"},
            {"code": "NBFI", "name": "风口赌徒", "oneline": "All in是一种信仰，输了从头再来"},
            {"code": "NBFP", "name": "野路子游资", "oneline": "直觉告诉我，这波能翻倍"},
            {"code": "NHTI", "name": "搞钱合伙人", "oneline": "组队开黑，一起财富自由"},
            {"code": "NHTP", "name": "带货团长", "oneline": "兄弟们跟我冲，这波团购必赚"},
            {"code": "NHFI", "name": "画饼资本家", "oneline": "梦想很大，跟我干的人更多"},
            {"code": "NHFP", "name": "搞钱气氛组", "oneline": "天天喊搞钱，先搞个奶茶钱"},
            {"code": "SBTI", "name": "稳健复利佬", "oneline": "年化5%，但我睡得着觉"},
            {"code": "SBTP", "name": "薅羊毛宗师", "oneline": "满减凑单，精确到分"},
            {"code": "SBFI", "name": "存钱罐本罐", "oneline": "钱放我这，比银行还安全"},
            {"code": "SBFP", "name": "抠门小能手", "oneline": "不是没钱，是钱花得心疼"},
            {"code": "SHTI", "name": "家庭CFO", "oneline": "全家财政大权，我一人执掌"},
            {"code": "SHTP", "name": "AA活算盘", "oneline": "这顿58块3毛，转我58就行"},
            {"code": "SHFI", "name": "守财暖炉", "oneline": "钱不多，但都花在在乎的人身上"},
            {"code": "SHFP", "name": "月光佛系人", "oneline": "钱是身外之物，花完再说"}
        ],
        "easter_eggs": {
            "schrodinger": "薛定谔的存款",
            "hexagon": "六边形财神",
            "buddha": "散财童子",
            "double": "搞钱双面人",
            "mouthpiece": "财经嘴替"
        },
        "scenes": [
            "发工资第一天：转账、还花呗、犒劳自己的极限拉扯",
            "朋友借钱：借与不借、催债的艺术、欠条文学",
            "冲动消费：直播间剁手、双十一满减、退货心理学",
            "理财惊魂：基金绿到发光、股票群大神、割肉还是补仓",
            "副业狂想：摆摊、自媒体、下班后的第二战场",
            "天降横财：中五百万怎么花、老板画饼值多少钱"
        ]
    },
    "spirit": {
        "id": "spirit",
        "name": "精神状态检测",
        "description": "当代年轻人精神图鉴，测测你的精神电量",
        "icon": "🔋",
        "colors": {
            "primary": "#7C3AED",
            "secondary": "#0EA5E9",
            "accent": "#FB7185"
        },
        "dimensions": [
            {"key": "nb", "positive": "N(亢奋)", "negative": "S(低迷)"},
            {"key": "bh", "positive": "B(内核稳)", "negative": "H(易破防)"},
            {"key": "tf", "positive": "T(理智在线)", "negative": "F(感性泛滥)"},
            {"key": "ip", "positive": "I(规律)", "negative": "P(混乱)"}
        ],
        "personality_types": [
            {"code": "NBTI", "name": "永动机卷王", "oneline": "精力用不完，自律到可怕"},
            {"code": "NBTP", "name": "特种兵玩家", "oneline": "一天打卡八个景点，攻略全靠临场"},
            {"code": "NBFI", "name": "热血小太阳", "oneline": "每天元气满满，朋友圈正能量批发商"},
            {"code": "NBFP", "name": "快乐疯批", "oneline": "精神状态遥遥领先，快乐得不讲道理"},
            {"code": "NHTI", "name": "紧绷发条人", "oneline": "表面积极上进，内心弦快崩了"},
            {"code": "NHTP", "name": "亢奋型焦虑", "oneline": "一边打鸡血，一边心慌慌"},
            {"code": "NHFI", "name": "元气哭包", "oneline": "白天哈哈哈，深夜嘤嘤嘤，早八照样起"},
            {"code": "NHFP", "name": "情绪过山车", "oneline": "上一秒嘻嘻，下一秒不嘻嘻"},
            {"code": "SBTI", "name": "低电量模式", "oneline": "节能运行中，请勿打扰"},
            {"code": "SBTP", "name": "摆烂哲学家", "oneline": "不是躺平，是与世界和解"},
            {"code": "SBFI", "name": "淡淡的", "oneline": "对什么都淡淡的，长期稳定地淡淡的"},
            {"code": "SBFP", "name": "人间小透明", "oneline": "存在感低，情绪也低，平稳地低"},
            {"code": "SHTI", "name": "体面崩溃人", "oneline": "哭都要挑时间，崩溃都按计划"},
            {"code": "SHTP", "name": "内耗大师", "oneline": "脑子里开了个批斗会，批的是自己"},
            {"code": "SHFI", "name": "深夜emo电台", "oneline": "凌晨准时开播，天亮自动闭麦"},
            {"code": "SHFP", "name": "破碎感本感", "oneline": "风一吹就碎，碎了还自己扫"}
        ],
        "easter_eggs": {
            "schrodinger": "薛定谔的精神状态",
            "hexagon": "满电六边形",
            "buddha": "精神活佛",
            "double": "早F晚E",
            "mouthpiece": "全网精神嘴替"
        },
        "scenes": [
            "周一早上：闹钟响第八遍、地铁人贴人、工位开机仪式",
            "深夜模式：刷手机停不下来、凌晨三点的胡思乱想",
            "ddl极限操作：死线前夜的爆发力、咖啡续命",
            "周末躺尸：48小时不下床、外卖盒堆成山",
            "两幅面孔：朋友圈精修vs现实、发工资前后对比",
            "返工综合征：节后第一天、假期余额焦虑"
        ]
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
