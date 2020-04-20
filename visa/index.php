<html>
<head>
	<title>预约美签，防止失学</title>
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="stylesheet" href="/style/bootstrap.min.css">
	<link rel="stylesheet" href="/style/bootstrap-theme.min.css">
	<script src="/style/jquery.min.js"></script>
	<script src="/style/bootstrap.min.js"></script>
	<script async src="//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
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
					美国F/J签证预约时间
				</h1>
	<center>
	<br>
<?php
$js = json_decode(file_get_contents("visa.json"), true);
$t = $js['time'];
$loc = ['北京', '北京2', '成都', '成都2', '广州', '广州2', '上海', '上海2', '沈阳', '沈阳2'];
$index = $js['index'];
echo "上一次更新时间：$t";
 ?>
	</center>
	<br><center><a href="/visa2">手动刷新入口</a></center>
	<br><center>“最早”指在该地点可以预约签证的日期，一天24h变化之中最早的一天</center>
	<br><center>点击左侧时间可以查看预约时间变化折线图表，<b>最下方有Disqus评论区可以玩耍（需要翻墙）</b></center><br>
	<table class="table table-hover table-striped table-bordered">
		<thead>
  <tr>
    <th>地点</th>
    <th colspan="2">北京</th>
    <th colspan="2">成都</th>
    <th colspan="2">广州</th>
    <th colspan="2">上海</th>
    <th colspan="2">沈阳</th>
  </tr>
  <tr>
    <th>时间</th>
    <th>当前</th>
    <th>最早</th>
    <th>当前</th>
    <th>最早</th>
    <th>当前</th>
    <th>最早</th>
    <th>当前</th>
    <th>最早</th>
    <th>当前</th>
    <th>最早</th>
  </tr>
		</thead>
		<tbody>
<?php
foreach ($index as $date) {
	$tmp = explode('/', $date);
	echo "<tr><td><a href='/visa2/view/?y=".$tmp[0]."&m=".$tmp[1]."&d=".$tmp[2]."'>".substr($date, 5)."</a></td>";
	foreach ($loc as $name) {
		$n = $name.'-'.$date;
		if ($js[$n] == '/') echo "<td>/</td>";
		else echo "<td>".substr($js[$n], 5)."</td>";
	}
	echo "</tr>\n";
}
?>
		</tbody>
	</table>
<center>
广告位招租，详情咨询：<a href="https://trinkle23897.github.io/">https://trinkle23897.github.io/</a><br><br>
  本网站一共见证了<span id="busuanzi_value_page_pv"></span>人次的失学。<a href="https://www.zhihu.com/question/318624725/answer/875527594">关于可怜的差点被全聚德的作者</a><br>
</center>
<br>
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
