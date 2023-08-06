.. Grease tutorial part 1

Grease Tutorial (Part I)
========================

In this tutorial, we will be creating a simple, but complete game. To make the most of this material, you should have a working Grease installation. The tutorial progresses through several revisions of an example game named *Blasteroids*. To keep things simple, all of the code in this game is in a single file. Each section of the tutorial builds a new revision of the game code. You can find the complete revisions of the tutorial game code for each section in the *tutorial* subdirectory of the Grease source package.  

For Grease installation instructions, see: <insert install doc link>

Diving In
---------

Grease is built upon the excellent Pyglet (http://www.pyglet.org) library. Pyglet provides the basic windowing, operating system event, scheduling and OpenGL graphics support for Grease. This tutorial assumes no prior knowledge of Pyglet or OpenGL, however it is not itself anything but a basic introduction to each. One of the advantages to Grease is that it abstracts away much of the details of using OpenGL, however its full power is still available to you if you need it. In fact there is no OpenGL-specific code in this tutorial, but several general graphic programming concepts will be introduced.

*Blasteroids* is a facimile of the similarly named classic arcade game. I chose this game specifically because it is familiar and simple, yet still complicated enough to be a non-trivial example. It's also still fun to play after all of these years. To implement *Blasteroids* we will need the following basic functionality:

* Window with a graphics context
* A way to create polygonal shapes, move and draw them
* Keyboard event handler
* Collision detection
* Game logic for game lifetime and scoring
* Title screen and game mode handling

Starting from the top, we will write the code that creates the window and graphics context. Luckily Pyglet makes that very easy::

	import pyglet

	def main():
		"""Initialize and run the game"""
		global window
		window = pyglet.window.Window()
		pyglet.app.run()
	
	if __name__ == '__main__':
		main()

The above is a complete Pyglet program that creates a window and enters the event loop listening for system events. The window is declared `global` because we will need to reference it elsewhere in the program to access things like its `width` and `height`. Although the above is not very interesting yet, it already has some important functionality. In particular the program will exit if the window is closed or the escape key is pressed. This functionality is included in the window's default `on_key_press()` event handler.

If you have not seen it before, the if statement at the end may appear a bit odd. This is a python idiom used in module files that can be run as scripts. Each module has a built-in `__name__` attribute set by the interpreter. The name `"__main__"` is used for a module that is being executed as a script. In our example this means that the `main()` function will be executed when the module is run as a script, but not it is imported by another module. Although our program is not intended to be imported by other programs, it can still be handy to do so from the python prompt for debugging. Without using this check, importing the module would unexpectedly execute `pyglet.app.run()` to start the event loop, which would not return control to the importing program.

The World of Grease
-------------------

Now that we have a window, we can move on to setting up our game environment. Grease provides a :class:`grease.World` class to organize and orchestrate all of the basic parts that we need. A convenient way to specify a world configuration is the subclass :class:`grease.World` and override the `configure()` method. This method gets called after the world is instantiated so that the application can configure it as desired. We need to configure the world with three different types of parts. We'll start with components.

Components
''''''''''

Components specify the data fields for the entities in the game and store all of their data. If you are familiar with relational databases, components can be thought of like tables with entities as their primary keys. Don't worry too much about what an entity is just yet, once we get the world configuration setup, we'll delve more deeply into how they work.

Below is the first part of our world configuration that subclasses the :class:`grease.World` base class and configures some basic components::

	from grease import component, controller, renderer

	class GameWorld(grease.World):

		def configure(self):
			"""Configure the game world's components, systems and renderers"""
			self.components.map(
				position=component.Position(),
				movement=component.Movement(),
				shape=component.Shape(),
				renderable=component.Renderable(),
			)

Components are accessed via the world attribute `components`. This attribute is a dict-like object that maps components by name. Above we use the `map()` method to configure multiple components at once. The keyword arguments for `map()` name each component in the world. Above four standard components are configured:

Position:
	The position component stores entity position data. It has the fields `position` amd `angle`.

Movement:
	The movement component describes how an entity moves over time. It has the fields `velocity`, `accel` and `rotation`.

Shape:
	The shape component decribes poylgonal entity shapes. It has the fields `verts` and `closed`.

Renderable:
	The renderable component stores some data about entity presentation. It has the fields `depth` and `color`.

Entities in a `GameWorld` instance can now have data in any of these components.

Systems
'''''''

Now that we have some components for our world, let's move on to systems. Systems define behavioral aspects of the world. They execute at regular intervals to update the state of the world in particular ways. This often means they take data from one or more components to modify the data in others.  Below we add a standard system to our world configuration::

	class GameWorld(grease.World):

		def configure(self):
			"""Configure the game world's components, systems and renderers"""
			self.components.map(
				position=component.Position(),
				movement=component.Movement(),
				shape=component.Shape(),
				renderable=component.Renderable(),
			)
			self.systems.add(
				('movement', controller.EulerMovement()),
			)

Similar to components, the world attribute `systems` is used to access the systems. Systems also have names like components. Unlike components, however, the order of systems in the world is important. When the systems are executed each time step, they are executed in the order defined in the systems map. Many times systems use the results calculated by other systems to do their work. System ordering allows the application to ensure that the world is updated in a consistent way.

The :class:`controller.EulerMovement` system is responsible for updating the position and movement components. It performs a Euler integration each time step to update the `movement.velocity`, `position.position` and `position.angle` fields for all entities with both position and movement data. Systems access components in the world by name. By default, the `EulerMovement` controller assumes the position component it will use is named `"position"` and the movement controller is named `"movement"`. This is just a convention, however. In fact you can have multiple position and movement components with different names if desired. For this application the defaults work fine, and require less configuration.

Renderers
'''''''''

The last piece of the world configuration puzzle are the renderers. Their role is unsurprisingly to create the visual presentation of the world. When the window needs to be redrawn, the renders will come to life and paint the world in its current state. We add two renderers to our world config::

	class GameWorld(grease.World):

		def configure(self):
			"""Configure the game world's components, systems and renderers"""
			self.components.map(
				position=component.Position(),
				movement=component.Movement(),
				shape=component.Shape(),
				renderable=component.Renderable(),
			)
			self.systems.add(
				('movement', controller.EulerMovement()),
			)
			self.renderers = (
				renderer.Camera(position=(window.width / 2, window.height / 2)),
				renderer.Vector(line_width=1.5),
			)

Like systems, renderer order is important. Renderers are always drawn in the order they are configured. Unlike systems and components, renderers do not have names.




