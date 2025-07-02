from ImageMarker import ImageMarker

class ImageMarkerNoAruco(ImageMarker):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.marker_type = "NoAruco"

    def convert_to_four_corner(self, *args, **kwargs):
        raise NotImplementedError("You are using the no-aruco version, the image is not supporsed to be converted into 4 corner model")
    