"""
Graphication, the pretty Python graphing library.

Copyright Andrew Godwin 2007
$Id: __init__.py 66 2008-07-11 11:15:49Z andrew $
"""


import graphication.css as css
css.install_hook()
from graphication import default_css

from graphication.output import FileOutput
from graphication.label import Label
from graphication.series import Series, SeriesSet, Node, NodeSet, NodeLink
from graphication.scales import SimpleScale, VerticalWavegraphScale
from graphication.scales.date import DateScale, AutoDateScale, AutoWeekDateScale, WeekdayDateScale
from graphication.colourer import Colourer