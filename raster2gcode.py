# -*- coding: utf-8 -*-
# sudo apt-get install python3-opencv

import numpy as np
import cv2
import sys


class VC:
    def __init__(self, min_v=255., max_v=0., feed_rate=1000, max_spindle=1000., spotsize=0.1):
        self.gcodes = []
        self.min_v = min_v      # min  power value = white
        self.max_v = max_v        # max  power value = black pixel
        self.max_spindle = max_spindle
        self.feed_rate01 = feed_rate
        self.spotsize = spotsize

        self.v_range = self.max_v - self.min_v

        self.last_x = sys.float_info.min
        self.last_y = sys.float_info.min
        self.last_v = sys.float_info.min

        self.first00 = True
        self.first01 = True
        self.feed_out = False

    def getValue(self, v):
        """
        get point normalized value (0 to 1
        :return:
        """
        v = (v-self.min_v)/self.v_range
        return v+0.

    def addPoint(self, x, y, v, lastx):
        v = self.getValue(v)
        if v < 0.02:
            self.last_y = sys.float_info.min
            return

#        if y == self.last_y and abs(v-self.last_v) < 0.02:
#            return

        xg = x*self.spotsize
        yg = y*self.spotsize

        if y != self.last_y:
            gcode = "G00 X{:.2f} Y{:.2f}".format(xg, yg)
            self.feed_out = False
        else:
            if self.feed_out:
                if abs(self.last_v-v) > 0.02 or (lastx and self.last_v > 0.02):
                    gcode = "G01 X{:.2f} Y{:.2f} S{:.0f}".format(xg, yg, v * self.max_spindle)
                else:
                    return
            else:
                gcode = "G01 X{:.2f} Y{:.2f} F{:.0f} S{:.0f}".format(xg, yg, self.feed_rate01, v * self.max_spindle)
            self.feed_out = True

        self.gcodes.append(gcode)
        self.last_x = x
        self.last_y = y
        self.last_v = v



def main( imagename, destgcode, destsize, spotsize, pre, post, max_spindle, feed_rate):
    img = cv2.imread(imagename)

# here change contrast/brightness if wanted
# https://stackoverflow.com/questions/32609098/how-to-fast-change-image-brightness-with-python-opencv

    ysize, xsize = img.shape[:2]
    print("Source image Width {}, Height {}".format(xsize, ysize))

    # compute destination virtual image size
    try:
        xb, yb = destsize.split('x')
        xb = float(xb)/spotsize if len(xb) else None
        yb = float(yb)/spotsize if len(yb) else None
    except ValueError:
        print("bad destsize format: valid is <xmax>x<ymax>, e.g. 100x, 100x100, 200x")
        return
    factor = 1
    if yb is None:
        # scale only x
        factor = xb/xsize
    if xb is None:
        # scale only x
        factor = yb/ysize
    if xb is not None and yb is not None:
        xf = xb / xsize
        yf = yb / ysize
        factor = xf if xf < yf else yf

    print("resize factor {}".format(factor))

    l_xsize = int(xsize*factor)
    l_ysize = int(ysize*factor)

    print("laser image size {} x {}".format(l_xsize, l_ysize))

    # resize the image
    l_image = cv2.resize(img, (l_xsize, l_ysize), interpolation=cv2.INTER_AREA)
    # convert to grayscale

    gray = cv2.cvtColor(l_image, cv2.COLOR_BGRA2GRAY)

    #cv2.imshow("pp", gray)
    print("rendering ( max_spindle={}, feed_rate={}) ....".format(max_spindle,feed_rate))

    vc = VC(spotsize=spotsize, max_spindle=max_spindle, feed_rate=feed_rate)
    y = l_ysize-1
    yc = 0
    while y >= 0:
        if yc % 2 == 0:
            el = lambda px, xl: px < xl
            stp = 1
            x = 0
        else:
            el = lambda px, xl: px >= 0
            stp = -1
            x = l_xsize - 1
        while el(x, l_xsize):
            v = gray[y, x]
            vc.addPoint(x, yc, v, (x == 0) or (x == l_xsize-1))
            x += stp
        y -= 1
        yc += 1

    with open(destgcode, "w") as h:
        h.write (pre)
        for gcode in vc.gcodes:
            h.write("{}\n".format(gcode))
        h.write(post)

    #cv2.waitKey()
    #cv2.destroyAllWindows()






if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='raster2gcode, convert an image into gcode for laser engraving',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--image", help="image file", required=True)
    parser.add_argument("--gcode", help="gcode output file", default="out.gcode", required=False)
    parser.add_argument("--destsize", help="destination engraved image size", default="100x100", required=False)
    parser.add_argument("--spotdia", help="laser spot diameter in mm", default="0.1", required=False,type=float)
    parser.add_argument("--pre", default="G21\nG92 X0 Y0\nM3\n", help="gcode prelude")
    parser.add_argument("--post", default="M5\n", help="gcode prelude")
    parser.add_argument("--max-spindle", default="150", help="max spindle value", type=float)
    parser.add_argument("--feed", default="1000", help="feed of G01 commands", type=float)

    args = parser.parse_args()
    main(args.image, args.gcode, args.destsize, args.spotdia, args.pre, args.post, feed_rate=args.feed,
         max_spindle=args.max_spindle)

