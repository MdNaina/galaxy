
def transform(self, x, y):
    #return self.transform_2D(x, y)
    return self.transform_perpective(x, y)

def transform_2D(self, x, y):
    return int(x), int(y)

def transform_perpective(self, x, y):
    #print()
    lin_y = y * self.perspective_y / self.height
    #print(f" {y} x {self.perspective_y} / {self.height} \n {y} x {self.perspective_y/self.height} => {lin_y}")

    if lin_y > self.perspective_y:
        lin_y = self.perspective_y

    dx = x - self.perspective_x
    #print(f" dx = {x} - {self.perspective_x} => {dx}")
    dy = self.perspective_y - lin_y
    #print(f" dx = {self.perspective_y} - {lin_y} => {dy}")
    factor_y = dy/self.perspective_y
    #print(f" factor_y = {dy} / {self.perspective_y} => {factor_y}")
    factor_y = pow(factor_y, 4)
    tr_x = self.perspective_x + dx * factor_y
    #print(f" tr_x = {self.perspective_x} + {dx} x {factor_y} => {tr_x}")
    tr_y = (1 - factor_y) * self.perspective_y

    return int(tr_x), int(tr_y)
