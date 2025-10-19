class IndexController:
    def __init__(self):
        pass

    def index(self, event):
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Hello, World!"
            })
        }
