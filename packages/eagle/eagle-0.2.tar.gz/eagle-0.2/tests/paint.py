#!/usr/bin/env python2

from eagle import *

class Undo( object ):
    def __init__( self, app ):
        self.last_images = []
        self.app = app
        app.undo = self
        self.canvas = app[ "canvas" ]
        self.button = app[ "undo" ]
        self.button.set_inactive()
    # __init__()


    def push( self ):
        img = self.canvas.get_image()
        self.last_images.append( img )
        self.button.set_active()
    # push()


    def pop( self ):
        if self.last_images:
            img = self.last_images.pop()
            self.canvas.draw_image( img )

        if not self.last_images:
            self.button.set_inactive()
    # pop()
# Undo



class Tool( object ):
    """Interface to be implemented by tools."""

    def set_active( self, app ):
        """This tool is now active."""
        pass
    # set_active()


    def set_inactive( self, app ):
        """This tool is now inactive. """
        pass
    # set_inactive()


    def mouse( self, app, canvas, buttons, x, y ):
        """This tool have a user feedback using mouse on canvas."""
        pass
    # mouse()
# Tool



class Line( Tool ):
    def __init__( self ):
        self.first_point = None
        self.message_id = None
    # __init__()


    def set_active( self, app ):
        self.message_id = app.status_message(
            "Press the left mouse button to mark the first point." )
    # set_active()


    def set_inactive( self, app ):
        if self.message_id is not None:
            app.remove_status_message( self.message_id )
    # set_inactive()


    def mouse( self, app, canvas, buttons, x, y ):
        if buttons & Canvas.MOUSE_BUTTON_1:
            if self.first_point is None:
                self.first_point = ( x, y )
                self.inner_message_id = app.status_message(
                    ( "First poit at ( %d, %d ). Now mark the second." ) %
                    ( x, y ) )
            else:
                color = app[ "fg" ]
                size  = app[ "size" ]
                x0, y0 = self.first_point
                app.undo.push()
                canvas.draw_line( x0, y0, x, y, color, size )
                self.first_point = None
                app.remove_status_message( self.inner_message_id )
    # mouse()
# Line



class Pencil( Tool ):
    def __init__( self ):
        self.last_point = None
        self.message_id = None
        self.changed = False
    # __init__()


    def set_active( self, app ):
        self.message_id = app.status_message(
            "Press the left mouse button and move your mouse." )
    # set_active()


    def set_inactive( self, app ):
        if self.message_id is not None:
            app.remove_status_message( self.message_id )
    # set_inactive()


    def mouse( self, app, canvas, buttons, x, y ):
        if buttons & Canvas.MOUSE_BUTTON_1:
            if not self.changed:
                app.undo.push()
            self.changed = True

            color = app[ "fg" ]
            size  = app[ "size" ]
            if self.last_point is not None:
                x0, y0 = self.last_point
            else:
                x0 = x + 1
                y0 = y

            if size == 1:
                canvas.draw_point( x, y, color )
            else:
                half = size / 2
                canvas.draw_rectangle( x-half, y-half, size, size, color, 1,
                                       color, True )
            canvas.draw_line( x0, y0, x, y, color, size )
            self.last_point = ( x, y )
        else:
            # Button 1 was released, reset last point
            self.last_point = None
            self.changed = False
    # mouse()
# Pencil



class Rectangle( Tool ):
    def __init__( self ):
        self.first_point = None
        self.message_id = None
    # __init__()


    def set_active( self, app ):
        app[ "rectgroup" ].show()
        self.message_id = app.status_message(
            "Press the left mouse button to mark first point." )
    # set_active()


    def set_inactive( self, app ):
        app[ "rectgroup" ].hide()
        if self.message_id is not None:
            app.remove_status_message( self.message_id )
    # set_inactive()


    def mouse( self, app, canvas, buttons, x, y ):
        if buttons & Canvas.MOUSE_BUTTON_1:
            if self.first_point is None:
                self.first_point = ( x, y )
                self.inner_message_id = app.status_message(
                    ( "First poit at ( %d, %d ). Now mark the second." ) %
                    ( x, y ) )
            else:
                fg   = app[ "fg" ]
                bg   = app[ "bg" ]
                size = app[ "size" ]
                fill = app[ "rectfill" ]

                x0, y0 = self.first_point

                if x0 > x:
                    x0, x = x, x0
                if y0 > y:
                    y0, y = y, y0

                w = x - x0
                h = y - y0

                app.undo.push()
                canvas.draw_rectangle( x0, y0, w, h, fg, size, bg, fill )
                self.first_point = None
                app.remove_status_message( self.inner_message_id )
    # mouse()
# Rectangle



class Text( Tool ):
    def __init__( self ):
        self.message_id = None
    # __init__()


    def set_active( self, app ):
        app[ "textgroup" ].show()
        self.message_id = app.status_message(
            "Type your text in 'Contents' and press the left button " \
            "to place it." )
    # set_active()


    def set_inactive( self, app ):
        app[ "textgroup" ].hide()
        if self.message_id is not None:
            app.remove_status_message( self.message_id )
    # set_inactive()


    def mouse( self, app, canvas, buttons, x, y ):
        if buttons & Canvas.MOUSE_BUTTON_1 and app[ "text" ]:
            text  = app[ "text" ]
            fg    = app[ "fg" ]
            bg    = app[ "bg" ]
            font  = app[ "font" ]

            if app[ "textbgtransp" ]:
                bg = None

            app.undo.push()
            canvas.draw_text( text, x, y, fg, bg, font )
    # mouse()
# Text



tools = {
    "Line": Line(),
    "Pencil": Pencil(),
    "Rectangle": Rectangle(),
    "Text": Text(),
    }
def_tool="Line"


def tool_changed( app, tool, value ):
    if tool_changed.last_tool:
        tool_changed.last_tool.set_inactive( app )

    t = tools[ value ]
    tool_changed.last_tool = t
    t.set_active( app )
# tool_changed()
tool_changed.last_tool = None


def canvas_action( app, canvas, buttons, x, y ):
    tool = app[ "tool" ]
    tools[ tool ].mouse( app, canvas, buttons, x, y )
# canvas_action()


def save( app, button, filename ):
    canvas = app[ "canvas" ]
    img = canvas.get_image()
    try:
        img.save( filename )
    except Exception, e:
        error( str( e ) )
# save()


def clear( app, button ):
    app.undo.push()
    app[ "canvas" ].clear()
# clear()


def confirm_quit( app ):
    return yesno( "Are you sure you want to close '%s'?" % app.title )
# confirm_quit()


def do_undo( app, button ):
    app.undo.pop()
# do_undo()



app = App( title="Paint",
           id="paint",
           statusbar=True,
           quit_callback=confirm_quit,
           left=( Color( id="fg",
                         label="Foreground:",
                         color="black",
                         ),
                  Color( id="bg",
                         label="Background:",
                         color=( 255, 0, 0 ),
                         ),
                  Selection( id="tool",
                             label="Tool:",
                             options=tools.keys(),
                             active=def_tool,
                             callback=tool_changed,
                             ),
                  UIntSpin( id="size",
                            label="Line Size:",
                            min=1,
                            value=1,
                            ),
                  ),
           right=( Group( id="textgroup",
                          label="Text Properties:",
                          children=( Entry( id="text",
                                            label="Contents:",
                                            ),
                                     Font( id="font",
                                           label="Font:",
                                           ),
                                     CheckBox( id="textbgtransp",
                                               label="Transparent background?",
                                               ),
                                     ),
                          ),
                   Group( id="rectgroup",
                          label="Rectangle Properties:",
                          children=( CheckBox( id="rectfill",
                                               label="Fill?",
                                               ),
                                     ),
                          ),
                   ),
           top=( SaveFileButton( callback=save ),
                 CloseButton(),
                 Button( id="undo",
                         stock="undo",
                         callback=do_undo,
                         ),
                 Button( id="clear",
                         stock="clear",
                         callback=clear,
                         ),
                 ),
           center=( Canvas( id="canvas",
                            label="Draw Here:",
                            width=400,
                            height=400,
                            bgcolor="white",
                            callback=canvas_action,
                            ),
                    )
           )

for tool in tools.itervalues():
    tool.set_inactive( app )

tool_changed( app, app.get_widget_by_id( "tool" ), def_tool )
Undo( app )

run()
