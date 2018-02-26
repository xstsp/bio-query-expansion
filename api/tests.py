import unittest
import json
from api import app


class TestApi(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_search_query(self):
        q = {"query": "What Is the most common infection?!?"}
        res = {"docs": ["common", "infection", "?", "!", "?"]}
        response = self.client.post('/search',
                                    data=json.dumps(q),
                                    content_type="application/json")
        # self.assertEqual(res, response.data)
        self.assertEqual(200, response.status_code)

if __name__ == "__main__":
    unittest.main()
