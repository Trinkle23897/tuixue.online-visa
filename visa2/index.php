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
$city = array('bj' => '北京', 'cd' => '成都', 'gz' => '广州', 'sh' => '上海', 'sy' => '沈阳', 'hk' => '香港', 'tp' => '台北', 'pp' => '金边', 'sg' => '新加坡', 'mel' => '墨尔本', 'per' => '珀斯', 'syd' => '悉尼', 'sel' => '首尔', 'brn' => '伯尔尼', "fuk" => "福冈", "itm" => "大坂", "oka" => "那霸", "cts" => "札幌", "hnd" => "东京", "ktm" => "加德满都", "bkk" => "曼谷", "cnx" => "清迈", 'bfs' => '贝尔法斯特', 'lcy'=> '伦敦', 'yyc'=> '卡尔加里', 'yhz'=> '哈利法克斯', 'yul'=> '蒙特利尔', 'yow'=> '渥太华', 'yqb'=> '魁北克城', 'yyz'=> '多伦多', 'yvr'=> '温哥华', 'auh'=> '阿布扎比', 'dxb'=> '迪拜', 'cdg' => '巴黎', 'beg' => '贝尔格莱德', "gye" => "瓜亚基尔", "uio" => "基多", "esb" => "安卡拉", "ist" => "伊斯坦布尔", "ath" => "雅典", 'cjs'=> '华雷斯城', 'gdl'=> '瓜达拉哈拉', 'hmo'=> '埃莫西约', 'cvj'=> '马塔莫罗斯', 'mid'=> '梅里达', 'mex'=> '墨西哥城', 'mty'=> '蒙特雷', 'ols'=> '诺加莱斯', 'nld'=> '新拉雷多', 'tij'=> '蒂华纳');
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
	<tr><th>订阅人数</th><th>F/J签</th><th>B签</th><th>H签</th><th>O签</th><th>L签</th></tr></thead><tbody>';
foreach ($city as $s => $z)
	echo '<tr><td>'.$z.'</td><td>'.get('../asiv/email/f/'.$s.'/').'</td><td>'.get('../asiv/email/b/'.$s.'/').'</td><td>'.get('../asiv/email/h/'.$s.'/').'</td><td>'.get('../asiv/email/o/'.$s.'/').'</td><td>'.get('../asiv/email/l/'.$s.'/').'</td></tr>';
echo '</tbody></table>';
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
