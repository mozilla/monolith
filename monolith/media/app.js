/* Angular app that defines two new directives: dashboard & chart

  Example:

  <div ng-app="components">
    <dashboard server="http://0.0.0.0:6543">
         <chart title="Downloads and Daily Users" 
                id="chart1"
                fields="downloads_count,users_count"
                type="series"/>

         <chart title="Daily Users" 
                id="chart2"
                fields="users_count"
                type="series"/>

         <chart title="Download counts per month" 
                id="chart4"
                type="aggregate"
                field="downloads_count" 
                interval="month"/>
    </dashboard>
  </div>

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

