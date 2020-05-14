<html>
<head>
<meta http-equiv="refresh" content="10;url=/visa"/>
<script async src="//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'UA-102409527-2');
    </script>
</head>
<body>
<?php
function update_status($type, $city, $email, $todo, $out) {
	$fn = 'email/'.$type.'/'.$city.'/'.$email;
	if ($todo) {
		if (file_exists($fn))
			return $email." 之前已经订阅了".$out."状态了<br>";
		else {
			$h = fopen($fn, 'w');
			fwrite($h, ' ');
			fclose($h);
			return $email." 刚刚成功订阅了".$out."状态<br>";
		}
	} else {
		if (file_exists($fn)) {
			unlink($fn);
			return $email." 刚刚成功取消订阅了".$out."状态<br>";
		} else return "";
	}
}
function check($c, $o) {
	if (!file_exists('../'.$o))
		return false;
	if (strlen($c) != 5)
		return false;
	for ($i = 0; $i < 5; ++$i) {
		if (strpos("abcdfhijklmnopqrstuvwxy", $c[$i]) === false)
			return false;
	}
	return true;
}
function save($c, $o) {
	if (!file_exists('../'.$o))
		return;
	$g = explode('/', $o)[3];
	if ($c.'.gif' != $g) {
		$h = fopen('email/log', 'a');
		fwrite($h, $c.' '.$o."\n");
		fclose($h);
	}
}
$email = $_REQUEST['liame'];
$t = $_REQUEST['visa'];
$type = array('f' => 'F1/J1签证', 'b' => 'B1/B2签证', 'h' => 'H1B签证', 'o' => 'O1/O2/O3签证', 'l' => 'L1/L2签证');
$city = array('bj' => '北京', 'cd' => '成都', 'gz' => '广州', 'sh' => '上海', 'sy' => '沈阳', 'hk' => '香港');
if (strlen($_REQUEST['s']) > 0) {
	echo "旧的链接已失效，请在首页重新提交一份订阅请求。";
}
else if (filter_var($email, FILTER_VALIDATE_EMAIL)) { // confirm
	if (file_exists('email/tmp/'.$email)) {
		$result = '';
		foreach ($type as $i => $a)
			foreach ($city as $j => $b)
				$result = $result.update_status($i, $j, $email, in_array($i.$j, $t), $b.$a);
		if (strlen($result) > 0)
			system("python3 ../visa2/notify.py --type confirm --email ".$email." > /dev/null", $ret);
	}
	else
		$result = '不要老想着搞个大新闻！没有订阅成功，请重新在首页提交一次，或者把确认邮件转发给 <a href="mailto:trinkle23897@gmail.com">trinkle23897@gmail.com</a> 让他debug';
	echo $result;
} else { // test
	$email = $_REQUEST['email'];
	$tmp = $_REQUEST['time'];
	$captcha = $_REQUEST['captcha'];
	$orig = base64_decode($_REQUEST['orig']);
	$yy = explode('-', $tmp)[0];
	$mm = explode('-', $tmp)[1];
	$dd = explode('-', $tmp)[2];
	// echo $yy.'/'.$mm.'/'.$dd;
	if (is_numeric($yy) && is_numeric($mm) && is_numeric($dd) && $yy[0] != '-' && $mm[0] != '-' && $dd[0] != '-')
		$thres = $yy.'/'.$mm.'/'.$dd;
	else
		$thres = '';
	if (check($captcha, $orig)) {
		save($captcha, $orig);
		if (filter_var($email, FILTER_VALIDATE_EMAIL)) {
			if (file_exists('email/tmp/'.$email)) echo "之前已经发送过了，正在重新发送确认邮件中<br>";
			echo "您选择的订阅日期是：";
			if ($thres == '') echo '9999/12/31';
			else echo $thres;
			echo ' 及之前<br><br>';
			$result = '';
			foreach ($type as $i => $a)
				foreach ($city as $j => $b)
					if (in_array($i.$j, $t))
						$result = $result.$i.$j.',';
			$result = rtrim($result, ",");
			echo "发送确认邮件状态（空为没发出去）：";
			system("python3 ../visa2/notify.py --type test --email ".$email." --subscribe '".$result."' --time '".$thres."' 2>log", $ret);
			//echo("python3 ../visa2/notify.py --type test --email ".$email." --subscribe '".$result."' --time '".$thres."' 2>log");
			echo "<br>发送了确认邮件，请及时查收，<b>点击确认邮件中的链接之后才算正式订阅</b><br>";
		} else {
			echo "邮箱格式不合法，请仔细检查一下……？<br>";
		}
	} else {
		echo "验证码错误（五位纯英文小写字母，不含字母e/g/z），请重新提交<br>";
	}
}
?>
<br>
<a href="https://tuixue.online/visa2/">https://tuixue.online/visa2/</a> 里面展示了各个地区、各个签证类型的订阅情况
<br>
十秒钟后自动跳转到首页......
</body></html>

