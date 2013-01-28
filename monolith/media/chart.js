
var minute = 60000;

Highcharts.setOptions({
    global: {
        useUTC: false
    }
});

$.Class("Monolith", 
    {},
    {
    init: function(server, start_date, end_date, container){
        $.datepicker.setDefaults({dateFormat: 'yy-mm-dd'});
        $("#startdate").datepicker();
        $("#enddate").datepicker();
        this.start_date = start_date;
        this.end_date = end_date; 
        this.server = server;
        this.container = container;

        this.chart = new Highcharts.Chart({
          chart: {
            renderTo: this.container,
            type: 'spline',
            marginRight: 30,
            renderer: 'SVG'
            },
            title: {
                text: 'Downloads and Daily Users'
            },
            tooltip: {
                shared : true,
            crosshairs : true,
            },

            plotOptions: {
                line: {
                    dataLabels: {
                        enabled: true
                    },
            enableMouseTracking: true
                }
            },
            xAxis: {
                type: 'datetime',
                tickPixelInterval: 150
            },
            yAxis: [
            {
                title: {
                    text: 'Downloads'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            {
                opposite: true,
                title: {
                    text: 'Daily Users'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            ],
            legend: {
                enabled: true
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

    },

      draw: function () {
          // picking the dates
          var start_date = $(this.start_date).datepicker('getDate');
          var end_date = $(this.end_date).datepicker('getDate');
          this._drawRange($("#appid").val(), start_date, end_date);
      },

        _drawRange: function(app_id, start_date, end_date) {
            var delta = end_date - start_date;
            delta = Math.round(delta / 1000 / 60 / 60/ 24);
            var start_date_str = $.datepicker.formatDate('yy-mm-dd', start_date);
            var end_date_str = $.datepicker.formatDate('yy-mm-dd', end_date);
            this.chart.showLoading();
            var i, x, y;
            var query = {"query": {"field": {"add_on": app_id}},
                "facets": {"facet_os": {"terms": {"field": "os"}}},
                "filter": {"range": {"date": {"gte": start_date_str, "lt": end_date_str}}},
                "sort": [{"date": {"order" : "asc"}}],
                "size": delta
            };

            query = JSON.stringify(query);
            this._async(query);

            this.chart.hideLoading();
        },
    
   _async: function (query) {
            var downloads_series = this.chart.series[0];
            var users_series = this.chart.series[1];
            var _chart = this.chart;

            $.ajax({
                type: "POST",
                url: this.server,
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                processData: false,
                dataType: "json",
                data: query,
                success: function(json) {
                    var downloads = [];
                    var users = [];
                    var facets = [];
                    $.each(json.hits.hits, function(i, item) {
                        downloads.push({x: Date.parse(item._source.date), y: item._source.downloads_count});
                        users.push({x: Date.parse(item._source.date), y: item._source.users_count});
                    });
                    $.each(json.facets.facet_os.terms, function(i, item) {
                        facets.push({term: item.term, count: item.count});
                    });

                    downloads_series.setData(downloads);
                    users_series.setData(users);
                    _chart.redraw();
                },
                error: function (xhr, textStatus, errorThrown) {
                    alert(xhr.responseText);
                },
                failure: function(errMsg) {
                    alert(errMsg);
                }
            });

   }
    }
)


