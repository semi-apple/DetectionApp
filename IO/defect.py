class Defect:
    def __init__(self, image, cls, xyxy):
        self.cls = cls
        self.image = image
        self.xyxy = xyxy

    # def transfer_to_xyxy(self):
    #     min_x = self.image.shape[1]
    #     min_y = self.image.shape[0]
    #     max_x = 0
    #     max_y = 0
    #     for x, y in self.points:
    #         if x < min_x:
    #             min_x = x
    #         if y < min_y:
    #             min_y = y
    #         if x > max_x:
    #             max_x = x
    #         if y > max_y:
    #             max_y = y
    #
    #     return min_x, min_y, max_x, max_y


