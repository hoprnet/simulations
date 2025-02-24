class TaskManager:
    def __init__(self, text: str):
        self.text = text

    def __enter__(self):
        print(f"- {self.text}...", end=" ")

    def __exit__(self, type, value, traceback):
        if type:
            print("❌")
            print(f"\tErr: {value}")
            exit(0)
        else:
            print("✅")
