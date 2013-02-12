

describe("Utils suite", function() {
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

});





