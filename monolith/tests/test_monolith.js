

describe("Utils suite", function() {
  var $scope, ctrl, compile;

  beforeEach(module('components'));

  beforeEach(inject(function($rootScope, $controller, $compile) {
    $scope = $rootScope.$new();
    //ctrl = $controller('MainCtrl', {
    //  $scope: $scope
    //});
    compile = $compile;
  }));

  it("'queryES'", function() {
    var query = {"query": { "match_all": {}}};
    result = queryES("http://0.0.0.0:9998/time_2012-01/_search", query);
    var total = result.hits.total;
    expect(total).toBe(3100);
    });

  it("'getTerms'", function() {

    result = getTerms("http://0.0.0.0:9998/_search", "os");
    var wanted = ['Windows 8', 'Mac OS X', 'Ubuntu'];

    expect(result).toEqual(wanted);
    });

  it("'getInfo'", function() {
    var chart = new MonolithBase("http://0.0.0.0:9997", "", "", "", "", "", "");
    var wanted = [ 'downloads_count', 'users_count' ];
    expect(chart.info.fields).toEqual(wanted);
  });

  it("'chart'", function() {

     var directive = ['<div>',
        '<dashboard server="http://0.0.0.0:9997">',
          '<chart title="Downloads and Daily Users" ',
            'id="chart1" fields="downloads_count,users_count" type="series"> ',
          '</chart>',
        '</dashboard>',
      '</div>'];

     directive = directive.join(' ');
     var elm = compile(directive)($scope);

     $scope.$apply();
     $scope.$digest();

     var titles = elm.find('h3');
     expect(titles[1].innerHTML).toBe('Change "Downloads and Daily Users"');

  });


});





