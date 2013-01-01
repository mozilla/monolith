.. _sample:

Sample Queries
--------------

Some sample queries that might be useful. Please consult the Elastic Search
docs for the definitive answer.

All results for *addons.downloads.count* between two dates::

        GET /es/search/
        {
            "filter": {
                "and": [
                    {
                        "term": {
                            "name": "addons.downloads.count"
                        }
                    },
                    {
                        "range": {
                            "date": {
                                "gte": "2009-07-16",
                                "lte": "2012-07-18"
                            }
                        }
                    }
                ]
            }
        }

