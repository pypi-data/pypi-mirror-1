================================
tl.gcrop: Introduction and usage
================================

The goal of this program is to allow cropping an image using the mouse and
having visual feedback while at the same time applying various mathematical
constraints such as maintaining a given aspect ratio or ensuring minimal
values for the crop margins.

The current state of implementation does visual cropping but doesn't yet take
into account constraints. Also, the output of the program is only the crop
coordinates; the cropped image cannot be saved yet.

Key bindings:

  :Ctrl-O:
    Open a new image, replacing the previous one without warning.

Mouse actions inside the image window:

  :Left button:
    Change crop margins if the mouse is outside the crop area (one if it's
    outside an edge, two if it's outside a corner), otherwise move the crop
    area without changing its size.

  :Scroll wheel:
    Zoom the image up or down by factors of 2.

Widgets on the right panel:

- A line describing the current crop area (left and top margin, width
  and height) that can be copied using mouse selection.

- Input fields that allow setting all crop parameters to exact pixel values.

- Two preview windows that show the cropped image and the crop area relative
  to the total image.


.. Local Variables:
.. mode: rst
.. End:
