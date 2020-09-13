<html>
<head>
    <title>预约美签，防止失学</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap-theme.min.css" rel="stylesheet">
    <script src="https://cdn.bootcdn.net/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
    <script src="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@4.7.0/dist/echarts.min.js"></script>
    <script async src="//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
    <style type='text/css'>
        .table thead tr th { text-align: center; vertical-align: middle; }
        .table tbody tr td { text-align: center; vertical-align: middle; }
    </style>
    <!--<script data-ad-client="ca-pub-5419513334556516" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>-->
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'UA-102409527-2');
    </script>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="span12">
                <center>
                <h1 class="text-center" id="title">预约时间变化单日统计图</h1><br><br><br><br><br><br>
<!--				看情况是每个小时的01/11/21/31/41/51分钟放出来名额<br><br>-->
<?php
$y = $_GET['y'];
$m = $_GET['m'];
$d = $_GET['d'];
$type = $_GET['t'];
if (is_numeric($y) && is_numeric($m) && is_numeric($d))
    $date = $y.'/'.$m.'/'.$d;
else
    $date = date("Y/m/d", time());
if ($type == 'J') $type = 'F';
else if ($type != 'F' && $type != 'B' && $type != 'H' && $type != 'O' && $type != 'L')
    $type = 'F';
$loc = ["Belfast", "London", "Calgary", "Halifax", "Montreal", "Ottawa", "Quebec City", "Toronto", "Vancouver", "Abu Dhabi", "Dubai", "Paris", "Belgrade", "Guayaquil", "Quito", "Ciudad Juarez", "Guadalajara", "Hermosillo", "Matamoros", "Merida", "Mexico City", "Monterrey", "Nogales", "Nuevo Laredo", "Tijuana"];
$raw = [];
$data = [];
$x = [];
function check($a, $b) {
	if (explode('/', $a)[0] != explode('/', $b)[0])
		return explode('/', $a)[0] > explode('/', $b)[0];
	if (explode('/', $a)[1] != explode('/', $b)[1])
		return explode('/', $a)[1] > explode('/', $b)[1];
	if (explode('/', $a)[2] != explode('/', $b)[2])
		return explode('/', $a)[2] > explode('/', $b)[2];
	return false;
}
foreach ($loc as $name) {
    $tmp = explode("\n", file_get_contents('../'.$type.'/'.$name.'/'.$date));
    $raw[$name] = [];
    foreach ($tmp as $info) {
        $tm = explode(' ', $info)[0];
        if ($tm != '') {
			// $raw[$name][$tm] = explode(' ', $info)[1];
			if ($raw[$name][$tm] == null || check($raw[$name][$tm], explode(' ', $info)[1]))
				$raw[$name][$tm] = explode(' ', $info)[1];
            if (!in_array($tm, $x)) array_push($x, $tm);
        }
    }
}
sort($x);
$n = count($x);
foreach ($loc as $name) {
    $data[$name] = [];
    for ($i = 0; $i < $n; ++$i) $data[$name][$i] = $raw[$name][$x[$i]];
    for ($i = $n - 1; $i >= 0; --$i) {
        $j = $raw[$name][$x[$i]];
        if ($j == null && $i > 0)
            $j = $data[$name][$i - 1];
        $data[$name][$i] = $j;
    }
}
$show_tp = $type;
if ($type == 'F') $show_tp = 'F/J';
 ?>
                <div id="chart" style="height: 400px; width: '100%'"></div>
                <script type="text/javascript">
                    var c = echarts.init(document.getElementById('chart'));
                    var o = {
                        title: {text: "<?php echo substr($date, 5).' '.$show_tp ?>"},
                        tooltip: {
                            trigger: 'axis',
                            formatter: function(data) {
                                var result = data[0].name + '<br/>';
                                for (var i = 0, length = data.length; i < length; ++i) {
                                    result += data[i].marker + data[i].seriesName + ': ' + data[i].data + '<br>';
                                }
                                return result;
                            }
                        },
                        legend: {data: <?php echo json_encode($loc); ?>},
                        xAxis: {type: 'category', boundaryGap: false, data: <?php echo json_encode($x); ?>},
                        yAxis: {type: 'time'},
    dataZoom: [{
        type: 'slider',
        height: 8,
        bottom: 20,
        borderColor: 'transparent',
        backgroundColor: '#e2e2e2',
        handleIcon: 'M10.7,11.9H9.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4h1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7v-1.2h6.6z M13.3,22H6.7v-1.2h6.6z M13.3,19.6H6.7v-1.2h6.6z', // jshint ignore:line
        handleSize: 20,
        handleStyle: {
            shadowBlur: 6,
            shadowOffsetX: 1,
            shadowOffsetY: 2,
            shadowColor: '#aaa'
        }
    }, {
        type: 'inside'
    }],
                        series: [
<?php foreach ($loc as $name) echo '{name: "'.$name.'", type: "line", data: '.json_encode($data[$name]).'},'."\n";?>
                        ]
                    };
                    c.setOption(o);
                </script>
<?php
$d = new Datetime($date);
$pre = explode('/', $d->modify("-1 day")->format("Y/m/d"));
echo '<a class="btn btn-info" role="button" href="?y='.$pre[0].'&m='.$pre[1].'&d='.$pre[2].'&t='.$type.'">前一天</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';
echo '<a class="btn btn-info" role="button" href="/global/#'.$type.'ais">返回首页</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';
$nxt = explode('/', $d->modify("+2 day")->format("Y/m/d"));
echo '<a class="btn btn-info" role="button" href="?y='.$nxt[0].'&m='.$nxt[1].'&d='.$nxt[2].'&t='.$type.'">后一天</a>';
?>
                <br><br>广告位招租，详情咨询：<a href="https://trinkle23897.github.io/">https://trinkle23897.github.io/</a><br>
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
            </div>
        </div>
    </div>
    <br>
</body>
</html>

