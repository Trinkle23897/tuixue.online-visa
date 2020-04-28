<html>
<head>
<meta http-equiv="refresh" content="10;url=/visa"/>
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
	$yy = explode('-', $tmp)[0];
	$mm = explode('-', $tmp)[1];
	$dd = explode('-', $tmp)[2];
	// echo $yy.'/'.$mm.'/'.$dd;
	if (is_numeric($yy) && is_numeric($mm) && is_numeric($dd) && $yy[0] != '-' && $mm[0] != '-' && $dd[0] != '-')
		$thres = $yy.'/'.$mm.'/'.$dd;
	else
		$thres = '';
	if (filter_var($email, FILTER_VALIDATE_EMAIL)) {
		if (file_exists('email/tmp/'.$email)) echo "之前已经发送过了，正在重新发送确认邮件中<br>";
		$result = '';
		foreach ($type as $i => $a)
			foreach ($city as $j => $b)
				if (in_array($i.$j, $t))
					$result = $result.$i.$j.',';
		$result = rtrim($result, ",");
		system("python3 ../visa2/notify.py --type test --email ".$email." --subscribe '".$result."' --time '".$thres."' 2>log", $ret);
		//echo("python3 ../visa2/notify.py --type test --email ".$email." --subscribe '".$result."' --time '".$thres."' 2>log");
		echo "<br>发送了确认邮件，请及时查收，<b>点击确认邮件中的链接之后才算正式订阅</b><br>";
	} else {
		echo "邮箱格式不合法，请仔细检查一下……？<br>";
	}
}
?>
<br>
十秒钟后自动跳转到首页......
</body></html>

