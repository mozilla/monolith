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

angular.module('components', [])
 .directive('dashboard', function() {
    return {
      restrict: 'E',
      scope: {},
      transclude: true,
      controller: function($scope, $element) {
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
  })
 .directive('chart', function() {
    return {
      require: '^dashboard',
      restrict: 'E',
      scope: {title: '@', id: '@', 'end': '@'},
      transclude: false,
      controller: function($scope, $element) {
        $scope.draw = function () {
          $scope.chart.draw();
          $("#modal-" + $scope.id).modal('hide');
        };

      },
      // XXX can this be externalized as a template ?
      // not an ugly string
      template: 
        '<div>' +
         '<div id="chart-{{id}}" style="height:300px; margin: 0 auto">' +
         '</div>' +
         '<a href="#modal-{{id}}" role="button" class="span2 offset1 btn btn-primary" data-toggle="modal">Change</a>' + 
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
         '{{end}}</div>', 
      replace: true,
      link: function(scope, element, attrs, dashboard) {
        dashboard.addChart(scope);
        attrs.$observe('end', function(value) {
            setTimeout(function() {
            scope.chart = new Monolith("http://0.0.0.0:6543/es",
              "#startdate-" + scope.id, 
              "#enddate-" + scope.id,
              "#appid-" + scope.id, 
              "chart-" + scope.id,
              scope.title);
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

$.Class("Monolith", 
    {},
    {
    init: function(server, start_date, end_date, appid, container, title){
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
          var start_date = $(this.start_date).data('datepicker').date;
          var end_date = $(this.end_date).data('datepicker').date;
          var start_date_str = start_date.toISOString();
          var end_date_str = end_date.toISOString();
          this._drawRange($(this.appid).val(), start_date, end_date, 
                          start_date_str, end_date_str);
      },

        _drawRange: function(app_id, start_date, end_date, start_date_str, 
                             end_date_str) {
            var delta = end_date.getTime() - start_date.getTime();
            var one_day = 1000 * 60 * 60 * 24;
            delta = Math.round(delta / one_day);
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


