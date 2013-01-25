
var chart;
var minute = 60000;

function drawDataRange(from, size) {
   chart.showLoading();
   var i, x, y;
   var downloads_series = chart.series[0];
   var users_series = chart.series[1];

   var query = {"query": {"match_all": {}},
                "from": from, 
                "size": size,
                 "sort": [{"date": {"order" : "asc"}}]
                };

    query = JSON.stringify(query);

    $.ajax({
        type: "POST",
        url: "http://0.0.0.0:6543/es",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        processData: false,
        dataType: "json",
        data: query,
        success: function(json) {
          var downloads = [];
          var users = [];
          $.each(json.hits.hits, function(i, item) {
             downloads.push({x: Date.parse(item._source.date), y: item._source.downloads_count});
             users.push({x: Date.parse(item._source.date), y: item._source.users_count});
           });

          downloads_series.setData(downloads);
          users_series.setData(users);
          chart.redraw();
        },
        error: function (xhr, textStatus, errorThrown) {
            alert(xhr.responseText);
        },
        failure: function(errMsg) {
            alert(errMsg);
        }
    });
    chart.hideLoading();
}


function drawData() {
   // last 30 days
  var batch = 30;
  var from = 0;
  drawDataRange(from, batch);
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
        renderer: 'SVG'
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
       Highcharts.dateFormat('%Y-%m-%dT%H:%M:%S', this.x) +'<br/>'+
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
        name: 'Downloads',
        data: (function() {return [];})()
    },{
        name: 'Daily users',
        data: (function() {return [];})()
    }]
  });
}
