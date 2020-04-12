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
	.table thead tr th { text-align: center; }
	.table tbody tr td { text-align: center; }
    </style>
</head>
<body>
	<div class="container">
		<div class="row">
			<div class="span12">
				<h1 class="text-center" id="title">
					F/J签最早预约时间
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
	<br>
	<center><a href="/visa2">手动刷新入口</a></center>
	<br>
<!--	<center>源代码在<a href="https://github.com/Trinkle23897/us-visa">GitHub</a>上，如果看到它挂了可以提issue……</center><br>-->
	<table class="table table-hover table-striped">
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
	echo "<tr><td>$date</td>";
	foreach ($loc as $name) {
		$n = $name.'-'.$date;
		echo "<td>$js[$n]</td>";
	}
	echo "</tr>\n";
}
?>
		</tbody>
	</table>
			</div>
		</div>
	</div>
<footer class="page-footer font-small blue pt-4">
  <div class="footer-copyright text-center py-3">本网站一共见证了<span id="busuanzi_value_page_pv"></span>人次的失学。<a href="https://www.zhihu.com/question/318624725/answer/875527594">关于可怜的差点被全聚德的作者</a>
  </div>
</footer>

</html>
