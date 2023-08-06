"""
The widget library contains various widgets for use in your application.
Each of the widgets subclasses bezel.graphics.widget.Widget. This library
contains generic containers, a vertical box (VBox), a horizontal box (HBox),
a label (Text), an image (Image), a push button (Button), and will contain
various other input elements.
"""

# Containers
from containers import VBox, HBox
from proportional import ProportionalContainer

# Controls
from text import Text
from image import Image
from button import Button

