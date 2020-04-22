<html>
<head>
<meta http-equiv="refresh" content="10;url=https://tuixue.online/visa"/>
</head>
<body>
<?php
function update($email, $type, $todo) {
	$fn = 'email/'.$type.'/'.$email;
	if ($todo > -1) {
		if (file_exists($fn))
			return $email." 之前已经订阅了".$type."签证状态了<br>";
		else {
			$h = fopen($fn, 'w');
			fwrite($h, ' ');
			fclose($h);
			return $email." 刚刚成功订阅了".$type."签证状态<br>";
		}
	} else {
		if (file_exists($fn)) {
			unlink($fn);
			return $email." 刚刚成功取消订阅了".$type."签证状态<br>";
		} else return "";
	}
}	
$email = $_REQUEST['liame'];
$s = $_REQUEST['s'];
$t = '';
if (strpos($s, 'f') > -1) $t = $t.'f';
if (strpos($s, 'b') > -1) $t = $t.'b';
if (strpos($s, 'h') > -1) $t = $t.'h';
if (filter_var($email, FILTER_VALIDATE_EMAIL)) { // confirm
	if (file_exists('email/tmp/'.$email)) {
		$result = update($email, 'f', strpos($t, 'f')).update($email, 'b', strpos($t, 'b')).update($email, 'h', strpos($t, 'h'));
		if (strlen($result) > 0)
			system("python3 ../visa2/notify.py --type confirm --email ".$email." > /dev/null", $ret);
	}
	else
		$result = '不要老想着搞个大新闻！没有订阅成功，请重新在首页提交一次，或者把确认邮件转发给trinkle23897@gmail.com让他debug';
	echo $result;
} else { // test
	$email = $_REQUEST['email'];
	if (filter_var($email, FILTER_VALIDATE_EMAIL)) {
		if (file_exists($email)) echo "之前已经发送过了，正在重新发送确认邮件中<br>";
		system("python3 ../visa2/notify.py --type test --email ".$email." --subscribe '".$t."' > /dev/null", $ret);
		echo "发送了确认邮件，请及时查收，<b>点击确认邮件中的链接之后才算正式订阅</b><br>";
	} else {
		echo "邮箱格式不合法，请仔细检查一下……？<br>";
	}
}
?>
<br>
十秒钟后自动跳转到首页......
</body></html>
