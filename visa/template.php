<html>
<head>
    <title>预约美签，防止失学</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
	<link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap-theme.min.css" rel="stylesheet">
    <script src="https://cdn.bootcdn.net/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
    <script src="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@4.7.0/dist/echarts.min.js"></script>
    <script async src="//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
    <script data-ad-client="ca-pub-5419513334556516" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
	<script async src="https://www.googletagmanager.com/gtag/js?id=UA-102409527-2"></script>
	<script>
		window.dataLayer = window.dataLayer || [];
		function gtag(){dataLayer.push(arguments);}
		gtag('js', new Date());
		gtag('config', 'UA-102409527-2');
	</script>
    <style type="text/css">
    .table thead tr th { text-align: center; vertical-align: middle; }
    .table tbody tr td { text-align: center; vertical-align: middle; }
    </style>
    <script>
    $(document).ready(function() {
        if(location.hash) {
            $("a[href=" + location.hash + "]").tab("show");
            if (location.hash == "#F") chartF();
            else if (location.hash == "#B") chartB();
            else if (location.hash == "#H") chartH();
            else if (location.hash == "#O") chartO();
            else if (location.hash == "#L") chartL();
            else chartF();
        }
        else chartF();
        $(document.body).on("click", "a[data-toggle]", function(event) {
            location.hash = this.getAttribute("href");
            if (location.hash == "#F") chartF();
            else if (location.hash == "#B") chartB();
            else if (location.hash == "#H") chartH();
            else if (location.hash == "#O") chartO();
            else if (location.hash == "#L") chartL();
        });
    });
    $(window).on("popstate", function() {
        var anchor = location.hash || $("a[data-toggle=tab]").first().attr("href");
        $("a[href=" + anchor + "]").tab("show");
    });
    </script>
</head>
<body>
    <div class="container">
        <h1 class="text-center" id="title">美国签证预约时间</h1>
            <center>
				<br><a href="/visa2">系统当前状态</a> | <a href="https://t.me/f_visa">Telegram频道</a> | <a href="#email">个性化邮件通知</a> | <a href="#disqus_thread">需要翻墙的评论区</a> | <a href="https://checkee.info">签证结果统计</a>
                <br>QQ通知<a href="javascript:alert(1104038280)">1群</a>/<a href="javascript:alert(672921682)">2群</a>/<a href="javascript:alert(1091934602)">3群</a>/<a href="javascript:alert(1076963772)">4群</a><!--/<a href="javascript:alert(722281429)">5群</a>-->，密码是本站网址（共13个字符<code>t***e</code>），四个群内容都一样
                <br><span style="color:red">QQ邮箱把tuixue的邮件给扔进垃圾箱了，请大家注意一下，最好白名单</span>
                <!--<br><span style="color: green">发现还有好多人不知道tuixue在问……求一个推广呜呜呜（比如微博、票圈之类的）</span>-->
				<!--<br>加了割美帝资本主义韭菜的功能，不知道会在哪出现，不想割韭菜的话用AdBlock屏蔽掉就行（大雾-->
                <br>
                <br>
            </center>
            <div id="chart" style="height: 250px; width: 100%"></div>
            <center>更多图表请点击表格左侧时间</center><br>
            <div class="bs-example bs-example-tabs" data-example-id="togglable-tabs">
                <ul class="nav nav-tabs" role="tablist">
                    <li role="presentation" class=""><a href="#F" role="tab" id="F-tab" data-toggle="tab" aria-controls="F" aria-expanded="false">F1/J1</a></li>
                    <li role="presentation" class=""><a href="#B" role="tab" id="B-tab" data-toggle="tab" aria-controls="B" aria-expanded="false">B1/B2</a></li>
                    <li role="presentation" class=""><a href="#H" role="tab" id="H-tab" data-toggle="tab" aria-controls="H" aria-expanded="false">H1B</a></li>
                    <li role="presentation" class=""><a href="#O" role="tab" id="O-tab" data-toggle="tab" aria-controls="O" aria-expanded="false">O1/O2/O3</a></li>
                    <li role="presentation" class=""><a href="#L" role="tab" id="L-tab" data-toggle="tab" aria-controls="L" aria-expanded="false">L1/L2</a></li>
                    <li role="presentation" class=""><a href="#email" role="tab" id="email-tab" data-toggle="tab" aria-controls="email" aria-expanded="false">邮件通知</a></li>
                    <li role="presentation" class=""><a href="#notes" role="tab" id="notes-tab" data-toggle="tab" aria-controls="notes" aria-expanded="false">注意事项</a></li>
                    <li role="presentation" class=""><a href="#code" role="tab" id="code-tab" data-toggle="tab" aria-controls="code" aria-expanded="false">关于</a></li>
                </ul>
                <div id="myTabContent" class="tab-content">
					TBD_PANE
					<div role="tabpanel" class="tab-pane fade" id="notes" aria-labelledby="notes-tab">
<p></p>
<p>这里总结了一些<a href="#disqus_thread">需要翻墙的评论区</a>中出现的约签证的技巧和注意事项</p>
<p>目前测量结果是每个小时第48分04秒放名额，网站上的更新没法做到秒级别的更新，因此会稍稍慢于蹲点同学的获取时间（不过这些跳下来的尖峰都是几个人退出来的，不算批量放位置，没几分钟就被抢光了）</p>
<p>记录在案的大批量放位置的时间：成都04/21 10:24，广州04/17 13:38、05/13 09:25，上海04/13 11:56、04/23 15:28、05/14 15:25，沈阳 04/24 09:04、04/28 08:41、05/13 11:27，（香港比较迷），看起来都在早上或者下午</p>
<p>一般来说，大批量放位置之后会有人不停地退和选，因此在放位置之后的一两天都有很大概率能捡漏。</p>
<p>(04.17) <a href="https://disqus.com/by/disqus_9Z3ojTbVFe/">TRMSCT</a><br>如果要多领馆申请的话还要提前把不同领事馆所用的DS-160准备好，这样可以有位置马上去选</p>
<p>(04.18) <a href="https://disqus.com/by/disqus_rTmjxY4aqA/">YJX</a><br>成都领事馆目前只需要天府通健康码，非湖北只需要填两张表就可以了，以及使馆开门了</p>
<p>(04.22) <a href="https://disqus.com/by/disqus_cEqiNLHBj5/">JJHunter</a> &amp; <a href="https://disqus.com/by/disqus_rTmjxY4aqA/">YJX</a><br>大使馆cgi账号在你频繁刷新面签时间的情况下会被冻结3天账号不能登录。没有任何办法提前解封，显示：Your account has been frozen for suspicious activity, and you will not be able to access it for up to 72 hours.</p>
<p>(04.24 / 05.14) <a href="https://disqus.com/by/disqus_4onFXIu7jE/">尤大师</a> &amp; <a href="https://disqus.com/by/billzhaox/">Billzhaox</a><br>注意一个美签收据只能约三次，即使约了早了但到时候领馆没开（譬如之前广州可以约3月4月），被动取消竟然也算在次数里..可怜了160刀<br>问过领馆穿红衣的那些小姐姐们，是说只能约三次（也就是取消两次），担心160刀没了所以没试过<br>
肉身测试了一波重新预约的次数限制，重新约了3次，加上最开始的一次也就是总共约过4次，都是同一领馆只是更改时间，现在点进重新预约后出现“如果取消本次预约，您将超出取消预约的许可上限，您必须重新缴纳可机读签证申请费，才能继续预约。“字样，说明现在只剩最后一次修改机会。但我感觉这个次数限制并不是永久固定的，具体是多少次官方也没有一个说法，一切还是以系统提示为准吧。</p>
<p>(04.29) <a href="https://disqus.com/by/disqus_5Ptsb5Joj1/">qwezxc</a><br>香港入境更新：检疫政策持续到6.7，大家要是想来香港签还是再好好考虑一下吧。最简单的理解适用于大部分关注香港办签证的人： 内地游客身份从内地来港 或者 目前身在海外想来香港以过境签来香港。 这两种都不可以来香港。即便从内地出发，游客的签证只有7天，打不到14天，会被拒绝入境。过境签更不可能</p>
<p>(05.04) <a href="https://disqus.com/by/disqus_VFB75p0HHb/">Rishi</a> &amp; <a href="https://disqus.com/by/disqus_wz5ihrotlj/">Claire</a><br>Q: 请问我之前预约了一个地方，ds160然后费用也交了。现在想换个地方重新填了个ds160，那我要再重新缴费换一个receipt number吗？<br>A: 不用重新缴费，在profile那儿改一下DS160号码就行，DS160可以填很多个的<br>Q: 那再请问下如果已经约上了一个地方， reschedule appointment是会回到开始的界面重新填写ds160这些信息，还是直接只能回到那个已经约上了的地方选时间那里？<br>A: reschedule只能改时间不能改地址，想要换地方的话，只能取消再预约。DS160在profile那儿可以随时改的，你预约时候用的哪个不是很重要，只要最后面试前保持一致就行<br>Q: 那reschedule会有风险吗？比如既没有选到新的更早的时间的，旧的预约也没了:(<br>A: 其实你自己试一试就知道了。。。你选择了新的时间，以前的才会作废，你没有选新的时间，以前的就当然还有效。。。</p>
<p><br></p>
                    </div>
                    <div role="tabpanel" class="tab-pane fade" id="email" aria-labelledby="email-tab">
                    <br>
                    <center>每当时间变前的时候，tuixue.online就会向您发送邮件通知。<br>最好是国内邮箱比如qq（因为可以绑定微信，能第一时间看到），实测延时大概10s<br>国外的邮箱（比如gmail）<s>实测延迟很大...</s>好像也没延时了<br><br>
                    如果没收到确认邮件，可以翻一翻垃圾箱，并且把<code>dean@tuixue.online</code>加入白名单中；<br>或者可以重新在这里提交一次 or 换个邮箱试试<br>实在不行了就联系管理员吧<br><br>
                    <b>即使能正常收到也不意味着一定不会进垃圾邮箱里面，建议白名单。</b></center><br>
                    <form action="/asiv" method="get" enctype="multipart/form-data" id="notify-form">
                            <center>
                            <table>
                            <tr><td align="right">邮箱地址：</td><td><input type="email" name="email" class="form-control" placeholder="prefer *@qq.com"></td></tr>
                            <tr><td align="right">F1/J1：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fbj"> 北京</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fcd"> 成都</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fgz"> 广州</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fsh"> 上海</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fsy"> 沈阳</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fhk"> 香港</label>
                            </td></tr>
                            <tr><td align="right">B1/B2：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bbj"> 北京</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bcd"> 成都</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bgz"> 广州</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bsh"> 上海</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bsy"> 沈阳</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bhk"> 香港</label>
                            </td></tr>
                            <tr><td align="right">H1B：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hbj"> 北京</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hgz"> 广州</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hsh"> 上海</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hhk"> 香港</label>
                            </td></tr>
                            <tr><td align="right">O1/O2/O3：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="obj"> 北京</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ocd"> 成都</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ogz"> 广州</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="osh"> 上海</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="osy"> 沈阳</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ohk"> 香港</label>
                            </td></tr>
                            <tr><td align="right">L1/L2：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lbj"> 北京</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lgz"> 广州</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lsh"> 上海</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lhk"> 香港</label>
                            </td></tr>
							<tr><td>当出现的时间早于（并包含）该日期时发送提醒：</td><td><input class="form-control" type="date" value="" name="time"></td></tr>
							<tr><td align="right">输入以下验证码（五位小写英文字母）：</td><td><input class="form-control" type="text" value="" name="captcha" maxlength=5></td></tr>
                            </table>
                            TBD_CAPTCHA
                            <br><br><b>一般来说，每个小时的第48分会放出这个小时内被别人退掉的名额，不是很好抢到<br>但是如果邮件推送给您的时间不是48-53分，多半是这个地方放了一大波名额</b><br>
                            <br>如果要取消订阅的话，全不选然后提交，再重新戳确认邮件里面的链接就行了。<br><br>
                            <input type="submit" value="提交" class="btn btn-info"/>
                            </center>
                    </form>
                    </div>
                    <div role="tabpanel" class="tab-pane fade" id="code" aria-labelledby="code-tab">
                    <br>
                    GitHub 项目地址：<a href="https://github.com/Trinkle23897/us-visa">https://github.com/Trinkle23897/us-visa</a>
                    <br><br>
                    作者GitHub：<a href="https://github.com/Trinkle23897/">https://github.com/Trinkle23897/</a>
                    <br><br>
                    作者个人主页：<a href="https://trinkle23897.github.io/cv/">https://trinkle23897.github.io/cv/</a>
                    <br><br>
                    <b>感谢 <a href="https://github.com/z3dd1cu5">z3dd1cu5</a> 提供的改进版爬虫！</b>
                    <br><br>
                    写这玩意还是花了一些时间的，维护也不容易（服务器要钱，验证码要钱，邮件系统是私搭的可能会被封），随喜打赏
                    <center><img src="/upload/39CB3AB2-FEFD-44EC-88D3-F6C4A4C7B2B7.jpeg" style="width: 30%"><img src="/upload/F293524B-8160-4FB0-8CEE-3803ED464D4D.jpeg" style="width: 30%"></center>
					<br><br>
                    如果您觉得 tuixue.online 很有帮助，可以在毕业论文中加入如下致谢：（贵学术圈不都这么搞的嘛（狗头））
                    <br><br>
                    <code>感谢翁家翌同学制作的 tuixue.online 网站帮助我在紧张的毕业设计过程中 [请自由发挥]。</code>
					<br><br>
                    If you find tuixue.online helpful and useful, please add the following acknowledgement in your publication:
					<br><br>
					<code>Thanks to Mr. Jiayi Weng's website tuixue.online for [blabla] during my graduation project.</code>
                    <br><br>
                    </div>
                </div>
            </div>
            <center>
                广告位招租，详情咨询：<a href="https://trinkle23897.github.io/">https://trinkle23897.github.io/</a><br><br>
                本网站一共见证了<span id="busuanzi_value_page_pv"></span>人次的失学。<a href="https://www.zhihu.com/question/318624725/answer/875527594">关于可怜的差点被全聚德的作者</a><br>
            </center>
            <br>
            <div id="disqus_thread"></div>
            <script async src="https://tuixue-online.disqus.com/embed.js"></script>
            <br>
    </div>
</body>
</html>
