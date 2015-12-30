Table of Contents
=================
    * [介绍 Intro](#介绍-intro)
    * [更新日志 Updates](#更新日志-updates)
      * [「功能性更新 Features」](#功能性更新-features)
          * [¶ 我的进度](#-我的进度)
          * [¶ 登入、注册](#-登入注册)
          * [¶ 网站整体](#-网站整体)
      * [「修复 Bug Fix」](#修复-bug-fix)

# 介绍 Intro
- 个人维护的网站，逐渐完善并增加新功能
- 以做出优质而简单的应用为目标
- 不断优化已有代码
- 实现并完善新奇想法

# 更新日志 Updates
## 「功能性更新 Features」
### ¶ 我的进度
2015-12-30
- 现在个人资料页面可以看到自己的进度统计数据了！

2015-12-29
- 进行进度相关的操作时，增加活跃度。
    - 访问进度列表页面、进度存档页面、进度详情页面 +1
    - 尝试新增进度、新增进度、快捷更新进度、编辑进度 +2
    - 删除进度、弃置进度、取消弃置进度 +2

2015-12-06
- 对作品颜色进行了缓存，显示颜色更快了。
- 在「进度列表页」会显示已缓存作品的颜色了。

2015-12-04
- 增加新的进度状态：待阅读。
    - 除了“已弃置”的进度外，当前进度为0的进度会被自动设置为“待阅读”
    - 待阅读的进度们会默认被折叠，更专注于正在进行的进度。
- 将“已完成”和“已弃置”的进度移入「进度存档」页面。
- 对按钮的图标进行补充和细调，对按钮颜色进行调整。
- 「进度详情页」移除“新增”按钮，增加新增进度按钮。
- 「进度详情页」现在左侧可以显示代表当前作品的颜色了。

2015-12-03
- 「进度详情页」增加对“预计完成时间”的估算
- 「进度详情页」中，对“已完成”的进度显示完成时间，并隐藏预计完成时间。

2015-11-30
- 移除对“副标题”的判断，改为由专属的进度表信息“链接”来维护进度的外链地址。
    - “链接”在创建时、更新时，默认值为空。
- 新增进度增加“链接”
- 新增进度中，“链接”、“副标题”、“当前进度”默认折叠。
- 「进度列表页」和「进度详情页」中，名称过长的项可以正确的隐藏并滚动了。

2015-11-29
- 新增了对“副标题”的判断：
    - 当副标题以 'http://'、'https://'、'ftp://'开头时，显示时自动变为连接。

2015-11-26
- 现在在「进度详情页」点击作品名称可以看到同名作品的其他人的进度啦！
- 更新了「进度列表页」鼠标放置时的动画效果，使其看起来更合理。

2015-10-03
- 将“追剧”环节默认设定成展开。
- 使 api 返回的结果更靠谱
- 如果名称判断不是精确匹配时，会在“名称”处提示可能的名字和链接。

2015-10-02
- 新增“追剧进度”：
    - 创建、修改进度时，将“总共"设为 0，即为追剧进度。
    - 当一个进度为“追剧进度”时，计算百分比时分母为当前进度+1，分子为当前进度。
- 名称匹配解析：
    - 名称匹配时不会包含空格了。意味着你可以用空格分开关键词
    - 同时支持影片的中英文名称
- 当查看一个不属于你的进度时，会正确的跳转回「进度列表页」面了。

2015-09-30
- 修改了「进度列表页」page-header的图标，使其更加易懂
- 列表页按照最后修改时间排序

2015-09-29
- 增加到「作品详情页」的链接
- 作品详情页增加所有用户进度

2015-09-26
- 优化了副标题对作品类型的判断。
- 现在可以强制指定类型的标签有：（无视大小写）
    - 书，书籍，book，pdf，漫画，comic，文字，doc，txt
    - 动画，anime，电影，movie，电视剧，tv，show，美剧，英剧，韩剧，日剧

2015-09-25
- 支持副标题指定内容类型：书、动画、电影、电视剧、book、movie，不关心大小写。
- 当评分和标签为 0 时，自动隐藏对应的栏位
- 作品信息旁边的小 logo 现已可以链接到豆瓣的相应页面。

2015-09-15
- 支持新建时自动读取书籍总页数
- 支持新建时自动填写总页数及当前进度
- 支持查看详情时，通过豆瓣Api搜索对应的书、剧
- 查看详情时，显示豆瓣评分和标签。

### ¶ 登入、注册
2015-10-13
- 为网站增添了发送 Email 的功能

2015-10-07
- 修改登入时，提示信息的显示方法。（弹出提示变为直接显示提示）
- 登入时，判断当前输入中的用户名是否存在：
    1. 不存在，继续等待用户输入
    2. 存在：显示问题、提示
- 用户名存在时，判断用户名是否是其他用户名的前半部分：
    1. 不是，自动焦点至密码/回答输入框
    2. 是，焦点仍留在用户名输入框
- 现在注册时默认的模式是「传统模式」，不会弹出提示
- 将“忘记答案”变更为“忘记密码/答案”，并挪至左上角
- 注册时更严格的按钮判断标准，并且「提交注册」按钮在不可用时也可以切换焦点了。

2015-10-02
- 优化了注册、登录页面图片读取速度
- 登录页面输入完答案/密码可以按回车键登入了！

2015-09-25
- 现在登入时，如果问题里带有“密码”的字样，则输入框提示变成“密码”，同时不以明文方式显示。
- 现在注册时，可以点击左上角的按钮在「传统模式」和「问答模式」之间切换了。
    - 支持账号 + 密码模式了！
    - 进入注册页面时默认「问答模式」，但会弹出提示。

### ¶ 网站整体
2015-12-30
- 活跃度系统增加了最近5次的活跃记录。

2015-12-29
- 增加活跃度系统。进行不同的动作，得到不同的分数。
- 活跃度和等级，以及活跃度历史，在用户个人信息页面查看。
- 计算活跃度等级的算法分 2 种，目前选择为平方算法。
    - 斐波那契数列：
        - t(n+1) = t(n) + t(n-1)
        - delta = t(n+1) - t(n) = t(n-1) 指数增长
    - 平方算法：
        - t(n+1) = (n+1)² = n² + 2n + 1
        - t(n) = n²
        - delta = t(n+1) - t(n) = 2n + 1 线性增长

2015-12-04
- 移除了顶部用户头像，改为“Hi,”
- 新增 功能性按钮，在电脑/平板中显示在左上角，在手机/小屏幕时显示在右下角

## 「修复 Bug Fix」
2015-12-07
- 修复了进度缓存时 key 与读取时的 key 不同的问题。

2015-12-01
- 修复了「进度列表页」可能会空格的问题。

2015-11-26
- 首页：修复了一个导致页面宽度会大于浏览器的 bug

2015-10-03
- 我的进度：修复了名称判定时的一个bug，导致没有 OriginalTitle 的作品会通过判定

2015-10-02
- 修复了注册后登录会回到 newuser 页面的 bug

