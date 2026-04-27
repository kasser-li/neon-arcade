<template>
  <div class="novel">
    <header class="novel-header">
      <h1 class="title">🐉 龙血纪元</h1>
      <p class="subtitle">第一章 · 废柴的觉醒</p>
      <button class="back-btn" @click="goHome">← 返回游戏站</button>
    </header>

    <div class="chapter-nav">
      <button :class="{ active: currentChapter === 1 }" @click="currentChapter = 1">第一章：废柴的觉醒</button>
      <button :class="{ active: currentChapter === 2 }" @click="currentChapter = 2">第二章：卡塞尔学院</button>
    </div>

    <div class="novel-content">
      <!-- 第一章 -->
      <div v-if="currentChapter === 1" class="chapter">
        <h2>第一章：废柴的觉醒</h2>

        <p>路明非一直觉得自己是个废柴。</p>

        <p>这个认知从他七岁那年把邻居家的猫吓到绝食三天就开始生根发芽，到十六岁那年他已经在心里给自己盖了章、按了手印，顺便还办了张终身会员。</p>

        <p>废柴是一种气质，路明非觉得。不是那种"我其实很厉害只是不想表现"的凡尔赛式废柴，而是真正的、纯粹的、从骨子里透出来的废。就像一杯放了三天的白开水，连细菌都懒得在里面繁殖。</p>

        <p>但他没想到，废柴也有废柴的春天。</p>

        <p>那天是个普通的周二，北京的秋天总是很短，短到路明非还没来得及把夏装收起来，冷风就已经开始往他领口里钻了。他正蹲在出租屋楼下的马路牙子上啃煎饼果子，手机突然响了。</p>

        <p>来电显示是一串他从未见过的号码，区号不是国内的。</p>

        <p>"喂？"路明非咬了一口煎饼，含糊不清地接了电话。</p>

        <p>"请问是路明非先生吗？"电话那头是个女声，声音很冷，像冰镇过的矿泉水，但用词很正式，正式到路明非差点把煎饼掉地上。</p>

        <p>"我是。你是？"</p>

        <p>"我是卡塞尔学院的招生办主任，诺诺。路先生，恭喜你被我院录取了。"</p>

        <p>路明非愣了三秒。</p>

        <p>"哪个卡塞尔？打篮球那个？"</p>

        <p>电话那头沉默了一秒，然后传来一声几不可闻的叹息。</p>

        <p>"不是 NBA 的那个。我们是研究龙族的。"</p>

        <p>"龙？什么龙？恐龙？"</p>

        <p>"不是恐龙。是那种会喷火、有翅膀、住在山洞里、喜欢收集金币的龙。欧洲神话里的那种。"</p>

        <p>路明非把煎饼从嘴边拿开，认真思考了一下。</p>

        <p>"你们学院招生这么随便的吗？我高考都没参加。"</p>

        <p>"路先生，我们不看出身，不看成绩，只看血统。而你的血统……非常优秀。"</p>

        <p>"血统优秀？"路明非低头看了看自己沾了辣椒酱的拖鞋，"你确定没搞错？我连抽卡都抽不到 SSR 的。"</p>

        <p>"路先生，SSR 算什么。我们这里有 SSS。"</p>

        <p>路明非觉得这通电话要么是诈骗，要么是他昨晚打游戏打太晚产生了幻听。但那个叫诺诺的女生接下来的话让他没法不当回事。</p>

        <p>"路先生，你七岁那年是不是去过一次芝加哥？"</p>

        <p>路明非的呼吸滞了一下。</p>

        <p>"你怎么知道？"</p>

        <p>"因为那次你去的地方，不是芝加哥。是卡塞尔学院的地下三层。"</p>

        <p>风从胡同口吹过来，卷起几片落叶。路明非坐在马路牙子上，手里的煎饼已经凉了。他突然觉得，这个普通的周二，好像没那么普通了。</p>

        <p>"路先生，明天上午九点，会有人来接你。请不要告诉任何人你要去哪里，包括你的叔叔阿姨。"</p>

        <p>"等等——"路明非还没来得及问什么，电话已经挂了。</p>

        <p>他坐在马路牙子上，吹了十分钟冷风，然后把剩下的半个煎饼塞进嘴里，嚼了嚼，咽下去。</p>

        <p>"行吧，"他自言自语道，"反正再坏也坏不到哪去。"</p>

        <p>废柴的觉悟，有时候就是这么简单。</p>
      </div>

      <!-- 第二章 -->
      <div v-if="currentChapter === 2" class="chapter">
        <h2>第二章：卡塞尔学院</h2>

        <p>第二天早上八点五十，路明非站在他家楼下。</p>

        <p>他换了一身干净衣服——所谓的干净，就是没有辣椒油渍而已。他背了个书包，里面装了三件换洗衣服、一个充电宝、一本《五年高考三年模拟》（虽然用不上了但还是带着辟邪），以及一张他爸妈的合影。</p>

        <p>他其实不太记得他爸妈长什么样了。记忆里的脸总是模糊的，像一张被水洗过的照片。但他习惯带着那张合影，好像那样就能离他们近一点。</p>

        <p>八点五十五分，一辆黑色的轿车停在了他面前。</p>

        <p>车是迈巴赫，路明非认得，因为他只在汽车杂志上见过。车门打开，一个穿着黑色西装的男人走了下来。男人很高，大概一米八五以上，头发梳得一丝不苟，脸上没什么表情，看起来像是那种会在电影里说"时间到了"然后按核按钮的角色。</p>

        <p>"路明非先生？我是楚子航，卡塞尔学院的执行部主任。请上车。"</p>

        <p>路明非看了看楚子航，又看了看迈巴赫，觉得这个世界一定是出了什么bug。</p>

        <p>"执行部主任？你们学院还有执行部？执行什么？"</p>

        <p>楚子航的表情没有任何变化。</p>

        <p>"执行屠龙任务。"</p>

        <p>路明非张了张嘴，没说出话来。他默默地把书包往肩上提了提，坐进了迈巴赫的后座。</p>

        <p>车里很安静，安静到路明非能听到自己的心跳声。楚子航坐在他旁边，双手放在膝盖上，腰板挺得笔直，像一尊雕塑。</p>

        <p>"楚师兄，"路明非试探性地开口，"你们学院……平时都做些什么？"</p>

        <p>"上课，训练，执行任务。"</p>

        <p>"上什么课？"</p>

        <p>"龙族语言学、龙类生态学、言灵学、炼金学、武器锻造……"</p>

        <p>路明非觉得自己的世界观正在被按在地上摩擦。</p>

        <p>"言灵？那是什么？"</p>

        <p>"言灵是龙族的力量。通过特定的语言，可以触发超越人类认知的能力。比如——"</p>

        <p>楚子航顿了一下。</p>

        <p>"比如？"</p>

        <p>"比如让时间变慢。"</p>

        <p>路明非觉得楚子航在开玩笑。但楚子航的表情告诉他，这个人可能这辈子都不会开玩笑。</p>

        <p>"还有，"楚子航继续说，"你的血统评级是 S，这意味着你很可能拥有言灵。只是你还没有觉醒。"</p>

        <p>"S 级？"路明非愣了一下，"就像游戏里的 SSR？"</p>

        <p>"比 SSR 更稀有。卡塞尔学院建校一百年来，S 级不超过十个。"</p>

        <p>路明非不知道该高兴还是该害怕。他一个抽卡永远保底的人，突然告诉他你是万里挑一的天才？这感觉就像告诉你你其实是失散多年的王子——但前提是你是个废柴王子。</p>

        <p>车子开了两个小时，最后驶入了一片山林。路明非透过车窗往外看，发现山里面居然藏着一座巨大的城堡。</p>

        <p>"那就是卡塞尔学院？"路明非瞪大了眼睛。</p>

        <p>"是的。"</p>

        <p>"我靠……"</p>

        <p>"请不要说脏话。"</p>

        <p>"好的楚师兄。"</p>

        <p>迈巴赫驶入了城堡的大门。路明非看着那座古老的建筑，心里涌起一种奇怪的感觉——像是恐惧，又像是期待。</p>

        <p>就像一个废柴突然被扔进了一个他从未想象过的世界。</p>

        <p>他不知道等待他的是什么。但他隐约觉得，自己的人生，从今天开始，要不一样了。</p>

        <p>废柴的春天，或许真的来了。</p>
      </div>
    </div>

    <div class="chapter-nav bottom">
      <button @click="prevChapter" :disabled="currentChapter === 1">← 上一章</button>
      <span>{{ currentChapter }} / 2</span>
      <button @click="nextChapter" :disabled="currentChapter === 2">下一章 →</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentChapter = ref(1)

function goHome() {
  router.push('/')
}

function prevChapter() {
  if (currentChapter.value > 1) {
    currentChapter.value--
    window.scrollTo(0, 0)
  }
}

function nextChapter() {
  if (currentChapter.value < 2) {
    currentChapter.value++
    window.scrollTo(0, 0)
  }
}
</script>

<style scoped>
.novel {
  min-height: 100vh;
  background: #0a0a0a;
  color: #e0e0e0;
  font-family: 'Georgia', 'SimSun', serif;
}

.novel-header {
  text-align: center;
  padding: 40px 20px 20px;
  border-bottom: 1px solid #333;
}

.title {
  font-size: 2.5em;
  color: #ff6b35;
  margin: 0;
  text-shadow: 0 0 20px rgba(255, 107, 53, 0.3);
}

.subtitle {
  font-size: 1.2em;
  color: #888;
  margin: 10px 0;
}

.back-btn {
  margin-top: 15px;
  padding: 8px 20px;
  background: transparent;
  border: 1px solid #555;
  color: #aaa;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.back-btn:hover {
  border-color: #ff6b35;
  color: #ff6b35;
}

.chapter-nav {
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  border-bottom: 1px solid #222;
}

.chapter-nav.bottom {
  border-top: 1px solid #222;
  border-bottom: none;
  padding: 20px;
}

.chapter-nav button {
  padding: 10px 25px;
  background: #1a1a1a;
  border: 1px solid #444;
  color: #ccc;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
  transition: all 0.3s;
}

.chapter-nav button:hover:not(:disabled) {
  border-color: #ff6b35;
  color: #ff6b35;
}

.chapter-nav button.active {
  background: #ff6b35;
  border-color: #ff6b35;
  color: #000;
}

.chapter-nav button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.chapter-nav span {
  display: flex;
  align-items: center;
  color: #666;
  font-size: 14px;
}

.novel-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  line-height: 2;
  font-size: 17px;
}

.chapter h2 {
  color: #ff6b35;
  font-size: 1.8em;
  margin-bottom: 30px;
  text-align: center;
}

.chapter p {
  margin: 15px 0;
  text-indent: 2em;
}

@media (max-width: 768px) {
  .title {
    font-size: 1.8em;
  }

  .novel-content {
    padding: 20px 15px;
    font-size: 16px;
  }

  .chapter p {
    text-indent: 1.5em;
  }
}
</style>
