from pygrabber.dshow_graph import FilterGraph

class InputLoader:
    def __init__(self):
        self.available_cams = self.detect_cameras()

    def detect_cameras(self):
        try:
            graph = FilterGraph()
            cameras = graph.get_input_device()

            if not cameras:
                return 0
            return cameras

        except Exception as e:
            return 0


    def get_camera_name(self, index):
        if self.available_cams == 0:
            return 0

        if 0 <= index < len(self.available_cams):
            return self.available_cams[index]

        return 0

    def get_camera_count(self):
        if self.available_cams == 0:
            return 0
        else:
            return len(self.available_cams)