
var chart;
var minute = 60000;


function drawData() {
  // will be replaced by data from the server side.

    $.ajax({
        type: "POST",
        url: "http://0.0.0.0:6543/es",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: '{"query": {"match_all": {}}}',
        success: function(json) {
            console.log(json.hits.hits);
        },
        error: function (xhr, textStatus, errorThrown) {
            alert(xhr.responseText);
        }
    });


  var time = (new Date()).getTime();
  var i, x, y;
  var series = chart.series[0];

  for (i = -19; i <= 0; i++) {
    x = time + (i * minute);
    y = Math.random();
    series.addPoint([x, y]);
  }
}


function initChart() {

  Highcharts.setOptions({
      global: {
        useUTC: false
      }
  });
  chart = new Highcharts.Chart({
    chart: {
        renderTo: 'container',
        type: 'spline',
        marginRight: 10,
    },
    title: {
        text: 'Time series'
    },
    xAxis: {
        type: 'datetime',
        tickPixelInterval: 150
    },
    yAxis: {
        title: {
            text: 'Value'
        },
        plotLines: [{
            value: 0,
            width: 1,
            color: '#808080'
        }]
    },
    tooltip: {
     formatter: function() {
       return '<b>'+ this.series.name +'</b><br/>'+
       Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) +'<br/>'+
       Highcharts.numberFormat(this.y, 2);
     }
    },
    legend: {
        enabled: false
    },
    exporting: {
        enabled: false
    },
    series: [{
        name: 'Random data',
        data: (function() {return [];})()
    }]
  });
}
