def handler(event, context):
    print("Hello, World! -- Lambda Authorizer")
    print(f"Event: {event}, Context: {context}")
    return {
        "isAuthorized": True,
        "context": {
            "exampleKey": "exampleValue"
        }
    }
