<html>
<head>
    <title>预约美签，防止失学</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap-theme.min.css" rel="stylesheet">
	<script src="https://cdn.bootcdn.net/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
    <script src="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <script async src="//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
    <!--<script data-ad-client="ca-pub-5419513334556516" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>-->
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'UA-102409527-2');
    </script>
    <style type='text/css'>
    .table thead tr th { text-align: center; vertical-align: middle; }
    .table tbody tr td { text-align: center; vertical-align: middle; }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="span12">
                <h1 class="text-center" id="title">
                    系统当前状态
                </h1>
    <center>
    <br>
    （如果看到它连续两个小时没刷新的话，或者有新的Feature Request，可以去<a href="https://github.com/Trinkle23897/us-visa">GitHub</a>上提issue）
    <br>
    <br>
<?php
function get($dir) {
    $src = opendir($dir);
    $cnt = 0;
    while ($val = readdir($src)) {
        if ($val[0] == '.' || $val[0] == '_') continue;
        $cnt += 1;
	}
	if ($cnt == 0) $cnt = '/';
	return $cnt;
}
echo "爬虫策略：48分-50分每5秒更新一次，其余时间每分钟更新一次<br>通知策略（按照先后顺序）：刷新网页，邮件，TG频道，QQ1234群
	<br>爬虫当前状态：".file_get_contents('state').'，<a href="/visa">点击返回</a><br><br>';
echo '<table class="table table-hover table-striped table-bordered"><thead>
	<tr><th>签证类型</th><th>更新时间</th><th>更新频率</th></tr></thead><tbody>
    <tr><td>F1/J1</td><td>'.json_decode(file_get_contents('../visa/visa.json'), true)['time'].'</td><td>60s</td></tr>
    <tr><td>B1/B2</td><td>'.json_decode(file_get_contents('../visa/visa-b.json'), true)['time'].'</td><td>120s</td></tr>
    <tr><td>H1B</td><td>'.json_decode(file_get_contents('../visa/visa-h.json'), true)['time'].'</td><td>180s</td></tr>
    <tr><td>O1/O2/O3</td><td>'.json_decode(file_get_contents('../visa/visa-o.json'), true)['time'].'</td><td>180s</td></tr>
    <tr><td>L1/L2</td><td>'.json_decode(file_get_contents('../visa/visa-l.json'), true)['time'].'</td><td>180s</td></tr></tbody></table><br>';
echo '<table class="table table-hover table-striped table-bordered"><thead>
	<tr><th>订阅人数</th><th>F/J签</th><th>B签</th><th>H签</th><th>O签</th><th>L签</th></tr></thead><tbody>
<tr><td>北京</td><td>'.get('../asiv/email/f/bj/').'</td><td>'.get('../asiv/email/b/bj/').'</td><td>'.get('../asiv/email/h/bj/').'</td><td>'.get('../asiv/email/o/bj/').'</td><td>'.get('../asiv/email/l/bj/').'</td></tr>
<tr><td>成都</td><td>'.get('../asiv/email/f/cd/').'</td><td>'.get('../asiv/email/b/cd/').'</td><td>'.get('../asiv/email/h/cd/').'</td><td>'.get('../asiv/email/o/cd/').'</td><td>'.get('../asiv/email/l/cd/').'</td></tr>
<tr><td>广州</td><td>'.get('../asiv/email/f/gz/').'</td><td>'.get('../asiv/email/b/gz/').'</td><td>'.get('../asiv/email/h/gz/').'</td><td>'.get('../asiv/email/o/gz/').'</td><td>'.get('../asiv/email/l/gz/').'</td></tr>
<tr><td>上海</td><td>'.get('../asiv/email/f/sh/').'</td><td>'.get('../asiv/email/b/sh/').'</td><td>'.get('../asiv/email/h/sh/').'</td><td>'.get('../asiv/email/o/sh/').'</td><td>'.get('../asiv/email/l/sh/').'</td></tr>
<tr><td>沈阳</td><td>'.get('../asiv/email/f/sy/').'</td><td>'.get('../asiv/email/b/sy/').'</td><td>'.get('../asiv/email/h/sy/').'</td><td>'.get('../asiv/email/o/sy/').'</td><td>'.get('../asiv/email/l/sy/').'</td></tr>
<tr><td>香港</td><td>'.get('../asiv/email/f/hk/').'</td><td>'.get('../asiv/email/b/hk/').'</td><td>'.get('../asiv/email/h/hk/').'</td><td>'.get('../asiv/email/o/hk/').'</td><td>'.get('../asiv/email/l/hk/').'</td></tr>
<tr><td>台北</td><td>'.get('../asiv/email/f/tp/').'</td><td>'.get('../asiv/email/b/tp/').'</td><td>'.get('../asiv/email/h/tp/').'</td><td>'.get('../asiv/email/o/tp/').'</td><td>'.get('../asiv/email/l/tp/').'</td></tr>
<tr><td>金边</td><td>'.get('../asiv/email/f/pp/').'</td><td>'.get('../asiv/email/b/pp/').'</td><td>'.get('../asiv/email/h/pp/').'</td><td>'.get('../asiv/email/o/pp/').'</td><td>'.get('../asiv/email/l/pp/').'</td></tr>
<tr><td>新加坡</td><td>'.get('../asiv/email/f/sg/').'</td><td>'.get('../asiv/email/b/sg/').'</td><td>'.get('../asiv/email/h/sg/').'</td><td>'.get('../asiv/email/o/sg/').'</td><td>'.get('../asiv/email/l/sg/').'</td></tr>
<tr><td>首尔</td><td>'.get('../asiv/email/f/sel/').'</td><td>'.get('../asiv/email/b/sel/').'</td><td>'.get('../asiv/email/h/sel/').'</td><td>'.get('../asiv/email/o/sel/').'</td><td>'.get('../asiv/email/l/sel/').'</td></tr>
<tr><td>墨尔本</td><td>'.get('../asiv/email/f/mel/').'</td><td>'.get('../asiv/email/b/mel/').'</td><td>'.get('../asiv/email/h/mel/').'</td><td>'.get('../asiv/email/o/mel/').'</td><td>'.get('../asiv/email/l/mel/').'</td></tr>
<tr><td>珀斯</td><td>'.get('../asiv/email/f/per/').'</td><td>'.get('../asiv/email/b/per/').'</td><td>'.get('../asiv/email/h/per/').'</td><td>'.get('../asiv/email/o/per/').'</td><td>'.get('../asiv/email/l/per/').'</td></tr>
<tr><td>悉尼</td><td>'.get('../asiv/email/f/syd/').'</td><td>'.get('../asiv/email/b/syd/').'</td><td>'.get('../asiv/email/h/syd/').'</td><td>'.get('../asiv/email/o/syd/').'</td><td>'.get('../asiv/email/l/syd/').'</td></tr>
<tr><td>伯尔尼</td><td>'.get('../asiv/email/f/brn/').'</td><td>'.get('../asiv/email/b/brn/').'</td><td>'.get('../asiv/email/h/brn/').'</td><td>'.get('../asiv/email/o/brn/').'</td><td>'.get('../asiv/email/l/brn/').'</td></tr>
<tr><td>福冈</td><td>'.get('../asiv/email/f/fuk/').'</td><td>'.get('../asiv/email/b/fuk/').'</td><td>'.get('../asiv/email/h/fuk/').'</td><td>'.get('../asiv/email/o/fuk/').'</td><td>'.get('../asiv/email/l/fuk/').'</td></tr>
<tr><td>大阪</td><td>'.get('../asiv/email/f/itm/').'</td><td>'.get('../asiv/email/b/itm/').'</td><td>'.get('../asiv/email/h/itm/').'</td><td>'.get('../asiv/email/o/itm/').'</td><td>'.get('../asiv/email/l/itm/').'</td></tr>
<tr><td>那霸</td><td>'.get('../asiv/email/f/oka/').'</td><td>'.get('../asiv/email/b/oka/').'</td><td>'.get('../asiv/email/h/oka/').'</td><td>'.get('../asiv/email/o/oka/').'</td><td>'.get('../asiv/email/l/oka/').'</td></tr>
<tr><td>札幌</td><td>'.get('../asiv/email/f/cts/').'</td><td>'.get('../asiv/email/b/cts/').'</td><td>'.get('../asiv/email/h/cts/').'</td><td>'.get('../asiv/email/o/cts/').'</td><td>'.get('../asiv/email/l/cts/').'</td></tr>
<tr><td>东京</td><td>'.get('../asiv/email/f/hnd/').'</td><td>'.get('../asiv/email/b/hnd/').'</td><td>'.get('../asiv/email/h/hnd/').'</td><td>'.get('../asiv/email/o/hnd/').'</td><td>'.get('../asiv/email/l/hnd/').'</td></tr>
<tr><td>加德满都</td><td>'.get('../asiv/email/f/ktm/').'</td><td>'.get('../asiv/email/b/ktm/').'</td><td>'.get('../asiv/email/h/ktm/').'</td><td>'.get('../asiv/email/o/ktm/').'</td><td>'.get('../asiv/email/l/ktm/').'</td></tr>
<tr><td>贝尔法斯特</td><td>'.get('../asiv/email/f/bfs/').'</td><td>'.get('../asiv/email/b/bfs/').'</td><td>'.get('../asiv/email/h/bfs/').'</td><td>'.get('../asiv/email/o/bfs/').'</td><td>'.get('../asiv/email/l/bfs/').'</td></tr>
<tr><td>伦敦</td><td>'.get('../asiv/email/f/lcy/').'</td><td>'.get('../asiv/email/b/lcy/').'</td><td>'.get('../asiv/email/h/lcy/').'</td><td>'.get('../asiv/email/o/lcy/').'</td><td>'.get('../asiv/email/l/lcy/').'</td></tr>
<tr><td>卡尔加里</td><td>'.get('../asiv/email/f/yyc/').'</td><td>'.get('../asiv/email/b/yyc/').'</td><td>'.get('../asiv/email/h/yyc/').'</td><td>'.get('../asiv/email/o/yyc/').'</td><td>'.get('../asiv/email/l/yyc/').'</td></tr>
<tr><td>哈利法克斯</td><td>'.get('../asiv/email/f/yhz/').'</td><td>'.get('../asiv/email/b/yhz/').'</td><td>'.get('../asiv/email/h/yhz/').'</td><td>'.get('../asiv/email/o/yhz/').'</td><td>'.get('../asiv/email/l/yhz/').'</td></tr>
<tr><td>蒙特利尔</td><td>'.get('../asiv/email/f/yul/').'</td><td>'.get('../asiv/email/b/yul/').'</td><td>'.get('../asiv/email/h/yul/').'</td><td>'.get('../asiv/email/o/yul/').'</td><td>'.get('../asiv/email/l/yul/').'</td></tr>
<tr><td>渥太华</td><td>'.get('../asiv/email/f/yow/').'</td><td>'.get('../asiv/email/b/yow/').'</td><td>'.get('../asiv/email/h/yow/').'</td><td>'.get('../asiv/email/o/yow/').'</td><td>'.get('../asiv/email/l/yow/').'</td></tr>
<tr><td>魁北克城</td><td>'.get('../asiv/email/f/yqb/').'</td><td>'.get('../asiv/email/b/yqb/').'</td><td>'.get('../asiv/email/h/yqb/').'</td><td>'.get('../asiv/email/o/yqb/').'</td><td>'.get('../asiv/email/l/yqb/').'</td></tr>
<tr><td>多伦多</td><td>'.get('../asiv/email/f/yyz/').'</td><td>'.get('../asiv/email/b/yyz/').'</td><td>'.get('../asiv/email/h/yyz/').'</td><td>'.get('../asiv/email/o/yyz/').'</td><td>'.get('../asiv/email/l/yyz/').'</td></tr>
<tr><td>温哥华</td><td>'.get('../asiv/email/f/yvr/').'</td><td>'.get('../asiv/email/b/yvr/').'</td><td>'.get('../asiv/email/h/yvr/').'</td><td>'.get('../asiv/email/o/yvr/').'</td><td>'.get('../asiv/email/l/yvr/').'</td></tr>
<tr><td>阿布扎比</td><td>'.get('../asiv/email/f/auh/').'</td><td>'.get('../asiv/email/b/auh/').'</td><td>'.get('../asiv/email/h/auh/').'</td><td>'.get('../asiv/email/o/auh/').'</td><td>'.get('../asiv/email/l/auh/').'</td></tr>
<tr><td>迪拜</td><td>'.get('../asiv/email/f/dxb/').'</td><td>'.get('../asiv/email/b/dxb/').'</td><td>'.get('../asiv/email/h/dxb/').'</td><td>'.get('../asiv/email/o/dxb/').'</td><td>'.get('../asiv/email/l/dxb/').'</td></tr>
<tr><td>巴黎</td><td>'.get('../asiv/email/f/cdg/').'</td><td>'.get('../asiv/email/b/cdg/').'</td><td>'.get('../asiv/email/h/cdg/').'</td><td>'.get('../asiv/email/o/cdg/').'</td><td>'.get('../asiv/email/l/cdg/').'</td></tr>
<tr><td>贝尔格莱德</td><td>'.get('../asiv/email/f/beg/').'</td><td>'.get('../asiv/email/b/beg/').'</td><td>'.get('../asiv/email/h/beg/').'</td><td>'.get('../asiv/email/o/beg/').'</td><td>'.get('../asiv/email/l/beg/').'</td></tr>
<tr><td>华雷斯城</td><td>'.get('../asiv/email/f/cjs/').'</td><td>'.get('../asiv/email/b/cjs/').'</td><td>'.get('../asiv/email/h/cjs/').'</td><td>'.get('../asiv/email/o/cjs/').'</td><td>'.get('../asiv/email/l/cjs/').'</td></tr>
<tr><td>瓜达拉哈拉</td><td>'.get('../asiv/email/f/gdl/').'</td><td>'.get('../asiv/email/b/gdl/').'</td><td>'.get('../asiv/email/h/gdl/').'</td><td>'.get('../asiv/email/o/gdl/').'</td><td>'.get('../asiv/email/l/gdl/').'</td></tr>
<tr><td>埃莫西约</td><td>'.get('../asiv/email/f/hmo/').'</td><td>'.get('../asiv/email/b/hmo/').'</td><td>'.get('../asiv/email/h/hmo/').'</td><td>'.get('../asiv/email/o/hmo/').'</td><td>'.get('../asiv/email/l/hmo/').'</td></tr>
<tr><td>马塔莫罗斯</td><td>'.get('../asiv/email/f/cvj/').'</td><td>'.get('../asiv/email/b/cvj/').'</td><td>'.get('../asiv/email/h/cvj/').'</td><td>'.get('../asiv/email/o/cvj/').'</td><td>'.get('../asiv/email/l/cvj/').'</td></tr>
<tr><td>梅里达</td><td>'.get('../asiv/email/f/mid/').'</td><td>'.get('../asiv/email/b/mid/').'</td><td>'.get('../asiv/email/h/mid/').'</td><td>'.get('../asiv/email/o/mid/').'</td><td>'.get('../asiv/email/l/mid/').'</td></tr>
<tr><td>墨西哥城</td><td>'.get('../asiv/email/f/mex/').'</td><td>'.get('../asiv/email/b/mex/').'</td><td>'.get('../asiv/email/h/mex/').'</td><td>'.get('../asiv/email/o/mex/').'</td><td>'.get('../asiv/email/l/mex/').'</td></tr>
<tr><td>蒙特雷</td><td>'.get('../asiv/email/f/mty/').'</td><td>'.get('../asiv/email/b/mty/').'</td><td>'.get('../asiv/email/h/mty/').'</td><td>'.get('../asiv/email/o/mty/').'</td><td>'.get('../asiv/email/l/mty/').'</td></tr>
<tr><td>诺加莱斯</td><td>'.get('../asiv/email/f/ols/').'</td><td>'.get('../asiv/email/b/ols/').'</td><td>'.get('../asiv/email/h/ols/').'</td><td>'.get('../asiv/email/o/ols/').'</td><td>'.get('../asiv/email/l/ols/').'</td></tr>
<tr><td>新拉雷多</td><td>'.get('../asiv/email/f/nld/').'</td><td>'.get('../asiv/email/b/nld/').'</td><td>'.get('../asiv/email/h/nld/').'</td><td>'.get('../asiv/email/o/nld/').'</td><td>'.get('../asiv/email/l/nld/').'</td></tr>
<tr><td>蒂华纳</td><td>'.get('../asiv/email/f/tij/').'</td><td>'.get('../asiv/email/b/tij/').'</td><td>'.get('../asiv/email/h/tij/').'</td><td>'.get('../asiv/email/o/tij/').'</td><td>'.get('../asiv/email/l/tij/').'</td></tr>
</tbody></table>
	';
?>
<h1 class="text-center">爬本站的建议</h1>
<center><br>其实没必要一直爬<code>/visa/</code>那个页面，研究研究代码会发现json格式存储的结果位于这五个url里面：<a href="https://tuixue.online/visa/visa.json">F签</a>，<a href="https://tuixue.online/visa/visa-b.json">B签</a>，<a href="https://tuixue.online/visa/visa-h.json">H签</a>，<a href="https://tuixue.online/visa/visa-o.json">O签</a>，<a href="https://tuixue.online/visa/visa-l.json">L签</a>，这可以随便爬而且还好爬...<br>（本站目前没有任何反爬措施，请各位大哥大姐下手轻点...）<br><br>
</center>


广告位招租，详情咨询：<a href="https://trinkle23897.github.io/">https://trinkle23897.github.io/</a><br><br>
    </center>
<div id="disqus_thread"></div>
<script>
(function() { // DON'T EDIT BELOW THIS LINE
var d = document, s = d.createElement('script');
s.src = 'https://tuixue-online.disqus.com/embed.js';
s.setAttribute('data-timestamp', +new Date());
(d.head || d.body).appendChild(s);
})();
</script>
<noscript>Please enable JavaScript to view the <a href="https://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
<br>
            </div>
        </div>
    </div>

</html>
