<?php
header("Access-Control-Allow-Origin: *");
$t = $_GET["t"];
$s = file_get_contents('state');
if ($s == '1' and $t != '') {
	$handle = fopen('state', 'w');
	fwrite($handle, $t);
	fclose($handle);
	$s = $t;
}
 ?>
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
					预约签证的验证码，太穷买不起自动识别服务
				</h1>
	<center>
	<br>
	<div>还在尝试怎么防止被封ip中……有可能会挂</div>
	<br>
<?php
if ($s == '1') {
	echo '<img src="try.gif"><br><form action="/visa2" method="get" enctype="multipart/form-data"><table>
                <tr><td>验证码（不对也没关系，可以交一个重来）：</td><td><input type="text" name="t" class="form-control"></td></table></tr><br>
				<input type="submit" name="submit" value="提交" class="btn btn-info"/>
        </form>';
} else if ($s == '3') {
	$t = file_get_contents('next');
	echo "下一次更新时间：$t<br>";
	echo '程序正在休息中（手动设置了两次拉取时间必须是个[100, 1000]秒的随机数，防止被拟合成一个线性函数，不然有可能会被封ip）... <a href="/visa/">点击返回</a>';
} else if ($s == '2') {
	echo '正在刷新拉取数据中 ... 大概要等一两分钟 <a href="/visa/">点击返回</a>';
} else {
	echo '正在准备拉数据 ... 再等一会儿验证码窗口就出来了！<a href="/visa2/">点击刷新</a>';
}
?>
	</center>
			</div>
		</div>
	</div>

</html>
