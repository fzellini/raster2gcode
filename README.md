# raster2gcode
a python3 program to convert an image into gcode for laser engraving

It uses opencv
```
python3 raster2gcode.py -h
usage: raster2gcode.py [-h] --image IMAGE [--gcode GCODE]
                       [--destsize DESTSIZE] [--spotdia SPOTDIA] [--pre PRE]
                       [--post POST] [--max-spindle MAX_SPINDLE] [--feed FEED]

raster2gcode, convert an image into gcode for laser engraving

optional arguments:
  -h, --help            show this help message and exit
  --image IMAGE         image file (default: None)
  --gcode GCODE         gcode output file (default: out.gcode)
  --destsize DESTSIZE   destination engraved image size (default: 100x100)
  --spotdia SPOTDIA     laser spot diameter in mm (default: 0.1)
  --pre PRE             gcode prelude (default: G21 G92 X0 Y0 M3 )
  --post POST           gcode prelude (default: M5 )
  --max-spindle MAX_SPINDLE
                        max spindle value (default: 150)
  --feed FEED           feed of G01 commands (default: 1000)

```