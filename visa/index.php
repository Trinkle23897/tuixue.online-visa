<html>
<head>
    <title>预约美签，防止失学</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/style/bootstrap.min.css">
    <link rel="stylesheet" href="/style/bootstrap-theme.min.css">
    <script src="/style/jquery.min.js"></script>
    <script src="/style/bootstrap.min.js"></script>
    <script src="/style/echarts.min.js"></script>
    <script async src="//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
    <style type='text/css'>
    .table thead tr th { text-align: center; vertical-align: middle; }
    .table tbody tr td { text-align: center; vertical-align: middle; }
    </style>
    <script>
    $(document).ready(function() {
        if(location.hash) {
            $('a[href=' + location.hash + ']').tab('show');
            if (location.hash == '#F') chartF();
            else if (location.hash == '#B') chartB();
            else if (location.hash == '#H') chartH();
            console.log(location.hash, 'anchor');
        }
        else chartF();
        $(document.body).on("click", "a[data-toggle]", function(event) {
            location.hash = this.getAttribute("href");
        });
    });
    $(window).on('popstate', function() {
        var anchor = location.hash || $("a[data-toggle=tab]").first().attr("href");
        $('a[href=' + anchor + ']').tab('show');
        if (anchor == '#F') chartF();
        else if (anchor == '#B') chartB();
        else if (anchor == '#H') chartH();
        console.log(anchor, 'anchor');
    });
    </script>
</head>
<body>
<?php
function get_table($type, $jsfn, $loc) {
    $js = json_decode(file_get_contents($jsfn), true);
    $t = $js['time'];
    $index = $js['index'];
    $date = date("Y/m/d", time());
    $table = '<center><br>上一次更新时间：'.$t.'</center><br>';
    // chart
    $raw = [];
    $data = [];
    $x = [];
    foreach ($loc as $name) {
        $tmp = explode("\n", file_get_contents('../visa2/'.$type.'/'.$name.'/'.$date));
        $raw[$name] = [];
        foreach ($tmp as $info) {
            $tm = explode(' ', $info)[0];
            if ($tm != '') {
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
    $table = $table."";
    $mid = '';
    $full = ['北京', '成都', '广州', '上海', '沈阳', '香港'];
    foreach ($full as $name) $mid = $mid.'{name: "'.$name.'", type: "line", data: '.json_encode($data[$name]).'},'."\n";
    $script = '<script type="text/javascript">
                function chart'.$type.'() {
                    console.log(".$type.");
                    var c = echarts.init(document.getElementById("chart"));
                    var o = {
                        tooltip: {
                            trigger: "axis",
                            formatter: function(data) {
                                var result = data[0].name + "<br/>";
                                for (var i = 0, length = data.length; i < length; ++i) {
                                    result += data[i].marker + data[i].seriesName + ": " + data[i].data + "<br>";
                                }
                                return result;
                            }
                        },
                        legend: {data: '.json_encode($loc).'},
                        xAxis: {type: "category", boundaryGap: false, data: '.json_encode($x).'},
                        yAxis: {type: "time"},
                        series: ['.$mid.']
                    };
                    c.setOption(o);
                }
                </script>';
    $table = $table.$script.'<table class="table table-hover table-striped table-bordered"><thead><tr><th>地点</th>';
    foreach ($loc as $name)
        $table = $table.'<th colspan="2">'.$name.'</th>';
    $table = $table."</tr><tr><th>时间</th>";
    foreach ($loc as $name)
        $table = $table.'<th>当前</th><th>最早</th>';
    $table = $table."</tr></thead><tbody>";
    foreach ($index as $date) {
        $tmp = explode('/', $date);
        $line = "<tr><td><a href='/visa2/view/?y=".$tmp[0]."&m=".$tmp[1]."&d=".$tmp[2]."&t=".$type."'>".substr($date, 5)."</a></td>";
        $flag = false;
        foreach ($loc as $name) {
            $n = $name.'-'.$date;
            if ($js[$n] == '/') $line = $line."<td>/</td>";
            else {
                $line = $line."<td>".substr($js[$n], 5)."</td>";
                if ($js[$n] != '') $flag = true;
            }
            $n = $name.'2-'.$date;
            if ($js[$n] == '/') $line = $line."<td>/</td>";
            else {
                $line = $line."<td>".substr($js[$n], 5)."</td>";
                if ($js[$n] != '') $flag = true;
            }
        }
        $line = $line."</tr>";
        if ($flag) $table = $table.$line;

    }
    $table = $table."</tbody></table>";
    return $table;
}
?>
    <div class="container">
        <h1 class="text-center" id="title">美国签证预约时间</h1>
            <center>
                <br><a href="/visa2">爬虫当前状态</a>
                <br><br>“最早”指在该地点可以预约签证的日期，一天24h变化之中最早的一天
                <br><br>点击左侧时间可以查看预约时间变化折线图表，最下方有Disqus评论区可以玩耍（需要翻墙）
                <br><br>
            </center>
            <div id='chart' style='height: 400px; width: 100%'></div>
            <div class="bs-example bs-example-tabs" data-example-id="togglable-tabs">
                <ul class="nav nav-tabs" role="tablist">
                    <li role="presentation" class=""><a href="#F" role="tab" id="F-tab" data-toggle="tab" aria-controls="F" aria-expanded="false">F1/J1签证</a></li>
                    <li role="presentation" class=""><a href="#B" role="tab" id="B-tab" data-toggle="tab" aria-controls="B" aria-expanded="false">B1/B2签证</a></li>
                    <li role="presentation" class=""><a href="#H" role="tab" id="H-tab" data-toggle="tab" aria-controls="H" aria-expanded="false">H1B签证</a></li>
                <li role="presentation" class=""><a href="#email" role="tab" id="email-tab" data-toggle="tab" aria-controls="email" aria-expanded="false">邮件订阅通知</a></li>
                </ul>
                <div id="myTabContent" class="tab-content">
                    <div role="tabpanel" class="tab-pane fade active in" id="F" aria-labelledby="F-tab">
                        <?php echo get_table("F", "visa.json", ['北京', '成都', '广州', '上海', '沈阳', '香港']);?>
                    </div>
                    <div role="tabpanel" class="tab-pane fade" id="B" aria-labelledby="B-tab">
                        <?php echo get_table("B", "visa-b.json", ['北京', '成都', '广州', '上海', '沈阳', '香港']);?>
                    </div>
                    <div role="tabpanel" class="tab-pane fade" id="H" aria-labelledby="H-tab">
                        <?php echo get_table("H", "visa-h.json", ['北京', '广州', '上海', '香港']);?>
                    </div>
                    <div role="tabpanel" class="tab-pane fade" id="email" aria-labelledby="email-tab">
                        <center><br>还在开发中，再等等<br><br></center>
                    </div>
                </div>
            </div>
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
</body>
</html>
