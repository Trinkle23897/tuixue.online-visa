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
$loc = ['北京', '成都', '广州', '上海', '沈阳'];
$index = $js['index'];
echo "上一次更新时间：$t";
 ?>
	</center>
	<br>
	<center><a href="/visa2">手动刷新入口</a></center>
	<br>
	<table class="table table-hover table-striped">
		<thead>
			<tr>
				<th>更新时间</th>
<?php foreach ($loc as $name) echo "<th>$name</th>"; ?>
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
  <div class="footer-copyright text-center py-3">本网站一共见证了<span id="busuanzi_value_page_pv"></span>人次的失学。<a href="https://www.zhihu.com/question/318624725/answer/875527594">关于作者</a>
  </div>
</footer>

</html>
