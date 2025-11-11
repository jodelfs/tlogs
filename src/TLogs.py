from bokeh.plotting import curdoc

from tluserinterface import UserInterface

user_interface = UserInterface()

layout = user_interface.layout()

curdoc().add_root(layout)