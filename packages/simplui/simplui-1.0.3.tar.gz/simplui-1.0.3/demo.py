#! /usr/bin/env python

# import pyglet, as usual
import pyglet

# and import out gui toolkit
from simplui import *

# create a basic pyglet window
window = pyglet.window.Window(800, 600, caption='gui demo')

# load some gui themes
themes = [Theme('themes/macos'), Theme('themes/pywidget')]
theme = 0

# create a frame to contain our gui, the full size of our window
frame = Frame(themes[theme], w=800, h=600)
# let the frame recieve events from the window
window.push_handlers(frame)

# these are some action callbacks, to be called by gui elements
def cycle_themes(button):
	# switch gui themes at runtime
	global theme
	theme = (theme + 1) % len(themes)
	frame.theme = themes[theme]

def check_action(checkbox):
	print 'checkox', ('checked' if checkbox.value else 'unchecked')

def slider_action(slider):
	print 'slider moved to:', round(slider.value, 2)

def button_action(button):
	# when the button is clicked, we retrieve a named element from the gui
	element = frame.get_element_by_name('misc_layout')
	# and add a new label to it
	element.add( Label('This is another label...') )

def text_action(input):
	print 'text entered:', input.text

# create dialogue - note that we create the entire gui in a single call
dialogue = Dialogue('Inspector', x=200, y=500, content=
# add a vertical layout to hold the window contents
	VerticalLayout(autosizex=True, hpadding=0, children=[
	# now add some folding boxes
		FoldingBox('stats', content=
		# each box needs a content layout
			VerticalLayout(w=200, children=[
			# add a text label, note that this element is named...
				Label('0.0 fps', name='fps_label'),
			# and this element is not named
				Label('10,000 triangles')
				])
			),
		FoldingBox('settings', content=
			VerticalLayout(w=200, children=[
			# a clickable button to change the theme
				Button('Change GUI Theme', action=cycle_themes),
				Label('Detail level:'),
			# a slider
				Slider(w=160, min=0.0, max=4.0, action=slider_action),
			# a checkbox, note the action function is provided directly
				Checkbox('Show wireframe', action=check_action),
			# a text input field
				TextInput(w=160, text='edit me', action=text_action)
				])
			),
		FoldingBox('misc', content=
		# We need to name this layout, because we used it in the callback above
			VerticalLayout(w=200, name='misc_layout', children=[
			# a random label
				Label('Hello, World!'),
			# and a clickable button
				Button('Click me!', action=button_action)
				])
			)
		])
	)
# add the dialogue to the frame
frame.add( dialogue )

# remove and add the dialogue from the screen on user input
@window.event
def on_key_press(sym, mod):
	if sym == pyglet.window.key.I:
		if dialogue.parent != None:
			frame.remove( dialogue )
		else:
			frame.add( dialogue )

# in the on_draw event, we just call frame.draw()
@window.event
def on_draw():
	window.clear()
		
	frame.draw()

# schedule an empty update function
# this forces the window to be refreshed regularly
def update(dt):
	pass

pyglet.clock.schedule(update)

# schedule a update function to be called less often
def update_stats(dt):
	# if the dialogue is onscreen, update the fps counter
	if dialogue.parent != None:
		fps = pyglet.clock.get_fps()
		
		# retrieve the named element from the gui
		element = frame.get_element_by_name('fps_label')
		# and change the text, to display the current fps
		element. text = '%.1f fps' % (fps)

pyglet.clock.schedule_interval(update_stats, 0.5)

# finally, run the application...
pyglet.app.run()
