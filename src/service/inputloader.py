from pygrabber.dshow_graph import FilterGraph

class InputLoader:
    def __init__(self):
        self.available_cams = self.detect_cameras()

    def detect_cameras(self):
        try:
            graph = FilterGraph()
            cameras = graph.get_input_devices()

            if not cameras:
                return ["No camera was found"]

            return cameras

        except Exception as e:
            print(e)
            return ["No camera was found"]

    def get_camera_name(self, index):
        if not self.available_cams or self.available_cams[0] == "No camera was found":
            return "No camera was found"

        if 0 <= index < len(self.available_cams):
            return self.available_cams[index]

        return "Unknown camera"

    def get_camera_count(self):
        if not self.available_cams or self.available_cams[0] == "No camera was found":
            return 0
        else:
            return len(self.available_cams)