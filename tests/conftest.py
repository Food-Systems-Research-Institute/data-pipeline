class MockResponse:
    """Mock API, configure responses as needed"""

    def __init__(self):
        self.json_data = {}
        self.status_code = 200
        self.calls = []  # start empty, fill with calls

    @property
    def text(self):
        return str(self.json_data)

    def json(self):
        return self.json_data
