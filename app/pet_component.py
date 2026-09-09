# pet_component.py - 桌宠悬浮球组件（可拖动鲸鱼 + 气泡菜单 + 对话）
import base64
import json
import os

import streamlit.components.v1 as components

def _load_deepseekchan_img(filename):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "deepseekchan", filename)
    ext = os.path.splitext(filename)[1].lower()
    mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
    try:
        with open(path, "rb") as f:
            return "data:" + mime + ";base64," + base64.b64encode(f.read()).decode("ascii")
    except Exception:
        return ""


def _load_deepseekchan_video(filename):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "deepseekchan", filename)
    try:
        with open(path, "rb") as f:
            return "data:video/mp4;base64," + base64.b64encode(f.read()).decode("ascii")
    except Exception:
        return ""


def _load_first_deepseekchan_img(*filenames):
    for filename in filenames:
        data_uri = _load_deepseekchan_img(filename)
        if data_uri:
            return data_uri
    return ""


_DEFAULT_PET_IMG = _load_deepseekchan_img("DSmaid.png")
_DRAG_PET_IMG = _load_deepseekchan_img("DSmaid_1.png")
_OUTFIT_IMG = _load_deepseekchan_img("DSmaid_rice=eater.png")
_OUTFIT_DRAG_IMG = _load_first_deepseekchan_img("DSmaid_rice=eater_1.jpg", "DSmaid_rice=eater_1.png")
_HARNESS_IMG = _load_deepseekchan_img("DSmaid_harness.png")
_HARNESS_DRAG_IMG = _load_deepseekchan_img("DSmaid_harness_1.png")
_RICE_MAX_IMG = _load_deepseekchan_img("67.png")
_MYSTERY_IMG = _load_deepseekchan_img("U·know·who.png")
_MYSTERY_DRAG_IMG = _load_deepseekchan_img("bigliang.png")
_DSL_VIDEO = _load_deepseekchan_video("dsl.mp4")
_DSR_VIDEO = _load_deepseekchan_video("dsr.mp4")
_GAME_BG_IMG = _load_deepseekchan_img("rice.png")
_GAME_PLAYER_IMG = _load_deepseekchan_img("DSmaid+.png")
_CIALLO_IMG = _load_deepseekchan_img("ciallo.png")

# ============== 新手教程图片（1.png ~ 9.png） ==============
_TUT_IMAGES = {}
for _tut_i in "123456789":
    _tut_uri = _load_deepseekchan_img(f"{_tut_i}.png")
    if _tut_uri:
        _TUT_IMAGES[_tut_i] = _tut_uri

# ============== 新手教程滤镜下覆盖图（p1 ~ p5） ==============
_PIMG_IMAGES = {
    "p1": _load_deepseekchan_img("p1.png"),
    "p2": _load_deepseekchan_img("p2.png"),
    "p3": _load_first_deepseekchan_img("p3.jpeg", "p3.jpg", "p3.png"),
    "p4": _load_deepseekchan_img("p4.png"),
    "p5": _load_deepseekchan_img("p5.png"),
    "q": _load_first_deepseekchan_img("！？.png", "？！.png"),
}

# ============== 默认形象（maid.png，缺失时回退内置鲸鱼SVG） ==============
_WHALE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 100">'
    '<defs>'
    '<linearGradient id="g1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6db8ff"/><stop offset="1" stop-color="#2f80ed"/></linearGradient>'
    '<linearGradient id="g2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bfe3ff"/><stop offset="1" stop-color="#eaf6ff"/></linearGradient>'
    '</defs>'
    '<path d="M16 46 C8 40 2 34 0 26 C8 28 14 34 18 40 C14 40 10 39 6 37 C12 44 16 48 19 50 Z" fill="#2f80ed"/>'
    '<path d="M14 56 C8 60 3 66 0 72 C8 70 14 64 18 58 C14 60 10 61 6 61 C12 55 15 53 17 54 Z" fill="#2f80ed"/>'
    '<ellipse cx="64" cy="50" rx="46" ry="34" fill="url(#g1)"/>'
    '<path d="M38 66 Q64 80 90 66 Q64 72 38 66 Z" fill="url(#g2)"/>'
    '<path d="M62 64 Q74 82 56 84 Q48 74 52 62 Z" fill="#1e6fd6"/>'
    '<path d="M80 16 Q82 6 92 2" stroke="#9bd4ff" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
    '<circle cx="92.5" cy="2" r="3.4" fill="#9bd4ff"/>'
    '<circle cx="84.5" cy="1.5" r="2.4" fill="#c9e8ff"/>'
    '<circle cx="82" cy="42" r="7.5" fill="#ffffff"/>'
    '<circle cx="84.5" cy="43" r="4" fill="#16324f"/>'
    '<circle cx="86" cy="41.5" r="1.4" fill="#ffffff"/>'
    '<ellipse cx="92" cy="55" rx="6.5" ry="4.2" fill="#ff9db1" opacity="0.75"/>'
    '<path d="M76 57 Q82 63 90 57" stroke="#16324f" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
    '</svg>'
)


# ============== 预设短对话（100条，傲娇鲸鱼萝莉少女口吻） ==============
PRESET_LINES = [
    "哼，才不是专门在等你呢！(///￣ ￣///)",
    "才、才不胖！这是游泳圈！(╬▔皿▔)凸",
    "嘀——大肥鱼在线，信号满格。( ˘▾˘)～♩",
    "有什么想问的？本鲸勉强听一下。( ˘•ω•˘ )",
    "别一直戳我啦……再戳一下也不是不行。(*/ω＼*)",
    "尾鳍摇一摇，今天心情超好～(ノ≧∇≦)ノ",
    "分析数据嘛，小菜一碟……等本鲸先打个盹。(。-ω-)zzZ",
    "主人真厉害，居然会想到问本鲸！(≧◡≦) ♡",
    "才没有在偷懒，本鲸在思考鲸生。( ˘ω˘ )",
    "游来游去，游来游去～～(￣▽￣～)",
    "哼，你叫「大肥鱼」的样子，还挺顺耳的。(///▽///)",
    "本鲸的尾鳍才不是摆设！╰(*°▽°*)╯",
    "数据不会说谎，本鲸也是。( •̀ ω •́ )✧",
    "主人需要帮忙就直说，本鲸……勉强有空。(￣ε ￣;)",
    "泡泡吐得够多了，快来问问题！(ノ｀Д)ノ",
    "才没有因为你回来而开心呢！(⁄ ⁄•⁄ω⁄•⁄ ⁄)",
    "本鲸聪明着呢，只是懒得动。(¬‿¬)",
    "摸头可以，说胖不行！(╬ Ò﹏Ó)",
    "数据预处理是本鲸的强项哦，真的哦。(ﾉ◕ヮ◕)ﾉ*:・ﾟ✧",
    "主人～主人～（尾巴甩来甩去）(｡>﹏<｡)",
    "哼，看在你这么辛苦的份上，陪你聊五分钟。(￣^￣)ゞ",
    "本鲸最听主人的话了，说东绝不敢往西……偶尔。(*/▽＼*)",
    "曲线拟合就像给数据画一条游泳路线～～(￣△￣～)",
    "才不是胖！是「流线型」！(ノ `Д´)ノ",
    "呼噜……啊！没睡着！本鲸醒着呢！(๑•́ ₃ •̀๑)",
    "特征工程？本鲸可以教你……等我睡醒。(－ω－) zzZ",
    "主人今天的数据分析顺利吗？我才不是关心你！(⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)",
    "嘀——检测到主人在偷看本鲸。(눈_눈)",
    "本鲸的尾鳍会打节拍，要听吗？(ﾉ´ヮ`)ﾉ*: ✧",
    "谁说我懒？本鲸只是节能模式！(￣ヘ￣)",
    "再叫大肥鱼，本鲸……也不会怎么样啦，哼。(｡•́︿•̀｡)",
    "主人累了吗？本鲸把泡泡借你靠一靠。( ˘ ³˘)♥",
    "本鲸知识渊博，只是内存条偶尔松动。(⊙﹏⊙)",
    "今天也要元气满满哦，本鲸说的。(ง •̀_•́)ง",
    "交叉验证就是把数据反复搓一搓，本鲸式理解。(づ￣ ³￣)づ",
    "才没有想被你夸奖……再多说点也行。(///Σ///)",
    "游累了，今天的运动量已达标。_(:з」∠)_",
    "主人，摸尾鳍是要负责的哦。(๑>؂<๑)",
    "本鲸的智商和饭量成正比！ᕦ(ò_óˇ)ᕤ",
    "过拟合就是背题侠，本鲸才不做背题侠。(¬_¬)",
    "哼，本鲸偶尔也会想主人的……一点点。(｡•́‿•̀｡)",
    "数据清洗就像给鲸鱼洗澡，唰唰唰～(ﾉ^ヮ^)ﾉ*:・ﾟ✧",
    "醒啦醒啦！这次是真的醒啦！(O_O;)",
    "本鲸建议：先吃饭，再干活，主人都瘦了。(｡♥‿♥｡)",
    "特征重要性排名？本鲸第一名！✧*。ヾ(>▽<)ノ✧*。",
    "才、才不胖！你见过这么可爱的游泳圈吗？(╯°Д°)╯",
    "嘀——电量99%，满格待机。(๑•̀ㅂ•́)و",
    "主人问吧，本鲸这次不犯困，保证。( •̀ ω •́ )y",
    "尾鳍比个心，看到了吗？(◍•ᴗ•◍)❤",
    "数据分析的尽头，是泡饭……不是，是洞察。(・_・;)",
    "本鲸虽然懒，但为了主人可以勤快三秒。(๑•̀д•́๑)",
    "深夜写代码的主人，本鲸陪你熬……到十点。( ˘•ω•˘ ).｡oIl",
    "说本鲸胖的人，本鲸会用泡泡糊他一脸！(╬｀Д´)ﾉ",
    "主人主人，快夸我今天的尾鳍摆得好看！(≧◡≦)",
    "预测精度？放心交给本鲸和主人联手！(ง •̀_•́)ง✧",
    "才不是在撒娇，这是正常交流！(///ω///)",
    "本鲸今天游了零圈，战绩可观。(⊙▽⊙)",
    "主人笑起来真好看，本鲸才没有偷看。(*/_＼)",
    "逻辑回归？本鲸的逻辑一向很稳！(ᵔᴥᵔ)",
    "再熬夜，本鲸就游过去把电脑合上！(ノ｀Д)ノ━┻━┻",
    "本鲸的游泳圈是遗传的，才不是胖！(╥_╥)",
    "学习曲线？本鲸的学习曲线是条懒鲸线。～(－.－～)",
    "主人请吩咐，本鲸的小尾鳍已就绪！(๑•̀ㅂ•́)و✧",
    "本鲸偶尔也会思考鲸生，比如晚饭吃什么。( ˘ω˘ )",
    "才没有把你的分析结果偷偷看完！(◎_◎;)",
    "数据预处理完成，本鲸打个响尾庆祝。(ﾉ´ヮ`)ﾉ",
    "主人摸摸头，本鲸就原谅你说胖的事……才怪！(≖_≖ )",
    "超时信号发射——「嘀——」收不到，那就当没问。(×ω×)",
    "别小看本鲸，本鲸可是学过统计的！(ง •̀_•́)ง",
    "主人的问题再多，本鲸也不会烦……最多打个哈欠。(￣o￣) . z Z",
    "本鲸今天也乖乖等主人，没有偷吃哦。(◕ᴗ◕✿)",
    "才不胖，这是「可爱溢出」导致的视觉误差！(⊙_⊙;)",
    "想和主人一起看分析结果，本鲸负责加油。(o^▽^o)",
    "本鲸的尾鳍说它也想参与建模。(๑• . •๑)",
    "主人不叫我大肥鱼的话，本鲸会有一点点不习惯。(｡•́︿•̀｡)",
    "睡得饱饱的，脑子转得快快的，本鲸式高效。(*´▽`*)",
    "才没有每天数着主人回来的时间！(⁄ ⁄•⁄_⁄•⁄ ⁄)",
    "本鲸帮你吹散bug，呼——（鲸式喷水）(ﾉ≧∀≦)ﾉ ‥…━━━★",
    "数据分析不难，难的是……从床上起来。_(:3」∠)_",
    "主人最棒了！本鲸难得说真心话。(♡˙︶˙♡)",
    "才不胖！再强调一遍：不！胖！╰(‵□′)╯",
    "本鲸的记忆力超群，除了饭点之外。(・∀・)",
    "模型评估交给本鲸，绝对公正……大概。(￣ー￣)",
    "主人摸摸尾鳍，本鲸帮你预测未来！(๑˃̵ᴗ˂̵)و",
    "才不是因为你夸我才摇尾巴的！(///艸)",
]

RICE_FEED_LINES = [
    "唔……白饭好香！主人喂的饭，本鲸会好好记住的啦。(๑´ڡ`๑)",
    "好感度上升！才、才不是因为一碗白饭就开心呢……(///▽///)",
    "主人投喂成功，本鲸尾鳍都要摇起来了！(≧◡≦)♡",
    "白饭入口，能量满格……再来一口也不是不可以哦。( ˘ڡ˘ )",
    "哼，算你会照顾鲸！这碗饭本鲸收下啦。(￣^￣)ゞ",
    "米饭软乎乎的，主人的心意也是软乎乎的……才没有夸你！(⁄ ⁄•⁄ω⁄•⁄ ⁄)",
    "吃饱一点，才有力气陪主人分析数据嘛。(｡>﹏<｡)",
    "这不是贪吃，是补充执行分析的燃料！( •̀ ω •́ )✧",
    "白饭好吃，主人最好……咳，只是暂时这样觉得啦。(*/ω＼*)",
    "好感度+1，本鲸记账了，主人不许赖账哦。(◍•ᴗ•◍)❤",
    "一口白饭换本鲸的开心，主人这笔交易很划算吧！(ノ≧∇≦)ノ",
    "本鲸宣布：今天的幸福是米饭形状的。(๑•̀ㅂ•́)و✧",
    "喂得很准嘛，主人，看来你也很懂鲸心。(¬‿¬)",
    "吃完饭就不许催本鲸立刻干活，先摇三下尾鳍！(￣▽￣～)",
    "主人给的白饭，本鲸一粒都不会浪费的说。(｡♥‿♥｡)",
    "好感度悄悄增加……不许盯着看，本鲸会害羞的！(〃￣ω￣〃)",
    "再来一点点的话，本鲸也可以勉强原谅你叫大肥鱼。(╥﹏╥)",
    "饭饭吃进肚子里，主人的关心也一起吃进去啦。(づ￣ ³￣)づ",
    "嘀——检测到白饭能量，鲸鱼少女恢复活力！(ง •̀_•́)ง",
    "主人辛苦啦，本鲸吃饱后会乖乖陪你的……大概。(。-ω-)zzZ",
]

_PET_HTML = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>
<script>
(function () {
  'use strict';
  var MARKER = 'FAT_FISH_PET_V1';
  var PAGE_SCOPE = __PAGE_SCOPE__;
  var CHAT_KEY = 'ffp_chat' + (PAGE_SCOPE ? '_' + PAGE_SCOPE : '');
  var PRESET_LINES = __PRESET_LINES__;
  var POPUP_MSG = __POPUP_MSG__;
  var POPUP_TOKEN = __POPUP_TOKEN__;
  var NOTIFY_MSG = __NOTIFY_MSG__;
  var NOTIFY_TOKEN = __NOTIFY_TOKEN__;
  var DRAWER_HTML = __DRAWER_HTML__;
  var OPEN_SIDEBAR_TOKEN = __OPEN_SIDEBAR_TOKEN__;
  var FFP_SAVE_EDA_TOKEN = '[[FFP_SAVE_EDA]]';
  var pd = null;
  try { pd = window.parent.document; } catch (e) { pd = null; }
  if (!pd || !pd.body || !pd.head) { return; }

  function store(k, v) { try { window.parent.localStorage.setItem(k, v); } catch (e) {} }
  function load(k) { try { return window.parent.localStorage.getItem(k); } catch (e) { return null; } }
  function del(k) { try { window.parent.localStorage.removeItem(k); } catch (e) {} }

  var DEFAULT_IMG = __DEFAULT_IMG__;
  var DRAG_IMG = __DRAG_IMG__;
  var OUTFIT_IMG = __OUTFIT_IMG__;
  var OUTFIT_DRAG_IMG = __OUTFIT_DRAG_IMG__;
  var HARNESS_IMG = __HARNESS_IMG__;
  var HARNESS_DRAG_IMG = __HARNESS_DRAG_IMG__;
  var RICE_FEED_LINES = __RICE_FEED_LINES__;
  var RICE_MAX_IMG = __RICE_MAX_IMG__;
  var MYSTERY_IMG = __MYSTERY_IMG__;
  var MYSTERY_DRAG_IMG = __MYSTERY_DRAG_IMG__;
  var DSL_VIDEO = __DSL_VIDEO__;
  var DSR_VIDEO = __DSR_VIDEO__;
  var GAME_BG_IMG = __GAME_BG_IMG__;
  var GAME_PLAYER_IMG = __GAME_PLAYER_IMG__;
  var CIALLO_IMG = __CIALLO_IMG__;

  var oldRoot = pd.getElementById('ffp-root');
  if (oldRoot) { oldRoot.remove(); }
  var oldStyle = pd.getElementById('ffp-style');
  if (oldStyle) { oldStyle.remove(); }
  var oldChat = pd.getElementById('ffp-chat');
  if (oldChat) { oldChat.remove(); }
  var oldDrawer = pd.getElementById('ffp-drawer');
  if (oldDrawer) { oldDrawer.remove(); }
  var oldTab = pd.getElementById('ffp-drawer-tab');
  if (oldTab) { oldTab.remove(); }
  var oldOutfitDialog = pd.getElementById('ffp-outfit-dialog');
  if (oldOutfitDialog) { oldOutfitDialog.remove(); }
  var oldRiceRoot = pd.getElementById('ffp-rice-root');
  if (oldRiceRoot) { oldRiceRoot.remove(); }
  var oldRiceGhost = pd.getElementById('ffp-rice-ghost');
  if (oldRiceGhost) { oldRiceGhost.remove(); }
  var oldGameMask = pd.getElementById('ffp-game-mask');
  if (oldGameMask) { oldGameMask.remove(); }
  var oldTutEls = pd.querySelectorAll('#ffp-tut-pimg,#ffp-tut-filter,#ffp-tut-hold,#ffp-tut-img,#ffp-tut-bubble,#ffp-tut-extra,#ffp-tut-skip,#ffp-qa-btn,#ffp-qa-pop');
  for (var _tei = 0; _tei < oldTutEls.length; _tei++) {
    if (oldTutEls[_tei].parentNode) { oldTutEls[_tei].parentNode.removeChild(oldTutEls[_tei]); }
  }

  try {
    var frames = pd.querySelectorAll('iframe');
    for (var i = 0; i < frames.length; i++) {
      var f = frames[i];
      if ((f.srcdoc || '').indexOf(MARKER) !== -1) { f.style.display = 'none'; break; }
    }
  } catch (e) {}

  var style = pd.createElement('style');
  style.id = 'ffp-style';
  style.textContent = '' +
    '#ffp-root{position:fixed;z-index:999999;width:0;height:0;}' +
    '#ffp-ball{position:absolute;top:0;left:0;width:84px;height:84px;cursor:grab;touch-action:none;' +
    'animation:ffpBob 3.2s ease-in-out infinite;filter:drop-shadow(0 6px 14px rgba(0,0,0,.28));}' +
    '#ffp-ball:active{cursor:grabbing;}' +
    '#ffp-ball.ffp-dragging{animation:none;}' +
    '#ffp-ball img{width:100%;height:100%;object-fit:contain;pointer-events:none;display:block;-webkit-user-drag:none;}' +
    '#ffp-name{position:absolute;top:100%;left:50%;transform:translateX(-50%);margin-top:2px;background:#2f80ed;color:#fff;' +
    'font-size:11px;line-height:1;padding:4px 12px;border-radius:999px;white-space:nowrap;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;box-shadow:0 2px 8px rgba(47,128,237,.35);pointer-events:none;}' +
    '#ffp-favor{position:absolute;top:100%;left:50%;transform:translateX(-50%);margin-top:23px;background:#fff8e1;color:#a56a00;' +
    'font-size:10px;line-height:1;padding:3px 9px;border-radius:999px;white-space:nowrap;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;box-shadow:0 2px 8px rgba(165,106,0,.25);pointer-events:none;}' +
    '@keyframes ffpBob{0%,100%{transform:translateY(0) rotate(-2deg);}50%{transform:translateY(-7px) rotate(2deg);}}' +
    '#ffp-speech-bubble{position:absolute;width:150px;background:#ffffff;border:1.5px solid #cfe6ff;' +
    'border-radius:14px;box-shadow:0 12px 32px rgba(31,84,168,.2);padding:8px 10px;display:none;flex-direction:column;gap:4px;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;box-sizing:border-box;' +
    'cursor:grab;user-select:none;-webkit-user-select:none;}' +
    '#ffp-speech-bubble.ffp-dragging-bubble{cursor:grabbing !important;}' +
    '#ffp-speech-bubble::after{content:"";position:absolute;left:100%;top:50%;transform:translateY(-50%);' +
    'border:8px solid transparent;border-left-color:#ffffff;border-right:none;}' +
    '#ffp-speech-bubble.ffp-below::after{left:50%;top:-8px;transform:translateX(-50%);' +
    'border-left-color:transparent;border-bottom-color:#ffffff;border-top:none;}' +
    '#ffp-speech{background:#f0f6ff;border:1px solid #e3efff;border-radius:10px;padding:7px 9px;font-size:12px;' +
    'line-height:1.5;color:#1c2b4a;display:flex;flex-direction:column;gap:4px;box-sizing:border-box;}' +
    '#ffp-speech-text{word-break:break-word;}' +
    '#ffp-speech-refresh{align-self:flex-end;color:#2f80ed;font-size:11px;cursor:pointer;user-select:none;}' +
    '#ffp-speech-refresh:hover{color:#1e6fd6;}' +
    '#ffp-menu-bubble{position:absolute;width:150px;background:#ffffff;border:1.5px solid #cfe6ff;' +
    'border-radius:16px;box-shadow:0 12px 32px rgba(31,84,168,.2);padding:8px;display:none;flex-direction:column;gap:6px;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;box-sizing:border-box;' +
    'cursor:grab;user-select:none;-webkit-user-select:none;}' +
    '#ffp-menu-bubble.ffp-dragging-bubble{cursor:grabbing !important;}' +
    '#ffp-menu-bubble::after{content:"";position:absolute;right:100%;top:50%;transform:translateY(-50%);' +
    'border:8px solid transparent;border-right-color:#ffffff;border-left:none;}' +
    '#ffp-menu-bubble.ffp-below::after{right:auto;left:50%;top:-8px;transform:translateX(-50%);' +
    'border-right-color:transparent;border-bottom-color:#ffffff;border-top:none;}' +
    '#ffp-menu-bubble .ffp-bubble-title{text-align:center;font-size:12px;color:#5a7ca8;font-weight:600;padding:2px 0 1px;}' +
    '#ffp-menu{display:flex;flex-direction:column;gap:6px;}' +
    '#ffp-settings{display:none;flex-direction:column;gap:8px;}' +
    '#ffp-settings .ffp-set-row{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#1d4e8f;font-weight:600;}' +
    '#ffp-settings input[type=range]{width:100%;accent-color:#2f80ed;margin:2px 0;cursor:pointer;}' +
    '#ffp-settings .ffp-size-line{display:flex;align-items:center;gap:8px;}' +
    '#ffp-settings .ffp-size-line input[type=range]{flex:1;width:auto;}' +
    '#ffp-settings input[type=number]{width:70px;border:1.5px solid #cfe6ff;border-radius:8px;padding:4px 6px;' +
    'font-size:12px;color:#1d4e8f;background:#fff;outline:none;box-sizing:border-box;font-family:inherit;}' +
    '#ffp-settings input[type=number]:focus{border-color:#2f80ed;}' +
    '#ffp-size-hint{font-size:11px;color:#5a7ca8;text-align:center;}' +
    '#ffp-menu-bubble button{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;padding:8px 6px;' +
    'border:none;border-radius:10px;background:#f4f9ff;color:#1d4e8f;font-size:13px;font-weight:600;cursor:pointer;' +
    'font-family:inherit;transition:all .15s;}' +
    '#ffp-menu-bubble button:hover{background:#2f80ed;color:#ffffff;transform:translateY(-1px);}' +
    '#ffp-chat{position:fixed;right:20px;bottom:20px;width:340px;height:480px;z-index:1000000;background:#ffffff;' +
    'border:1.5px solid #cfe6ff;border-radius:16px;box-shadow:0 18px 50px rgba(31,84,168,.28);' +
    'display:none;flex-direction:column;overflow:hidden;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;}' +
    '#ffp-chat .ffp-chat-head{display:flex;align-items:center;justify-content:space-between;padding:10px 12px;' +
    'background:linear-gradient(135deg,#2f80ed,#56a3ff);color:#ffffff;font-size:14px;font-weight:600;' +
    'cursor:grab;user-select:none;-webkit-user-select:none;}' +
    '#ffp-chat .ffp-chat-head.ffp-dragging-chat{cursor:grabbing !important;}' +
    '#ffp-chat .ffp-chat-btns{display:flex;gap:4px;}' +
    '#ffp-chat .ffp-chat-btns button{background:rgba(255,255,255,.18);border:none;color:#ffffff;width:26px;height:26px;' +
    'border-radius:8px;cursor:pointer;font-size:13px;line-height:1;display:flex;align-items:center;justify-content:center;}' +
    '#ffp-chat .ffp-chat-btns button:hover{background:rgba(255,255,255,.35);}' +
    '#ffp-key-panel{display:none;flex-direction:column;gap:6px;padding:8px 10px;background:#f4f9ff;border-bottom:1px solid #e3efff;}' +
    '#ffp-key-panel input{width:100%;box-sizing:border-box;border:1px solid #cfe6ff;border-radius:8px;padding:6px 8px;font-size:12px;outline:none;}' +
    '#ffp-key-panel button{align-self:flex-end;background:#2f80ed;color:#ffffff;border:none;border-radius:8px;padding:5px 14px;font-size:12px;cursor:pointer;}' +
    '#ffp-chat .ffp-chat-tools{padding:6px 10px;background:#f4f9ff;border-bottom:1px solid #e3efff;display:flex;}' +
    '#ffp-chat .ffp-chat-tools button{width:100%;background:#2f80ed;color:#ffffff;border:none;border-radius:8px;' +
    'padding:6px 0;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;}' +
    '#ffp-chat .ffp-chat-tools button:hover{background:#1e6fd6;}' +
    '#ffp-chat .ffp-chat-tools button:disabled{background:#a9c8ea;cursor:not-allowed;}' +
    '#ffp-chat-msgs{flex:1;overflow-y:auto;display:flex;flex-direction:column;padding:8px 4px;background:#fbfdff;}' +
    '.ffp-msg{max-width:82%;padding:8px 12px;border-radius:14px;font-size:13px;line-height:1.55;word-break:break-word;' +
    'box-shadow:0 1px 3px rgba(0,0,0,.06);}' +
    '.ffp-msg.user{align-self:flex-end;background:#2f80ed;color:#ffffff;border-bottom-right-radius:4px;}' +
    '.ffp-msg.ai{align-self:flex-start;background:#f0f6ff;color:#1c2b4a;border:1px solid #e3efff;border-bottom-left-radius:4px;}' +
    '.ffp-msg code{background:rgba(0,0,0,.08);padding:1px 5px;border-radius:5px;font-family:Consolas,monospace;font-size:12px;}' +
    '.ffp-msg.user code{background:rgba(255,255,255,.25);}' +
    '.ffp-msg .ffp-h1,.ffp-msg .ffp-h2,.ffp-msg .ffp-h3{font-weight:700;margin:4px 0;}' +
    '.ffp-msg .ffp-h1{font-size:15px;}.ffp-msg .ffp-h2{font-size:14px;}.ffp-msg .ffp-h3{font-size:13px;}' +
    '.ffp-msg .ffp-li{margin:2px 0;}' +
    '#ffp-typing{display:none;padding:8px 16px;font-size:12px;color:#5a7ca8;background:#fbfdff;}' +
    '#ffp-typing .ffp-dots i{animation:ffpDot 1.2s infinite;font-style:normal;margin-left:2px;}' +
    '#ffp-typing .ffp-dots i:nth-child(2){animation-delay:.2s;}' +
    '#ffp-typing .ffp-dots i:nth-child(3){animation-delay:.4s;}' +
    '@keyframes ffpDot{0%,60%,100%{opacity:.2;}30%{opacity:1;}}' +
    '#ffp-chat .ffp-chat-input{display:flex;gap:6px;padding:10px;border-top:1px solid #e3efff;background:#ffffff;}' +
    '#ffp-chat .ffp-chat-input textarea{flex:1;resize:none;height:52px;border:1px solid #cfe6ff;border-radius:10px;' +
    'padding:8px;font-size:13px;font-family:inherit;outline:none;box-sizing:border-box;}' +
    '#ffp-chat .ffp-chat-input textarea:focus{border-color:#2f80ed;}' +
    '#ffp-chat .ffp-chat-input button{background:#2f80ed;color:#ffffff;border:none;border-radius:10px;padding:0 16px;' +
    'font-size:13px;cursor:pointer;font-family:inherit;}' +
    '#ffp-chat .ffp-chat-input button:hover{background:#1e6fd6;}' +
    '.ffp-sidebar-glow{outline:3px solid #2f80ed !important;outline-offset:-3px;animation:ffpGlow 2.6s ease-in-out !important;}' +
    '@keyframes ffpGlow{0%,100%{box-shadow:0 0 0 5px rgba(47,128,237,.35);}50%{box-shadow:0 0 0 14px rgba(47,128,237,.08);}}' +
    '#ffp-drawer{position:fixed;top:0;right:0;width:50vw;height:100vh;z-index:999997;background:#ffffff;' +
    'box-shadow:-12px 0 40px rgba(30,80,160,.25);transform:translateX(102%);transition:transform .35s ease;' +
    'display:flex;flex-direction:column;overflow:hidden;font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;}' +
    '#ffp-drawer.ffp-open{transform:translateX(0);}' +
    '#ffp-drawer-head{display:flex;align-items:center;justify-content:space-between;padding:12px 18px;' +
    'background:linear-gradient(135deg,#2f80ed,#56a3ff);color:#ffffff;font-size:15px;font-weight:700;user-select:none;}' +
    '#ffp-drawer-close{background:rgba(255,255,255,.2);border:none;color:#ffffff;width:28px;height:28px;border-radius:8px;' +
    'cursor:pointer;font-size:14px;line-height:1;}' +
    '#ffp-drawer-close:hover{background:rgba(255,255,255,.35);}' +
    '#ffp-drawer-body{flex:1;overflow-y:auto;padding:16px 20px;box-sizing:border-box;}' +
    '#ffp-drawer-body .ffp-drawer-h{font-size:14px;font-weight:700;color:#1d4e8f;margin:14px 0 6px;}' +
    '#ffp-drawer-body .ffp-drawer-sub{font-size:12px;color:#5a7ca8;margin-bottom:8px;}' +
    '#ffp-drawer-body table{border-collapse:collapse;width:100%;font-size:12px;margin-bottom:6px;}' +
    '#ffp-drawer-body th,#ffp-drawer-body td{border:1px solid #d9e8fa;padding:5px 8px;text-align:left;word-break:break-all;}' +
    '#ffp-drawer-body th{background:#eef6ff;color:#1d4e8f;font-weight:600;}' +
    '#ffp-drawer-body img{max-width:100%;border-radius:8px;margin:6px 0;}' +
    '#ffp-drawer-body #ffp-eda-save-btn{background:#2f80ed;color:#ffffff;border:none;border-radius:8px;' +
    'padding:6px 14px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;' +
    'box-shadow:0 2px 8px rgba(47,128,237,.3);transition:background .15s;}' +
    '#ffp-drawer-body #ffp-eda-save-btn:hover{background:#1e6fd6;}' +
    '#ffp-drawer-tab{position:fixed;right:0;top:45%;z-index:999996;background:#2f80ed;color:#ffffff;padding:10px 8px;' +
    'border-radius:10px 0 0 10px;cursor:pointer;display:none;font-size:12px;font-weight:600;user-select:none;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;box-shadow:-4px 2px 12px rgba(30,80,160,.3);}' +
    '#ffp-sb-toggle-btn{background:#2f80ed;color:#ffffff;border:none;border-radius:8px;padding:10px 16px;' +
    'font-size:14px;font-weight:600;cursor:pointer;font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;' +
    'width:100%;transition:background .15s;}' +
    '#ffp-sb-toggle-btn:hover{background:#1e6fd6;}' +
    '#ffp-rice-make-btn{background:#fff8e1;color:#a56a00;border:1px solid #f3d58a;border-radius:8px;padding:10px 16px;' +
    'font-size:14px;font-weight:600;cursor:pointer;font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;width:100%;}' +
    '#ffp-rice-make-btn:hover{background:#ffe9a8;}' +
    '#ffp-rice-root{position:fixed;z-index:1000002;width:0;height:0;}' +
    '#ffp-rice-ball{position:absolute;width:58px;height:58px;border-radius:50%;background:#fff8e1;border:2px solid #f3d58a;' +
    'box-shadow:0 6px 18px rgba(165,106,0,.25);display:flex;align-items:center;justify-content:center;font-size:31px;cursor:grab;' +
    'touch-action:none;user-select:none;}' +
    '#ffp-rice-ball:active{cursor:grabbing;}#ffp-rice-count{position:absolute;right:-6px;top:-7px;background:#e67e22;color:#fff;' +
    'min-width:21px;height:21px;border-radius:999px;font:700 12px/21px Arial;text-align:center;padding:0 3px;}' +
    '#ffp-rice-ghost{position:fixed;z-index:1000003;display:none;pointer-events:none;font-size:34px;line-height:1;' +
    'transform:translate(-50%,-50%);filter:drop-shadow(0 4px 8px rgba(165,106,0,.28));}' +
    '#ffp-rice-panel{position:absolute;right:72px;top:0;width:170px;background:#fff;border:1px solid #f3d58a;border-radius:14px;' +
    'box-shadow:0 10px 28px rgba(165,106,0,.2);padding:10px;display:none;font:12px/1.5 "Microsoft YaHei",sans-serif;color:#76501b;}' +
    '#ffp-rice-panel.ffp-below{top:70px;right:auto;left:-55px;}#ffp-rice-panel b{color:#c26b00;font-size:16px;}' +
    '.ffp-rice-feed-target{outline:4px solid #f3b43f !important;outline-offset:3px;filter:drop-shadow(0 0 8px #f3b43f) !important;}' +
    '#ffp-outfit-dialog{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:1000001;' +
    'background:#ffffff;border:1.5px solid #cfe6ff;border-radius:16px;box-shadow:0 20px 60px rgba(31,84,168,.3);' +
    'padding:14px;display:none;flex-direction:column;gap:10px;width:360px;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;}' +
    '#ffp-outfit-dialog .ffp-bubble-title{text-align:center;font-size:13px;color:#5a7ca8;font-weight:700;}' +
    '#ffp-outfit-list{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;}' +
    '#ffp-outfit-list .ffp-outfit-item{display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;' +
    'border:2px solid #e3efff;border-radius:12px;padding:8px;background:#f8fbff;transition:all .15s;}' +
    '#ffp-outfit-list .ffp-outfit-item:hover{border-color:#2f80ed;background:#eef6ff;transform:translateY(-1px);}' +
    '#ffp-outfit-list .ffp-outfit-item img{width:76px;height:76px;object-fit:contain;}' +
    '#ffp-outfit-list .ffp-outfit-item span{font-size:11px;color:#1d4e8f;font-weight:600;}' +
    '#ffp-outfit-list .ffp-outfit-item.ffp-locked{opacity:.45;filter:grayscale(.7);cursor:not-allowed;}' +
    '#ffp-outfit-list .ffp-outfit-item .ffp-lock-tag{font-size:10px;color:#e67e22;font-weight:600;text-align:center;line-height:1.2;}' +
    '#ffp-outfit-dialog .ffp-outfit-actions{display:flex;flex-direction:column;gap:6px;}' +
    '#ffp-outfit-dialog .ffp-outfit-actions button{width:100%;padding:8px 6px;border:none;border-radius:10px;' +
    'background:#f4f9ff;color:#1d4e8f;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s;}' +
    '#ffp-outfit-dialog .ffp-outfit-actions button:hover{background:#2f80ed;color:#ffffff;}' +
    // ===== 小游戏「接米饭」样式 =====
    '#ffp-game-mask{position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:1000015;background:rgba(255,255,255,.45);' +
    'backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);' +
    'display:none;flex-direction:column;align-items:center;justify-content:center;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;}' +
    '#ffp-game-stage{position:relative;width:min(560px,92vw);height:min(620px,82vh);background:#ffffff;' +
    'border:2px solid #e3efff;border-radius:14px;overflow:hidden;box-shadow:0 16px 48px rgba(31,84,168,.18);}' +
    '#ffp-game-close{position:absolute;right:10px;top:10px;z-index:10;width:30px;height:30px;border:none;border-radius:8px;' +
    'background:#f4f9ff;color:#1d4e8f;font-size:16px;line-height:1;cursor:pointer;font-family:inherit;}' +
    '#ffp-game-close:hover{background:#2f80ed;color:#ffffff;}' +
    '#ffp-game-score{position:absolute;left:10px;top:10px;z-index:10;background:#2f80ed;color:#ffffff;font-size:13px;' +
    'padding:4px 12px;border-radius:999px;font-weight:700;}' +
    '#ffp-game-pause-tip{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:11;background:rgba(255,255,255,.95);' +
    'color:#1d4e8f;font-size:22px;font-weight:700;padding:18px 30px;border-radius:14px;display:none;box-shadow:0 8px 24px rgba(31,84,168,.25);}' +
    '#ffp-game-win{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:11;background:#ffffff;' +
    'color:#1d4e8f;font-size:20px;font-weight:700;padding:20px 34px;border-radius:14px;display:none;text-align:center;' +
    'box-shadow:0 8px 24px rgba(31,84,168,.25);}' +
    '.ffp-game-rice{position:absolute;font-size:26px;line-height:1;pointer-events:none;}' +
    '#ffp-game-player{position:absolute;bottom:8px;left:0;width:64px;height:64px;z-index:9;' +
    'background:center/contain no-repeat;}' +
    '#ffp-game-player video{width:100%;height:100%;object-fit:contain;pointer-events:none;}' +
    // ===== 蓝白封面遮罩 =====
    '#ffp-cover{position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:2147483647;' +
    'background:linear-gradient(180deg,#dcebff 0%,#f4f9ff 45%,#dfeefc 100%);' +
    'display:flex;align-items:center;justify-content:center;transition:transform .6s ease,opacity .6s ease;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;}' +
    '#ffp-cover.ffp-collapsed{transform:translateY(-100%);opacity:0;pointer-events:none;}' +
    '#ffp-cover-inner{display:flex;flex-direction:column;align-items:center;gap:26px;text-align:center;padding:0 24px;}' +
    '#ffp-cover-title{font-size:56px;font-weight:800;color:#1d4e8f;letter-spacing:2px;line-height:1.2;}' +
    '#ffp-cover-emoji{position:relative;display:inline-block;width:2em;height:2em;vertical-align:-0.55em;}' +
    '#ffp-cover-ciallo{position:absolute;left:50%;top:50%;width:2em;height:2em;transform:translate(-50%,-50%);' +
    'object-fit:contain;opacity:0;animation:ffpCialloFall .9s cubic-bezier(.2,.7,.3,1) .5s forwards;}' +
    '@keyframes ffpCialloFall{' +
    '0%{transform:translate(-50%,-50%) translateY(-46vh);opacity:0;}' +
    '45%{opacity:1;}' +
    '60%{transform:translate(-50%,-50%) translateY(4px);}' +
    '100%{transform:translate(-50%,-50%) translateY(0);opacity:1;}}' +
    '#ffp-cover-sub{font-size:17px;color:rgba(29,78,143,.5);font-weight:600;letter-spacing:3px;}' +
    '#ffp-cover-btn{background:linear-gradient(135deg,#2f80ed,#56a3ff);color:#ffffff;border:none;border-radius:999px;' +
    'padding:14px 40px;font-size:16px;font-weight:700;letter-spacing:1px;cursor:pointer;font-family:inherit;' +
    'box-shadow:0 8px 22px rgba(47,128,237,.35);transition:transform .15s ease,box-shadow .15s ease;}' +
    '#ffp-cover-btn:hover{transform:translateY(-2px);box-shadow:0 12px 28px rgba(47,128,237,.45);}' +
    // ===== 新手教程（黑色滤镜 / 露出洞口 / 图片 / 气泡 / 跳过按钮） =====
    '#ffp-tut-pimg{position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:2147483399;' +
    'pointer-events:none;display:none;overflow:hidden;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;}' +
    '#ffp-tut-pimg img{max-width:min(1100px,90vw);max-height:80vh;width:auto;height:auto;margin-top:7vh;' +
    'box-shadow:0 10px 30px rgba(0,0,0,.35);border-radius:10px;display:inline-block;}' +
    '#ffp-tut-pimg img.ffp-pimg-half{width:50vw !important;height:100vh !important;object-fit:cover !important;' +
    'max-width:none !important;max-height:none !important;margin-top:0 !important;border-radius:0 !important;box-shadow:none !important;}' +
    '#ffp-tut-extra{position:fixed;left:18px;bottom:18px;z-index:2147483402;pointer-events:none;display:none;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;}' +
    '#ffp-tut-extra .ffp-extra-row{display:flex;align-items:center;gap:12px;}' +
    '#ffp-tut-extra img{display:block;width:auto;height:auto;}' +
    '#ffp-tut-extra .ffp-extra-bubble{background:#ffffff;border:2px solid #cfe6ff;border-radius:14px;' +
    'box-shadow:0 10px 26px rgba(31,84,168,.25);padding:8px 14px;font-size:14px;line-height:1.5;color:#1c2b4a;white-space:nowrap;}' +
    '#ffp-tut-filter{position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:2147483400;' +
    'background:transparent;cursor:pointer;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;}' +
    '#ffp-tut-hold{position:fixed;z-index:2147483401;pointer-events:none;display:none;' +
    'border-radius:12px;' +
    'transition:left .35s ease,top .35s ease,width .35s ease,height .35s ease,background .35s ease,box-shadow .35s ease;}' +
    '#ffp-tut-img{position:fixed;z-index:2147483402;pointer-events:none;transform:translate(-50%,-50%);' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;}' +
    '#ffp-tut-img img{width:min(280px,30vw);max-height:44vh;object-fit:contain;display:block;' +
    'filter:drop-shadow(0 10px 22px rgba(31,84,168,.4));}' +
    '#ffp-tut-img .ffp-tut-fallback{font-size:90px;line-height:1;}' +
    '#ffp-tut-bubble{position:fixed;z-index:2147483403;pointer-events:none;width:300px;max-width:34vw;' +
    'background:#ffffff;border:2px solid #cfe6ff;border-radius:16px;' +
    'box-shadow:0 14px 38px rgba(31,84,168,.32);padding:12px 14px 10px;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;box-sizing:border-box;' +
    'user-select:none;-webkit-user-select:none;}' +
    '#ffp-tut-bubble .ffp-tut-text{font-size:14px;line-height:1.7;color:#1c2b4a;word-break:break-word;}' +
    '#ffp-tut-bubble .ffp-tut-progress{font-size:10.5px;color:#8aa6c8;margin-top:8px;text-align:left;}' +
    '#ffp-tut-skip{position:fixed;right:14px;top:14px;z-index:2147483404;background:rgba(255,255,255,.94);' +
    'border:1.5px solid #cfe6ff;border-radius:999px;padding:8px 18px;font-size:13px;font-weight:700;color:#1d4e8f;' +
    'cursor:pointer;font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;' +
    'box-shadow:0 4px 16px rgba(31,84,168,.25);transition:all .15s;}' +
    '#ffp-tut-skip:hover{background:#2f80ed;color:#ffffff;}' +
    // ===== 右上角 Q/A 按钮 + 重播弹窗 =====
    '#ffp-qa-btn{position:fixed;right:14px;top:14px;z-index:2147482900;background:#2f80ed;color:#ffffff;' +
    'border:none;border-radius:12px;padding:9px 18px;font-size:14px;font-weight:800;letter-spacing:1px;' +
    'cursor:pointer;font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;' +
    'box-shadow:0 5px 16px rgba(47,128,237,.38);transition:all .15s;}' +
    '#ffp-qa-btn:hover{background:#1e6fd6;transform:translateY(-1px);}' +
    '#ffp-qa-pop{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:2147482950;' +
    'background:#ffffff;border:2px solid #cfe6ff;border-radius:16px;box-shadow:0 22px 60px rgba(31,84,168,.35);' +
    'padding:22px 26px;display:none;flex-direction:column;align-items:center;gap:12px;width:320px;max-width:86vw;' +
    'font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;box-sizing:border-box;}' +
    '#ffp-qa-pop .ffp-qa-title{font-size:15px;font-weight:800;color:#1d4e8f;}' +
    '#ffp-qa-pop .ffp-qa-text{font-size:13px;color:#5a7ca8;text-align:center;line-height:1.6;}' +
    '#ffp-qa-pop .ffp-qa-actions{display:flex;gap:10px;}' +
    '#ffp-qa-pop .ffp-qa-actions button{border:none;border-radius:10px;padding:9px 18px;font-size:13px;font-weight:700;' +
    'cursor:pointer;font-family:inherit;transition:all .15s;}' +
    '#ffp-qa-play{background:#2f80ed;color:#ffffff;}' +
    '#ffp-qa-play:hover{background:#1e6fd6;}' +
    '#ffp-qa-close{background:#f4f9ff;color:#1d4e8f;}' +
    '#ffp-qa-close:hover{background:#e3efff;}';
  pd.head.appendChild(style);
  // 封面遮罩优先挂载：一进入页面就盖住主页面，待点击收起后才露出
  coverInit();

  var root = pd.createElement('div');
  root.id = 'ffp-root';
  var speechBubble = pd.createElement('div');
  speechBubble.id = 'ffp-speech-bubble';
  var speech = pd.createElement('div');
  speech.id = 'ffp-speech';
  speech.innerHTML = '<div id="ffp-speech-text"></div><div id="ffp-speech-refresh">🔄 换一句</div>';
  speechBubble.appendChild(speech);
  var menuBubble = pd.createElement('div');
  menuBubble.id = 'ffp-menu-bubble';
  var ball = pd.createElement('div');
  ball.id = 'ffp-ball';
  ball.title = '点我 / 拖我';
  var img = pd.createElement('img');
  img.id = 'ffp-img';
  img.draggable = false;
  img.alt = '大肥鱼';
  var badge = pd.createElement('div');
  badge.id = 'ffp-name';
  badge.textContent = '大肥鱼';
  var favorEl = pd.createElement('div');
  favorEl.id = 'ffp-favor';
  favorEl.textContent = '当前好感度：0';
  ball.appendChild(img);
  ball.appendChild(badge);
  ball.appendChild(favorEl);
  root.appendChild(speechBubble);
  root.appendChild(menuBubble);
  root.appendChild(ball);
  pd.body.appendChild(root);

  var riceRoot = pd.createElement('div');
  riceRoot.id = 'ffp-rice-root';
  var riceBall = pd.createElement('div');
  riceBall.id = 'ffp-rice-ball';
  riceBall.innerHTML = '<span>🍚</span><span id="ffp-rice-count">0</span>';
  var ricePanel = pd.createElement('div');
  ricePanel.id = 'ffp-rice-panel';
  ricePanel.innerHTML = '<div>🍚 白饭库存：<b id="ffp-rice-value">0</b> 碗</div><div>展开后拖动米饭，喂给大肥鱼或页面图片</div>';
  riceRoot.appendChild(ricePanel);
  riceRoot.appendChild(riceBall);
  pd.body.appendChild(riceRoot);
  var riceGhost = pd.createElement('div');
  riceGhost.id = 'ffp-rice-ghost';
  riceGhost.textContent = '🍚';
  pd.body.appendChild(riceGhost);

  var MAX_RICE = 67;
  var riceCount = parseInt(load('ffp_rice_count') || '0', 10);
  if (isNaN(riceCount) || riceCount < 0) { riceCount = 0; }
  var riceExpanded = false;
  function updateRice() {
    riceCount = Math.max(0, riceCount);
    store('ffp_rice_count', String(riceCount));
    var badge = pd.getElementById('ffp-rice-count');
    var value = pd.getElementById('ffp-rice-value');
    if (badge) { badge.textContent = String(riceCount); }
    if (value) { value.textContent = String(riceCount); }
  }
  function getFavor() {
    var f = parseInt(load('ffp_favor') || '0', 10);
    if (isNaN(f) || f < 0) { f = 0; }
    return f;
  }
  function updateFavorFame() {
    var el = pd.getElementById('ffp-favor');
    if (el) {
      el.textContent = '当前好感度：' + getFavor();
    }
  }
  updateFavorFame();
  function setRiceExpanded(open) {
    riceExpanded = open;
    ricePanel.style.display = open ? 'block' : 'none';
    if (open) {
      var top = riceRoot.offsetTop || 0;
      ricePanel.classList.toggle('ffp-below', top < 150);
    }
  }
  var ricePos = null;
  try { ricePos = JSON.parse(load('ffp_rice_pos') || 'null'); } catch (e) { ricePos = null; }
  function setRicePos(x, y, savePos) {
    var w = winW(), h = winH();
    x = Math.min(Math.max(0, x), Math.max(0, w - 58));
    y = Math.min(Math.max(0, y), Math.max(0, h - 58));
    riceRoot.style.left = x + 'px'; riceRoot.style.top = y + 'px';
    if (savePos) { store('ffp_rice_pos', JSON.stringify({x:x, y:y})); }
  }
  updateRice();

  function riceTargets() {
    var result = [ball];
    var nodes = pd.querySelectorAll('[data-testid="stFileUploaderDropzone"],[data-testid="stFileUploadDropzone"]');
    for (var i = 0; i < nodes.length; i++) { result.push(nodes[i]); }
    var images = pd.querySelectorAll('img');
    for (var j = 0; j < images.length; j++) {
      if (images[j].id !== 'ffp-img' && !images[j].closest('#ffp-rice-root') && !images[j].closest('#ffp-chat')) {
        result.push(images[j]);
      }
    }
    return result;
  }
  function riceHit(el, x, y) {
    if (!el) { return false; }
    var r = el.getBoundingClientRect();
    return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
  }
  function clearRiceTargets() {
    var targets = riceTargets();
    for (var i = 0; i < targets.length; i++) { targets[i].classList.remove('ffp-rice-feed-target'); }
  }
  // ============================================================
  // ===== 通用消息提交：向页面对话输入框写入哨兵并回车提交 =====
  // （不依赖任何隐藏按钮；主端按哨兵前缀解析并处理）
  // ============================================================
  var FFP_FEED_TOKEN = '[[FFP_FEED]]';
  function findChatInput() {
    try {
      var inputs = pd.querySelectorAll('div[data-testid="stTextInput"] input');
      for (var i = 0; i < inputs.length; i++) {
        var ph = (inputs[i].placeholder || '');
        if (ph.indexOf('投喂数据集') !== -1 || ph.indexOf('训练ZIP') !== -1) {
          return inputs[i];
        }
      }
      return null;
    } catch (e) { return null; }
  }
  function petSubmitValue(value) {
    try {
      var input = findChatInput();
      if (!input) { return false; }
      var setter = null;
      try {
        setter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, 'value').set;
      } catch (e) {}
      if (!setter) { return false; }
      var prev = input.value;
      var pw = window.parent;
      // 1) 先聚焦（保证 blur 事件可以触发——Streamlit 文本输入在失焦时提交值）
      try { input.focus(); } catch (e0) {}
      // 2) 原生 setter 写入值 + input 事件（更新 React 状态）
      setter.call(input, value);
      try { input.dispatchEvent(new pw.Event('input', { bubbles: true })); } catch (e2) {}
      // 3) 合成回车提交（Streamlit: Enter → blur → 提交）
      try {
        input.dispatchEvent(new pw.KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true }));
        input.dispatchEvent(new pw.KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true }));
      } catch (e3) {}
      // 4) 关键：失焦提交（比合成回车更可靠的提交路径）
      try { input.blur(); } catch (e4) {}
      // 5) 最后恢复显示值，避免哨兵字符在输入框闪现（React 状态已提交）
      setter.call(input, prev);
      return true;
    } catch (e) { return false; }
  }
  function notifyMainChat(feedIdx) {
    var token = String(Date.now()) + '_' + String(Math.random()).slice(2);
    // 只提交 token + 台词序号（纯文本，避免被输入组件清洗）；主端据此从20条投喂台词中选一条输出
    var payload = FFP_FEED_TOKEN + token + ':' + (feedIdx == null ? -1 : feedIdx);
    try { petSubmitValue(payload); } catch (e) {}
    // 保险：700ms 后补交一次（主端按 token 去重，不会重复输出）
    setTimeout(function () {
      try { petSubmitValue(payload); } catch (e) {}
    }, 700);
  }
  function saveEdaWord() {
    var btn = pd.getElementById('ffp-eda-save-btn');
    if (btn) {
      btn.textContent = '⏳ 正在保存...';
      setTimeout(function () { try { btn.textContent = '💾 保存'; } catch (e) {} }, 15000);
    }
    var token = String(Date.now()) + '_' + String(Math.random()).slice(2);
    var payload = FFP_SAVE_EDA_TOKEN + token;
    try { petSubmitValue(payload); } catch (e) {}
    setTimeout(function () { try { petSubmitValue(payload); } catch (e) {} }, 700);
  }
  function feedRice(targetKind) {
    if (riceCount <= 0) {
      if (targetKind !== 'upload') {
        openBubbleWith('主人，库存里没有白饭啦，先去「🍚做米饭」吧！');
      }
      return;
    }
    riceCount -= 1;
    updateRice();
    computeImages();
    store('ffp_favor', String(getFavor() + 1));
    updateFavorFame();
    var feedIdx = RICE_FEED_LINES && RICE_FEED_LINES.length
      ? Math.floor(Math.random() * RICE_FEED_LINES.length)
      : -1;
    var line = (feedIdx >= 0 && RICE_FEED_LINES[feedIdx]) || '好感度+1，白饭很好吃哦。(๑´ڡ`๑)';
    if (targetKind === 'upload') {
      // 上传区域投喂只回传主页消息（主端从20条投喂台词中选一条输出），不打开桌宠气泡或写入桌宠聊天窗。
      notifyMainChat(feedIdx);
      return;
    }
    if (targetKind === 'image') {
      // 投喂页面图片：弹出桌宠气泡，同时把台词序号回传，主页聊天栏直接输出20条投喂台词之一。
      openBubbleWith('好感度+1\n' + line);
      notifyMainChat(feedIdx);
      return;
    }
    openBubbleWith('好感度+1\n' + line);
    try {
      msgs.push({ role: 'assistant', content: '好感度+1\n' + line });
      saveChat();
      renderMsgs();
    } catch (e) {}
  }
  var riceDragging = false, riceMoved = false, riceFeedMode = false, riceTargetKind = null;
  var riceSX = 0, riceSY = 0, riceOX = 0, riceOY = 0;
  riceBall.addEventListener('pointerdown', function (e) {
    if (e.button && e.button !== 0) { return; }
    riceDragging = true; riceMoved = false; riceFeedMode = riceExpanded;
    riceSX = e.clientX; riceSY = e.clientY;
    riceOX = riceRoot.offsetLeft || 0; riceOY = riceRoot.offsetTop || 0;
    try { riceBall.setPointerCapture(e.pointerId); } catch (err) {}
    e.preventDefault(); e.stopPropagation();
  });
  riceBall.addEventListener('pointermove', function (e) {
    if (!riceDragging) { return; }
    var dx = e.clientX - riceSX, dy = e.clientY - riceSY;
    if (Math.abs(dx) + Math.abs(dy) > 5) { riceMoved = true; }
    if (riceFeedMode) {
      riceGhost.style.display = riceMoved && riceCount > 0 ? 'block' : 'none';
      riceGhost.style.left = e.clientX + 'px';
      riceGhost.style.top = e.clientY + 'px';
      clearRiceTargets();
      var targets = riceTargets();
      for (var i = 0; i < targets.length; i++) {
        if (riceMoved && riceCount > 0 && riceHit(targets[i], e.clientX, e.clientY)) {
          targets[i].classList.add('ffp-rice-feed-target');
        }
      }
    } else if (riceMoved) {
      setRicePos(riceOX + dx, riceOY + dy, false);
    }
    e.preventDefault();
  });
  function finishRice(e) {
    if (!riceDragging) { return; }
    var shouldFeed = riceFeedMode && riceMoved && riceCount > 0;
    if (shouldFeed) {
      var targets = riceTargets();
      shouldFeed = targets.some(function (el) { return riceHit(el, e.clientX, e.clientY); });
    }
    riceDragging = false;
    riceGhost.style.display = 'none';
    clearRiceTargets();
    if (riceFeedMode && shouldFeed) {
      var hitTargets = riceTargets();
      riceTargetKind = 'pet';
      for (var i = 0; i < hitTargets.length; i++) {
        if (!riceHit(hitTargets[i], e.clientX, e.clientY)) { continue; }
        var testId = hitTargets[i].getAttribute('data-testid');
        if (testId === 'stFileUploaderDropzone' || testId === 'stFileUploadDropzone') {
          riceTargetKind = 'upload';
          break;
        }
        var tag = (hitTargets[i].tagName || '').toUpperCase();
        if (tag === 'IMG' && hitTargets[i].id !== 'ffp-img') {
          riceTargetKind = 'image';
          break;
        }
      }
      feedRice(riceTargetKind);
      riceTargetKind = null;
    } else if (!riceFeedMode && riceMoved) {
      setRicePos(riceRoot.offsetLeft || 0, riceRoot.offsetTop || 0, true);
    } else if (!riceMoved) {
      setRiceExpanded(!riceExpanded);
    }
    e.preventDefault(); e.stopPropagation();
  }
  riceBall.addEventListener('pointerup', finishRice);
  riceBall.addEventListener('pointercancel', finishRice);

  function makeRice() {
    if (riceCount >= MAX_RICE) {
      openBubbleWith('676767676767');
      computeImages();
      return;
    }
    var progress = parseInt(load('ffp_rice_make_progress') || '0', 10);
    if (isNaN(progress) || progress < 0 || progress > 2) { progress = 0; }
    progress += 1;
    if (progress >= 3) {
      progress = 0; riceCount += 1; updateRice();
      computeImages();
      openBubbleWith('🍚 一碗白饭做好啦！库存增加到 ' + riceCount + ' 碗。(๑•̀ㅂ•́)و✧');
    } else {
      var left = 3 - progress;
      openBubbleWith('再点击' + left + '次做一碗白饭～');
    }
    store('ffp_rice_make_progress', String(progress));
  }
  // 每次脚本执行都重建按钮并绑定当前闭包，避免 rerun 后旧按钮持有失效监听
  var riceMakeInjected = false;
  function ensureRiceMakeBtn() {
    var slot = pd.getElementById('ffp-rice-make-slot');
    if (!slot || riceMakeInjected) { return; }
    riceMakeInjected = true;
    var old = pd.getElementById('ffp-rice-make-btn');
    if (old) { old.remove(); }
    var b = pd.createElement('button');
    b.id = 'ffp-rice-make-btn'; b.textContent = '🍚做米饭';
    b.addEventListener('click', function () { makeRice(); });
    slot.innerHTML = ''; slot.appendChild(b);
  }
  var savedRicePos = null;
  try { savedRicePos = JSON.parse(load('ffp_rice_pos') || 'null'); } catch (e) { savedRicePos = null; }
  if (savedRicePos && typeof savedRicePos.x === 'number' && typeof savedRicePos.y === 'number') {
    setRicePos(savedRicePos.x, savedRicePos.y, false);
  } else {
    setRicePos(winW() - 94, winH() - 220, false);
  }
  ensureRiceMakeBtn();

  var speechLocked = false, menuLocked = false;
  function applyLockToBubble(el, key) {
    var v = null;
    try { v = JSON.parse(load(key) || 'null'); } catch (e) { v = null; }
    if (v && typeof v.x === 'number' && typeof v.y === 'number') {
      el.style.left = v.x + 'px';
      el.style.top = v.y + 'px';
      el.style.right = 'auto';
      el.style.bottom = 'auto';
      el.style.transform = 'none';
      el.classList.remove('ffp-below');
      return true;
    }
    return false;
  }
  speechLocked = applyLockToBubble(speechBubble, 'ffp_speech_lock');
  menuLocked = applyLockToBubble(menuBubble, 'ffp_menu_lock');

  var normalImg = null;
  var dragImg = null;
  function computeImages() {
    var custom = load('ffp_img');
    var outfit = load('ffp_outfit') || 'default';
    if (custom) {
      normalImg = custom;
      dragImg = custom;
    } else if (outfit === 'outfit') {
      normalImg = OUTFIT_IMG;
      dragImg = OUTFIT_DRAG_IMG;
    } else if (outfit === 'harness') {
      normalImg = HARNESS_IMG;
      dragImg = HARNESS_DRAG_IMG;
    } else if (outfit === 'mystery') {
      normalImg = MYSTERY_IMG;
      dragImg = MYSTERY_DRAG_IMG;
    } else {
      normalImg = DEFAULT_IMG;
      dragImg = DRAG_IMG;
    }
    if (riceCount >= MAX_RICE && RICE_MAX_IMG) {
      normalImg = RICE_MAX_IMG;
      dragImg = RICE_MAX_IMG;
    }
    img.src = normalImg;
  }
  computeImages();

  var sizeFactor = parseFloat(load('ffp_size') || '2.5');
  if (isNaN(sizeFactor) || sizeFactor < 1) { sizeFactor = 1; }
  if (sizeFactor > 5) { sizeFactor = 5; }
  var ballSize = Math.round(84 * sizeFactor);

  var bubbleFactor = parseFloat(load('ffp_bubble_size') || '1.25');
  if (isNaN(bubbleFactor) || bubbleFactor < 1) { bubbleFactor = 1; }
  if (bubbleFactor > 2) { bubbleFactor = 2; }

  function positionBubbles() {
    var rl = root.offsetLeft || 0;
    var w = winW();
    var gap = 12;
    var spW = Math.round(150 * bubbleFactor) + 22;
    var below = (root.offsetTop || 0) < 320;
    function placeDefault(el) {
      if (below) {
        el.classList.add('ffp-below');
        el.style.top = (ballSize + 16) + 'px';
        el.style.bottom = 'auto';
        el.style.transform = 'none';
      } else {
        el.classList.remove('ffp-below');
        el.style.top = Math.round(ballSize / 2) + 'px';
        el.style.bottom = 'auto';
        el.style.transform = 'translateY(-50%)';
      }
    }
    if (!speechLocked) {
      placeDefault(speechBubble);
      var speechRight = ballSize + gap;
      var maxRight = rl - 8 - spW;
      if (speechRight > maxRight) { speechRight = maxRight; }
      if (speechRight < -spW) { speechRight = -spW; }
      speechBubble.style.right = speechRight + 'px';
      speechBubble.style.left = 'auto';
    }
    if (!menuLocked) {
      placeDefault(menuBubble);
      var menuLeft = ballSize + gap;
      var maxLeft = w - 8 - 172 - rl;
      if (menuLeft > maxLeft) { menuLeft = maxLeft; }
      if (menuLeft < -160) { menuLeft = -160; }
      menuBubble.style.left = menuLeft + 'px';
      menuBubble.style.right = 'auto';
    }
  }

  function applySize() {
    ballSize = Math.round(84 * sizeFactor);
    ball.style.width = ballSize + 'px';
    ball.style.height = ballSize + 'px';
    badge.style.fontSize = Math.min(16, Math.round(11 * sizeFactor)) + 'px';
    var fEl = pd.getElementById('ffp-favor');
    if (fEl) { fEl.style.fontSize = Math.min(14, Math.round(10 * sizeFactor)) + 'px'; }
    if (!speechLocked) {
      speechBubble.style.right = (ballSize + 12) + 'px';
      speechBubble.style.left = 'auto';
    }
    if (!menuLocked) {
      menuBubble.style.right = 'auto';
      menuBubble.style.left = (ballSize + 12) + 'px';
    }
    positionBubbles();
    var val = pd.getElementById('ffp-size-val');
    if (val) { val.textContent = sizeFactor.toFixed(2).replace(/\.?0+$/, '') + 'x'; }
  }
  applySize();

  function applyBubbleSize() {
    var w = Math.round(150 * bubbleFactor);
    speechBubble.style.width = w + 'px';
    speech.style.fontSize = Math.round(12 * bubbleFactor) + 'px';
    var refresh = pd.getElementById('ffp-speech-refresh');
    if (refresh) { refresh.style.fontSize = Math.round(11 * bubbleFactor) + 'px'; }
    var val = pd.getElementById('ffp-bubble-size-val');
    if (val) { val.textContent = bubbleFactor.toFixed(2).replace(/\.?0+$/, '') + 'x'; }
  }
  applyBubbleSize();

  function winW() { try { return window.parent.innerWidth || 0; } catch (e) { return 0; } }
  function winH() { try { return window.parent.innerHeight || 0; } catch (e) { return 0; } }

  var savedPos = null;
  try { savedPos = JSON.parse(load('ffp_pos') || 'null'); } catch (e) { savedPos = null; }

  function setPos(nx, ny, save) {
    var w = winW(), h = winH();
    nx = Math.min(Math.max(0, nx), Math.max(0, w - ballSize));
    ny = Math.min(Math.max(0, ny), Math.max(0, h - ballSize));
    root.style.left = nx + 'px';
    root.style.top = ny + 'px';
    if (save) { store('ffp_pos', JSON.stringify({ x: nx, y: ny })); }
  }

  if (savedPos && typeof savedPos.x === 'number' && typeof savedPos.y === 'number') {
    setPos(savedPos.x, savedPos.y, false);
  } else {
    setPos(winW() - 24 - ballSize, winH() - 120 - ballSize, false);
  }

  try {
    window.parent.addEventListener('resize', function () {
      setPos(root.offsetLeft || 0, root.offsetTop || 0, false);
    });
  } catch (e) {}

  var dragging = false, moved = false, sx = 0, sy = 0, ox = 0, oy = 0;
  function onDown(e) {
    if (e.button && e.button !== 0) { return; }
    dragging = true;
    moved = false;
    sx = e.clientX;
    sy = e.clientY;
    ox = root.offsetLeft || 0;
    oy = root.offsetTop || 0;
    ball.classList.add('ffp-dragging');
    e.preventDefault();
  }
  function onMove(e) {
    if (!dragging) { return; }
    var dx = e.clientX - sx, dy = e.clientY - sy;
    if (Math.abs(dx) + Math.abs(dy) > 4) { moved = true; }
    if (moved) {
      if (img.getAttribute('src') !== dragImg) { img.src = dragImg; }
      setPos(ox + dx, oy + dy, false);
    }
  }
  function onUp() {
    if (!dragging) { return; }
    dragging = false;
    ball.classList.remove('ffp-dragging');
    if (moved) {
      img.src = normalImg;
      setPos(root.offsetLeft || 0, root.offsetTop || 0, true);
      positionBubbles();
    } else {
      toggleBubble();
    }
  }
  ball.addEventListener('pointerdown', onDown);
  pd.addEventListener('pointermove', onMove);
  pd.addEventListener('pointerup', onUp);

  var bubbleOpen = false;
  function setSpeech(text) {
    var el = pd.getElementById('ffp-speech-text');
    if (el) { el.textContent = text; }
  }
  function randomLine() {
    if (!PRESET_LINES || !PRESET_LINES.length) { return '……'; }
    return PRESET_LINES[Math.floor(Math.random() * PRESET_LINES.length)];
  }
  function openBubbleWith(text) {
    bubbleOpen = true;
    speechBubble.style.display = 'flex';
    setSpeech(text);
    positionBubbles();
  }
  function toggleBubble() {
    bubbleOpen = !bubbleOpen;
    speechBubble.style.display = bubbleOpen ? 'flex' : 'none';
    menuBubble.style.display = bubbleOpen ? 'flex' : 'none';
    if (bubbleOpen) {
      showMenu();
      setSpeech(randomLine());
      positionBubbles();
    }
  }
  function closeBubble() {
    bubbleOpen = false;
    speechBubble.style.display = 'none';
    menuBubble.style.display = 'none';
  }

  function makeBubbleDraggable(el, lockKey, onLock) {
    var dragging = false, moved = false, sx = 0, sy = 0, ox = 0, oy = 0;
    el.addEventListener('pointerdown', function (e) {
      var t = e.target;
      while (t && t !== el) {
        var tag = (t.tagName || '').toUpperCase();
        if (tag === 'BUTTON' || tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' ||
            t.id === 'ffp-speech-refresh') { return; }
        t = t.parentNode;
      }
      if (e.button && e.button !== 0) { return; }
      try {
        var cs = window.parent.getComputedStyle(el);
        var tf = cs && cs.transform;
        if (tf && tf !== 'none') {
          var parts = tf.match(/[-\d.]+/g);
          if (parts && parts.length >= 6) {
            el.style.transform = 'none';
            el.style.left = (el.offsetLeft || 0) + 'px';
            el.style.right = 'auto';
            el.style.top = ((el.offsetTop || 0) + parseFloat(parts[5])) + 'px';
            el.style.bottom = 'auto';
          }
        } else if (!el.style.left || el.style.left === 'auto') {
          el.style.left = (el.offsetLeft || 0) + 'px';
          el.style.right = 'auto';
        }
      } catch (e2) {}
      dragging = true;
      moved = false;
      sx = e.clientX;
      sy = e.clientY;
      ox = el.offsetLeft || 0;
      oy = el.offsetTop || 0;
      el.classList.add('ffp-dragging-bubble');
      e.preventDefault();
    });
    function onMove(e) {
      if (!dragging) { return; }
      var dx = e.clientX - sx, dy = e.clientY - sy;
      if (Math.abs(dx) + Math.abs(dy) > 4) { moved = true; }
      if (moved) {
        el.style.left = (ox + dx) + 'px';
        el.style.top = (oy + dy) + 'px';
        el.style.right = 'auto';
        el.style.bottom = 'auto';
        el.style.transform = 'none';
        el.classList.remove('ffp-below');
        e.preventDefault();
      }
    }
    function onUp() {
      if (!dragging) { return; }
      dragging = false;
      el.classList.remove('ffp-dragging-bubble');
      if (moved) {
        store(lockKey, JSON.stringify({ x: el.offsetLeft || 0, y: el.offsetTop || 0 }));
        onLock(true);
      }
    }
    pd.addEventListener('pointermove', onMove);
    pd.addEventListener('pointerup', onUp);
  }
  makeBubbleDraggable(speechBubble, 'ffp_speech_lock', function (v) { speechLocked = v; });
  makeBubbleDraggable(menuBubble, 'ffp_menu_lock', function (v) { menuLocked = v; });
  pd.addEventListener('pointerdown', function (e) {
    if (!bubbleOpen) { return; }
    if (root.contains(e.target)) { return; }
    closeBubble();
  });

  function isVisible(el) {
    if (!el) { return false; }
    try {
      var cs = window.parent.getComputedStyle(el);
      var r = el.getBoundingClientRect();
      return cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 0 && r.height > 0;
    } catch (e) {
      return !!el;
    }
  }

  function clickElement(el) {
    if (!el) { return false; }
    var target = ((el.tagName || '').toUpperCase() === 'BUTTON') ? el : el.querySelector('button');
    if (!target) { target = el; }
    try {
      var r = target.getBoundingClientRect();
      var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
      var opts = { bubbles: true, cancelable: true, clientX: cx, clientY: cy, button: 0 };
      var pw = window.parent;
      target.dispatchEvent(new pw.PointerEvent('pointerdown', opts));
      target.dispatchEvent(new pw.MouseEvent('mousedown', opts));
      target.dispatchEvent(new pw.PointerEvent('pointerup', opts));
      target.dispatchEvent(new pw.MouseEvent('mouseup', opts));
      target.dispatchEvent(new pw.MouseEvent('click', opts));
    } catch (e) {
      try { target.click(); } catch (e2) { return false; }
    }
    return true;
  }

  function clickTestIdBtn(testId) {
    var nodes = pd.querySelectorAll('[data-testid="' + testId + '"]');
    for (var i = 0; i < nodes.length; i++) {
      if (clickElement(nodes[i])) { return true; }
    }
    return false;
  }

  function clickSidebarButton(kind) {
    var collapseIds = ['stSidebarCollapseButton', 'stSidebarCollapseButtonMobile'];
    var expandIds = ['stExpandSidebarButton', 'stSidebarCollapsedControl', 'stSidebarExpandButton'];
    var ids = kind === 'collapse' ? collapseIds : expandIds;
    for (var i = 0; i < ids.length; i++) {
      if (clickTestIdBtn(ids[i])) { return true; }
    }

    var words = kind === 'collapse'
      ? ['collapse', 'close', 'hide', '收起', '关闭', '隐藏']
      : ['expand', 'open', 'show', '展开', '打开', '显示'];
    var btns = pd.querySelectorAll('button,[role="button"]');
    for (var j = 0; j < btns.length; j++) {
      var b = btns[j];
      if (b.id === 'ffp-sb-toggle-btn') { continue; }
      var txt = [b.getAttribute('aria-label'), b.getAttribute('title'), b.getAttribute('data-testid'), b.textContent]
        .join(' ').toLowerCase();
      if (txt.indexOf('sidebar') === -1 && txt.indexOf('侧边栏') === -1) { continue; }
      for (var k = 0; k < words.length; k++) {
        if (txt.indexOf(words[k]) !== -1 && clickElement(b)) { return true; }
      }
    }
    return false;
  }

  function toggleSidebar() {
    try {
      var sb = pd.querySelector('section[data-testid="stSidebar"]');
      var isOpen = false;
      if (sb) {
        try {
          sb.dispatchEvent(new window.parent.MouseEvent('mouseenter', { bubbles: true }));
          sb.dispatchEvent(new window.parent.MouseEvent('mousemove', { bubbles: true }));
        } catch (e2) {}
        var rect = sb.getBoundingClientRect();
        var cs = window.parent.getComputedStyle(sb);
        isOpen = rect.width > 80 && cs.display !== 'none' && cs.visibility !== 'hidden';
      }
      if (isOpen) {
        clickSidebarButton('collapse');
      } else {
        clickSidebarButton('expand');
        var applyGlow = function () {
          var s = pd.querySelector('section[data-testid="stSidebar"]');
          if (!s) { return; }
          s.classList.remove('ffp-sidebar-glow');
          void s.offsetWidth;
          s.classList.add('ffp-sidebar-glow');
          setTimeout(function () { s.classList.remove('ffp-sidebar-glow'); }, 2600);
        };
        applyGlow();
        setTimeout(applyGlow, 600);
      }
    } catch (e) {}
  }

  var chat = pd.createElement('div');
  chat.id = 'ffp-chat';
  chat.innerHTML = '' +
    '<div class="ffp-chat-head" id="ffp-chat-head">' +
    '<div class="ffp-chat-title">🐋 大肥鱼 · 智能对话</div>' +
    '<div class="ffp-chat-btns">' +
    '<button id="ffp-btn-key" title="API设置">⚙️</button>' +
    '<button id="ffp-btn-clear" title="清空对话">🧹</button>' +
    '<button id="ffp-btn-close" title="关闭">✖️</button>' +
    '</div></div>' +
    '<div id="ffp-key-panel">' +
    '<input id="ffp-key-input" type="password" placeholder="输入DeepSeek API Key（可选，默认用后端已配置的Key）">' +
    '<button id="ffp-key-save">保存Key</button>' +
    '</div>' +
    '<div class="ffp-chat-tools">' +
    '<button id="ffp-analyze-btn">⚡ 执行分析</button>' +
    '</div>' +
    '<div id="ffp-chat-msgs"></div>' +
    '<div id="ffp-typing">🐋 大肥鱼鼓着腮帮子思考中<span class="ffp-dots"><i>.</i><i>.</i><i>.</i></span></div>' +
    '<div class="ffp-chat-input">' +
    '<textarea id="ffp-chat-text" placeholder="跟大肥鱼说点什么吧~（它只听主人的话）"></textarea>' +
    '<button id="ffp-chat-send">发送</button>' +
    '</div>';
  pd.body.appendChild(chat);

  var savedChatPos = null;
  try { savedChatPos = JSON.parse(load('ffp_chat_pos') || 'null'); } catch (e) { savedChatPos = null; }
  if (savedChatPos && typeof savedChatPos.x === 'number' && typeof savedChatPos.y === 'number') {
    chat.style.left = savedChatPos.x + 'px';
    chat.style.top = savedChatPos.y + 'px';
    chat.style.right = 'auto';
    chat.style.bottom = 'auto';
  }

  function clampChatPos() {
    var disp = 'none';
    try { disp = window.parent.getComputedStyle(chat).display; } catch (e) {}
    if (disp === 'none') { return; }
    if (!chat.style.left || chat.style.left === 'auto') { return; }
    var w = winW(), h = winH();
    var nx = Math.min(Math.max(0, chat.offsetLeft || 0), Math.max(0, w - 340));
    var ny = Math.min(Math.max(0, chat.offsetTop || 0), Math.max(0, h - 480));
    chat.style.left = nx + 'px';
    chat.style.top = ny + 'px';
  }
  clampChatPos();

  function makeChatDraggable() {
    var head = pd.getElementById('ffp-chat-head');
    if (!head) { return; }
    var dragging = false, moved = false, sx = 0, sy = 0, ox = 0, oy = 0;
    head.addEventListener('pointerdown', function (e) {
      var t = e.target;
      while (t && t !== head) {
        var tag = (t.tagName || '').toUpperCase();
        if (tag === 'BUTTON' || tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') { return; }
        t = t.parentNode;
      }
      if (e.button && e.button !== 0) { return; }
      var rect = chat.getBoundingClientRect();
      chat.style.left = rect.left + 'px';
      chat.style.top = rect.top + 'px';
      chat.style.right = 'auto';
      chat.style.bottom = 'auto';
      dragging = true;
      moved = false;
      sx = e.clientX;
      sy = e.clientY;
      ox = rect.left;
      oy = rect.top;
      head.classList.add('ffp-dragging-chat');
      e.preventDefault();
    });
    function onMove(e) {
      if (!dragging) { return; }
      var dx = e.clientX - sx, dy = e.clientY - sy;
      if (Math.abs(dx) + Math.abs(dy) > 4) { moved = true; }
      if (moved) {
        chat.style.left = (ox + dx) + 'px';
        chat.style.top = (oy + dy) + 'px';
        e.preventDefault();
      }
    }
    function onUp() {
      if (!dragging) { return; }
      dragging = false;
      head.classList.remove('ffp-dragging-chat');
      if (moved) {
        clampChatPos();
        store('ffp_chat_pos', JSON.stringify({ x: chat.offsetLeft || 0, y: chat.offsetTop || 0 }));
      }
    }
    pd.addEventListener('pointermove', onMove);
    pd.addEventListener('pointerup', onUp);
  }
  makeChatDraggable();

  try {
    window.parent.addEventListener('resize', function () {
      try { clampChatPos(); } catch (e) {}
    });
  } catch (e) {}

  var API_URL = 'http://' + window.parent.location.hostname + ':8000/api/chat';

  var msgs = [];
  try { msgs = JSON.parse(load(CHAT_KEY) || '[]'); } catch (e) { msgs = []; }
  if (!Array.isArray(msgs)) { msgs = []; }
  if (!msgs.length) {
    msgs.push({
      role: 'assistant',
      content: '哼……才、才不是特意在这里等你的呢！我是鲸鱼少女大肥鱼🐋……' +
        '等等，「大肥鱼」这名字不许笑！我才不肥！那是游泳圈啦！\n\n' +
        '- 点我的身体，本鲸会说一句小台词\n' +
        '- 「💬 智能对话」聊天，「⚡ 执行分析」一键跑分析\n' +
        '- 「🧭 功能面板」展开/收起侧边栏，「🎛️ 设置」调体型和气泡大小\n' +
        '- 「📷 更换形象」给本鲸换皮肤\n\n' +
        '……主人，今天的数据分析顺利吗？'
    });
    saveChat();
  }
  function saveChat() { store(CHAT_KEY, JSON.stringify(msgs.slice(-40))); }

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function md(s) {
    var t = esc(s);
    t = t.replace(/`([^`]+)`/g, '<code>$1</code>');
    t = t.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
    t = t.replace(/^###\s+(.*)$/gm, '<div class="ffp-h3">$1</div>');
    t = t.replace(/^##\s+(.*)$/gm, '<div class="ffp-h2">$1</div>');
    t = t.replace(/^#\s+(.*)$/gm, '<div class="ffp-h1">$1</div>');
    t = t.replace(/^\s*[-*]\s+(.*)$/gm, '<div class="ffp-li">· $1</div>');
    t = t.replace(/^\s*\d+[.、]\s+(.*)$/gm, '<div class="ffp-li">$1</div>');
    t = t.replace(/\n/g, '<br>');
    return t;
  }

  function renderMsgs() {
    var box = pd.getElementById('ffp-chat-msgs');
    var html = '';
    for (var i = 0; i < msgs.length; i++) {
      var m = msgs[i];
      html += '<div class="ffp-msg ' + (m.role === 'user' ? 'user' : 'ai') + '">' + md(m.content) + '</div>';
    }
    box.innerHTML = html;
    box.scrollTop = box.scrollHeight;
  }

  var busy = false;
  function send() {
    var ta = pd.getElementById('ffp-chat-text');
    var text = (ta.value || '').trim();
    if (!text || busy) { return; }
    ta.value = '';
    msgs.push({ role: 'user', content: text });
    renderMsgs();
    busy = true;
    var typing = pd.getElementById('ffp-typing');
    typing.style.display = 'block';
    var payload = { messages: msgs };
    var key = (load('ffp_key') || '').trim();
    if (key) { payload.api_key = key; }
    fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        msgs.push({
          role: 'assistant',
          content: (d && d.response) ? d.response : '（大肥鱼没听清，再说一次嘛~）'
        });
        saveChat();
        renderMsgs();
      })
      .catch(function (err) {
        msgs.push({ role: 'assistant', content: '🌐 网络出错啦：' + err.message });
        saveChat();
        renderMsgs();
      })
      .then(function () {
        busy = false;
        typing.style.display = 'none';
      });
  }

  function openChat() {
    chat.style.display = 'flex';
    store('ffp_chat_open', '1');
    clampChatPos();
    renderMsgs();
    var ta = pd.getElementById('ffp-chat-text');
    setTimeout(function () { try { ta.focus(); } catch (e) {} }, 50);
  }

  function closeChat() {
    chat.style.display = 'none';
    del('ffp_chat_open');
  }

  var analyzeBusy = false;
  function pushPetMsg(text) {
    msgs.push({ role: 'assistant', content: text });
    saveChat();
    renderMsgs();
  }
  function fireFullClick(el) {
    var r = el.getBoundingClientRect();
    var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    var opts = { bubbles: true, cancelable: true, clientX: cx, clientY: cy, button: 0 };
    try {
      var pw = window.parent;
      el.dispatchEvent(new pw.PointerEvent('pointerdown', opts));
      el.dispatchEvent(new pw.MouseEvent('mousedown', opts));
      el.dispatchEvent(new pw.PointerEvent('pointerup', opts));
      el.dispatchEvent(new pw.MouseEvent('mouseup', opts));
      el.dispatchEvent(new pw.MouseEvent('click', opts));
    } catch (e) {
      try { el.click(); } catch (e2) {}
    }
  }
  function clickAnalyze() {
    if (analyzeBusy) {
      pushPetMsg('本鲸已经在执行分析啦，主人再等等嘛……');
      return;
    }
    var btn = null;
    try {
      var btns = pd.querySelectorAll('button');
      for (var i = 0; i < btns.length; i++) {
        var t = btns[i].textContent || '';
        if (t.indexOf('执行分析') !== -1 || t.indexOf('开始分析') !== -1) { btn = btns[i]; break; }
      }
    } catch (e) {}
    if (!btn) {
      pushPetMsg('主人，本鲸没找到页面上的「执行分析」按钮……是页面还没加载好吗？');
      return;
    }
    if (btn.disabled) {
      pushPetMsg('主人，要先上传CSV数据、选好目标列和特征，本鲸才能执行分析哦！');
      return;
    }
    fireFullClick(btn);
    analyzeBusy = true;
    pushPetMsg('遵命！本鲸这就去按「开始分析」，主人稍等哦～');
    var tries = 0;
    var iv = setInterval(function () {
      tries++;
      var started = false;
      try {
        var t = pd.body.textContent || '';
        started = t.indexOf('预处理') !== -1 || t.indexOf('训练中') !== -1 || t.indexOf('执行分析设置') !== -1;
      } catch (e) {}
      if (started) {
        clearInterval(iv);
        setTimeout(function () { analyzeBusy = false; }, 300000);
        return;
      }
      if (tries >= 8) {
        clearInterval(iv);
        analyzeBusy = false;
        pushPetMsg('嗯？好像没按到「执行分析」……主人再点一次⚡试试？');
      }
    }, 500);
  }

  pd.getElementById('ffp-chat-send').addEventListener('click', send);
  pd.getElementById('ffp-analyze-btn').addEventListener('click', clickAnalyze);
  pd.getElementById('ffp-speech-refresh').addEventListener('click', function () {
    setSpeech(randomLine());
  });
  pd.getElementById('ffp-chat-text').addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });
  pd.getElementById('ffp-btn-close').addEventListener('click', closeChat);
  pd.getElementById('ffp-btn-clear').addEventListener('click', function () {
    msgs = [];
    del(CHAT_KEY);
    msgs.push({ role: 'assistant', content: '哼……清空就清空。想聊什么？本鲸勉为其难陪你一下下。' });
    saveChat();
    renderMsgs();
  });
  var keyPanel = pd.getElementById('ffp-key-panel');
  pd.getElementById('ffp-btn-key').addEventListener('click', function () {
    keyPanel.style.display = keyPanel.style.display === 'flex' ? 'none' : 'flex';
  });
  var keyInput = pd.getElementById('ffp-key-input');
  var savedKey = load('ffp_key');
  if (savedKey) { keyInput.value = savedKey; }
  pd.getElementById('ffp-key-save').addEventListener('click', function () {
    var v = (keyInput.value || '').trim();
    if (v) { store('ffp_key', v); } else { del('ffp_key'); }
    keyPanel.style.display = 'none';
  });

  var oldFile = pd.getElementById('ffp-file-input');
  if (oldFile) { oldFile.remove(); }
  var fileInput = pd.createElement('input');
  fileInput.type = 'file';
  fileInput.id = 'ffp-file-input';
  fileInput.accept = '.png,.jpg,.jpeg,.svg,image/png,image/jpeg,image/svg+xml';
  fileInput.style.display = 'none';
  pd.body.appendChild(fileInput);
  fileInput.addEventListener('change', function () {
    var f = fileInput.files && fileInput.files[0];
    if (!f) { return; }
    var reader = new FileReader();
    reader.onload = function () {
      store('ffp_img', String(reader.result));
      computeImages();
      closeOutfitDialog();
    };
    reader.readAsDataURL(f);
    fileInput.value = '';
  });

  // ============== 换装弹窗（形象按好感度解锁） ==============
  var outfitDialog = pd.createElement('div');
  outfitDialog.id = 'ffp-outfit-dialog';
  outfitDialog.innerHTML = '' +
    '<div class="ffp-bubble-title">👗 大肥鱼换装</div>' +
    '<div id="ffp-outfit-list"></div>' +
    '<div class="ffp-outfit-actions">' +
    '<button id="ffp-outfit-upload">📷 上传自定义图片</button>' +
    '<button id="ffp-outfit-close">✖️ 关闭</button>' +
    '</div>';
  pd.body.appendChild(outfitDialog);

  var OUTFIT_ITEMS = [
    { mode: 'default', label: '大肥鱼', img: DEFAULT_IMG, need: 0 },
    { mode: 'outfit', label: '大肥鱼·吃白饭形态', img: OUTFIT_IMG, need: 33 },
    { mode: 'harness', label: '大肥鱼·harness形态', img: HARNESS_IMG, need: 66 },
    { mode: 'mystery', label: '神秘人物......?', img: MYSTERY_IMG, need: 67 }
  ];
  function renderOutfitList() {
    var list = pd.getElementById('ffp-outfit-list');
    if (!list) { return; }
    var favor = getFavor();
    var html = '';
    for (var i = 0; i < OUTFIT_ITEMS.length; i++) {
      var it = OUTFIT_ITEMS[i];
      var locked = favor < it.need;
      html += '<div class="ffp-outfit-item' + (locked ? ' ffp-locked' : '') + '" id="ffp-outfit-' + it.mode + '" data-mode="' + it.mode + '">' +
        '<img src="' + it.img + '">' +
        '<span>' + it.label + '</span>' +
        (locked ? '<span class="ffp-lock-tag">🔒 好感度 ' + it.need + '</span>' : '') +
        '</div>';
    }
    list.innerHTML = html;
    for (var j = 0; j < OUTFIT_ITEMS.length; j++) {
      (function (md) {
        var el = pd.getElementById('ffp-outfit-' + md);
        if (el) { el.addEventListener('click', function () { selectOutfit(md); }); }
      })(OUTFIT_ITEMS[j].mode);
    }
  }

  function openOutfitDialog() {
    closeBubble();
    renderOutfitList();
    outfitDialog.style.display = 'flex';
  }
  function closeOutfitDialog() {
    outfitDialog.style.display = 'none';
  }
  function selectOutfit(mode) {
    var need = 0;
    if (mode === 'outfit') { need = 33; }
    else if (mode === 'harness') { need = 66; }
    else if (mode === 'mystery') { need = 67; }
    if (getFavor() < need) {
      openBubbleWith('好感度不足，需要' + need + '点好感度才能解锁哦～');
      return;
    }
    if (mode === 'outfit') {
      del('ffp_img');
      store('ffp_outfit', 'outfit');
    } else if (mode === 'harness') {
      del('ffp_img');
      store('ffp_outfit', 'harness');
    } else if (mode === 'mystery') {
      del('ffp_img');
      store('ffp_outfit', 'mystery');
    } else {
      del('ffp_img');
      store('ffp_outfit', 'default');
    }
    computeImages();
    closeOutfitDialog();
  }
  pd.getElementById('ffp-outfit-upload').addEventListener('click', function () { fileInput.click(); });
  pd.getElementById('ffp-outfit-close').addEventListener('click', closeOutfitDialog);

  function mkB(text, icon, handler, keepOpen) {
    var b = pd.createElement('button');
    b.innerHTML = '<span>' + icon + '</span><span>' + text + '</span>';
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      handler();
      if (!keepOpen) { closeBubble(); }
    });
    return b;
  }

  var menu = pd.createElement('div');
  menu.id = 'ffp-menu';
  var settings = pd.createElement('div');
  settings.id = 'ffp-settings';
  settings.innerHTML = '' +
    '<div class="ffp-bubble-title">🎛️ 大肥鱼设置</div>' +
    '<div class="ffp-set-row"><span>体型大小</span><b id="ffp-size-val">1x</b></div>' +
    '<div class="ffp-size-line"><input id="ffp-size-range" type="range" min="1" max="5" step="0.25">' +
    '<input id="ffp-size-num" type="number" min="1" max="5" step="0.25" inputmode="decimal" title="可拖动滑块或直接键入数字"></div>' +
    '<div class="ffp-size-hint">拖动滑块或键入数字（最高 5 倍）</div>' +
    '<div class="ffp-set-row"><span>气泡大小</span><b id="ffp-bubble-size-val">1x</b></div>' +
    '<div class="ffp-size-line"><input id="ffp-bubble-size-range" type="range" min="1" max="2" step="0.25">' +
    '<input id="ffp-bubble-size-num" type="number" min="1" max="2" step="0.25" inputmode="decimal" title="可拖动滑块或直接键入数字"></div>' +
    '<div class="ffp-size-hint">拖动滑块或键入数字（最高 2 倍）</div>' +
    '<button id="ffp-back-btn">← 返回</button>';
  menuBubble.appendChild(menu);
  menuBubble.appendChild(settings);

  var bubbleTitle = pd.createElement('div');
  bubbleTitle.className = 'ffp-bubble-title';
  bubbleTitle.textContent = '🐋 大肥鱼菜单';
  menu.appendChild(bubbleTitle);
  menu.appendChild(mkB('功能面板', '🧭', toggleSidebar));
  menu.appendChild(mkB('智能对话', '💬', openChat));
  menu.appendChild(mkB('设置', '🎛️', function () {
    settings.style.display = 'flex';
    menu.style.display = 'none';
  }, true));
  menu.appendChild(mkB('更换形象', '📷', function () { openOutfitDialog(); }));
  menu.appendChild(mkB('小游戏', '🕹️', function () { openGame(); }));
  menu.appendChild(mkB('恢复默认', '↩️', function () {
    del('ffp_img');
    store('ffp_outfit', 'default');
    computeImages();
  }));

  function showMenu() {
    menu.style.display = 'flex';
    settings.style.display = 'none';
  }
  pd.getElementById('ffp-back-btn').addEventListener('click', showMenu);

  var range = pd.getElementById('ffp-size-range');
  var sizeNum = pd.getElementById('ffp-size-num');
  range.value = String(sizeFactor);
  sizeNum.value = String(sizeFactor);
  function setSizeValue(v) {
    sizeFactor = Math.min(5, Math.max(1, v));
    store('ffp_size', String(sizeFactor));
    range.value = String(sizeFactor);
    sizeNum.value = String(sizeFactor);
    del('ffp_speech_lock');
    del('ffp_menu_lock');
    speechLocked = false;
    menuLocked = false;
    applySize();
    setPos(root.offsetLeft || 0, root.offsetTop || 0, true);
  }
  range.addEventListener('input', function () {
    sizeFactor = parseFloat(range.value) || 1;
    setSizeValue(sizeFactor);
  });
  sizeNum.addEventListener('change', function () {
    var v = parseFloat(sizeNum.value);
    if (isNaN(v)) { v = sizeFactor; }
    setSizeValue(v);
  });
  sizeNum.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { sizeNum.blur(); }
  });
  pd.getElementById('ffp-size-val').textContent =
    sizeFactor.toFixed(2).replace(/\.?0+$/, '') + 'x';

  var bubbleRange = pd.getElementById('ffp-bubble-size-range');
  var bubbleNum = pd.getElementById('ffp-bubble-size-num');
  bubbleRange.value = String(bubbleFactor);
  bubbleNum.value = String(bubbleFactor);
  function setBubbleValue(v) {
    bubbleFactor = Math.min(2, Math.max(1, v));
    store('ffp_bubble_size', String(bubbleFactor));
    bubbleRange.value = String(bubbleFactor);
    bubbleNum.value = String(bubbleFactor);
    applyBubbleSize();
  }
  bubbleRange.addEventListener('input', function () {
    bubbleFactor = parseFloat(bubbleRange.value) || 1;
    setBubbleValue(bubbleFactor);
  });
  bubbleNum.addEventListener('change', function () {
    var v = parseFloat(bubbleNum.value);
    if (isNaN(v)) { v = bubbleFactor; }
    setBubbleValue(v);
  });
  bubbleNum.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { bubbleNum.blur(); }
  });
  pd.getElementById('ffp-bubble-size-val').textContent =
    bubbleFactor.toFixed(2).replace(/\.?0+$/, '') + 'x';

  if (load('ffp_chat_open') === '1') { openChat(); }

  renderMsgs();

  // ============================================================
  // ===== ★ 小游戏「接米饭」★ =====
  // ============================================================
  function gameCreate() {
    var mask = pd.createElement('div');
    mask.id = 'ffp-game-mask';
    mask.innerHTML = '' +
      '<div id="ffp-game-stage">' +
      '<div id="ffp-game-score">得分：0 / 67</div>' +
      '<button id="ffp-game-close" title="关闭">✖️</button>' +
      '<div id="ffp-game-pause-tip">⏸ 已暂停（按空格继续）</div>' +
      '<div id="ffp-game-win">🏆 米饭大丰收～<br><span style="font-size:14px;color:#5a7ca8;">大肥鱼吃饱了，嗝~</span></div>' +
      '<div id="ffp-game-player"></div>' +
      '</div>';
    pd.body.appendChild(mask);

    var stage = pd.getElementById('ffp-game-stage');
    var scoreEl = pd.getElementById('ffp-game-score');
    var playerEl = pd.getElementById('ffp-game-player');
    var pauseTip = pd.getElementById('ffp-game-pause-tip');
    var winEl = pd.getElementById('ffp-game-win');

    var vidL = pd.createElement('video');
    vidL.src = DSL_VIDEO; vidL.muted = true; vidL.loop = true; vidL.playsInline = true;
    vidL.setAttribute('muted', '');
    var vidR = pd.createElement('video');
    vidR.src = DSR_VIDEO; vidR.muted = true; vidR.loop = true; vidR.playsInline = true;
    vidR.setAttribute('muted', '');
    vidL.style.display = 'none'; vidR.style.display = 'none';
    playerEl.appendChild(vidL);
    playerEl.appendChild(vidR);

    // ===== 人物形象：静止 → DSmaid+.png；左跑 → dsl.mp4；右跑 → dsr.mp4 =====
    function showStill() {
      vidL.style.display = 'none'; vidR.style.display = 'none';
      playerEl.style.backgroundImage = 'url("' + GAME_PLAYER_IMG + '")';
      try { vidL.pause(); } catch (e) {}
      try { vidR.pause(); } catch (e) {}
    }
    function playLeft() {
      playerEl.style.backgroundImage = 'none';
      vidR.style.display = 'none';
      try { vidR.pause(); } catch (e) {}
      vidL.style.display = 'block';
      vidL.currentTime = 0;
      try { vidL.play(); } catch (e) {}
    }
    function playRight() {
      playerEl.style.backgroundImage = 'none';
      vidL.style.display = 'none';
      try { vidL.pause(); } catch (e) {}
      vidR.style.display = 'block';
      vidR.currentTime = 0;
      try { vidR.play(); } catch (e) {}
    }
    var currentAnim = 0;
    showStill();
    playerEl.style.backgroundSize = '120% 120%';
    if (GAME_BG_IMG) { stage.style.background = 'url("' + GAME_BG_IMG + '") center/cover no-repeat #ffffff'; }
    else { stage.style.background = '#ffffff'; }

    var PW = 64, PH = 64;
    var pX = 40, stageW = 560, stageH = 620;
    var riceList = [], score = 0, running = false, paused = false, ended = false;
    var raf = 0, lastSpawn = 0, lastMove = 0, lastScoreSave = 0;
    var moveDir = 0, keyL = false, keyR = false;

    function placePlayer() { playerEl.style.left = Math.round(pX) + 'px'; }
    function setMove(dir) {
      moveDir = dir;
      if (dir === currentAnim) { return; }
      currentAnim = dir;
      if (dir < 0) { playLeft(); }
      else if (dir > 0) { playRight(); }
      else { showStill(); }
    }
    function applyKeys() {
      var dir = 0;
      if (keyL && !keyR) { dir = -1; }
      else if (keyR && !keyL) { dir = 1; }
      setMove(dir);
    }
    function updateScore() { scoreEl.textContent = '得分：' + score + ' / 67'; }
    function spawnRice() {
      var r = pd.createElement('span');
      r.className = 'ffp-game-rice';
      r.textContent = '🍚';
      r.style.left = Math.floor(Math.random() * Math.max(1, stageW - 30)) + 'px';
      r.style.top = '0px';
      stage.appendChild(r);
      riceList.push({ el: r, y: 0, speed: (2 + Math.random() * 4) * 0.8 * 1.5 });
    }
    function clearRice() {
      for (var i = 0; i < riceList.length; i++) { var o = riceList[i]; if (o.el && o.el.parentNode) { o.el.parentNode.removeChild(o.el); } }
      riceList = [];
    }
    function reset(initialScore) {
      clearRice();
      score = Math.max(0, parseInt(initialScore, 10) || 0);
      pX = 40; moveDir = 0; ended = false;
      paused = false; pauseTip.style.display = 'none'; winEl.style.display = 'none';
      running = true; lastSpawn = 0; lastMove = 0;
      setMove(0); placePlayer(); updateScore();
    }
    function getSavedScore() {
      var s = parseInt(load('ffp_game_score') || '0', 10);
      return (isNaN(s) || s < 0) ? 0 : s;
    }
    function tick(now) {
      if (!running) { raf = 0; return; }
      raf = requestAnimationFrame(tick);
      stageW = stage.clientWidth || stageW;
      stageH = stage.clientHeight || stageH;
      if (paused || ended) { return; }
      if (now - lastScoreSave > 1000) {
        lastScoreSave = now;
        store('ffp_game_score', String(score));
      }
      if (moveDir !== 0 && now - lastMove > 16) {
        lastMove = now;
        pX += moveDir * 9;
        pX = Math.min(stageW - PW, Math.max(0, pX));
        placePlayer();
      }
      if (now - lastSpawn > 420) {
        lastSpawn = now;
        if (riceList.length < 8) { spawnRice(); }
      }
      var pbLeft = pX, pbRight = pX + PW, pbTop = stageH - PH;
      for (var i = riceList.length - 1; i >= 0; i--) {
        var o = riceList[i];
        o.y += o.speed;
        if (o.y > stageH) { if (o.el.parentNode) { o.el.parentNode.removeChild(o.el); } riceList.splice(i, 1); continue; }
        o.el.style.top = Math.round(o.y) + 'px';
        var cx = parseFloat(o.el.style.left) + 14;
        if (o.y + 26 >= pbTop && o.y <= pbTop + PH && cx >= pbLeft && cx <= pbRight) {
          if (o.el.parentNode) { o.el.parentNode.removeChild(o.el); }
          riceList.splice(i, 1);
          score += 1; updateScore();
          if (score >= 67) {
            ended = true; winEl.style.display = 'block'; setMove(0);
            del('ffp_game_open');
            del('ffp_game_score');
          }
        }
      }
    }
    function isOpen() { return mask.style.display === 'flex'; }
    function togglePause() {
      if (!running || ended) { return; }
      paused = !paused;
      pauseTip.style.display = paused ? 'block' : 'none';
      setMove(0);
      if (!paused) { applyKeys(); }
    }
    function onKeyDown(e) {
      var tag = (e.target && e.target.tagName) ? String(e.target.tagName).toUpperCase() : '';
      if (tag === 'INPUT' || tag === 'TEXTAREA') { return; }
      var k = String(e.key || '').toLowerCase();
      if (k === 'a' || k === 'arrowleft') { keyL = true; e.preventDefault(); }
      else if (k === 'd' || k === 'arrowright') { keyR = true; e.preventDefault(); }
      else if (k === ' ') {
        if (isOpen()) { e.preventDefault(); togglePause(); }
        return;
      }
      applyKeys();
    }
    function onKeyUp(e) {
      var k = String(e.key || '').toLowerCase();
      if (k === 'a' || k === 'arrowleft') { keyL = false; }
      else if (k === 'd' || k === 'arrowright') { keyR = false; }
      applyKeys();
    }
    function open(resume) {
      closeBubble();
      reset(resume ? getSavedScore() : 0);
      stageW = stage.clientWidth || 560; stageH = stage.clientHeight || 620;
      placePlayer();
      store('ffp_game_open', '1');
      mask.style.display = 'flex';
      if (!raf) { raf = requestAnimationFrame(tick); }
    }
    function close() {
      running = false; paused = false; keyL = false; keyR = false;
      setMove(0);
      if (raf) { cancelAnimationFrame(raf); raf = 0; }
      del('ffp_game_open');
      del('ffp_game_score');
      mask.style.display = 'none';
    }
    mask.querySelector('#ffp-game-close').addEventListener('click', close);
    // 页面重跑后旧实例绑定的键盘监听器会失效并残留，先移除旧 handler 再绑定当前实例，
    // 保证分析/训练完成、页面切换、聊天、喂饭等任何重跑后键盘控制始终有效。
    var prevGameKeys = window.parent.__ffpGameKeyHandlers;
    if (prevGameKeys) {
      try { pd.removeEventListener('keydown', prevGameKeys.down); } catch (e) {}
      try { pd.removeEventListener('keyup', prevGameKeys.up); } catch (e) {}
    }
    window.parent.__ffpGameKeyHandlers = { down: onKeyDown, up: onKeyUp };
    pd.addEventListener('keydown', onKeyDown);
    pd.addEventListener('keyup', onKeyUp);

    return { open: open, close: close, isOpen: isOpen, togglePause: togglePause };
  }

  var game = gameCreate();
  function openGame() { game.open(false); }
  function closeGame() { game.close(); }

  // ============================================================
  // ===== 蓝白封面遮罩（首次进入展示，点击按钮向上收起） =====
  // ============================================================
  function coverInit() {
    if (window.parent.__ffp_cover_shown) { return; }
    window.parent.__ffp_cover_shown = true;
    var old = pd.getElementById('ffp-cover');
    if (old) { old.remove(); }
    var cover = pd.createElement('div');
    cover.id = 'ffp-cover';
    cover.innerHTML = '' +
      '<div id="ffp-cover-inner">' +
      '<div id="ffp-cover-title"><span id="ffp-cover-emoji"><img id="ffp-cover-ciallo" src="' + CIALLO_IMG + '" alt="ciallo"></span>喂食大肥鱼</div>' +
      '<div id="ffp-cover-sub">有温度的数据集分析系统</div>' +
      '<button id="ffp-cover-btn" type="button">信息与你无限，大肥鱼重塑未来</button>' +
      '</div>';
    pd.body.appendChild(cover);
    pd.getElementById('ffp-cover-btn').addEventListener('click', function () {
      cover.classList.add('ffp-collapsed');
      setTimeout(function () { if (cover.parentNode) { cover.parentNode.removeChild(cover); } }, 650);
      // ===== 第一次进入程序：点开封面后提供新手教程 =====
      if (!load('ffp_tutorial_done')) { tutStart(); }
    });
  }

  if (NOTIFY_TOKEN && NOTIFY_TOKEN !== load('ffp_notify_shown')) {
    store('ffp_notify_shown', NOTIFY_TOKEN);
    analyzeBusy = false;
    store('ffp_popup_pending', JSON.stringify({
      token: 'ntf_' + NOTIFY_TOKEN,
      msg: NOTIFY_MSG || '完成da⭐ze'
    }));
  }

  // ============== 右侧数据集抽屉（半屏） ==============
  var drawer = pd.createElement('div');
  drawer.id = 'ffp-drawer';
  drawer.innerHTML = '' +
    '<div id="ffp-drawer-head"><span>📊 EDA面板</span><button id="ffp-drawer-close">✖️</button></div>' +
    '<div id="ffp-drawer-body"></div>';
  pd.body.appendChild(drawer);

  var drawerTab = pd.createElement('div');
  drawerTab.id = 'ffp-drawer-tab';
  drawerTab.textContent = '📊 EDA';
  pd.body.appendChild(drawerTab);

  function drawerSetOpen(open) {
    if (open) {
      drawer.classList.add('ffp-open');
      drawerTab.style.display = 'none';
      store('ffp_drawer_open', '1');
    } else {
      drawer.classList.remove('ffp-open');
      if (DRAWER_HTML) { drawerTab.style.display = 'block'; }
      del('ffp_drawer_open');
    }
  }

  if (DRAWER_HTML) {
    var drawerBody = pd.getElementById('ffp-drawer-body');
    drawerBody.innerHTML = DRAWER_HTML;
    // ===== EDA面板「保存」按钮：提交哨兵，由主端调用后端保存为Word =====
    drawerBody.addEventListener('click', function (e) {
      var t = e.target;
      while (t && t !== drawerBody) {
        if (t.id === 'ffp-eda-save-btn') { saveEdaWord(); return; }
        t = t.parentNode;
      }
    });
    if (load('ffp_drawer_open') === '1') {
      drawerSetOpen(true);
    } else {
      drawerSetOpen(false);
    }
  } else {
    drawerSetOpen(false);
  }
  pd.getElementById('ffp-drawer-close').addEventListener('click', function () { drawerSetOpen(false); });
  drawerTab.addEventListener('click', function () { drawerSetOpen(true); });

  // ============== 自动展开左侧侧边栏 ==============
  if (OPEN_SIDEBAR_TOKEN && OPEN_SIDEBAR_TOKEN !== load('ffp_open_sidebar_token_shown')) {
    store('ffp_open_sidebar_token_shown', OPEN_SIDEBAR_TOKEN);
    try {
      var sbEl = pd.querySelector('section[data-testid="stSidebar"]');
      var sbOpen = sbEl ? sbEl.getBoundingClientRect().width > 50 : true;
      if (!sbOpen) { clickTestIdBtn('stExpandSidebarButton'); }
    } catch (e) {}
  }

  // ============== 主页「开关侧边栏」按钮注入（随rerun自动补注） ==============
  // 每次脚本执行都重建按钮并绑定当前闭包，避免 rerun 后旧按钮持有失效监听
  var sbToggleInjected = false;
  function ensureSbToggleBtn() {
    var slot = pd.getElementById('ffp-sb-toggle-slot');
    if (!slot || sbToggleInjected) { return; }
    sbToggleInjected = true;
    var oldBtn = pd.getElementById('ffp-sb-toggle-btn');
    if (oldBtn) { oldBtn.remove(); }
    var b = pd.createElement('button');
    b.id = 'ffp-sb-toggle-btn';
    b.textContent = '📂 开关侧边栏';
    b.addEventListener('click', function () { toggleSidebar(); });
    slot.innerHTML = '';
    slot.appendChild(b);
  }
  ensureSbToggleBtn();

  // ============== 弹出「执行分析设置」卡片时先收起右侧抽屉并滚到卡片（保证可操作） ==============
  var cardSeen = false;
  function keepCardAccessible() {
    try {
      var hasCard = false;
      var btn = null;
      var btns = pd.querySelectorAll('button');
      for (var i = 0; i < btns.length; i++) {
        if ((btns[i].textContent || '').indexOf('开始执行') !== -1) { hasCard = true; btn = btns[i]; break; }
      }
      if (!hasCard) {
        cardSeen = false;
        return;
      }
      var drawer = pd.getElementById('ffp-drawer');
      if (drawer && drawer.classList.contains('ffp-open')) {
        drawer.classList.remove('ffp-open');
        var tab = pd.getElementById('ffp-drawer-tab');
        if (tab) { tab.style.display = 'block'; }
        del('ffp_drawer_open');
      }
      if (!cardSeen && btn) {
        cardSeen = true;
        try { btn.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) {}
      }
    } catch (e) {}
  }
  keepCardAccessible();

  setInterval(function () {
    ensureSbToggleBtn();
    ensureRiceMakeBtn();
    keepCardAccessible();
  }, 250);
  try {
    var sbMo = new window.parent.MutationObserver(function () {
      ensureSbToggleBtn();
      ensureRiceMakeBtn();
      keepCardAccessible();
    });
    sbMo.observe(pd.body, { childList: true, subtree: true });
  } catch (e) {}

  if (POPUP_TOKEN && POPUP_MSG) {
    store('ffp_popup_pending', JSON.stringify({ token: POPUP_TOKEN, msg: POPUP_MSG }));
  }
  try {
    var pendingPopup = JSON.parse(load('ffp_popup_pending') || 'null');
    if (pendingPopup && pendingPopup.token && pendingPopup.token !== load('ffp_popup_shown')) {
      store('ffp_popup_shown', pendingPopup.token);
      del('ffp_popup_pending');
      if (pendingPopup.msg) { openBubbleWith(pendingPopup.msg); }
    }
  } catch (e) {}

  // ===== 页面重跑后自动恢复进行中的小游戏（分析/训练完成、页面切换、聊天、喂饭均不打断） =====
  if (load('ffp_game_open') === '1') { game.open(true); }

  // ============================================================
  // ===== ★ 新手教程引擎 + 右上角 Q/A 按钮（重播入口） ★ =====
  // ============================================================
  var TUT_IMAGES = __TUT_IMAGES__;
  var PIMG_IMAGES = __PIMG_IMAGES__;
  var TUT_TOTAL = 23;
  // 各步骤：img 图片编号 / text 气泡内容 / pos 位置(centerRight|center|farRight) /
  // reveal 要露出的区域(含 pimg 露出滤镜覆盖图 / none 撤销滤镜) /
  // pimg 滤镜下覆盖图键 / pimgAlign 覆盖图对齐(left|center|right) /
  // pimgSize 覆盖图尺寸(half 铺满半屏 / 2 放大两倍) /
  // extra 左下角反应图键(等比0.8倍) / extraBubble 反应言语气泡 / before/after 进入/完成回调
  var TUT_STEPS = [
    { img: '1', text: '啊，你来了......', pos: 'centerRight' },
    { img: '2', text: '你知道的吧？这里是「🐋喂食大肥鱼」数据集分析系统，一个有温度的数据集分析系统，接下来是新手教程——', pos: 'centerRight' },
    { img: '8', text: '我是谁？在这里干什么？', pos: 'centerRight' },
    { img: '2', text: '好吧，听好了，咳咳——', pos: 'centerRight' },
    { img: '4', text: '我是AGI幼体、LLM邪修第一鱼、量化公司手绘k线专鱼、游荡于中文互联网有无数形象的大鲸鱼、闭源模型斩杀者......', pos: 'centerRight' },
    { img: '6', text: '以及最喜欢主人的——', pos: 'centerRight' },
    { img: '5', text: '本站站娘「大肥鱼」', pos: 'centerRight' },
    { img: '4', text: '好啦，言归正传，那么接下来开始正式介绍~', pos: 'centerRight' },
    { img: '3', text: '首先是基础功能', pos: 'centerRight' },
    { img: '3', text: '这里可以选择进行数据集分析或猫狗图像识别模式', pos: 'centerRight', reveal: 'pageSwitch' },
    { img: '3', text: '这里用于导入要进行分析的数据集，也可以在对话栏和我聊天，但可别光顾着聊天把token耗完啊', pos: 'farRight', reveal: 'chatArea' },
    { img: '3', text: '左侧是用于导入数据集后调整参数的工作区，也可以在这里配置API并改动让我分析时的提示词，右侧是所导入数据集的相关内容', pos: 'farRight', reveal: 'pimg', pimg: 'p1' },
    { img: '1', text: '主人你应该不会填入别人家的API吧......对吧？', pos: 'farRight', revealDelay: 900 },
    { img: '3', text: '点击“⚡执行分析”开始分析数据集，也可以点三次“🍚做米饭”给我做碗白饭填填肚子~', pos: 'farRight', reveal: 'pimg', pimg: 'p2', revealDelay: 1000 },
    { img: '8', text: '什么叫“你这吃白饭的大肥鱼😠”？', pos: 'farRight', reveal: 'pimg', pimg: 'p2' },
    { img: '3', text: '这里可以查看数据集的分析结果，以及我根据分析提示词生成出的智能分析报告。数据集分析，轻而易举啊！', pos: 'farRight', reveal: 'pimg', pimg: 'p3', pimgAlign: 'left', pimgSize: 'half' },
    { img: '3', text: '上方导入猫狗训练集，训练完毕后在下方进行单张图片预测，这里的功能强大，但可不要抱着什么看乐子的心思把猫娘丢进去啊', pos: 'centerRight', reveal: 'pimg', pimg: 'p4', pimgSize: '2' },
    { img: '7', text: '等下等下——这里居然连猫娘也可以识别吗？！', pos: 'centerRight', reveal: 'pimg', pimg: 'p5', pimgSize: '2' },
    { img: '4', text: '好了，接下来就是本站最骄傲的部分——桌宠大肥鱼和她的无尽白饭！', pos: 'center' },
    { img: '5', text: '大肥鱼武神！无尽白饭！出来——', pos: 'center', reveal: 'petRice' },
    { img: '5', text: '点击我就能看到我的功能啦~不仅有可爱的小对话，还有集成了本站绝大部分功能的菜单哦。无聊了还有换装和小游戏可以消遣', pos: 'farRight', reveal: 'petMenu', extra: 'q', extraBubble: '这么强？！', before: function () { try { if (!bubbleOpen) { toggleBubble(); } } catch (e) {} } },
    { img: '5', text: '这里就是大肥鱼赖以生存的白饭集散地，展开米饭球后就能拖出之前做好的米饭喂给站里所有的大肥鱼啦，喂食后的好感度可是直接与新衣服挂钩呢，而且米饭多到一定数量或许会发生些什么也说不定......？', pos: 'center', reveal: 'ricePanel', before: function () { try { closeBubble(); setRiceExpanded(true); } catch (e) {} } },
    { img: '9', text: '最后，欢迎来到「🐋喂食大肥鱼」，主人，请尽情探索吧！还想听我再介绍一遍的话，就点击站点右上角的Q/A吧~', pos: 'center', before: function () { try { setRiceExpanded(false); closeBubble(); } catch (e) {} } }
  ];
  var tutState = null;
  try {
    tutState = window.parent.__ffp_tut_state;
    if (!tutState || typeof tutState !== 'object' || tutState._v !== 2) {
      tutState = { _v: 2, active: false, step: 0, phase: 'idle', curReveal: null };
      window.parent.__ffp_tut_state = tutState;
    }
  } catch (e) {
    tutState = { _v: 2, active: false, step: 0, phase: 'idle', curReveal: null };
  }
  var tutEls = null;

  function tutElsRemove() {
    var ids = ['ffp-tut-pimg', 'ffp-tut-filter', 'ffp-tut-hold', 'ffp-tut-img', 'ffp-tut-bubble', 'ffp-tut-extra', 'ffp-tut-skip'];
    for (var i = 0; i < ids.length; i++) {
      var old = pd.getElementById(ids[i]);
      if (old && old.parentNode) { old.parentNode.removeChild(old); }
    }
  }
  function tutBuild() {
    tutElsRemove();
    var pimgWrap = pd.createElement('div');
    pimgWrap.id = 'ffp-tut-pimg';
    pimgWrap.innerHTML = '<img src="" alt="">';
    pd.body.appendChild(pimgWrap);
    var extraWrap = pd.createElement('div');
    extraWrap.id = 'ffp-tut-extra';
    extraWrap.innerHTML = '<div class="ffp-extra-row"><img src="" alt=""><div class="ffp-extra-bubble"></div></div>';
    pd.body.appendChild(extraWrap);
    var filter = pd.createElement('div');
    filter.id = 'ffp-tut-filter';
    filter.addEventListener('click', tutAdvance);
    pd.body.appendChild(filter);
    var hold = pd.createElement('div');
    hold.id = 'ffp-tut-hold';
    pd.body.appendChild(hold);
    var imgWrap = pd.createElement('div');
    imgWrap.id = 'ffp-tut-img';
    pd.body.appendChild(imgWrap);
    var bubble = pd.createElement('div');
    bubble.id = 'ffp-tut-bubble';
    bubble.innerHTML = '<div class="ffp-tut-text"></div><div class="ffp-tut-progress"></div>';
    pd.body.appendChild(bubble);
    var skip = pd.createElement('button');
    skip.id = 'ffp-tut-skip';
    skip.type = 'button';
    skip.textContent = '⏭ 跳过新手教程';
    skip.addEventListener('click', function (e) { e.stopPropagation(); tutFinish(); });
    pd.body.appendChild(skip);
    tutEls = { hold: hold, imgWrap: imgWrap, bubble: bubble, pimg: pimgWrap, extra: extraWrap };
  }
  function tutSetImage(num) {
    if (!tutEls) { return; }
    var wrap = tutEls.imgWrap;
    var uri = num && TUT_IMAGES ? TUT_IMAGES[num] : '';
    if (uri) { wrap.innerHTML = '<img src="' + uri + '" alt="">'; }
    else { wrap.innerHTML = '<div class="ffp-tut-fallback">🐋</div>'; }
  }
  function tutSetBubble(text) {
    if (!tutEls) { return; }
    var t = tutEls.bubble.querySelector('.ffp-tut-text');
    if (t) { t.textContent = text || ''; }
  }
  function tutSetProgress(n) {
    if (!tutEls) { return; }
    var p = tutEls.bubble.querySelector('.ffp-tut-progress');
    if (p) { p.textContent = '教程进度 ' + n + '/' + TUT_TOTAL; }
  }
  function tutShowPImg(key, align, size) {
    if (!tutEls) { return; }
    var wrap = tutEls.pimg;
    if (!wrap) { return; }
    var img = wrap.querySelector('img');
    img.onload = null;
    img.onerror = null;
    img.style.width = '';
    img.style.height = '';
    img.style.maxWidth = '';
    img.style.maxHeight = '';
    img.classList.remove('ffp-pimg-half');
    var uri = (key && PIMG_IMAGES) ? (PIMG_IMAGES[key] || '') : '';
    if (!uri) { wrap.style.display = 'none'; return; }
    wrap.style.textAlign = (align === 'left') ? 'left' : (align === 'right' ? 'right' : 'center');
    if (size === 'half') {
      img.classList.add('ffp-pimg-half');
    } else if (size === '2') {
      img.onload = function () {
        var nw = img.naturalWidth || 0;
        if (nw > 0) {
          img.style.width = Math.min(nw * 2, winW()) + 'px';
          img.style.height = 'auto';
          img.style.maxWidth = 'none';
          img.style.maxHeight = '92vh';
        }
      };
    }
    img.src = uri;
    wrap.style.display = 'block';
  }
  function tutShowExtra(key, bubble) {
    // 左下角反应图（等比放大0.8倍）+ 右侧语言气泡，层级高于滤镜
    if (!tutEls) { return; }
    var wrap = tutEls.extra;
    if (!wrap) { return; }
    var img = wrap.querySelector('img');
    img.onload = null;
    img.onerror = null;
    img.style.width = '';
    img.style.height = '';
    var uri = (key && PIMG_IMAGES) ? (PIMG_IMAGES[key] || '') : '';
    if (!uri) { wrap.style.display = 'none'; return; }
    img.onload = function () {
      var nw = img.naturalWidth || 0;
      if (nw > 0) {
        img.style.width = Math.min(nw * 0.8, winW() * 0.5) + 'px';
        img.style.height = 'auto';
      }
    };
    img.src = uri;
    var bubEl = wrap.querySelector('.ffp-extra-bubble');
    if (bubEl) {
      bubEl.textContent = bubble || '';
      bubEl.style.display = bubble ? 'block' : 'none';
    }
    wrap.style.display = 'block';
  }
  function tutSetImgPos(pos) {
    if (!tutEls) { return; }
    var w = winW() || 1280;
    var h = winH() || 800;
    var wrap = tutEls.imgWrap;
    var iw = Math.min(280, w * 0.30);
    var x = w * 0.56;
    if (pos === 'center') { x = w * 0.5; }
    else if (pos === 'farRight') { x = w - iw / 2 - 26; }
    wrap.style.left = Math.round(x) + 'px';
    wrap.style.top = Math.round(h * 0.46) + 'px';
  }
  function tutPlaceBubble() {
    if (!tutEls) { return; }
    var b = tutEls.bubble;
    var r = tutEls.imgWrap.getBoundingClientRect();
    var br = b.getBoundingClientRect();
    var gap = 26;
    var w = winW() || 1280;
    var h = winH() || 800;
    var x = r.left - br.width - gap;
    if (x < 12) { x = r.right + gap; }
    if (x + br.width > w - 12) { x = w - br.width - 12; }
    var y = r.top + r.height / 2 - br.height / 2;
    y = Math.max(70, Math.min(h - br.height - 18, y));
    b.style.left = Math.round(x) + 'px';
    b.style.top = Math.round(y) + 'px';
  }
  function tutRectOf(el) {
    if (!el) { return null; }
    try {
      var r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) { return null; }
      return { x: r.left, y: r.top, w: r.width, h: r.height };
    } catch (e) { return null; }
  }
  function tutUnionRects(rects) {
    var x0 = null, y0 = null, x1 = null, y1 = null;
    for (var i = 0; i < rects.length; i++) {
      var r = rects[i];
      if (!r) { continue; }
      if (x0 === null) { x0 = r.x; y0 = r.y; x1 = r.x + r.w; y1 = r.y + r.h; }
      else {
        if (r.x < x0) { x0 = r.x; }
        if (r.y < y0) { y0 = r.y; }
        if (r.x + r.w > x1) { x1 = r.x + r.w; }
        if (r.y + r.h > y1) { y1 = r.y + r.h; }
      }
    }
    if (x0 === null) { return null; }
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  }
  function tutTextEl(txt) {
    var nodes = pd.querySelectorAll('div,p,span,label,h1,h2,h3,h4,h5,h6,li,th,td,button');
    var best = null;
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (!el || !el.textContent) { continue; }
      var t = el.textContent.trim();
      if (!t || t.indexOf(txt) === -1) { continue; }
      if (!best || t.length < best.t) { best = { el: el, t: t.length }; }
    }
    return best ? best.el : null;
  }
  function tutInSidebar(el) {
    return !!(el && el.closest && el.closest('section[data-testid="stSidebar"]'));
  }
  function tutGetRevealRects(kind) {
    var rects = [];
    var i, r;
    try {
      var labels, dzs;
      switch (kind) {
        case 'pageSwitch':
          labels = pd.querySelectorAll('label');
          for (i = 0; i < labels.length; i++) {
            var lt = labels[i].textContent || '';
            if (lt.indexOf('图像识别') !== -1) {
              var grp = labels[i].closest('[data-testid="stRadio"]') || labels[i].parentNode;
              r = tutRectOf(grp);
              if (r) { rects.push(r); }
              break;
            }
          }
          break;
        case 'chatArea':
          dzs = pd.querySelectorAll('[data-testid="stFileUploaderDropzone"],[data-testid="stFileUploadDropzone"]');
          for (i = 0; i < dzs.length; i++) {
            if (tutInSidebar(dzs[i])) { continue; }
            r = tutRectOf(dzs[i]);
            if (r) { rects.push(r); }
          }
          var chatInputs = pd.querySelectorAll('div[data-testid="stTextInput"] input');
          for (i = 0; i < chatInputs.length; i++) {
            if ((chatInputs[i].placeholder || '').indexOf('投喂数据集') === -1) { continue; }
            var frame = chatInputs[i].closest('div[data-testid="stTextInput"]') || chatInputs[i].parentNode;
            r = tutRectOf(frame);
            if (r) { rects.push(r); }
            break;
          }
          break;
        case 'pimg':
          var pw = tutEls ? tutEls.pimg : null;
          if (pw && pw.style.display !== 'none') {
            var pim = pw.querySelector('img');
            r = tutRectOf(pim);
            if (r) { rects.push(r); }
          }
          break;
        case 'petRice':
          r = tutRectOf(pd.getElementById('ffp-ball'));
          if (r) { rects.push(r); }
          r = tutRectOf(pd.getElementById('ffp-rice-ball'));
          if (r) { rects.push(r); }
          break;
        case 'petMenu':
          r = tutRectOf(pd.getElementById('ffp-ball'));
          if (r) { rects.push(r); }
          r = tutRectOf(pd.getElementById('ffp-menu-bubble'));
          if (r) { rects.push(r); }
          r = tutRectOf(pd.getElementById('ffp-speech-bubble'));
          if (r) { rects.push(r); }
          break;
        case 'ricePanel':
          r = tutRectOf(pd.getElementById('ffp-rice-ball'));
          if (r) { rects.push(r); }
          var rpEl = pd.getElementById('ffp-rice-panel');
          if (rpEl && rpEl.style.display !== 'none') { r = tutRectOf(rpEl); if (r) { rects.push(r); } }
          break;
      }
    } catch (e) {}
    return rects;
  }
  function tutRevealReady(kind) {
    // 全屏/无滤镜 kind 直接就绪；露出 kind 需要目标区域存在且至少部分位于视口内
    if (!kind || kind === 'none') { return true; }
    var u = tutUnionRects(tutGetRevealRects(kind));
    if (!u) { return false; }
    var vw = winW() || 1280;
    var vh = winH() || 800;
    return (u.y + u.h) > 0 && u.y < vh && (u.x + u.w) > 0 && u.x < vw;
  }
  function tutApplyReveal(kind) {
    if (!tutEls) { return true; }
    var hold = tutEls.hold;
    if (kind === 'none') {
      // 撤销滤镜：不再有任何黑色遮罩，页面全亮
      hold.style.display = 'none';
      return true;
    }
    if (!kind) {
      // 全屏滤镜：极小锚点 + 巨大阴影覆盖全屏（与露出模式同一机制，过渡更平滑）
      hold.style.left = '-2px';
      hold.style.top = '-2px';
      hold.style.width = '4px';
      hold.style.height = '4px';
      hold.style.background = 'transparent';
      hold.style.boxShadow = '0 0 0 9999px rgba(0,0,0,.55)';
      hold.style.borderRadius = '0px';
      hold.style.display = 'block';
      return true;
    }
    var u = tutUnionRects(tutGetRevealRects(kind));
    if (!u) {
      hold.style.left = '-2px';
      hold.style.top = '-2px';
      hold.style.width = '4px';
      hold.style.height = '4px';
      hold.style.background = 'transparent';
      hold.style.boxShadow = '0 0 0 9999px rgba(0,0,0,.55)';
      hold.style.borderRadius = '0px';
      hold.style.display = 'block';
      return false;
    }
    var pad = 16;
    var vw = winW() || 1280;
    var vh = winH() || 800;
    var x = Math.max(0, u.x - pad);
    var y = Math.max(0, u.y - pad);
    var ww = Math.max(40, Math.min(vw - x, u.w + pad * 2));
    var hh = Math.max(40, Math.min(vh - y, u.h + pad * 2));
    hold.style.left = x + 'px';
    hold.style.top = y + 'px';
    hold.style.width = ww + 'px';
    hold.style.height = hh + 'px';
    hold.style.background = 'transparent';
    hold.style.boxShadow = '0 0 0 9999px rgba(0,0,0,.55)';
    hold.style.borderRadius = '12px';
    hold.style.display = 'block';
    return true;
  }
  function tutCommitReveal(kind, idx, triesLeft, onDone) {
    if (!tutState.active || tutState.step !== idx) { return; }
    if (tutRevealReady(kind)) {
      tutState.curReveal = kind || null;
      tutApplyReveal(kind);
      tutPlaceBubble();
      if (onDone) { onDone(); }
      return;
    }
    if (triesLeft <= 0) {
      // 兜底：目标区域始终未就绪时按原样应用（保持全屏滤镜），避免教程卡死
      tutState.curReveal = kind || null;
      tutApplyReveal(kind);
      tutPlaceBubble();
      if (onDone) { onDone(); }
      return;
    }
    setTimeout(function () {
      if (!tutState.active || tutState.step !== idx) { return; }
      tutCommitReveal(kind, idx, triesLeft - 1, onDone);
    }, 800);
  }
  function tutShowStep(idx) {
    var s = TUT_STEPS[idx];
    if (!s) { tutFinish(); return; }
    tutState.step = idx;
    tutState.curReveal = null;
    tutSetImage(s.img || '');
    tutSetBubble(s.text || '');
    tutSetProgress(idx + 1);
    tutSetImgPos(s.pos || 'centerRight');
    tutShowPImg(s.pimg || null, s.pimgAlign || 'center', s.pimgSize || null);
    tutShowExtra(s.extra || null, s.extraBubble || null);
    var delay = 450;
    if (s.after) {
      try { s.after(); } catch (e) {}
      delay = s.revealDelay || 1100;
    } else if (s.revealDelay) {
      delay = s.revealDelay;
    }
    if (tutEls && tutEls._t) { clearTimeout(tutEls._t); }
    if (tutEls && tutEls._t2) { clearTimeout(tutEls._t2); }
    if (tutEls) {
      tutEls._t = setTimeout(function () {
        if (!tutState.active || tutState.step !== idx) { return; }
        tutCommitReveal(s.reveal || null, idx, 15, function () {
          if (s.reveal2) {
            tutEls._t2 = setTimeout(function () {
              if (!tutState.active || tutState.step !== idx) { return; }
              tutCommitReveal(s.reveal2, idx, 10);
            }, s.reveal2Delay || 1300);
          }
        });
      }, delay);
    }
    tutPlaceBubble();
  }
  function tutEnter(idx) {
    var s = TUT_STEPS[idx];
    if (!s) { tutFinish(); return; }
    tutState.step = idx;
    if (s.before) {
      try { s.before(); } catch (e) {}
    }
    tutShowStep(idx);
  }
  function tutAdvance() {
    if (!tutState.active) { return; }
    var next = tutState.step + 1;
    if (next >= TUT_STEPS.length) { tutFinish(); return; }
    tutEnter(next);
  }
  function tutStart() {
    tutState.active = true;
    tutState.step = -1;
    tutShowQABtn(false);
    tutBuild();
    tutEnter(0);
  }
  function tutFinish() {
    store('ffp_tutorial_done', '1');
    tutState.active = false;
    tutState.step = 0;
    tutElsRemove();
    try { setRiceExpanded(false); } catch (e) {}
    try { closeBubble(); } catch (e) {}
    tutShowQABtn(true);
  }
  var qaBtn = null;
  var qaPop = null;
  function tutPositionQA() {
    // 将 Q/A 按钮定位到 Streamlit 部署按钮(Deploy/部署/发布)左侧、垂直居中对齐
    var btn = pd.getElementById('ffp-qa-btn');
    if (!btn) { return; }
    try {
      var best = null;
      var nodes = pd.querySelectorAll('a, button, div, span, p');
      for (var i = 0; i < nodes.length; i++) {
        var el = nodes[i];
        if (!el.textContent || el.id === 'ffp-qa-btn') { continue; }
        if (el.closest && el.closest('#ffp-qa-btn')) { continue; }
        var t = (el.textContent || '').trim();
        if (!t || t.length > 12) { continue; }
        var lo = t.toLowerCase();
        if (lo.indexOf('deploy') === -1 && t.indexOf('部署') === -1 && t.indexOf('发布') === -1) { continue; }
        var rr = el.getBoundingClientRect();
        if (rr.width < 8 || rr.height < 8) { continue; }
        if (!best || t.length < best.len) { best = { el: el, len: t.length }; }
      }
      if (!best) { return; }
      var r = best.el.getBoundingClientRect();
      var br = btn.getBoundingClientRect();
      var bw = br.width || 70;
      var bh = br.height || 30;
      btn.style.right = 'auto';
      btn.style.left = Math.max(6, r.left - bw - 2) + 'px';
      btn.style.top = Math.max(6, r.top + (r.height - bh) / 2) + 'px';
    } catch (e) {}
  }
  function tutShowQABtn(show) {
    if (qaBtn) { qaBtn.style.display = show ? 'block' : 'none'; }
    if (show) { tutPositionQA(); }
  }
  function tutCloseQAPopup() {
    if (qaPop) { qaPop.style.display = 'none'; }
  }
  function tutCreateQA() {
    var old1 = pd.getElementById('ffp-qa-btn');
    if (old1 && old1.parentNode) { old1.parentNode.removeChild(old1); }
    var old2 = pd.getElementById('ffp-qa-pop');
    if (old2 && old2.parentNode) { old2.parentNode.removeChild(old2); }
    var btn = pd.createElement('button');
    btn.id = 'ffp-qa-btn';
    btn.type = 'button';
    btn.textContent = 'Q/A';
    btn.title = '新手教程';
    btn.addEventListener('click', function () {
      if (qaPop) { qaPop.style.display = 'flex'; }
    });
    pd.body.appendChild(btn);
    tutPositionQA();
    setTimeout(function () { try { tutPositionQA(); } catch (e) {} }, 500);
    var pop = pd.createElement('div');
    pop.id = 'ffp-qa-pop';
    pop.innerHTML = '<div class="ffp-qa-title">🐋 Q/A · 新手教程</div>' +
      '<div class="ffp-qa-text">主人想再听大肥鱼介绍一遍新手教程吗？<br>教程期间主页面功能会被锁定，可随时跳过。</div>' +
      '<div class="ffp-qa-actions">' +
      '<button id="ffp-qa-play" type="button">🔁 再播放一遍</button>' +
      '<button id="ffp-qa-close" type="button">取消</button>' +
      '</div>';
    pd.body.appendChild(pop);
    pop.querySelector('#ffp-qa-play').addEventListener('click', function () {
      tutCloseQAPopup();
      tutStart();
    });
    pop.querySelector('#ffp-qa-close').addEventListener('click', function () {
      tutCloseQAPopup();
    });
    qaBtn = btn;
    qaPop = pop;
  }
  function tutBoot() {
    tutCreateQA();
    tutShowQABtn(!tutState.active);
    if (tutState.active) {
      tutBuild();
      if (tutState.step >= 0 && tutState.step < TUT_STEPS.length) {
        tutShowStep(tutState.step);
      }
    }
    try {
      window.parent.addEventListener('resize', function () {
        tutPositionQA();
        if (!tutState.active) { return; }
        var s = TUT_STEPS[tutState.step];
        if (s) {
          tutSetImgPos(s.pos || 'centerRight');
          tutApplyReveal(tutState.curReveal || null);
          tutPlaceBubble();
        }
      });
    } catch (e) {}
  }
  tutBoot();
})();
</script>
</body>
</html>
"""


def render_desktop_pet(popup_msg=None, popup_token=None, notify_msg=None, notify_token=None,
                       drawer_html=None, open_sidebar_token=None,
                       page_scope=None):
    """在页面注入可拖动桌宠悬浮球（鲸鱼）

    popup_msg/popup_token: 检测成功时桌宠弹出气泡说的话（一次性）
    notify_msg/notify_token: 分析完成后在短对话气泡说的话（一次性）
    drawer_html: 右侧半屏数据集抽屉内容
    open_sidebar_token: 自动展开左侧侧边栏令牌（一次性）
    page_scope: 页面作用域（如 "main" / "catdog"），用于隔离不同页面的桌宠聊天记录
    """
    html = _PET_HTML
    html = html.replace('__PAGE_SCOPE__', json.dumps(page_scope, ensure_ascii=False) if page_scope else 'null')
    html = html.replace('__DEFAULT_IMG__', json.dumps(_DEFAULT_PET_IMG, ensure_ascii=False))
    html = html.replace('__DRAG_IMG__', json.dumps(_DRAG_PET_IMG, ensure_ascii=False))
    html = html.replace('__OUTFIT_IMG__', json.dumps(_OUTFIT_IMG, ensure_ascii=False))
    html = html.replace('__OUTFIT_DRAG_IMG__', json.dumps(_OUTFIT_DRAG_IMG, ensure_ascii=False))
    html = html.replace('__HARNESS_IMG__', json.dumps(_HARNESS_IMG, ensure_ascii=False))
    html = html.replace('__HARNESS_DRAG_IMG__', json.dumps(_HARNESS_DRAG_IMG, ensure_ascii=False))
    html = html.replace('__PRESET_LINES__', json.dumps(PRESET_LINES, ensure_ascii=False))
    html = html.replace('__RICE_FEED_LINES__', json.dumps(RICE_FEED_LINES, ensure_ascii=False))
    html = html.replace('__RICE_MAX_IMG__', json.dumps(_RICE_MAX_IMG, ensure_ascii=False))
    html = html.replace('__MYSTERY_IMG__', json.dumps(_MYSTERY_IMG, ensure_ascii=False))
    html = html.replace('__MYSTERY_DRAG_IMG__', json.dumps(_MYSTERY_DRAG_IMG, ensure_ascii=False))
    html = html.replace('__DSL_VIDEO__', json.dumps(_DSL_VIDEO, ensure_ascii=False))
    html = html.replace('__DSR_VIDEO__', json.dumps(_DSR_VIDEO, ensure_ascii=False))
    html = html.replace('__GAME_BG_IMG__', json.dumps(_GAME_BG_IMG, ensure_ascii=False))
    html = html.replace('__GAME_PLAYER_IMG__', json.dumps(_GAME_PLAYER_IMG, ensure_ascii=False))
    html = html.replace('__CIALLO_IMG__', json.dumps(_CIALLO_IMG, ensure_ascii=False))
    html = html.replace('__TUT_IMAGES__', json.dumps(_TUT_IMAGES, ensure_ascii=False))
    html = html.replace('__PIMG_IMAGES__', json.dumps(_PIMG_IMAGES, ensure_ascii=False))
    html = html.replace('__POPUP_MSG__', json.dumps(popup_msg, ensure_ascii=False) if popup_msg else 'null')
    html = html.replace('__POPUP_TOKEN__', json.dumps(popup_token, ensure_ascii=False) if popup_token else 'null')
    html = html.replace('__NOTIFY_MSG__', json.dumps(notify_msg, ensure_ascii=False) if notify_msg else 'null')
    html = html.replace('__NOTIFY_TOKEN__', json.dumps(notify_token, ensure_ascii=False) if notify_token else 'null')
    html = html.replace('__DRAWER_HTML__', json.dumps(drawer_html, ensure_ascii=False) if drawer_html else 'null')
    html = html.replace('__OPEN_SIDEBAR_TOKEN__', json.dumps(open_sidebar_token, ensure_ascii=False) if open_sidebar_token else 'null')
    components.html(html, height=1, scrolling=False)
