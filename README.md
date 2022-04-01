### 已爬数据
所有爬取的数据目前都存放在lemon(10.112.181.126)的`/home/data/zhangzhenhao-21/crawlers`文件夹下
* `guoxuemi`中的数据来自网站http://www.guoxuemi.com/
* `mitcsail`中的数据来自网站https://www.csail.mit.edu/
* `src`存放的是相关代码
#### guoxuemi
* `SiKuQuanShu`:来自http://www.guoxuemi.com/SiKuQuanShu/ ，代码`src/siku.py`,其中的每一个子文件夹都代表一本书，文件夹以书名命名，文件夹中的文件是以
`章节名.txt`命名的文本文件；如`《聊斋志异》`文件夹下的部分内容为：
```text
卷一 三生.txt      卷三 李伯言.txt    卷二 祝翁.txt        卷十一 仇大娘.txt    卷十二 蚰蜓.txt
卷一 偷桃.txt      卷三 李司鉴.txt    卷二 红玉.txt        卷十一 何仙　.txt    卷十二 衢州三怪.txt
卷一 僧孽.txt      卷三 梦别.txt      卷二 耿十八.txt      卷十一 布商　.txt    卷十二 陈云牺.txt
卷一 劳山道士.txt  卷三 毛狐.txt      卷二 聂小倩.txt      卷十一 席方平.txt    卷十二 青蛙神.txt
卷一 叶生.txt      卷三 江中.txt      卷二 胡四姐.txt      卷十一 彭二挣　.txt  卷十二 韦公子.txt
```
示意结构
```text
SiKuQuanShu
├── 《七修类稿》
├── 《七剑十三侠》
├── 《万历野获编》
├── 《万历野获编》1
├── 《三侠五义》
├── 《三刻拍案惊奇》
├── 《三十六计》
├── 《三命通会》
├── 《三国志 裴松之注》
├── 《三国杂事》
├── 《三国杂事》1
├── 《三国演义》
├── 《三国遗事》
├── 《三國志 裴松之注》
├── 《三字经》
├── 《三家注史记》
├── 《三朝北盟会编》

```
* `shuku`：来自http://www.guoxuemi.com/shuku/ ，代码`src/shuku.py`,是按照类型分类的文本古籍，其一级子文件夹以书籍的类别命名，二级子文件夹以更细粒度的
类别命名，三次子文件夹以书名命名，其中内容是章节名命名的文本文件；示意图
```text
shuku
├── 【丛部】
│   ├── 其他
│   │   ├── 《侯鲭录（宋）赵令畤 》
│   │   ├── 《全後漢文 》全后汉文(清)嚴可均輯
│   │   ├── 《割臺三記 》
│   │   ├── 《劍花室詩集 》(清)連橫
│   │   ├── 《北堂書鈔 》(唐)虞世南輯錄
│   │   ├── 《北戸録 》北戸錄(唐)段公路
│   │   ├── 《北郭園詩鈔 》(清)鄭用錫
│   │   ├── 《周易集解（唐）李鼎祚 》
│   │   ├── 《哀臺灣箋釋 》(清)李鶴田
│   │   ├── 《噶瑪蘭志略 》(清)柯培元
│   │   ├── 《寄园寄所寄（摘录） 》(清)浙岸赵吉士恒夫
│   │   ├── 《广陵潮 》(民国)李涵秋著
│   │   ├── 《彩云曲（有序） 》彩云曲(近人)恩施樊增祥云门
│   │   ├── 《從征實錄 》(明)楊英
│   │   ├── 《恒春縣志 》(清)屠繼善纂輯

```
* `gjzx`：来自http://www.guoxuemi.com/gjzx/ ， 代码`src/gjzx.py`,是以图片（包括jpg，png等）形式存储的影印版本的古籍；一级子目录为书名，书目录下是以章节名
命名的二级子目录，部分书目录下有以`intro.txt`命名的文本文件作为古籍的简介，章节目录下是章节内容对应的图片文件，示例结构：
```text
gjzx/
├── 万寿盛典初集 百二十卷
│   ├── 第10册
│   ├── 第11册
│   ├── 第12册
│   ├── 第13册
│   ├── 第14册
│   ├── 第15册
│   ├── 第16册
│   ├── 第17册
│   ├── 第18册
│   ├── 第19册
│   ├── 第1册
│   ├── 第20册
│   ├── 第21册
│   ├── 第22册
│   ├── 第23册
│   ├── 第24册
│   ├── 第25册
│   ├── 第26册
```
#### mitcsail
* `news`：来自https://www.csail.mit.edu/news/ ，代码`src/mitcsail.py`，每个子目录的标题是新闻的标题，其中有三个文件，分别是文本新闻、配图
和描述信息。示意图：
```text
news
├── 3Q: D. Fox Harrell on his video game for the #MeToo era
├── 3Q: How good is Natural Language Processing?
├── 3 Questions: Can we fix our flawed software?
├── 3 Questions: John Leonard on the future of autonomous vehicles
├── 4 CSAIL faculty named among top 100 leaders in AI & health
├── A better approach to preventing MeltdownSpectre attacks
├── Accelerating the discovery of new materials for 3D printing
├── Accelerator names annual award winners
├── A comprehensive map of the SARS-CoV-2 genome
├── Adelson awarded 2020 Ken Nakayama Medal
├── Advance boosts efficiency of flash storage in data centers
├── After release of MIT security report, West Virginia will no longer use voting app Voatz
├── A "GPS for inside your body"
```
### 定时运行
`crontab -l` 查看已有的定时项目
`crontab -e` 编辑定时项目表
### 参考链接
1. 面对较为复杂的网页结构，常常需要用到`xpath`来定位需要的元素，可用的`xpath`教程:
    1) https://devhints.io/xpath
    2) https://developer.mozilla.org/en-US/docs/Web/XPath
    3) https://www.w3school.com.cn/xpath/index.asp
2. 面对动态网页，`requests`和`bs4`会变得难以处理，需要寻求`selenium`的帮助；
    1) 在Linux上安装`selenium`：https://zhuanlan.zhihu.com/p/451163617
3. `crontab`简介：https://www.runoob.com/linux/linux-comm-crontab.html
