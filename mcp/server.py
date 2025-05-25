class Server:
    def __init__(self, name):
        self.name = name
        self.tools = {}
        print(f"Initialized MCP Server: {name}")

    def tool(self):
        """Decorator to register a tool with the server"""
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

    def run(self):
        print(f"Starting MCP Server: {self.name}")
        print(f"Registered tools: {list(self.tools.keys())}")
        # Keep the server running
        import time
        while True:
            time.sleep(1)