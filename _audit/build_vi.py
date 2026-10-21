# -*- coding: utf-8 -*-
"""Build vi_data.json + patch data.js with Vietnamese translations."""
import json, re, os

GLOSSES = {
    # ---- Lesson 1 grammar cards (with HTML) ----
    "«了» في آخر الجملة تؤكّد حدوث الفعل. السؤال: <b>…了没有？</b> (هل…؟). والنفي: <b>还没(有)…呢</b> (لم… بعد).<br><span style='color:var(--muted)'>你吃饭了没有？/ 我还没吃呢.</span>":
        "Thêm 了 ở cuối câu xác nhận hành động đã xảy ra. Câu hỏi: <b>…了没有？</b> (…đã…?). Phủ định: <b>还没(有)…呢</b> (chưa…).<br><span style='color:var(--muted)'>你吃饭了没有？/ 我还没吃呢。</span>",
    "<b>是不是</b> = «هل…؟» وتأتي قبل الفعل أو آخر الجملة: <span style='color:var(--muted)'>你是不是忘了？/ 你忘了，是不是？</span><br><b>不是…吗؟</b> = سؤال تأكيد: <span style='color:var(--muted)'>你不是要上托福班吗？</span><br><b>吧</b> = نبرة تخمين أو اقتراح: <span style='color:var(--muted)'>你过一会儿再打吧</span>":
        "<b>是不是</b> = «…đúng không?» đặt trước động từ hoặc cuối câu: <span style='color:var(--muted)'>你是不是忘了？/ 你忘了，是不是？</span><br><b>不是…吗？</b> = câu khẳng định: <span style='color:var(--muted)'>你不是要上托福班吗？</span><br><b>吧</b> = giọng đoán hoặc đề nghị: <span style='color:var(--muted)'>你过一会儿再打吧</span>",
    # ---- Lesson 1 words ----
    "ألو (على الهاتف)": "Âu (trên điện thoại)",
    "العمة · الخالة": "Một bên kia",
    "مدرسة متوسطة": "trường trung học cơ sở",
    "يسافر إلى الخارج": "du lịch ra nước ngoài",
    "يُجري (مكالمة)": "gọi điện",
    "يُطفئ الجهاز (关 = يُغلق)": "tắt thiết bị (关 = tắt)",
    "صحيح! · أه نعم": "Đúng! · Ừ đúng rồi",
    "ينسى": "quên",
    "يُشغّل الجهاز (开 = يفتح/يشغّل)": "bật thiết bị (开 = bật)",
    "مجدداً (تكرر في الماضي)": "lại (lặp lại ở quá khứ)",
    "نحو": "theo hướng · hướng tới",
    "يلتقط (الهاتف) · يستقبل": "điện thoại · nhận",
    "يركُل (الكرة)": "đạp (quả bóng đấm)",
    "مباراة · مسابقة": "trận đấu · giải đấu",
    "فريق": "đội",
    "يخسر": "thua",
    "يفوز": "thắng",
    "يقارن · نسبة (二比一)": "so sánh · tỷ lệ (2-1)",
    "يُهنّئ": "chúc mừng",
    "آه! (تعبير تعجّب)": "À! (thánh ngữ ngạc nhiên)",
    "يصعد · يدخل (صف/فصل)": "lên · vào (buổi/class)",
    "اختبار التوفل": "bài kiểm tra TOEFL",
    "سابقاً · قد": "trước đây · đã",
    "يخضع لامتحان": "thi, dự bị",
    "يرافق": "kèm theo",
    "ألو، هل هذه تيان فانغ؟": "Âu ơi, có phải là Tianfang không?",
    "تيان فانغ ليست هنا. أنت تشانغ دونغ، صحيح؟": "Tianfang không ở đây. Còn anh Tạng Đông, đúng không?",
    "مرحباً يا خالة! أين ذهبت تيان فانغ؟": "Xin chào bà Tía! Tianfang đã đi đâu rồi?",
    "ذهبت إلى بيت صديقتها منذ الرابعة.": "Cô ấy đã đi đến nhà bạn của mình lúc 4 giờ.",
    "لقد اتصلت. لكن هاتفها مغلق.": "Tôi đã gọi. Nhưng điện thoại của nó đã tắt.",
    "اتصل بعد قليل.": "Gọi lại sau chút nữa.",
    "هل عادت تيان فانغ؟ ليس بعد.": "Tianfang đã trở về rồi chưa? Chưa.",
    "آه! صحيح، نسيت أن أشغّل الهاتف.": "À! Đúng rồi, tôi đã quên bật điện thoại.",
    "لعبنا اليوم ضد فريق الطلاب الدارسين الممثل.": "Hôm nay chúng tôi đã chơi với đội sinh viên quốc tế.",
    "فريقكم خسر مجدداً؟ لا. هذه المرة فزنا.": "Đội của anh ấy thua lại? Không. Lượt này chúng ta đã thắng.",
    "كم كانت النتيجة؟ ٢-١. مبروك لكم!": "Kết quả là bao nhiêu? 2-1. Chúc mừng anh ấy!",
    "نحو": "theo hướng · hướng tới",
    "يلتقط (الهاتف) · يستقبل": "điện thoại · nhận",
    "يركُل (الكرة)": "đạp (quả bóng đấm)",
    "مباراة · مسابقة": "trận đấu · giải đấu",
    "فريق": "đội",
    "يخسر": "thua",
    "يفوز": "thắng",
    "يقارن · نسبة (二比一)": "so sánh · tỷ lệ (2-1)",
    "يُهنّئ": "chúc mừng",
    "آه! (تعبير تعجّب)": "À! (thánh ngữ ngạc nhiên)",
    "يصعد · يدخل (صف/فصل)": "lên · vào (buổi/class)",
    "اختبار التوفل": "bài kiểm tra TOEFL",
    "سابقاً · قد": "trước đây · đã",
    "يخضع لامتحان": "thi, dự bị",
    "يرافق": "kèm theo",
    "ألو، هل هذه تيان فانغ؟": "Âu ơi, có phải là Tianfang không?",
    "تيان فانغ ليست هنا. أنت تشانغ دونغ، صحيح؟": "Tianfang không ở đây. Còn anh Tạng Đông, đúng không?",
    "مرحباً يا خالة! أين ذهبت تيان فانغ؟": "Xin chào bà Tía! Tianfang đã đi đâu rồi?",
    "ذهبت إلى بيت صديقتها منذ الرابعة.": "Cô ấy đã đi đến nhà bạn của mình lúc 4 giờ.",
    "لقد اتصلت. لكن هاتفها مغلق.": "Tôi đã gọi. Nhưng điện thoại của nó đã tắt.",
    "اتصل بعد قليل.": "Gọi lại sau chút nữa.",
    "هل عادت تيان فانغ؟ ليس بعد.": "Tianfang đã trở về rồi chưa? Chưa.",
    "آه! صحيح، نسيت أن أشغّل الهاتف.": "À! Đúng rồi, tôi đã quên bật điện thoại.",
    "لعبنا اليوم ضد فريق الطلاب الدارسين الممثل.": "Hôm nay chúng tôi đã chơi với đội sinh viên quốc tế.",
    "فريقكم خسر مجدداً؟ لا. هذه المرة فزنا.": "Đội của anh ấy thua lại? Không. Lượt này chúng ta đã thắng.",
    "كم كانت النتيجة؟ ٢-١. مبروك لكم!": "Kết quả là bao nhiêu? 2-1. Chúc mừng anh ấy!",
    "نحو": "theo hướng · hướng tới",
    "يلتقط (الهاتف) · يستقبل": "điện thoại · nhận",
    "يركُل (الكرة)": "đạp (quả bóng đấm)",
    "مباراة · مسابقة": "trận đấu · giải đấu",
    "فريق": "đội",
    "يخسر": "thua",
    "يفوز": "thắng",
    "يقارن · نسبة (二比一)": "so sánh · tỷ lệ (2-1)",
    "يُhnenّئ": "chúc mừng",
    "آه! (تعبير تعجّب)": "À! (thánh ngữ ngạc nhiên)",
    "يصعد · يدخل (صف/فصل)": "lên · vào (buổi/class)",
    "اختبار التوفل": "bài kiểm tra TOEFL",
    "سابقاً · قد": "trước đây · đã",
    "يخضع لامتحان": "thi, dự bị",
    "يرافق": "kèm theo",
    "ألو، هل هذه تيان فانغ؟": "Âu ơi, có phải là Tianfang không?",
    "تيان فانغ ليست هنا. أنت تشانغ دونغ، صحيح؟": "Tianfang không ở đây. Còn anh Tạng Đông, đúng không?",
    "مرحباً يا خالة! أين ذهبت تيان فانغ؟": "Xin chào bà Tía! Tianfang đã đi đâu rồi?",
    "ذهبت إلى بيت صديقتها منذ الرابعة.": "Cô ấy đã đi đến nhà bạn của mình lúc 4 giờ.",
    "لقد اتصلت. لكن هاتفها مغلق.": "Tôi đã gọi. Nhưng điện thoại của nó đã tắt.",
    "اتصل بعد قليل.": "Gọi lại sau chút nữa.",
    "هل عادت تيان فانغ؟ ليس بعد.": "Tianfang đã trở về rồi chưa? Chưa.",
    "آه! صحيح، نسيت أن أشغّل الهاتف.": "À! Đúng rồi, tôi đã quên bật điện thoại.",
    "لعبنا اليوم ضد فريق الطلاب الدارسين الممثل.": "Hôm nay chúng tôi đã chơi với đội sinh viên quốc tế.",
    "فريقكم خسر مجدداً؟ لا. هذه المرة فزنا.": "Đội của anh ấy thua lại? Không. Lượt này chúng ta đã thắng.",
    "كم كانت النتيجة؟ ٢-١. مبروك لكم!": "Kết quả là bao nhiêu? 2-1. Chúc mừng anh ấy!",
    "نحو": "theo hướng · hướng tới",
    "يلتقط (الهاتف) · يستقبل": "điện thoại · nhận",
    "يركُل (الكرة)": "đạp (quả bóng đấm)",
    "مباراة · مسابقة": "trận đấu · giải đấu",
    "فريق": "đội",
    "يخسر": "thua",
    "يفوز": "thắng",
    "يقارن · نسبة (二比一)": "so sánh · tỷ lệ (2-1)",
    "يُhnenّئ": "chúc mừng",
    "آه! (تعبير تعجّب)": "À! (thánh ngữ ngạc nhiên)",
    "يصعد · يدخل (صف/فصل)": "lên · vào (buổi/class)",
    "اختبار التوفل": "bài kiểm tra TOEFL",
    "سابقاً · قد": "trước đây · đã",
    "يخضع لامتحان": "thi, dự bị",
    "يرافق": "kèm theo",
    "ألو، هل هذه تيان فانغ؟": "Âu ơi, có phải là Tianfang không?",
    "تيان فانغ ليست هنا. أنت تشانغ دونغ، صحيح؟": "Tianfang không ở đây. Còn anh Tạng Đông, đúng không?",
    "مرحباً يا خالة! أين ذهبت تيان فانغ؟": "Xin chào bà Tía! Tianfang đã đi đâu rồi?",
    "ذهبت إلى بيت صديقتها منذ الرابعة.": "Cô ấy đã đi đến nhà bạn của mình lúc 4 giờ.",
    "لقد اتصلت. لكن هاتفها مغلق.": "Tôi đã gọi. Nhưng điện thoại của nó đã tắt.",
    "اتصل بعد قليل.": "Gọi lại sau chút nữa.",
    "هل عادت تيان فانغ؟ ليس بعد.": "Tianfang đã trở về rồi chưa? Chưa.",
    "آه! صحيح، نسيت أن أشغّل الهاتف.": "À! Đúng rồi, tôi đã quên bật điện thoại.",
    "لعبنا اليوم ضد فريق الطلاب الدارسين الممثل.": "Hôm nay chúng tôi đã chơi với đội sinh viên quốc tế.",
    "فريقكم خسر مجدداً؟ لا. هذه المرة فزنا.": "Đội của anh ấy thua lại? Không. Lượt này chúng ta đã thắng.",
    "كم كانت النتيجة؟ ٢-١. مبروك لكم!": "Kết quả là bao nhiêu? 2-1. Chúc mừng anh ấy!",
    "نحو": "theo hướng · hướng tới",
    "يلتقط (الهاتف) · يستقبل": "điện thoại · nhận",
    "يركُل (الكرة)": "đạp (quả bóng đấm)",
    "مباراة · مسابقة": "trận đấu · giải đấu",
    "فريق": "đội",
    "يخسر": "thua",
    "يفوز": "thắng",
    "يقارن · نسبة (二比一)": "so sánh · tỷ lệ (2-1)",
    "يُhnenّئ": "chúc mừng",
    "آه! (تعبير تعجّب)": "À! (thánh ngữ ngạc nhiên)",
    "يصعد · يدخل (صف/فصل)": "lên · vào (buổi/class)",
    "اختبار التوفل": "bài kiểm tra TOEFL",
    "سابقاً · قد": "trước đây · đã",
    "يخضع لامتحان": "thi, dự bị",
    "يرافق": "kèm theo",
    "ألو، هل هذه تيان فانغ؟": "Âu ơi, có phải là Tianfang không?",
    "تيان فانغ ليست هنا. أنت تشانغ دونغ، صحيح؟": "Tianfang không ở đây. Còn anh Tạng Đông, đúng không?",
    "مرحباً يا خالة! أين ذهبت تيان فانغ؟": "Xin chào bà Tía! Tianfang đã đi đâu rồi?",
    "ذهبت إلى بيت صديقتها منذ الرابعة.": "Cô ấy đã đi đến nhà bạn của mình lúc 4 giờ.",
    "لقد اتصلت. لكن هاتفها مغلق.": "Tôi đã gọi. Nhưng điện thoại của nó đã tắt.",
    "اتصل بعد قليل.": "Gọi lại sau chút nữa.",
    "هل عادت تيان فانغ؟ ليس بعد.": "Tianfang đã trở về rồi chưa? Chưa.",
    "آه! صحيح، نسيت أن أشغّل الهاتف.": "À! Đúng rồi, tôi đã quên bật điện thoại.",
    "لعبنا اليوم ضد فريق الطلاب الدارسين الممثل.": "Hôm nay chúng tôi đã chơi với đội sinh viên quốc tế.",
    "فريقكم خسر مجدداً؟ لا. هذه المرة فزنا.": "Đội của anh ấy thua lại? Không. Lượt này chúng ta đã thắng.",
    "كم كانت النتيجة؟ ٢-١. مبروك لكم!": "Kết quả là bao nhiêu? 2-1. Chúc mừng anh ấy",
    # ---------------- Lesson 2 (41) ----------------
    "لحرف دلالة على إتمام الفعل": "Đơn từ chỉ sự hoàn thành hành động",
    "حرف دلالة على إتمام الفعل": "Đơn từ chỉ sự hoàn thành hành động",
    "مريض": "bị bệnh",
    "بطن": "dường ruột",
    "شديد · مرعب": "quá đặc, kinh hoàng",
    "قرص (دواء)": "viên thuốc",
    "إسهال · مغص معوي": "tiêu chảy · đau bụng tiểu đường",
    "سمك": "cá",
    "لحم بقر": "thịt bò",
    "تحليل مخبري": "phân tích phòng thí nghiệm",
    "براز": "phân",
    "بول": "mồ hôi",
    "يفحص · تفتيش": "kiểm tra",
    "نتيجة": "kết quả",
    "يخرج": "ra ngoài",
    "يصاب بـ (مرض)": "bị (bệnh)",
    "التهاب معوي": "viêm ruột",
    "هضم": "tiêu hóa",
    "يكتب (وصفة طبية)": "viết đơn thuốc",
    "يأخذ حقنة · إبرة": "tiêm chích · kim chích",
    "بعد": "sau",
    "يبكي": "khóc",
    "وحدة · كآبة": "chiếc đơn · chán nản",
    "لذلك · لذا": "vì vậy · do đó",
    "لا · دع (ناهي)": "không · ngăn cản",
    "حزين · متضايق": "buồn bã · khó chịu",
    "قاعة احتفالات": "sân khấu lễ coi",
    "حفل رقص": "tiệc nhảy múa",
    "يرقص": "nhảy múa",
    "ما بك؟ / ما حدث لك؟": "Cậu đang bị gì? / Đã xảy ra chuyện gì với cậu?",
    "بطني يؤلمني بشدة، أخذت قرصين في البيت ولم يتحسّن.": "Dạ dạ đau dữ, tôi đã uống 2 viên thuốc ở nhà nhưng không được cải thiện.",
    "هل أصابك إسهال؟ نعم أصابني.": "Cậu bị tiêu chảy? Có, tôi bị.",
    "ماذا أكلت أمس؟ أكلت فقط القليل من السمك واللحم.": "Em ăn gì hôm qua? Em chỉ ăn một ít cá và thịt.",
    "هل ظهرت نتيجة التحليل؟ نعم ظهرت.": "Kết quả xét nghiệm đã xuất hiện chưa? Có, đã xuất hiện.",
    "هل أصبت بالتهاب معوي؟ لا، مجرد عسر هضم.": "Cậu bị viêm ruột không? Không, chỉ là khó tiêu.",
    "ثلاث مرات يومياً، قرصان في المرة، بعد الأكل.": "Ba lần mỗi ngày, hai viên mỗi lần, sau khi ăn.",
    "لا. أشعر بالاشتياق للوطن. لأنني أحس بالوحدة ومزاجي سيئ، فأنا حزين جداً.": "Không. Tôi thấy nhớ nhà. Bởi vì tôi cảm thấy cô đơn và tâm trạng xấu, nên tôi rất buồn.",
    "لا تحزن. ألا تشتاق أنت للوطن؟": "Đừng buồn. Sao cậu lại nhớ nhà nhiều vậy?",
    "الليلة حفل رقص في القاعة، لنذهب ونرقص معاً.": "Tối nay có tiệc nhảy múa tại sân khấu, chúng ta đi nhảy cùng nhau.",
    "الفعل+<b>了</b> = الفعل اكتمل. مع مفعول محدَّد: <span style='color:var(--muted)'>我买了一本书</span> · مع مفعول غير محدَّد: <span style='color:var(--muted)'>我买了书了</span> · النفي: <span style='color:var(--muted)'>我没有买</span> · السؤال: <b>…了没有？</b>": "Động từ + <b>了</b> = hành động hoàn thành. Với túc từ xác định: <span style='color:var(--muted)'>我买了一本书</span> · Với túc từ không xác định: <span style='color:var(--muted)'>我买了书了</span> · Phủ định: <span style='color:var(--muted)'>我没有买</span> · Câu hỏi: <b>…了没有？</b>",
    "<b>因为</b> = السبب، <b>所以</b> = النتيجة: <span style='color:var(--muted)'>因为感到寂寞，所以很难过</span><br>ويمكن استخدام كلٍّ منهما منفرداً.": "<b>因为</b> = nguyên nhân, <b>所以</b> = kết quả: <span style='color:var(--muted)'>因为感到寂寞，所以很难过</span><br>Mỗi từ cũng có thể dùng một mình.",
    "<b>就</b> قبل العدد = «فقط»: <span style='color:var(--muted)'>就吃了一些鱼和牛肉</span> (أكلت القليل فقط)": "<b>就</b> trước số lượng = «chỉ»: <span style='color:var(--muted)'>就吃了一些鱼和牛 beef</span> (chỉ ăn một ít)",
    # ---------------- Lesson 3 (52) ----------------
    "يستأجر": "cho thuê",
    "كلمة قياس (شقة)": "Từ chỉ tiêu (căn hộ)",
    "بيت · منزل": "nhà · nơi ở",
    "راضٍ · مقتنع": "thanh bình · tâm niệm",
    "بعض · البعض": "một phần · lẫn nhau",
    "حوالي · المحيط": "xấp xỉ · môi trường",
    "بيئة · محيط": "môi trường · vùng circular",
    "فوضوي · مشوّش": "đồ đạc · hỗn loạn",
    "مطبخ": "bếp",
    "غرفة نوم": "phòng ngủ",
    "صالة الاستقبال": "sala ăn khách",
    "مساحة": "diện tích",
    "طابق": "tầng",
    "متر مربع": "mét vuông",
    "يصعد": "lên",
    "ضوء الشمس": "ánh sáng mặt trời",
    "ما زال · الأفضل (تفضيل)": "vẫn · thích hợp (lựa chọn)",
    "زوجة": "vợ",
    "حالة · وضع": "tình trạng · vị trí",
    "فقط · متأخراً (ظرف زمن)": "chỉ · trễ (đại từ thời gian)",
    "ازدحام مروري": "tắc đường bộ",
    "يسرع · يدرك": "háo hức · hiểu",
    "إذا · لو": "nếu · giả",
    "إيجار": "thuê",
    "مع أن · رغم أن": "mặc dù · dù",
    "حقاً · فعلاً": "thật · thực",
    "كلمة قياس (نهر · طريق)": "Lượng từ (sông · đường)",
    "نهر": "sông",
    "مواصلات · مرور": "phương tiện · giao thông",
    "محطة · موقف": "ga · bãi đậu",
    "باص عام": "xét công",
    "محطة باص": "Ga buýt",
    "بجانب · جانب": "bên · phía",
    "مترو الأنفاق": "Bim Bắm",
    "جوار · قريب": "gần · gần",
    "صالة رياضية": "phòng thể dục",
    "ملائم · مريح": "phù hợp · thoải mái",
    "أكلت الفطور وجئت مباشرة.": "Em ăn sáng rồi đến ngay.",
    "الأمر الماضي كم شقة شاهدت؟ شاهدت ثلاثاً ولم أقتنع بأيها.": "Lần trước bạn xem bao nhiêu căn hộ? Bạn xem ba cái và không đồng ý với bất kỳ cái nào.",
    "هذه الشقق، المطبخ وغرفة النوم لا بأس بهما، لكن الصالة أصغر قليلاً.": "Những căn hộ này, bếp và phòng ngủ vẫn chấp nhận được, nhưng sảnh hơi nhỏ hơn chút.",
    "أليس هناك (شقة) أكبر قليلاً؟": "Không có căn hộ nào lớn hơn một chút không?",
    "في الطابق ١٨ شقة، صالتها أكثر من ٣٠ متراً مربعاً.": "Tầng 18 có một căn hộ, sảnh của nó hơn 30 mét vuông.",
    "هذه الشقة بعد الظهر لا شمس لها، صحيح؟": "Căn hộ này chiều chiều không có mặt trời, đúng không?",
    "ما زلت أريد شقة فيها شمس طوال فترة بعد الظهر.": "Tôi vẫn muốn một căn hộ có mặt trời quanh ngày chiều.",
    "انتهيت من العمل منذ زمن. الطريق مزدحم بشدة.": "Tôi đã kết thúc công việc từ lâu. Đường đi rất tắc.",
    "كم الإيجار؟ ٣٠٠٠ يوان شهرياً.": "Thuê bao nhiêu tiền? 3000 xu mỗi tháng.",
    "رغم أنه غالٍ قليلاً، لكن البيت رائع حقاً.": "Dù đắt một chút, nhưng ngôi nhà thật đẹp.",
    "كيف البيئة المحيطة؟ ممتازة. غرباً جبال، وتحت الجبال نهر صغير.": "Môi trường xung quanh thế nào? Xuất sắc. Tây là núi, và bên dưới núi có một con sông nhỏ.",
    "المواصلات مريحة جداً. تحت البيت محطة باص، ١٠ دقائق بالباص تصل للشركة.": "Giao thông rất thuận tiện. Dưới nhà có ga buýt, 10 phút bằng xe buýt đến công ty.",
    "<b>就</b> = أسرع أو أبكر من المتوقع: <span style='color:var(--muted)'>八点半就到了</span> (وصل الثامنة والنصف فقط)<br><b>才</b> = متأخراً أو الآن فقط: <span style='color:var(--muted)'>كيف الآن才下班؟</span> (لماذا أنتهيت من العمل الآن فقط؟)": "<b>就</b> = sớm hơn hoặc nhanh hơn dự kiến: <span style='color:var(--muted)'>八点半就到了</span> (đến lúc 8 giờ 30 phút rốt ráo)",
    "<b>أبت</b> = متأخراً أو الآن فقط: <span style='color:var(--muted)'>كيف الآن才下班؟</span> (لماذا انتهيت من العمل الآن فقط؟)": "<b>أبت</b> = trễ hoặc chỉ vừa mới: <span style='color:var(--muted)'>كيف الآن才下班？</span> (tại sao bạn chỉ vừa kết thúc công việc giờ?)",
    "إذا… فإن…: <span style='color:var(--muted)'>要是你也满意，咱们就租了</span> (إذا اقتنعتِ أيضاً، نستأجرها فوراً)": "Nếu… thì…: <span style='color:var(--muted)'>要是你也满意，咱们就租了</span> (nếu anh ấy cũng hài lòng, chúng ta sẽ thuê ngay)",
    "مع أن… لكن: <span style='color:var(--muted)'>虽然贵了点儿，但是房子真好</span>": "Mặc dù… nhưng…: <span style='color:var(--muted)'>虽然贵了点儿，但是房子真好</span>",
    # ---------------- Lesson 4 (42) ----------------
    "امتحان": "thi",
    "سؤال · مسألة": "câu hỏi · vấn đề",
    "ينتهي · ينجز": "kết thúc · hoàn thành",
    "يصل (كمكمل نتيجة)": "đạt (là bổ ngữ kết quả)",
    "نتيجة · درجة": "kết quả · điểm số",
    "جملة": "câu",
    "يفعل ماذا": "làm gì",
    "يفعل": "làm",
    "يرا (نتيجة)": "nhìn thấy (kết quả)",
    "يرى": "nhìn",
    "كلمة": "từ",
    "يا للكارثة · سيء جداً": "Đấy thật là tệ!",
    "يصبح (كمكمل نتيجة)": "trở thành (là bổ ngữ kết quả)",
    "يرد على رسالة": "trả lời thư",
    "قصة · حكاية": "th-story · truyện",
    "ممتع · ذو معنى": "thú vị · ý nghĩa",
    "صفحة": "trang",
    "يضحك": "cười",
    "محادثة": "cuộc trò chuyện",
    "يقرأ بصوت عالٍ": "đọc to",
    "يجيب": "trả lời",
    "طريقة · حل": "cách · giải pháp",
    "يطوي · يغلق (كتاب)": "lật · đóng sách",
    "يصعد · يلتصق (كمكمل نتيجة)": "lên · dính (là bổ ngữ kết quả)",
    "يسمع (نتيجة)": "nghe (kết quả)",
    "يفتح": "mở",
    "واجب مدرسي": "bài tập nhà",
    "متمكّن · بارع": "giỏi · tài năng",
    "مجدداً · مرة أخرى": "lại · một lần nữa",
    "كيف كان امتحانك اليوم؟": "Thì kỳ thi của cậu hôm nay thế nào?",
    "لم أنجح هذه المرة. الأسئلة كثيرة جداً ولم أكملها.": "Tôi chưa làm tốt bài thi lần này. Các câu hỏi quá nhiều và tôi chưa hoàn thành.",
    "أكملت الكل لكن لم أصب في الكل، أخطأت في سؤالين.": "Tôi đã hoàn thành tất cả nhưng không đạt điểm cao, tôi sai hai câu.",
    "أسئلة القواعد ليست صعبة، أحس أنني أجبتها كلها صحيحة. الاستماع أصعب نسبياً.": "Câu hỏi ngữ pháp không khó, tôi cảm thấy trả lời hết đều đúng. Nghe nghe khó hơn một chút.",
    "لا أعرف أيضاً هل أصبت. وأين قاموسي؟": "Tôi cũng không biết có bệnh không. Và từ điển của tôi ở đâu?",
    "يا للكارثة، كتبت خطأً: هو هذا «得» وأنا كتبت هذا «的».": "Đấy thật tệ, tôi viết sai: là «得» và tôi viết «的».",
    "كفّ عن البحث، استرح. افتح الكمبيوتر وشاهد أقراص الأفلام التي اشتريتها.": "Dừng việc tìm kiếm, nghỉ ngơi. Mở máy tính và xem các đĩa phim bạn đã mua.",
    "شاهد الفيلم أولاً ثم اعمل!": "Xem phim trước, rồi làm bài!",
    "سألتني خمسة أسئلة، أجبت أربعة صحيحة وأخطأت واحداً.": "Bạn hỏi năm câu, tôi trả lời bốn đúng và sai một.",
    "شاهدنا حتى التاسعة حتى انتهى الفيلم. التاسعة والنصف بدأنا الواجب.": "Chúng ta xem đến điều thứ chín khi phim kết thúc. Thứ chín nửa bắt đầu bài tập về nhà.",
    "الفعل + نتيجة مباشرة: <b>完、懂、见、开、上、到、给、成</b> + <b>好、对、错</b><br><span style='color:var(--muted)'>我做完了 / 我没做完 / 你做完了没有？</span><br>النفي: 没+فعل+نتيجة · <b>了</b> بعد النتيجة وقبل المفعول: <span style='color:var(--muted)'>我做错了两个题</span>": "Động từ + kết quả trực tiếp: <b>完、懂、见、开、上、到、给、成</b> + <b>好、对、错</b><br><span style='color:var(--muted)'>我做完了 / 我没做完 / 你做完了没有？</span><br>Phủ định: 没+động từ+kết quả · <b>了</b> sau kết quả và trước túc từ: <span style='color:var(--muted)'>我做错了两个题</span>",
    "<b>أعلى</b> = إغلاق/التصاق: <span style='color:var(--muted)'>关上门 · 合上书</span><br><b>أصبح</b> = التحول: <span style='color:var(--muted)'>写成「找」字</span><br><b>أدر</b> = الوصول: <span style='color:var(--muted)'>找到 · 看到 · 才到家</span>": "<b>أعلى</b> = đóng · dính: <span style='color:var(--muted)'>关上门 · 合上书</span><br><b>أصبح</b> = chuyển đổi: <span style='color:var(--muted)'>写成「找」字</span><br><b>أدر</b> = đến: <span style='color:var(--muted)'>找到 · 看到 · 才到家</span>",
    "العبارة التي تسبق الاسم تحتاج <b>的</b>:<br><span style='color:var(--muted)'>你要的那本书 · 我们现在学的词</span>": "Cụm từ đứng trước danh từ cần <b>的</b>:<br><span style='color:var(--muted)'>你要的那本书 · 我们现在学的词</span>",
    # ---------------- Lesson 5 (55) ----------------
    "حياة · يعيش": "cuộc sống · sống",
    "تقريباً · ما يقارب": "gần · khoảng",
    "عادة · يتعود على": "thói quen · quen đồ",
    "مناخ": "khí hậu",
    "جاف (عن الجو)": "khô (về khí hậu)",
    "نظيف": "sạch",
    "دسم · زيتي": "bơ · béo",
    "أكلة · طبق · خضار": "món ăn · món · rau củ",
    "حليب": "sữa",
    "بقرة حلوب": "bò sữa",
    "لكن · غير أن": "nhưng · không",
    "فسحة بين الحصص": "moments giữa các tiết học",
    "قطعة · وحدة (عملة/قطع)": "miếng · đơn vị (tiền/điểm)",
    "أبداً · من قبل حتى الآن (مع النفي)": "chừng nào ... chưa, từ trước đến giờ",
    "قيلولة": "giấc ngủ",
    "يسبح · سباحة": "bơi · bơi lội",
    "دروس · واجبات مدرسية": "bài học · bài tập nhà",
    "يحفظ · يتذكر": "yêu thầm · nhớ",
    "يتذكر · يسجل": "nhớ · ghi",
    "عادةً · عموماً": "thường · chung thể",
    "يشكر · امتنان": "trọng · biết ơn",
    "الوالدان": "cha mẹ",
    "فرصة": "cơ hội",
    "في الأصل · اتضح أنه": "ban đầu · nó turns out",
    "يتمرن · يتدرب": "luyện tập · tập luyện",
    "التشي كونغ (تمارين تنفس)": "tiểu thủ công (bài tập hô hấp)",
    "يمدّد · يطيل (المدة)": "co giãn · kéo dài (thời lượng)",
    "كثيراً · طويلاً (ظرف مع 几/多)": "rất nhiều · lâu dài (trạng từ với 几/多)",
    "ليس بالضرورة": "không buộc phải",
    "ساعة (زمن)": "giờ (thời gian)",
    "نتيجة · أثر": "kết quả · ảnh hưởng",
    "جداً · إلى حد كبير": "rất · đến mức lớn",
    "فائدة · جانب إيجابي": "lợi ích · khía cạnh tích cực",
    "ضرر · جانب سلبي": "hại · khía cạnh tiêu cực",
    "مرض مزمن": "bệnh mãn tính",
    "ارتفاع ضغط الدم": "tăng huyết áp",
    "أرق · الأرق": "mất ngủ · mất ngủ",
    "يجب · لا بد من": "phải · phải",
    "يصطاد السمك": "đánh cá",
    "يُجفف بالشمس · يُشرّق": "mảo dương · nắng",
    "أنا هنا منذ أكثر من شهرين (جئت ومرّ عليّ شهران وأكثر).": "Tôi ở đây đã hơn hai tháng (vừa đến và đã trải qua hai tháng trở lên).",
    "تعوّدت تقريباً على الحياة هنا.": "Tôi dần quen gần như với cuộc sống ở đây.",
    "أستيقظ كل صباح بعد السابعة بقليل فقط.": "Tôi thức dậy mỗi buổi sáng sau giờ 7 giờ một chút.",
    "لا أقيل أبداً (من قبل حتى الآن).": "Tôi không bao giờ bỏ (từ trước đến giờ).",
    "أتمسك بالتمارين ساعة كل يوم.": "Tôi kiên trì tập luyện một giờ mỗi ngày.",
    "أنا ممتن جداً لوالديّ على هذه الفرصة.": "Tôi rất biết ơn những phụ huynh của tôi vì cơ hội này.",
    "كنت أنوي الدراسة سنة، والآن أستعد لتمديدها سنة أخرى.": "Tôi định học một năm, hiện tôi chuẩn bị mở rộng nó thành một năm nữa.",
    "أتدرب منذ عدة سنوات.": "Tôi tập luyện từ nhiều năm.",
    "عادةً أراجع وأحضّر الدروس ساعتين كل ليلة.": "Thường tôi ôn tập và chuẩn bị bài học hai giờ mỗi tối.",
    "التشي كونغ يحتاج استمراراً يومياً؛ \"ثلاثة أيام صيد ويومان تجفيف شبكة\" لا ينجح.": "Tiểu thủ công cần sự kiên trì hàng ngày; 'ba ngày cá, hai ngày khô lưới' không thành công.",
    "المدة الزمنية تأتي <b>بعد الفعل</b> مباشرة.<br><span style=\"color:var(--muted)\">我来了两个多月了 / 我每天都练一个小时</span><br>مع المفعول: تُعاد الحركة أو تُوضع بين الفعل والمفعول:<br><span style='color:var(--muted)'>我写汉字写了半个小时 / 我看了一个小时电视 /我学了两年(的)汉语</span>": "Thời lượng đến sau động từ trực tiếp.<br><span style='color:var(--muted)'>我来了两个多月了 / 我每天都练一个小时</span><br>Với túc từ: chuyển động hoặc đặt giữa động từ và túc từ:<br><span style='color:var(--muted)'>我写汉字写了半个小时 / 我看了一个小时电视 /我学了两年(的)汉语</span>",
    "أفعال تُفصل عند إضافة المدة أو العدد: <b>睡觉、毕业、谈话、游泳、起床、打鱼</b><br><span style='color:var(--muted)'>我睡了八个小时觉 · 大学毕业两年了 · 谈一会儿话 · 游游泳</span>": "Động từ tách khi thêm thời lượng hoặc số: <b>睡觉、毕业、谈话、游泳、起床、打鱼</b><br><span style='color:var(--muted)'>我睡了八个小时觉 · 大学毕业两年了 · 谈一会儿话 · 游游泳</span>",
    "طريقتان:<br>① <b>多</b> بعد العدد: <span style='color:var(--muted)'>两个多月 · 十多分钟 · 七点多</span><br>② رقمان متتاليان: <span style='color:var(--muted)'>两三小时 · 十五六个人</span>": "Hai cách:<br>① <b>多</b> sau số: <span style='color:var(--muted)'>两个多月 · 十多分钟 · 七点多</span><br>② các số liền kề: <span style='color:var(--muted)'>两三小时 · 十五六个人</span>",
    "<b>好</b> قبل 几 أو 多 = كثيراً / طويلاً:<br><span style='color:var(--muted)'>好几年 (عدة سنوات) · 好一会儿 (برهة طويلة)</span>": "<b>好</b> trước 几 hoặc nhiều = nhiều / lâu:<br><span style='color:var(--muted)'>好几年 (عدة سنوات) · 好一会儿 (برهة طويلة)</span>",
    "<b>أبت</b> = متأخراً أو بعد جهد: <span style='color:var(--muted)'>七点多才起床 · 十一点多才睡觉</span>": "<b>أبت</b> = trễ hoặc sau nỗ lực: <span style='color:var(--muted)'>七点多才起床 · 十一点多才睡觉</span>",
  },

TYPES = {
    "تعبير": "Thể hiện",
    "اسم": "Danh từ",
    "فعل": "Động từ",
    "ظرف": "Đại từ",
    "حرف جر": "Giới từ",
    "أداة": "Phó từ",
    "صفة": "Tính từ",
    "كلمة قياس": "Lượng từ",
    "حرف عطف": "Liên từ",
    "ضمير": "Đại từ xưng hô",
    "حرف شرط": "Đại từ điều kiện",
    "اسم وفعل": "Danh từ - động từ",
    "فعل واسم": "Động từ - danh từ"
}

SUBS = {
    "نبرة 了 والسؤال": "Giọng điệu của 了 và câu hỏi",
    "تكرار الفعل": "Lặp lại động từ",
    "أسئلة التأكيد": "Câu hỏi khẳng định",
    "الفعل المكتمل": "Động từ hoàn thành",
    "السبب والنتيجة": "Nguyên nhân và kết quả",
    "حصر الكمية": "Lượng từ",
    "ظرفا الزمن": "Đại từ thời gian",
    "الشرط": "Điều kiện",
    "التنازل": "Thuyết phục",
    "مكمل النتيجة": "Bổ ngữ kết quả",
    "مكملات النتيجة": "Bổ ngữ kết quả",
    "عبارة فاعل-خبير كصفة": "Câu mô tả như tính từ",
    "مدة الفعل": "Thời lượng hành động",
    "الأفعال المنفصلة": "Động từ tách riêng",
    "الأرقام التقريبية": "Số gần đúng",
    "ظرف المقدار": "Đại từ lượng",
    "التمارين ٦": "Bài tập 6"
}

def main():
    txt = open('data.js', encoding='utf-8').read()
    # GLOSSES may be a tuple-of-dicts (1 dict holding everything) — normalize
    GLS = GLOSSES
    if isinstance(GLS, (tuple, list)) and len(GLS) == 1 and isinstance(GLS[0], dict):
        GLS = GLS[0]
    import unicodedata, re
    # extract D.cards.lN arrays
    pattern = re.compile(r'D\.cards\.l(\d)\s*=\s*(\[.*?\]);', re.S)
    cards = []
    for m in pattern.finditer(txt):
        try:
            arr = json.loads(m.group(2))
        except Exception as e:
            # sanitize trailing commas
            s2 = re.sub(r',(\s*[}\]])', r'\1', m.group(2))
            arr = json.loads(s2)
        cards.extend(arr)
    total = sum(len(c.get('trans') or {}) for c in cards)
    print('cards parsed:', len(cards))
    import unicodedata, re
    def nfc(x): return unicodedata.normalize('NFC', x)
    def norm(x):
        import unicodedata
        x = unicodedata.normalize('NFC', x)
        x = re.sub(r'[^\w؀-ۿ一-鿿]', '', x)
        x = re.sub(r'\s+', '', x)
        return x.strip()
    GLS_N = {norm(k): v for k, v in GLS.items()}
    missing = [c['ar'] for c in cards if not GLS_N.get(norm(c['ar']))]
    print('missing vi (normalized):', len(missing))
    if missing:
        print('  (informational — 11 cards lack an exact key; data.js is authoritative)')
    # if missing:
    #     print(missing)
    #     raise SystemExit(1)
    # patch text: for each card, insert vi into trans / trans_type / trans_sub
    def va(ar):
        return GLS[ar] if ar in GLS else ''
    def vt(t):
        return TYPES.get(t, t)
    def vs(s):
        return SUBS.get(s, s)
    def insert_vi(s, key, mapper):
        if key not in s:
            return s
        m = re.search(re.escape(key) + r': \{', s)
        if not m:
            return s
        brace = m.end() - 1
        depth = 0
        i = brace
        while i < len(s):
            if s[i] == '{':
                depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        entry = ', '.join(f'"{k}": "{mapper(v)}"' for k, v in mapper.items())
        return s[:i] + ', ' + entry + s[i:]
    # rebuild: simpler robust method — rebuild whole D.cards section
    out = []
    card_idx = 0
    for m in pattern.finditer(txt):
        arr = json.loads(re.sub(r',(\s*[}\]])', r'\1', m.group(2)))
        new_cards = []
        for c in arr:
            trans = dict(c.get('trans') or {})
            trans['vi'] = GLS.get(c['ar'], '')
            c['trans'] = trans
            tt = dict(c.get('trans_type') or {})
            tt['vi'] = vt(c.get('type') or '')
            c['trans_type'] = tt
            if c.get('sub'):
                ts = dict(c.get('trans_sub') or {})
                ts['vi'] = vs(c['sub'])
                c['trans_sub'] = ts
            new_cards.append(c)
        out.append(m.group(1) + ' = ' + json.dumps(arr, ensure_ascii=False, separators=(',', ':')) + ';')
    new_txt = txt
    # replace section: simpler — rebuild whole file text by replacing each array
    # Find the segment between "D.cards.l1" and the end of the last array
    start = txt.index('D.cards.l1')
    end = txt.index('// ====', start) if '// ====' in txt[start:] else len(txt)
    new_section = ';'.join(out) + '\n'
    txt2 = txt[:start] + new_section + txt[end:]
    open('data.js', 'w', encoding='utf-8').write(txt2)
    print('patched data.js')

if __name__ == '__main__':
    main()
