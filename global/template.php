<?php
header("Access-Control-Allow-Origin: *");
if (!empty($_REQUEST))
	echo '<meta http-equiv="refresh" content="0;url=/global"/>';
else echo '<html>
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
    <!--<script data-ad-client="ca-pub-5419513334556516" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>-->
	<script async src="https://www.googletagmanager.com/gtag/js?id=UA-102409527-2"></script>
	<script>
		window.dataLayer = window.dataLayer || [];
		function gtag(){dataLayer.push(arguments);}
		gtag("js", new Date());
		gtag("config", "UA-102409527-2");
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
            else if (location.hash == "#Fais") chartFais();
            else if (location.hash == "#Bais") chartBais();
            else if (location.hash == "#Hais") chartHais();
            else if (location.hash == "#Oais") chartOais();
            else if (location.hash == "#Lais") chartLais();
            else if (location.hash == "#Fmx") chartFmx();
            else if (location.hash == "#Bmx") chartBmx();
            else if (location.hash == "#Hmx") chartHmx();
            else if (location.hash == "#Omx") chartOmx();
            else if (location.hash == "#Lmx") chartLmx();
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
			else if (location.hash == "#Fais") chartFais();
            else if (location.hash == "#Bais") chartBais();
            else if (location.hash == "#Hais") chartHais();
            else if (location.hash == "#Oais") chartOais();
            else if (location.hash == "#Lais") chartLais();
            else if (location.hash == "#Fmx") chartFmx();
            else if (location.hash == "#Bmx") chartBmx();
            else if (location.hash == "#Hmx") chartHmx();
            else if (location.hash == "#Omx") chartOmx();
            else if (location.hash == "#Lmx") chartLmx();
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
        <h1 class="text-center" id="title"><a href="javascript:alert(\'CGI系统：https://cgifederal.secure.force.com/ \nAIS系统：https://ais.usvisa-info.com/ \n\')">美国签证</a>预约时间（国际版）</h1>
            <center>
				<br><a href="/visa/">国内版</a> | <a href="/visa2">系统当前状态</a> | <a href="#disqus_thread">需要翻墙的评论区</a> | <a href="https://checkee.info">签证结果统计</a>
				<br><span style="color:red">推送通知：</span><a href="#email">个性化邮件通知</a> | <a href="https://t.me/f_visa_global">Telegram频道</a>
<!--<a href="javascript:alert(646098814)">6群</a>/<a href="javascript:alert(739464328)">7群</a>/<a href="javascript:alert(1040436778)">8群</a>/<a href="javascript:alert(578968441)">9群</a>/<a href="javascript:alert(1044608829)">10群</a>/<a href="javascript:alert(921303937)">11群</a>-->
                <!--<br><span style="color:red">QQ邮箱把tuixue的邮件给扔进垃圾箱了，请大家注意一下，最好白名单</span>-->
                <!--<br><span style="color: green">发现还有好多人不知道tuixue在问……求一个推广呜呜呜（比如微博、票圈之类的）</span>-->
				<!--<br>加了割美帝资本主义韭菜的功能，已调低展示比例并排除垃圾内容，不想割韭菜的话用AdBlock屏蔽掉就行（大雾-->
                <br>
                <br>
            </center>
            <div id="chart" style="height: 250px; width: 100%"></div>
            <center>更多图表请点击表格左侧时间</center><br>
            <div class="bs-example bs-example-tabs" data-example-id="togglable-tabs">
                <ul class="nav nav-tabs" role="tablist">
                    <li role="presentation" class=""><a href="#F" role="tab" id="F-tab" data-toggle="tab" aria-controls="F" aria-expanded="false">F/J-cgi</a></li>
                    <li role="presentation" class=""><a href="#Fais" role="tab" id="Fais-tab" data-toggle="tab" aria-controls="Fais" aria-expanded="false">F/J-ais</a></li>
                    <li role="presentation" class=""><a href="#Fmx" role="tab" id="Fmx-tab" data-toggle="tab" aria-controls="Fmx" aria-expanded="false">F/J-mx</a></li>
                    <li role="presentation" class=""><a href="#B" role="tab" id="B-tab" data-toggle="tab" aria-controls="B" aria-expanded="false">B-cgi</a></li>
                    <li role="presentation" class=""><a href="#Bais" role="tab" id="Bais-tab" data-toggle="tab" aria-controls="Bais" aria-expanded="false">B-ais</a></li>
                    <li role="presentation" class=""><a href="#Bmx" role="tab" id="Bmx-tab" data-toggle="tab" aria-controls="Bmx" aria-expanded="false">B-mx</a></li>
                    <li role="presentation" class=""><a href="#H" role="tab" id="H-tab" data-toggle="tab" aria-controls="H" aria-expanded="false">H1B-cgi</a></li>
                    <li role="presentation" class=""><a href="#Hais" role="tab" id="Hais-tab" data-toggle="tab" aria-controls="Hais" aria-expanded="false">H1B-ais</a></li>
                    <li role="presentation" class=""><a href="#Hmx" role="tab" id="Hmx-tab" data-toggle="tab" aria-controls="Hmx" aria-expanded="false">H1B-mx</a></li>
                    <li role="presentation" class=""><a href="#O" role="tab" id="O-tab" data-toggle="tab" aria-controls="O" aria-expanded="false">O-cgi</a></li>
                    <li role="presentation" class=""><a href="#Oais" role="tab" id="Oais-tab" data-toggle="tab" aria-controls="Oais" aria-expanded="false">O-ais</a></li>
                    <li role="presentation" class=""><a href="#Omx" role="tab" id="Omx-tab" data-toggle="tab" aria-controls="Omx" aria-expanded="false">O-mx</a></li>
                    <li role="presentation" class=""><a href="#L" role="tab" id="L-tab" data-toggle="tab" aria-controls="L" aria-expanded="false">L-cgi</a></li>
                    <li role="presentation" class=""><a href="#Lais" role="tab" id="Lais-tab" data-toggle="tab" aria-controls="Lais" aria-expanded="false">L-ais</a></li>
                    <li role="presentation" class=""><a href="#Lmx" role="tab" id="Lmx-tab" data-toggle="tab" aria-controls="Lmx" aria-expanded="false">L-mx</a></li>
                    <li role="presentation" class=""><a href="#email" role="tab" id="email-tab" data-toggle="tab" aria-controls="email" aria-expanded="false">邮件通知</a></li>
                    <li role="presentation" class=""><a href="#notes" role="tab" id="notes-tab" data-toggle="tab" aria-controls="notes" aria-expanded="false"><b>柬埔寨签证注意事项 (NEW!)</b></a></li>
                    <li role="presentation" class=""><a href="#code" role="tab" id="code-tab" data-toggle="tab" aria-controls="code" aria-expanded="false">关于</a></li>
                </ul>
                <div id="myTabContent" class="tab-content">
					TBD_PANE
					<div role="tabpanel" class="tab-pane fade" id="notes" aria-labelledby="notes-tab">
<p></p>
<center><p>这里总结了一些去柬埔寨办理美签的注意事项，签证预约时间往上看就有</p></center>
<h3>入境准备</h3>
<p>0. 签证预约位置比较紧张，最好先在国内预约好之后再过来，不然呆多久都不能确定下来</p>
<p>1. 办理柬埔寨商务签证：费用为 255 RMB（单次往返足够了，一年多次那种需要工作证明，并且柬埔寨当地可以续签），邮寄【护照、两张白底两寸彩照】到相应领事馆即可，从发出到收回大概3天时间</p>
<p>2. 办理包含新冠状病毒的商业保险（一个月有效期，从入境之日起开始算）：需要两份彩色打印的保险证明（要红章，柬埔寨政府会收走留档），费用约为 150~200 RMB</p>
<p>3. 办理国内核酸检测证明（中英文版本都要，英文版由医院出具或者可以自己找有资质的翻译机构翻译，都需要红章）：注意证件号要填写护照号而不是身份证号，并要求送检时间和入境时间间隔不超过72小时，费用约为 120-200 RMB</p>
<p>4. 准备 2000刀 的押金，入境下飞机时在海关缴纳，第 13 天二次核酸检测之后扣除大概 300刀 退还，去银行取出押金。</p>
<p>5. 建议开通国际漫游流量套餐，到柬埔寨之后可更换为当地电话卡（2刀一张卡，单月套餐约 10刀）</p>
<p>6. 国内机票去各大航空公司官网APP查询，目前厦门航空最便宜（3000~5000，其他公司大概8000，国航9000）</p>
<h3>隔离及日常生活</h3>
<p>1. 在柬埔寨境内至少需要做三次核酸检测：刚入境、到达第13天、离境。前两次核酸检测费用和集中隔离酒店1~2天的住宿费用包含在押金扣除的 300刀 中，最后一次的离境检测需要花费约 130刀</p>
<p>2. 如果入境柬埔寨航班上所有乘客在当地做第一次核酸检测结果均为阴性，那么只会被强制隔离两天，之后可以自行寻找酒店入住和自由活动（一般都是两天）</p>
<p>3. 接机服务实际上是从隔离酒店接送出来的服务，不是从机场出来的服务……</p>
<p>4. 柬埔寨当地支持瑞尔和美元的流通，1 人民币 ≈ 600 柬埔寨瑞尔，1 美元 ≈ 4100 柬埔寨瑞尔；但是一般来说比如一份快餐5刀，给两万瑞尔也是可以接受的（于是就省下了一点小钱）</p>
<p>5. 打车软件有passApp、grab、携程海外打车</p>
<p>6. 外卖软件有柬单点（国人多，可以支付宝）、foodpanda、nham24，一份饭大概5刀</p>
<p>7. 超市有永旺超市（分一期和二期）和marko，可以刷visa</p>
<p>8. 电源电压接口和国内一样；打印店挺多</p>
<p>9. 携程一晚上普通房含早餐含税一晚上大概 200 RMB，高级一点的有早餐、有厨房、冰箱和微波炉大概 450 RMB 一晚上。此外，<a href="javascript:alert(\'微信：柬埔寨北京人，18618211016\')">这个老哥</a>包了一个<!--a href="/upload/1641687707.jpg"-->酒店，里面中国留学生居多，可以抱团取暖，价格也差不多是 30 美金一天，基本不怎么挣钱……</p>
<p>10. 柬埔寨属于热带雨林气候，登革热比较严重，一定要注意防蚊，不要在大街上站太久</p>
<p>11. 在大街上走路的时候不要边走边打电话，也尽量不要背包，飞车抢夺的事情时候发生，晚上尽量不要单独出门，可结伴多人出行</p>
<h3>关于签证</h3>
<p>1. 修改CGI信息至柬埔寨：如果你的CGI Profile在国内，打 (703)665-7346之后告知护照号姓名生日，选English、Non-Immigrant、Schedule、Have DS-160转接，说要求transfer record profile to Cambodia就行，两分钟操作完成；可以参考 <a href=https://www.ustraveldocs.com/cn_zh/cn-main-contactus.asp>https://www.ustraveldocs.com/cn_zh/cn-main-contactus.asp</a> 获取更多联系方式，大概需要两个工作日转移完毕</p>
<p>2. 需要填写新的DS-160表格，选择Phnom Penh作为签证地点，并打印Payment Slip，要到金边银行柜台交钱，付款后一个工作日之后到账，可以开始预约面签时间，需要预约到入境14天之后</p>
<p>3. 签证预约选项自9月20日起区分了resident和non-resident，选后者进行预约</p>
<p>4. 签证预约费用：需要160刀，还是<a href="javascript:alert(\'微信：柬埔寨北京人，18618211016\')">上面那个包酒店的老哥</a>，额外花费 20刀 就能代缴</p>
<p>5. 美领馆需要到达柬埔寨之日起 掐头去尾14天 之后才能进入，如果时间不够的话不让你进，相当于白白浪费了一个预约</p>
<p>6. 面签完成之后7天内可以拿回护照</p>
<h3>离境或继续停留</h3>
<p>1. 离境前需要做一次核酸检测，同样要求送检时间和入境时间不超过72小时，需要到niph医院（官方指定的离境检测机构）做离境检测</p>
<p>2. 如果被check或者拒签的话，可以在柬埔寨本地先续签商务签证，选择继续等待；或者回国。需要重新预约签证位置，第二次的vo一定和第一次的不一样，拒签也是可以重新预约，但是如果预约了很多次，所有的vo都被过了一遍之后都是没有issue，那么就不能再次预约了</p>
<h3>其他</h3>
<p>一些中介比如有半包服务，大概在三四万这样，全包服务不低于五万甚至更多；但是从上面看下来其实不用花那么多钱，<b>那些钱其实是完全没有必要花费的</b>，而且万一在柬埔寨当地被check的话他们不会退钱，沉没成本较大。</p>
<p>转发请声明出处: <a href="/global/#notes">https://tuixue.online/global/#notes</a></p>
<center><h3>祝大家一路顺利！</h3></center>
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
                            <tr><td align="right">金边：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fpp"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bpp"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hpp"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="opp"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lpp"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">新加坡：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fsg"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bsg"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hsg"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="osg"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lsg"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">首尔：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fsel"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bsel"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hsel"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="osel"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lsel"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">墨尔本：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fmel"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bmel"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hmel"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="omel"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lmel"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">珀斯：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fper"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bper"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hper"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="oper"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lper"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">悉尼：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fsyd"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bsyd"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hsyd"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="osyd"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lsyd"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">伯尔尼：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fbrn"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bbrn"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hbrn"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="obrn"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lbrn"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">福冈：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ffuk"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bfuk"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hfuk"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ofuk"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lfuk"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">大阪：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fitm"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bitm"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hitm"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="oitm"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="litm"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">那霸：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="foka"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="boka"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hoka"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ooka"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="loka"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">札幌：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fcts"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bcts"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hcts"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="octs"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lcts"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">东京：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fhnd"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bhnd"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hhnd"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ohnd"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lhnd"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">加德满都：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fktm"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bktm"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hktm"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="oktm"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lktm"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">曼谷：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fbkk"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bbkk"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hbkk"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="obkk"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lbkk"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">清迈：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fcnx"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bcnx"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hcnx"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ocnx"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lcnx"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">贝尔法斯特：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fbfs"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bbfs"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hbfs"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="obfs"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lbfs"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">伦敦：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="flcy"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="blcy"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hlcy"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="olcy"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="llcy"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">卡尔加里：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fyyc"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="byyc"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hyyc"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="oyyc"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lyyc"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">哈利法克斯：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fyhz"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="byhz"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hyhz"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="oyhz"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lyhz"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">蒙特利尔：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fyul"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="byul"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hyul"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="oyul"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lyul"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">渥太华：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fyow"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="byow"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hyow"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="oyow"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lyow"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">魁北克城：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fyqb"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="byqb"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hyqb"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="oyqb"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lyqb"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">多伦多：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fyyz"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="byyz"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hyyz"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="oyyz"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lyyz"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">温哥华：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fyvr"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="byvr"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hyvr"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="oyvr"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lyvr"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">阿布扎比：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fauh"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bauh"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hauh"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="oauh"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lauh"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">迪拜：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fdxb"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bdxb"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hdxb"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="odxb"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ldxb"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">巴黎：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fcdg"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bcdg"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hcdg"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ocdg"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lcdg"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">贝尔格莱德：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fbeg"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bbeg"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hbeg"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="obeg"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lbeg"> L1/L2</label>
							</td></tr>
                            <tr><td align="right">瓜亚基尔：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fgye"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bgye"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hgye"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ogye"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lgye"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">基多：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fuio"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="buio"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="huio"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ouio"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="luio"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">华雷斯城：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fcjs"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bcjs"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hcjs"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ocjs"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lcjs"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">瓜达拉哈拉：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fgdl"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bgdl"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hgdl"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ogdl"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lgdl"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">埃莫西约：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fhmo"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bhmo"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hhmo"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ohmo"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lhmo"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">马塔莫罗斯：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fcvj"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bcvj"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hcvj"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ocvj"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lcvj"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">梅里达：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fmid"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bmid"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hmid"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="omid"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lmid"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">墨西哥城：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fmex"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bmex"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hmex"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="omex"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lmex"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">蒙特雷：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fmty"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bmty"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hmty"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="omty"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lmty"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">诺加莱斯：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fols"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bols"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hols"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ools"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lols"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">新拉雷多：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fnld"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bnld"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hnld"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="onld"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="lnld"> L1/L2</label>
                            </td></tr>
                            <tr><td align="right">蒂华纳：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ftij"> F1/J1</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="btij"> B1/B2</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="htij"> H1B</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="otij"> O1/O2/O3</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ltij"> L1/L2</label>
                            </td></tr>
							<tr><td>当出现的时间早于（并包含）该日期时发送提醒：</td><td><input class="form-control" type="date" value="" name="time"></td></tr>
							<tr><td align="right">输入以下验证码（五位小写英文字母）：</td><td><input class="form-control" type="text" value="" name="captcha" maxlength=5></td></tr>
                            </table>
                            TBD_CAPTCHA
                            <br><br><b>一般来说，每个小时的第48分会放出7-8小时前被别人退掉的名额，不是很好抢到<br>但是如果邮件推送给您的时间不是48分，多半是这个地方放了一大波名额</b><br>
                            <br>如果要取消订阅的话，全不选然后提交，再<b>重新戳确认邮件里面的链接</b>就行了。<br><br>
                            <input type="text" name="glob" style="display: none" value="1">
                            <input type="submit" value="提交" class="btn btn-info"/>
                            </center>
                    </form>
                    </div>
                </div>
            </div>
            <hr>
                    <div role="tabpanel" class="tab-pane" id="code" aria-labelledby="code-tab">
<hline>
                    项目信息：<a href="https://github.com/Trinkle23897/us-visa">GitHub 项目地址</a>，
                    <a href="https://github.com/Trinkle23897/">作者GitHub</a>，
                    <a href="https://trinkle23897.github.io/cv/">作者个人主页</a>，
                    <a href="https://www.zhihu.com/people/jiayi-weng">作者知乎主页</a>，
                    以及感谢 <a href="https://github.com/z3dd1cu5">z3dd1cu5</a> 提供的改进版爬虫！</b>
                    <br><br>
                    写这玩意还是花了一些时间的，维护也不容易（服务器要钱，验证码要钱，邮件系统是私搭的可能会被封），随喜打赏
					<br><br>
                    <center><img src="/files/pay.png" style="width: 60%"></center>
                    <!--如果您觉得 tuixue.online 很有帮助，还可以在毕业论文中加入如下致谢：（贵学术圈不都这么搞的嘛（狗头
                    <br><br>
                    <code>感谢翁家翌同学制作的 tuixue.online 网站帮助我在紧张的毕业设计过程中 [请自由发挥]。</code>
					<br><br>
                    If you find tuixue.online helpful and useful, please add the following acknowledgement in your publication:
					<br><br>
					<code>Thanks to the website tuixue.online of Mr. Jiayi Weng for [blabla] during my graduation project.</code>
                    <br><br>-->
					</div>
            <hr>
            <center><!--
                这里是广告：<br><br>
                <img src="/upload/zlr.jpg" style="align: center; width: 60%"><br><br>-->
                广告位招租，详情咨询：<a href="https://trinkle23897.github.io/">https://trinkle23897.github.io/</a><br><br>
                本网站一共见证了<span id="busuanzi_value_page_pv"></span>人次的失学。<a href="https://www.zhihu.com/question/318624725/answer/875527594">关于可怜的差点被全聚德的作者</a><br>
            </center>
            <br>
            <div id="disqus_thread"></div>
            <script async src="https://tuixue-online.disqus.com/embed.js"></script>
            <br>
    </div>
</body>
</html>';
?>
