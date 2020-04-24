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
            else if (location.hash == '#O') chartO();
            else chartF();
        }
        else chartF();
        $(document.body).on("click", "a[data-toggle]", function(event) {
            location.hash = this.getAttribute("href");
            if (location.hash == '#F') chartF();
            else if (location.hash == '#B') chartB();
            else if (location.hash == '#H') chartH();
            else if (location.hash == '#O') chartO();
        });
    });
    $(window).on('popstate', function() {
        var anchor = location.hash || $("a[data-toggle=tab]").first().attr("href");
        $('a[href=' + anchor + ']').tab('show');
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
    $table = '<center><br>“最早”指在该地预约日期24h变化中最早的一天<br>上一次更新时间：'.$t.'</center><br>';
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
                    var c = echarts.init(document.getElementById("chart"));
                    var o = {
                        title: {text: "'.substr($date, 5).' '.$type.'"},
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
    $table = $table.$script.'<div class="table-responsive"><table class="table table-hover table-striped table-bordered"><thead><tr><th>地点</th>';
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
    $table = $table."</tbody></table></div>";
    return $table;
}
?>
    <div class="container">
        <h1 class="text-center" id="title">美国签证预约时间</h1>
            <center>
                <br><a href="/visa2">爬虫当前状态</a>
                <br><br>
            </center>
            <div id='chart' style='height: 250px; width: 100%'></div>
            <center>更多图表请点击表格左侧时间</center><br>
            <div class="bs-example bs-example-tabs" data-example-id="togglable-tabs">
                <ul class="nav nav-tabs" role="tablist">
                    <li role="presentation" class=""><a href="#F" role="tab" id="F-tab" data-toggle="tab" aria-controls="F" aria-expanded="false">F1/J1签证</a></li>
                    <li role="presentation" class=""><a href="#B" role="tab" id="B-tab" data-toggle="tab" aria-controls="B" aria-expanded="false">B1/B2签证</a></li>
                    <li role="presentation" class=""><a href="#H" role="tab" id="H-tab" data-toggle="tab" aria-controls="H" aria-expanded="false">H1B签证</a></li>
                    <li role="presentation" class=""><a href="#O" role="tab" id="O-tab" data-toggle="tab" aria-controls="O" aria-expanded="false">O1/O2/O3签证</a></li>
                    <li role="presentation" class=""><a href="#email" role="tab" id="email-tab" data-toggle="tab" aria-controls="email" aria-expanded="false"><b>(New!!!)</b> 邮件订阅通知</a></li>
                    <li role="presentation" class=""><a href="#code" role="tab" id="code-tab" data-toggle="tab" aria-controls="code" aria-expanded="false">关于</a></li>
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
                    <div role="tabpanel" class="tab-pane fade" id="O" aria-labelledby="O-tab">
                        <?php echo get_table("O", "visa-o.json", ['北京', '成都', '广州', '上海', '沈阳', '香港']);?>
                    </div>
                    <div role="tabpanel" class="tab-pane fade" id="email" aria-labelledby="email-tab">
                    <br>
                    <center>每当时间变前的时候，tuixue.online就会向您发送邮件通知。<br>最好是国内邮箱比如qq（因为可以绑定微信，能第一时间看到），实测延时大概10s；国外的邮箱（比如gmail）<s>实测延迟很大...</s>好像也没延时了<br><br>
                    如果没收到确认邮件，可以翻一翻垃圾箱，并且把*@tuixue.online加入白名单中；<br>或者可以重新在这里提交一次 or 换个邮箱试试<br><br>
                    即使能正常收到也不意味着一定不会进垃圾邮箱里面，建议白名单。</center><br>
                    <form action="/asiv" method="get" enctype="multipart/form-data" id="notify-form">
                            <center>
                            <table>
                            <tr><td>邮箱地址：&nbsp;</td><td><input type="email" name="email" class="form-control" placeholder="prefer *@qq.com"></td></tr>
                            <tr><td>F1/J1：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fbj"> 北京</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fcd"> 成都</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fgz"> 广州</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fsh"> 上海</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fsy"> 沈阳</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="fhk"> 香港</label>
                            </td></tr>
                            <tr><td>B1/B2：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bbj"> 北京</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bcd"> 成都</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bgz"> 广州</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bsh"> 上海</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bsy"> 沈阳</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="bhk"> 香港</label>
                            </td></tr>
                            <tr><td>H1B：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hbj"> 北京</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hgz"> 广州</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hsh"> 上海</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="hhk"> 香港</label>
                            </td></tr>
                            <tr><td>O1/O2/O3：</td><td>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="obj"> 北京</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ocd"> 成都</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ogz"> 广州</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="osh"> 上海</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="osy"> 沈阳</label>
                                <label class="checkbox-inline"><input type="checkbox" name="visa[]" value="ohk"> 香港</label>
                            </td></tr>
                            <tr><td></td><td>如果要取消订阅的话，全不选然后提交就行了。</td></tr>
                            </table><br>
                            <input type="submit" value="提交" class="btn btn-info"/>
                            </center>
                    </form>
                    </div>
                    <div role="tabpanel" class="tab-pane fade" id="code" aria-labelledby="code-tab">
                    <br>
                    GitHub 项目地址：<a href="https://github.com/Trinkle23897/us-visa">https://github.com/Trinkle23897/us-visa</a>
                    <br><br>
                    作者GitHub：<a href="https://github.com/Trinkle23897/">https://github.com/Trinkle23897/</a>
                    <br><br>
                    作者个人主页：<a href="https://trinkle23897.github.io/cv/">https://trinkle23897.github.io/cv/</a>
                    <br><br>
                    写这玩意还是花了一些时间的，维护也不容易（服务器要钱，验证码要钱，邮件系统是私搭的可能会被封），随喜打赏
                    <center><img src="/upload/39CB3AB2-FEFD-44EC-88D3-F6C4A4C7B2B7.jpeg" style="width: 30%"><img src="/upload/F293524B-8160-4FB0-8CEE-3803ED464D4D.jpeg" style="width: 30%"></center>
					<br><br>
                    如果您觉得 tuixue.online 很有帮助，可以在毕业论文中加入如下致谢：（贵学术圈不都这么搞的嘛（狗头））
                    <br><br>
                    <code>感谢翁家翌同学制作的 tuixue.online 网站帮助我在紧张的毕业设计过程中 [请自由发挥]。</code>
					<br><br>
                    If you find tuixue.online helpful and useful, please add the below acknowledgement in your publication:
					<br><br>
					<code>Thanks to Mr. Jiayi Weng's website tuixue.online for [blabla] in my graduation project.</code>
                    <br><br>
                    </div>
                </div>
            </div>
            <center>
                广告位招租，详情咨询：<a href="https://trinkle23897.github.io/">https://trinkle23897.github.io/</a><br><br>
                本网站一共见证了<span id="busuanzi_value_page_pv"></span>人次的失学。<a href="https://www.zhihu.com/question/318624725/answer/875527594">关于可怜的差点被全聚德的作者</a><br>
            </center>
            <br>
            <div id="disqus_thread"></div>
            <script async src="https://tuixue-online.disqus.com/embed.js"></script>
            <br>
    </div>
</body>
</html>
