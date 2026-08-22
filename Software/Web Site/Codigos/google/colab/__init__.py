# Mock google.colab.files for local execution

class MockFiles:
    def upload(self):
        print("Mock files.upload() called")
        return {}

files = MockFiles()
