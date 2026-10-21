# -*- coding: utf-8 -*-
# Phase 3: Indonesian (id) translations builder for r3d-flashcards
# Adds trans.id + trans_type.id + trans_sub.id to all 229 cards in data.js
import io, json, re, sys

# ---- Indonesian gloss per card, keyed by "front||ar" (unique per card) ----
G = {}

def add(front, ar, idtxt):
    G[front + '||' + ar] = idtxt

# ================= LESSON 1 =================
add('喂', 'ألو (على الهاتف)', 'Halo (di telepon)')
add('阿姨', 'العمة · الخالة', 'Bibi (saudara ibu)')
add('中学', 'مدرسة متوسطة', 'Sekolah menengah')
add('出国', 'يسافر إلى الخارج', 'Pergi ke luar negeri')
add('打(电话)', 'يُجري (مكالمة)', 'Menelepon (membuat panggilan)')
add('关机', 'يُطفئ الجهاز (关 = يُغلق)', 'Mematikan perangkat (关 = menutup/mematikan)')
add('对了', 'صحيح! · أه نعم', 'Benar! · Oh ya')
add('忘', 'ينسى', 'Lupa')
add('开机', 'يُشغّل الجهاز (开 = يفتح/يشغّل)', 'Menghidupkan perangkat (开 = membuka/menghidupkan)')
add('又', 'مجدداً (تكرر في الماضي)', 'Lagi (pengulangan di masa lalu)')
add('向', 'نحو', 'Ke arah · menuju')
add('接', 'يلتقط (الهاتف) · يستقبل', 'Mengangkat (telepon) · menerima')
add('踢', 'يركُل (الكرة)', 'Menendang (bola)')
add('比赛', 'مباراة · مسابقة', 'Pertandingan · kompetisi')
add('队', 'فريق', 'Tim')
add('输', 'يخسر', 'Kalah')
add('赢', 'يفوز', 'Menang')
add('比', 'يقارن · نسبة (二比一)', 'Membandingkan · skor (二比一)')
add('祝贺', 'يُهنّئ', 'Memberi selamat')
add('哎', 'آه! (تعبير تعجّب)', 'Aduh! (seruan kagum)')
add('上', 'يصعد · يدخل (صف/فصل)', 'Naik · masuk (kelas)')
add('托福', 'اختبار التوفل', 'Tes TOEFL')
add('已经', 'سابقاً · قد', 'Sudah · telah')
add('考', 'يخضع لامتحان', 'Mengikuti ujian')
add('陪', 'يرافق', 'Menemani')
add('喂，是田芳吗؟', 'ألو، هل هذه تيان فانغ؟', 'Halo, apakah ini Tianfang?')
add('田芳不在。是张东吧。', 'تيان فانغ ليست هنا. أنت تشانغ دونغ، صحيح؟', 'Tianfang tidak ada. Kamu Zhangdong, kan?')
add('阿姨，您好！田芳去哪儿了؟', 'مرحباً يا خالة! أين ذهبت تيان فانغ؟', 'Halo, Bibi! Tianfang pergi ke mana?')
add('她四点就去同学家了。', 'ذهبت إلى بيت صديقتها منذ الرابعة.', 'Dia pergi ke rumah temannya jam empat.')
add('我打了。可是她关机了。', 'لقد اتصلت. لكن هاتفها مغلق.', 'Aku sudah menelepon. Tapi ponselnya mati.')
add('你过一会儿再打吧。', 'اتصل بعد قليل.', 'Telepon lagi nanti saja.')
add('田芳回来了没有？还没有呢。', 'هل عادت تيان فانغ؟ ليس بعد.', 'Apakah Tianfang sudah pulang? Belum.')
add('啊！对了，我忘开机了。', 'آه! صحيح، نسيت أن أشغّل الهاتف.', 'Ah! Benar, aku lupa menyalakan ponsel.')
add('今天我们跟留学生代表队比赛了。', 'لعبنا اليوم ضد فريق الطلاب الدارسين الممثل.', 'Hari ini kami bertanding melawan tim perwakilan mahasiswa internasional.')
add('你们队又输了吧？没有。这次我们赢了。', 'فريقكم خسر مجدداً؟ لا. هذه المرة فزنا.', 'Tim kalian kalah lagi, kan? Tidak. Kali ini kami menang.')
add('几比几？二比一。祝贺你们！', 'كم كانت النتيجة؟ ٢-١. مبروك لكم!', 'Skornya berapa? Dua banding satu. Selamat!')
add('了…没有؟ / 还没…呢', '«了» في آخر الجملة تؤكّد حدوث الفعل. السؤال: <b>…了没有؟</b> (هل…؟). والنفي: <b>还没(有)…呢</b> (لم… بعد).<br><span style=\'color:var(--muted)\'>你吃饭了没有؟/ 我还没吃呢.</span>', '«了» di akhir kalimat menegaskan suatu tindakan telah terjadi. Pertanyaan: <b>…了没有؟</b> (Apakah…?). Negasi: <b>还没(有)…呢</b> (belum…).<br><span style=\'color:var(--muted)\'>你吃饭了没有？/ 我还没吃呢.</span>')
add('又 vs 再', '<b>又</b> = الفعل تكرّر في الماضي: <span style=\'color:var(--muted)\'>他昨天来，今天又来了</span><br><b>再</b> = التكرار في المستقبل (لم يحدث بعد): <span style=\'color:var(--muted)\'>明天再来</span>', '<b>又</b> = tindakan terjadi berulang di masa lalu: <span style=\'color:var(--muted)\'>他昨天来，今天又来了</span><br><b>再</b> = pengulangan di masa depan (belum terjadi): <span style=\'color:var(--muted)\'>明天再来</span>')
add('是不是 / 不是…吗؟ / 吧', '<b>是不是</b> = «هل…؟» وتأتي قبل الفعل أو آخر الجملة: <span style=\'color:var(--muted)\'>你是不是忘了؟/ 你忘了،是不是؟</span><br><b>不是…吗؟</b> = سؤال تأكيدي: <span style=\'color:var(--muted)\'>你不是要上托福班吗؟</span><br><b>吧</b> = نبرة تخمين أو اقتراح: <span style=\'color:var(--muted)\'>你过一会儿再打吧</span>', '<b>是不是</b> = «apakah…?» diletakkan sebelum kata kerja atau di akhir kalimat: <span style=\'color:var(--muted)\'>你是不是忘了？/ 你忘了，是不是؟</span><br><b>不是…吗؟</b> = pertanyaan konfirmasi: <span style=\'color:var(--muted)\'>你不是要上托福班吗؟</span><br><b>吧</b> = nada dugaan atau usulan: <span style=\'color:var(--muted)\'>你过一会儿再打吧</span>')

# ================= LESSON 2 =================
add('了', 'حرف دلالة على إتمام الفعل', 'Partikel penanda tindakan selesai')
add('病人', 'مريض', 'Pasien · orang sakit')
add('肚子', 'بطن', 'Perut')
add('厉害', 'شديد · مرعب', 'Heibatt · parah')
add('片', 'قرص (دواء)', 'Butir (obat)')
add('拉肚子', 'إسهال · مغص معوي', 'Diare · kram perut')
add('鱼', 'سمك', 'Ikan')
add('牛肉', 'لحم بقر', 'Daging sapi')
add('化验', 'تحليل مخبري', 'Tes laboratorium')
add('大便', 'براز', 'Feses · tinja')
add('小便', 'بول', 'Urine')
add('检查', 'يفحص · تفتيش', 'Memeriksa')
add('结果', 'نتيجة', 'Hasil')
add('出来', 'يخرج', 'Keluar · muncul')
add('得', 'يصاب بـ (مرض)', 'Kena (penyakit)')
add('肠炎', 'التهاب معوي', 'Radang usus')
add('消化', 'هضم', 'Mencerna · pencernaan')
add('开(药)', 'يكتب (وصفة طبية)', 'Menulis (resep obat)')
add('打针', 'يأخذ حقنة · إبرة', 'Suntik · jarum')
add('后', 'بعد', 'Sesudah')
add('哭', 'يبكي', 'Menangis')
add('寂寞', 'وحدة · كآبة', 'Kesepian · kesuraman')
add('所以', 'لذلك · لذا', 'Jadi · karena itu')
add('别', 'لا · دع (ناهي)', 'Jangan · larangan')
add('难过', 'حزين · متضايق', 'Sedih · terganggu')
add('礼堂', 'قاعة احتفالات', 'Aula')
add('舞会', 'حفل رقص', 'Pesta dansa')
add('跳舞', 'يرقص', 'Menari')
add('你怎么了？', 'ما بك؟ / ما حدث لك؟', 'Ada apa? / Apa yang terjadi denganmu?')
add('肚子疼得厉害，在家吃了两片药，还不行。', 'بطني يؤلمني بشدة، أخذت قرصين في البيت ولم يتحسّن.', 'Perutku sakit sekali, di rumah minum dua butir obat, masih tidak mempan.')
add('拉肚子了吗？拉了。', 'هل أصابك إسهال؟ نعم أصابني.', 'Apakah kamu diare? Ya.')
add('昨天吃什么了？就吃了一些鱼和牛肉。', 'ماذا أكلت أمس؟ أكلت فقط القليل من السمك واللحم.', 'Kemarin makan apa? Hanya makan sedikit ikan dan daging sapi.')
add('化验结果出来了吗？出来了。', 'هل ظهرت نتيجة التحليل؟ نعم ظهرت.', 'Apakah hasil tes sudah keluar? Sudah.')
add('我是不是得了肠炎؟不是肠炎，只是消化不好。', 'هل أصبت بالتهاب معوي؟ لا، مجرد عسر هضم.', 'Apakah aku kena radang usus? Bukan radang usus, hanya pencernaan kurang baik.')
add('一天三次،一次两片،饭后吃。', 'ثلاث مرات يومياً، قرصان في المرة، بعد الأكل.', 'Tiga kali sehari, dua butir setiap kali, dimakan setelah makan.')
add('不是。想家了。因为感到寂寞，心情不好，所以很难过。', 'لا. أشعر بالاشتياق للوطن. لأنني أحس بالوحدة ومزاجي سيئ، فأنا حزين جداً.', 'Tidak. Aku rindu rumah. Karena merasa kesepian dan suasana hatiku buruk, jadi sangat sedih.')
add('别难过了。你不想家吗؟', 'لا تحزن. ألا تشتاق أنت للوطن؟', 'Jangan sedih. Apakah kamu tidak rindu rumah?')
add('今天晚上礼堂有舞会，我们一起去跳跳舞吧。', 'الليلة حفل رقص في القاعة، لنذهب ونرقص معاً.', 'Malam ini ada pesta dansa di aula, mari kita pergi menari bersama.')
add('动词 + 了', 'الفعل+<b>了</b> = الفعل اكتمل. مع مفعول محدَّد: <span style=\'color:var(--muted)\'>我买了一本书</span> · مع مفعول غير محدَّد: <span style=\'color:var(--muted)\'>我买了书了</span> · النفي: <span style=\'color:var(--muted)\'>我没有买</span> · السؤال: <b>…了没有؟</b>', 'Kata kerja + <b>了</b> = tindakan selesai. Dengan objek tertentu: <span style=\'color:var(--muted)\'>我买了一本书</span> · Dengan objek tidak tertentu: <span style=\'color:var(--muted)\'>我买了书了</span> · Negasi: <span style=\'color:var(--muted)\'>我没有买</span> · Pertanyaan: <b>…了没有؟</b>')
add('因为…所以…', '<b>因为</b> = السبب، <b>所以</b> = النتيجة: <span style=\'color:var(--muted)\'>因为感到寂寞，所以很难过</span><br>ويمكن استخدام كلٍّ منهما منفرداً.', '<b>因为</b> = sebab, <b>所以</b> = akibat: <span style=\'color:var(--muted)\'>因为感到寂寞，所以很难过</span><br>Masing-masing juga bisa dipakai sendirian.')
add('就 (القليل)', '<b>就</b> قبل العدد = «فقط»: <span style=\'color:var(--muted)\'>就吃了一些鱼和牛肉</span> (أكلت القليل فقط)', '<b>就</b> sebelum jumlah = «hanya»: <span style=\'color:var(--muted)\'>就吃了一些鱼和牛肉</span> (hanya makan sedikit)')

# ================= LESSON 3 =================
add('租', 'يستأجر', 'Menyewa')
add('套', 'كلمة قياس (شقة)', 'Kata penggolong (apartemen)')
add('房子', 'بيت · منزل', 'Rumah · hunian')
add('满意', 'راضٍ · مقتنع', 'Puas · cocok')
add('有的', 'بعض · البعض', 'Sebagian · ada yang')
add('周围', 'حوالي · المحيط', 'Sekitar · lingkungan')
add('环境', 'بيئة · محيط', 'Lingkungan · sekitar')
add('乱', 'فوضوي · مشوّش', 'Berantakan · kacau')
add('厨房', 'مطبخ', 'Dapur')
add('卧室', 'غرفة نوم', 'Kamar tidur')
add('客厅', 'صالة الاستقبال', 'Ruang tamu')
add('面积', 'مساحة', 'Luas')
add('层', 'طابق', 'Lantai')
add('平方米', 'متر مربع', 'Meter persegi')
add('上去', 'يصعد', 'Naik')
add('阳光', 'ضوء الشمس', 'Sinar matahari')
add('还是', 'ما زال · الأفضل (تفضيل)', 'Tetap · lebih suka (preferensi)')
add('妻子', 'زوجة', 'Istri')
add('情况', 'حالة · وضع', 'Situasi · keadaan')
add('才', 'فقط · متأخراً (ظرف زمن)', 'Baru · terlambat (adverbia waktu)')
add('堵车', 'ازدحام مروري', 'Kemacetan lalu lintas')
add('赶', 'يسرع · يدرك', 'Buru-buru · mengejar')
add('要是', 'إذا · لو', 'Kalau · seandainya')
add('房租', 'إيجار', 'Sewa rumah')
add('虽然', 'مع أن · رغم أن', 'Meskipun · walaupun')
add('真', 'حقاً · فعلاً', 'Benar-benar · sungguh')
add('条', 'كلمة قياس (نهر · طريق)', 'Kata penggolong (sungai · jalan)')
add('河', 'نهر', 'Sungai')
add('交通', 'مواصلات · مرور', 'Transportasi · lalu lintas')
add('站', 'محطة · موقف', 'Stasiun · halte')
add('公共汽车', 'باص عام', 'Bus umum')
add('车站', 'محطة باص', 'Terminal bus')
add('旁边', 'بجانب · جانب', 'Sebelah · samping')
add('地铁', 'مترو الأنفاق', 'Kereta bawah tanah')
add('附近', 'جوار · قريب', 'Sekitar · dekat')
add('体育馆', 'صالة رياضية', 'Gedung olahraga')
add('方便', 'ملائم · مريح', 'Nyaman · praktis')
add('我吃了早饭就来了。', 'أكلت الفطور وجئت مباشرة.', 'Aku sarapan lalu langsung datang.')
add('上次您看了几套房子؟看了三套，都不是太满意。', 'المرة الماضية كم شقة شاهدت؟ شاهدت ثلاثاً ولم أقتنع بأيها.', 'Tadi sudah lihat berapa apartemen? Sudah lihat tiga, tidak cocok yang mana pun.')
add('这几套房子，厨房،卧室还可以，但是客厅面积小了一点。', 'هذه الشقق، المطبخ وغرفة النوم لا بأس بهما، لكن الصالة أصغر قليلاً.', 'Apartemen ini, dapur dan kamar tidurnya tidak apa-apa, tetapi ruang tamunya agak kecil.')
add('有没有大一点的？', 'أليس هناك (شقة) أكبر قليلاً؟', 'Apakah tidak ada yang sedikit lebih besar?')
add('楼上18层有一套，客厅30多平方米。', 'في الطابق ١٨ شقة، صالتها أكثر من ٣٠ متراً مربعاً.', 'Di lantai 18 ada satu apartemen, ruang tamunya lebih dari 30 meter persegi.')
add('这套房子下午就没有阳光了吧؟', 'هذه الشقة بعد الظهر لا شمس لها، صحيح؟', 'Apartemen ini siang hari tidak ada mataharinya, ya?')
add('我还是想要下午都有阳光的。', 'ما زلت أريد شقة فيها شمس طوال فترة بعد الظهر.', 'Aku tetap mau apartemen yang kena matahari sepanjang siang.')
add('我早就下班了。路上堵车堵得厉害。', 'انتهيت من العمل منذ زمن. الطريق مزدحم بشدة.', 'Aku sudah lama pulang kerja. Jalan macet parah.')
add('房租多少钱؟一个月三千块。', 'كم الإيجار؟ ٣٠٠٠ يوان شهرياً.', 'Sewanya berapa? Tiga ribu yuan sebulan.')
add('虽然贵了点儿،但是房子真好。', 'رغم أنه غالٍ قليلاً، لكن البيت رائع حقاً.', 'Meskipun agak mahal, tapi rumahnya bagus sekali.')
add('周围环境怎么样؟环境特别好。西边是山，山下便有一条小河。', 'كيف البيئة المحيطة؟ ممتازة. غرباً جبال، وتحت الجبال نهر صغير.', 'Bagaimana lingkungan sekitarnya? Sangat bagus. Sebelah barat ada gunung, dan di bawah gunung ada sungai kecil.')
add('交通很方便。楼下有公共汽车站،坐车十分钟就到公司了。', 'المواصلات مريحة جداً. تحت البيت محطة باص، ١٠ دقائق بالباص تصل للشركة.', 'Transportasinya sangat praktis. Di bawah rumah ada terminal bus, naik bus sepuluh menit sudah sampai perusahaan.')
add('就 / 才', '<b>就</b> = أسرع أو أبكر من المتوقع: <span style=\'color:var(--muted)\'>八点半就到了</span> (وصل الثامنة والنصف فقط)<br><b>才</b> = متأخراً أو الآن فقط: <span style=\'color:var(--muted)\'>怎么现在才下班؟</span> (لماذا انتهيت من العمل الآن فقط؟)', '<b>就</b> = lebih cepat atau lebih awal dari perkiraan: <span style=\'color:var(--muted)\'>八点半就到了</span> (tiba tepat jam delapan lebih)<br><b>才</b> = terlambat atau baru saja: <span style=\'color:var(--muted)\'>怎么现在才下班؟</span> (kenapa baru pulang sekarang?)')
add('要是…就…', 'إذا… فإن…: <span style=\'color:var(--muted)\'>要是你也满意،咱们就租了</span> (إذا اقتنعتِ أيضاً، نستأجرها فوراً)', 'Kalau… maka…: <span style=\'color:var(--muted)\'>要是你也满意，咱们就租了</span> (kalau kamu juga cocok, kita langsung sewanya)')
add('虽然…但是…', 'مع أن… لكن: <span style=\'color:var(--muted)\'>虽然贵了点儿،但是房子真好</span>', 'Meskipun… tetapi: <span style=\'color:var(--muted)\'>虽然贵了点儿،但是房子真好</span>')

# ================= LESSON 4 =================
add('考试', 'امتحان', 'Ujian')
add('题', 'سؤال · مسألة', 'Soal · pertanyaan')
add('完', 'ينتهي · ينجز', 'Selesai · menuntaskan')
add('到', 'يصل (كمكمل نتيجة)', 'Sampai (sebagai komplemen hasil)')
add('成绩', 'نتيجة · درجة', 'Nilai · hasil')
add('句子', 'جملة', 'Kalimat')
add('干什么', 'يفعل ماذا', 'Melakukan apa')
add('干', 'يفعل', 'Melakukan')
add('看见', 'يرى (نتيجة)', 'Melihat (sebagai komplemen hasil)')
add('见', 'يرى', 'Melihat')
add('词', 'كلمة', 'Kata')
add('糟糕', 'يا للكارثة · سيء جداً', 'Celaka! · sangat buruk')
add('成', 'يصبح (كمكمل نتيجة)', 'Menjadi (sebagai komplemen hasil)')
add('回信', 'يرد على رسالة', 'Membalas surat')
add('故事', 'قصة · حكاية', 'Cerita')
add('有意思', 'ممتع · ذو معنى', 'Menarik · bermakna')
add('页', 'صفحة', 'Halaman')
add('笑', 'يضحك', 'Tertawa')
add('会话', 'محادثة', 'Percakapan')
add('念', 'يقرأ بصوت عالٍ', 'Membaca dengan lantang')
add('答', 'يجيب', 'Menjawab')
add('办法', 'طريقة · حل', 'Cara · solusi')
add('合上', 'يطوي · يغلق (كتاب)', 'Menutup (buku)')
add('上', 'يصعد · يلتصق (كمكمل نتيجة)', 'Naik · menempel (sebagai komplemen hasil)')
add('听见', 'يسمع (نتيجة)', 'Mendengar (sebagai komplemen hasil)')
add('打开', 'يفتح', 'Membuka')
add('作业', 'واجب مدرسي', 'Tugas sekolah')
add('熟', 'متمكّن · بارع', 'Mahir · terampil')
add('在', 'مجدداً · مرة أخرى', 'Lagi · sekali lagi')
add('你今天考得怎么样؟', 'كيف كان امتحانك اليوم؟', 'Bagaimana ujianmu hari ini?')
add('这次没考好。题太多了،我没有做完。', 'لم أنجح هذه المرة. الأسئلة كثيرة جداً ولم أكملها.', 'Kali ini tidak berhasil. Soalnya terlalu banyak dan aku tidak selesai.')
add('我都做完了，但是没都做对،做错了两道题。', 'أكملت الكل لكن لم أصب في الكل، أخطأت في سؤالين.', 'Aku sudah selesaikan semuanya, tapi tidak semua benar, salah dua soal.')
add('语法题不太难，我觉得都做对了。听力比较难。', 'أسئلة القواعد ليست صعبة، أحس أنني أجبتها كلها صحيحة. الاستماع أصعب نسبياً.', 'Soal tata bahasa tidak sulit, kurasa semuanya benar. Mendengarkan agak sulit.')
add('我也不知道做对了没有。我的词典呢؟', 'لا أعرف أيضاً هل أصبت. وأين قاموسي؟', 'Aku juga tidak tahu apakah benar. Lalu kamusku di mana?')
add('糟糕，写错了，是这个«得»،我写成这个«的»了。', 'يا للكارثة، كتبت خطأً: هو هذا «得» وأنا كتبت هذا «的».', 'Celaka, salah tulis: yang benar ini «得», aku tulis «的».')
add('别查了،休息休息吧。快打开电脑，看看你买的电影光盘吧。', 'كفّ عن البحث، استرح. افتح الكمبيوتر وشاهد أقراص الأفلام التي اشتريتها.', 'Sudah, jangan cari lagi, istirahatlah. Cepat buka komputernya, lihatlah kaset film yang kamu beli.')
add('看完电影再做吧！', 'شاهد الفيلم أولاً ثم اعمل!', 'Nonton film dulu baru kerjakan!')
add('她问了五个问题،我答对了四个،打错了一个。', 'سألتني خمسة أسئلة، أجبت أربعة صحيحة وأخطأت واحداً.', 'Dia bertanya lima soal, aku empat benar satu salah.')
add('我们看到九点才看完。九点半才开始做作业。', 'شاهدنا حتى التاسعة حتى انتهى الفيلم. التاسعة والنصف بدأنا الواجب.', 'Kami nonton sampai jam sembilan filmnya baru selesai. Jam sembilan setengah baru mulai mengerjakan tugas.')
add('结果补语', 'الفعل + نتيجة مباشرة: <b>完، 懂، 见، 开، 上، 到، 给، 成</b> + <b>好، 对، 错</b><br><span style=\'color:var(--muted)\'>我做完了 / 我没做完 / 你做完了没有؟</span><br>النفي: 没+فعل+نتيجة · <b>了</b> بعد النتيجة وقبل المفعول: <span style=\'color:var(--muted)\'>我做错了两个题</span>', 'Kata kerja + hasil langsung: <b>完، 懂، 见، 开، 上، 到، 给، 成</b> + <b>好، 对، 错</b><br><span style=\'color:var(--muted)\'>我做完了 / 我没做完 / 你做完了没有؟</span><br>Negasi: 没+kata kerja+hasil · <b>了</b> setelah hasil dan sebelum objek: <span style=\'color:var(--muted)\'>我做错了两个题</span>')
add('上 · 成 · 到', '<b>上</b> = إغلاق/التصاق: <span style=\'color:var(--muted)\'>关上门 · 合上书</span><br><b>成</b> = التحول: <span style=\'color:var(--muted)\'>写成«找»字</span><br><b>到</b> = الوصول: <span style=\'color:var(--muted)\'>找到 · 看到 · 才到家</span>', '<b>上</b> = menutup/menempel: <span style=\'color:var(--muted)\'>关上门 · 合上书</span><br><b>成</b> = menjadi: <span style=\'color:var(--muted)\'>写成«找»字</span><br><b>到</b> = sampai: <span style=\'color:var(--muted)\'>找到 · 看到 · 才到家</span>')
add('主谓短语作定语', 'العبارة التي تسبق الاسم تحتاج <b>的</b>:<br><span style=\'color:var(--muted)\'>你要的那本书 · 我们现在学的词</span>', 'Frasa yang mendahului kata benda memerlukan <b>的</b>:<br><span style=\'color:var(--muted)\'>你要的那本书 · 我们现在学的词</span>')

# ================= LESSON 5 =================
add('生活', 'حياة · يعيش', 'Kehidupan · hidup')
add('差不多', 'تقريباً · ما يقارب', 'Hampir · kira-kira')
add('习惯', 'عادة · يتعود على', 'Kebiasaan · terbiasa')
add('气候', 'مناخ', 'Iklim')
add('干燥', 'جاف (عن الجو)', 'Kering (cuaca)')
add('干净', 'نظيف', 'Bersih')
add('油腻', 'دسم · زيتي', 'Berminyak')
add('菜', 'أكلة · طبق · خضار', 'Makanan · hidangan · sayur')
add('牛奶', 'حليب', 'Susu')
add('奶牛', 'بقرة حلوب', 'Sapi perah')
add('不过', 'لكن · غير أن', 'Tetapi · namun')
add('课间', 'فسحة بين الحصص', 'Istirahat antarpelajaran')
add('块', 'قطعة · وحدة (عملة/قطع)', 'Potong · satuan (uang/keping)')
add('从来', 'أبداً · من قبل حتى الآن (مع النفي)', 'Tidak pernah · selama ini (dengan negasi)')
add('午觉', 'قيلولة', 'Tidur siang')
add('游泳', 'يسبح · سباحة', 'Berenang')
add('功课', 'دروس · واجبات مدرسية', 'Pelajaran · PR')
add('记住', 'يحفظ · يتذكر', 'Menghafal · mengingat')
add('记', 'يتذكر · يسجل', 'Mengingat · mencatat')
add('一般', 'عادةً · عموماً', 'Biasanya · umumnya')
add('感谢', 'يشكر · امتنان', 'Berterima kasih')
add('父母', 'الوالدان', 'Orang tua')
add('机会', 'فرصة', 'Kesempatan')
add('原来', 'في الأصل · اتضح أنه', 'Awalnya · ternyata')
add('练', 'يتمرن · يتدرب', 'Berlatih · berolahraga')
add('气功', 'التشي كونغ (تمارين تنفس)', 'Qigong (latihan pernapasan)')
add('延长', 'يمدّد · يطيل (المدة)', 'Memperpanjang')
add('好', 'كثيراً · طويلاً (ظرف مع 几/多)', 'Banyak · lama (adverbia dengan 几/多)')
add('不一定', 'ليس بالضرورة', 'Belum tentu')
add('钟头', 'ساعة (زمن)', 'Jam (waktu)')
add('效果', 'نتيجة · أثر', 'Hasil · efek')
add('挺', 'جداً · إلى حد كبير', 'Sangat · cukup')
add('好处', 'فائدة · جانب إيجابي', 'Manfaat · keuntungan')
add('坏处', 'ضرر · جانب سلبي', 'Kerugian · bahaya')
add('慢性病', 'مرض مزمن', 'Penyakit kronis')
add('高血压', 'ارتفاع ضغط الدم', 'Darah tinggi')
add('失眠', 'أرق · الأرق', 'Insomnia')
add('必须', 'يجب · لا بد من', 'Harus')
add('打鱼', 'يصطاد السمك', 'Menangkap ikan')
add('晒', 'يُجفف بالشمس · يُشرّق', 'Menjemur · disinari matahari')
add('我来了两个多月了。', 'أنا هنا منذ أكثر من شهرين (جئت ومرّ عليّ شهران وأكثر).', 'Aku sudah di sini lebih dari dua bulan (datang dan sudah lewat dua bulan lebih).')
add('对这儿的生活差不多已经习惯了。', 'تعوّدت تقريباً على الحياة هنا.', 'Aku sudah hampir biasa dengan kehidupan di sini.')
add('我每天早上七点多才起床。', 'أستيقظ كل صباح بعد السابعة بقليل فقط.', 'Setiap pagi aku baru bangun lewat tujuh sedikit.')
add('我从来不睡午觉。', 'لا أقيل أبداً (من قبل حتى الآن).', 'Aku tidak pernah tidur siang.')
add('每天都坚持锻炼一个小时。', 'أتمسك بالتمارين ساعة كل يوم.', 'Setiap hari bertekun berolahraga satu jam.')
add('我很感谢父母给我这个机会。', 'أنا ممتن جداً لوالديّ على هذه الفرصة.', 'Aku sangat berterima kasih kepada orang tuaku atas kesempatan ini.')
add('原来打算学一年，现在准备再延长一年。', 'كنت أنوي الدراسة سنة، والآن أستعد لتمديدها سنة أخرى.', 'Awalnya berencana belajar setahun, sekarang siap memperpanjang setahun lagi.')
add('已经练了好几年了。', 'أتدرب منذ عدة سنوات.', 'Sudah berlatih beberapa tahun.')
add('我每天晚上一般要复习预习两个小时。', 'عادةً أراجع وأحضّر الدروس ساعتين كل ليلة.', 'Setiap malam biasanya mengulas dan menyiapkan pelajaran dua jam.')
add('练气功必须坚持天天练،三天打鱼两天晒网不行。', 'التشي كونغ يحتاج استمراراً يومياً؛ "ثلاثة أيام صيد ويومان تجفيف شبكة" لا ينجح.', 'Latihan qigong harus tekun berlatih setiap hari; "tiga hari menangkap ikan dua hari jemur jala" tidak bisa.')
add('时量补语', 'المدة الزمنية تأتي <b>بعد الفعل</b> مباشرة.<br><span style=\\"color:var(--muted)\\">我来了两个多月了 / 我每天都练一个小时</span><br>مع المفعول: تُعاد الحركة أو تُوضع بين الفعل والمفعول:<br><span style=\\"color:var(--muted)\\">我写汉字写了半个小时 / 我看了一个小时电视 / 我学了两年(的)汉语</span>', 'Durasi datang <b>setelah kata kerja</b> secara langsung.<br><span style=\\"color:var(--muted)\\">我来了两个多月了 / 我每天都练一个小时</span><br>Dengan objek: kata kerja diulang atau durasi diletakkan antara kata kerja dan objek:<br><span style=\\"color:var(--muted)\\">我写汉字写了半个小时 / 我看了一个小时电视 / 我学了两年(的)汉语</span>')
add('离合词', 'أفعال تُفصل عند إضافة المدة أو العدد: <b>睡觉، 毕业، 谈话، 游泳، 起床، 打鱼</b><br><span style=\\"color:var(--muted)\\">我睡了八个小时觉 · 大学毕业两年了 · 谈一会儿话 · 游游泳</span>', 'Kata kerja yang terpisah saat menambahkan durasi atau jumlah: <b>睡觉، 毕业، 谈话، 游泳، 起床، 打鱼</b><br><span style=\\"color:var(--muted)\\">我睡了八个小时觉 · 大学毕业两年了 · 谈一会儿话 · 游游泳</span>')
add('概数', 'طريقتان:<br>① <b>多</b> بعد العدد: <span style=\\"color:var(--muted)\\">两个多月 · 十多分钟 · 七点多</span><br>② رقمان متتاليان: <span style=\\"color:var(--muted)\\">两三个小时 · 十五六个人</span>', 'Dua cara:<br>① <b>多</b> setelah angka: <span style=\\"color:var(--muted)\\">两个多月 · 十多分钟 · 七点多</span><br>② Dua angka berurutan: <span style=\\"color:var(--muted)\\">两三个小时 · 十五六个人</span>')
add('好 + 几/多', '<b>好</b> قبل 几 أو 多 = كثيراً / طويلاً:<br><span style=\\"color:var(--muted)\\">好几年 (عدة سنوات) · 好一会儿 (برهة طويلة)</span>', '<b>好</b> sebelum 几 atau 多 = banyak / lama:<br><span style=\\"color:var(--muted)\\">好几年 (beberapa tahun) · 好一会儿 (cukup lama)</span>')
add('才 / 就', '<b>才</b> = متأخراً أو بعد جهد: <span style=\\"color:var(--muted)\\">七点多才起床 · 十一点多才睡觉</span><br><b>就</b> = مبكراً أو بسهولة: <span style=\\"color:var(--muted)\\">五点多就起来了</span>', '<b>才</b> = terlambat atau setelah usaha: <span style=\\"color:var(--muted)\\">七点多才起床 · 十一点多才睡觉</span><br><b>就</b> = awal atau mudah: <span style=\\"color:var(--muted)\\">五点多就起来了</span>')

add('糟糕،写错了，是这个「得」，我写成这个«的»了。', 'يا للكارثة، كتبت خطأً: هو هذا «得» وأنا كتبت هذا «的».', 'Celaka, salah tulis: yang benar ini «得», aku tulis «的».')

# ---- types ----
TYPES = {
    'اسم': 'kata benda', 'فعل': 'kata kerja', 'صفة': 'kata sifat', 'ظرف': 'kata keterangan',
    'تعبير': 'ungkapan', 'أداة': 'partikel', 'حرف جر': 'kata depan', 'حرف عطف': 'kata penghubung',
    'حرف شرط': 'kata pengandaian', 'كلمة قياس': 'kata penggolong', 'ضمير': 'kata ganti',
    'اسم وفعل': 'kata benda & kata kerja', 'فعل واسم': 'kata kerja & kata benda',
}
SUBS = {
    'نبرة 了 والسؤال': 'Nada 了 dan pertanyaan',
    'تكرار الفعل': 'Pengulangan kata kerja',
    'أسئلة التأكيد': 'Pertanyaan konfirmasi',
    'الفعل المكتمل': 'Kata kerja selesai',
    'السبب والنتيجة': 'Sebab dan akibat',
    'حصر الكمية': 'Pembatasan jumlah',
    'ظرفا الزمن': 'Adverbia waktu',
    'الشرط': 'Kondisional (kalau)',
    'التنازل': 'Konsesif (meskipun)',
    'مكمل النتيجة': 'Komplemen hasil',
    'مكملات النتيجة': 'Komplemen hasil',
    'عبارة فاعل-خبير كصفة': 'Frasa subjek-predikat sebagai adjektiva',
    'مدة الفعل': 'Durasi kata kerja',
    'الأفعال المنفصلة': 'Kata kerja terpisah',
    'الأرقام التقريبية': 'Perkiraan jumlah',
    'ظرف المقدار': 'Adverbia tingkat',
    'التمارين ٦': 'Latihan 6',
}

NORM_CHARS = ' ,?! \' " ؟ ٫ ، 。 ， ！ ？ · : ؛ .,،\u060c\u061f\u3001\u3002\uff0c\uff1f\uff01\u300a\u300b\u00ab\u00bb\「」'
def norm(s):
    s = (s or '').strip()
    for ch in NORM_CHARS:
        s = s.replace(ch, '')
    return s

G_NORM = {}
for k, v in G.items():
    G_NORM[norm(k)] = v

def main():
    s = io.open('data.js', 'r', encoding='utf-8').read()
    applied = 0
    missing = []
    for num in range(1, 6):
        start = s.find('cards.l%d = [' % num)
        if start == -1:
            continue
        b = start + s[start:].index('[')
        depth = 0
        i = b
        while i < len(s):
            if s[i] == '[': depth += 1
            elif s[i] == ']':
                depth -= 1
                if depth == 0: break
            i += 1
        cards = json.loads(s[b:i+1])
        for c in cards:
            key = (c.get('front') or '') + '||' + (c.get('ar') or '')
            nkey = norm(key)
            tr = c.get('trans') or {}
            if nkey in G_NORM:
                tr['id'] = G_NORM[nkey]
                applied += 1
            elif not (tr.get('id') or '').strip():
                missing.append(key)
            c['trans'] = tr
            tt = c.get('trans_type') or {}
            if c.get('type') in TYPES:
                tt['id'] = TYPES[c['type']]
                c['trans_type'] = tt
            ts = c.get('trans_sub') or {}
            if c.get('sub') in SUBS:
                ts['id'] = SUBS[c['sub']]
                c['trans_sub'] = ts
        new_arr = json.dumps(cards, ensure_ascii=False)
        s = s[:b] + new_arr + s[i+1:]
    io.open('data.js', 'w', encoding='utf-8').write(s)
    print('applied glosses:', applied)
    print('missing:', len(missing))
    for m in missing[:20]:
        print('  MISSING:', m[:120])
    # coverage report
    s = io.open('data.js', 'r', encoding='utf-8').read()
    total = withid = 0
    for num in range(1, 6):
        start = s.find('cards.l%d = [' % num)
        b = start + s[start:].index('[')
        depth = 0; i = b
        while i < len(s):
            if s[i] == '[': depth += 1
            elif s[i] == ']':
                depth -= 1
                if depth == 0: break
            i += 1
        cards = json.loads(s[b:i+1])
        for c in cards:
            total += 1
            if (c.get('trans') or {}).get('id'): withid += 1
    print('cards WITH id: %d / %d' % (withid, total))

if __name__ == '__main__':
    main()
