

describe("Utils suite", function() {
  it("'queryES'", function() {

    var query = {"query": { "match_all": {}}};

    result = queryES("http://0.0.0.0:9998/time_2012-01/_search", query);
    var total = result.hits.total;
    expect(total).toBe(3100);
    });
});




