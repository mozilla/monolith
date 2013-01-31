/*
   monolith.js

   Provides a Monolith class that will draw a HighCharts diagram
   by querying Elastic Search

   options:

   - server: the elastic server server full URL
   - start_date: the id of the start date picker
   - end_date: the id of the end date picker
   - appid: the id of the app id input text
   - container: the name of the chart container

*/

var app = angular.module('components', []);


app.directive('dashboard', function() {
    return {
      restrict: 'E',
      scope: {},
      transclude: true,
      controller: function($scope, $element, $attrs) {
        this.server = $scope.server = $attrs.server;
        var charts = $scope.charts = [];
        this.addChart = function(chart) {
           charts.push(chart);
        }
      },
      template:
        '<div class="tabbable">' +
         '<h3>Monolith Dashboard</h3>' +
          '<div class="tab-content" ng-transclude></div>' +
        '</div>',
      replace: true
    };
  });

app.directive('chart', function() {
    return {
      require: '^dashboard',
      restrict: 'E',
      scope: {title: '@', id: '@', fields: '@', field: '@', 
              type: '@', interval: '@'},
      transclude: false,
      controller: function($scope, $element, $attrs) {
        $scope.draw = function () {
          $scope.chart.draw();
          $("#modal-" + $scope.id).modal('hide');
        };

      },
      // XXX can this be externalized as a template ?
      // not an ugly string
      template:
        '<div class="droppable chart"><div class="draggable">' +
         '<div id="chart-{{id}}" style="height:300px; margin: 0 auto">' +
         '</div>' +
         '<a href="#modal-{{id}}" role="button" class="span2 offset1 btn btn-primary" data-toggle="modal">Change</a>' +
          '<div style="clear:both"/>' + 
          '<div id="modal-{{id}}" class="modal hide fade">' +
          '<div class="modal-header">' +
           '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
           '<h3>Change "{{ title }}"</h3>' +
           '</div>' +
         '<div class="modal-body">' +
         '<form id="query-{{id}}"><fieldset>' +
           '<label for="startdate-{{id}}">Start Date</label>' +
           '<input type="text" id="startdate-{{id}}" value="01/01/2012"/>' +
           '<label for="enddate-{{id}}"> End date </label>' +
           '<input type="text" id="enddate-{{id}}" value="03/01/2012"/>' +
           '<label for="appid-{{id}}"> App id (1 to 100)</label>' +
           '<input type="text" id="appid-{{id}}" value="1"/>' +
           '<br/>' +    // err well
           '<button type="submit" class="btn btn-primary" ng-click="draw()">Update</button>' +
         '</fieldset></form></div></div>' +
         '</div>{{end}}</div>',
      replace: true,
      link: function(scope, element, attrs, dashboard) {
        dashboard.addChart(scope);

        attrs.$observe('end', function(value) {
            setTimeout(function() {
            if (scope.type == 'series') {
              scope.chart = new MonolithSeries(dashboard.server,
				"#startdate-" + scope.id,
				"#enddate-" + scope.id,
				"#appid-" + scope.id,
				"chart-" + scope.id,
				scope.title, 
				scope.fields);
			}

		   	if (scope.type == 'aggregate') {
              scope.chart = new MonolithAggregate(dashboard.server,
				"#startdate-" + scope.id,
				"#enddate-" + scope.id,
				"#appid-" + scope.id,
				"chart-" + scope.id,
				scope.title, 
				scope.field, 
				scope.interval);
			}


            scope.chart.draw();

          });
      }, 1000);
      },
    };
  })


var minute = 60000;

Highcharts.setOptions({
    global: {
        useUTC: false
    }
});


// XXX we shoulduse Angular classes here

// Monolith series - plain series, up to 2
$.Class("MonolithSeries",
    {},
    {
    init: function(server, start_date, end_date, appid, container, title, fields) {
        // init the date pickers
        $(start_date).datepicker();
        $(start_date).datepicker().on('changeDate',
            function(ev) {$(start_date).datepicker('hide')});
        $(end_date).datepicker();
        $(end_date).datepicker().on('changeDate',
            function(ev) {$(end_date).datepicker('hide')});

        this.appid = appid;
        this.start_date = start_date;
        this.end_date = end_date;
        this.server = server;
        this.container = container;
        this.title = title;
        this.info = this._getInfo(server);
        this.es_server = this.server + this.info.es_endpoint;
        
        // building the series and the y axis
        this._fields = fields.split(",");

        if (this._fields.length > 2) {
          throw new Error("We support 1 or 2 series per chart, no more.");
        }

        this.series = [];
        this.yAxis = [];
        var opposite;

        for (var i = 0; i < this._fields.length; i++) {
            this.series.push({name: this._fields[i],
                              data: (function() {return [];})()});
            opposite =  i % 2 != 0

            this.yAxis.push({
                title: {text: this._fields[i]},
                opposite: opposite, 
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            })
        }

        // We should move all of this in its own json file...
        this.chart = new Highcharts.Chart({
          chart: {
            renderTo: this.container,
            type: 'spline',
            marginRight: 30,
            renderer: 'SVG'
            },
            title: {
                text: this.title
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
            yAxis: this.yAxis,
            legend: {
                enabled: true
            },
            exporting: {
                enabled: false
            },
            series: this.series
        });
    },

      draw: function () {
          // picking the dates
          var start_date = $(this.start_date).data('datepicker').date;
          var end_date = $(this.end_date).data('datepicker').date;
          var start_date_str = start_date.toISOString();
          var end_date_str = end_date.toISOString();
          this._drawRange($(this.appid).val(), start_date, end_date,
                          start_date_str, end_date_str);
      },
        _getInfo: function() {
          var info;

          $.ajax({url: this.server,
                  type: 'GET',
                  async: false,
                  success: function(result) { info = result; }
            });
          return info;
        },

        _drawRange: function(app_id, start_date, end_date, start_date_str,
                             end_date_str) {
            var delta = end_date.getTime() - start_date.getTime();
            var one_day = 1000 * 60 * 60 * 24;
            delta = Math.round(delta / one_day);
            this.chart.showLoading();
            var i, x, y;
            var query = {"query": {"field": {"add_on": app_id}},
                         "filter": {"range": {"date": {"gte": start_date_str, "lt": end_date_str}}},
                         "sort": [{"date": {"order" : "asc"}}],
                         "size": delta };

            query = JSON.stringify(query);
            this._async(query);
            this.chart.hideLoading();
        },

       _async: function (query) {
            var _series = this.chart.series;
            var _chart = this.chart;
            var _fields = this._fields;

            $.ajax({
                type: "POST",
                url: this.es_server,
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                processData: false,
                dataType: "json",
                data: query,
                success: function(json) {
                    var dataSeries = [];
                    var name;
                    var num = _fields.length;

                    for (var i = 0; i < num; i++) {
                      dataSeries[i] = [];
                    }
                    $.each(json.hits.hits, function(i, item) {
                      for (var i = 0; i < num; i++) {
                         name = _fields[i];
                         if (item._source.hasOwnProperty(name)) {
                           dataSeries[i].push({x: Date.parse(item._source.date), 
                                               y: item._source[name]});
                         }
                      }
                    });

                    for (var i = 0; i < num; i++) {
                      _series[i].setData(dataSeries[i]);
                    }

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


// Monolith series - facet search
$.Class("MonolithAggregate",
    {},
    {
    init: function(server, start_date, end_date, appid, container, title, field, interval) {
        // init the date pickers
        $(start_date).datepicker();
        $(start_date).datepicker().on('changeDate',
            function(ev) {$(start_date).datepicker('hide')});
        $(end_date).datepicker();
        $(end_date).datepicker().on('changeDate',
            function(ev) {$(end_date).datepicker('hide')});

        this.appid = appid;
        this.start_date = start_date;
        this.end_date = end_date;
        this.server = server;
        this.container = container;
        this.title = title;
        this.info = this._getInfo(server);
        this.es_server = this.server + this.info.es_endpoint;

        this.interval = interval;
        this.field = field;
        this.series = [{name: field, data: (function() {return [];})()}];
        this.yAxis = [{
                title: {text: field},
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]}]


        // We should move all of this in its own json file...
        this.chart = new Highcharts.Chart({
          chart: {
            renderTo: this.container,
            type: 'spline',
            marginRight: 30,
            renderer: 'SVG'
            },
            title: {
                text: this.title
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
            yAxis: this.yAxis,
            legend: {
                enabled: true
            },
            exporting: {
                enabled: false
            },
            series: this.series
        });
    },

      draw: function () {
          // picking the dates
          var start_date = $(this.start_date).data('datepicker').date;
          var end_date = $(this.end_date).data('datepicker').date;
          var start_date_str = start_date.toISOString();
          var end_date_str = end_date.toISOString();
          this._drawRange($(this.appid).val(), start_date, end_date,
                          start_date_str, end_date_str);
      },
        _getInfo: function() {
          var info;

          $.ajax({url: this.server,
                  type: 'GET',
                  async: false,
                  success: function(result) { info = result; }
            });
          return info;
        },

        _drawRange: function(app_id, start_date, end_date, start_date_str,
                             end_date_str) {
            var delta = end_date.getTime() - start_date.getTime();
            var one_day = 1000 * 60 * 60 * 24;
            delta = Math.round(delta / one_day);
            this.chart.showLoading();
            var i, x, y;
            var query = {"query": {"field": {"add_on": app_id}},
                "facets": {
                   "facet_histo" : {"date_histogram" : {"key_field" : "date",  
                                    "value_field": this.field, 
                                    "interval": this.interval}}
                 },
                "filter": {"range": {"date": {"gte": start_date_str, "lt": end_date_str}}},
                "sort": [{"date": {"order" : "asc"}}],
                "size": delta
            };

            query = JSON.stringify(query);
            this._async(query);
            this.chart.hideLoading();
        },

       _async: function (query) {
            var _series = this.chart.series;
            var _chart = this.chart;
            var _fields = this._fields;

            $.ajax({
                type: "POST",
                url: this.es_server,
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                processData: false,
                dataType: "json",
                data: query,
                success: function(json) {
                    var name;
                    var data = [];

                    $.each(json.facets.facet_histo.entries, function(i, item) {
                         data.push({x: new Date(item.time), 
                                    y: item.total});
                    });

                    _series[0].setData(data) ;
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


