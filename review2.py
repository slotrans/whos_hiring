import sys
import webbrowser
from contextlib import contextmanager

import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer


SAMPLE_COMMENT = """
Grafana Labs | Backend Engineers, Frontend Engineers, Engineering Managers, Senior Backend Engineers | Remote Global | Full-Time | Remote | https://grafana.com/

You know us, we make the Grafana dashboard you use to observe your systems and business. We also work on Prometheus, Cortex, Loki, Tempo, a SaaS offering, an Enterprise offering. We're well-funded and have a long list of customers whose brands your family recognise. We are OSS, AGPL and CNCF.

We are hiring globally in full-time remote roles. Note: The entire company has been remote first forever and our founders are on multiple continents, this is not something we are learning - this is who we are.

We are looking for engineers at all levels, wherever you are. But specifically right now we are hiring in the Americas and APAC. It doesn't matter where you are in those time zones.

https://grafana.com/about/careers/

If you cannot see something on that page that you identify as... apply to the nearest role and describe what you are looking for in your cover letter as we do read them all.
"""


@contextmanager
def ctx_begin_group():
    try:
        imgui.begin_group()
        yield
    finally:
        imgui.end_group()


@contextmanager
def ctx_begin_child(label, width=0, height=0, border=False, flags=0):
    try:
        visible = imgui.begin_child(label, width, height, border, flags)
        yield visible
    finally:
        imgui.end_child()


def impl_glwf_init() -> None:
    width, height = 1024, 768
    window_name = "imgui/glfw example"

    if not glfw.init():
        print("glfw.init() failed", file=sys.stderr)
        sys.exit(1)

    # not sure if these are required on Windows...
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    window = glfw.create_window(width, height, window_name, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("could not initialize GLFW window", file=sys.stderr)
        sys.exit(2)

    return window


def draw_ui(default_font) -> None:
    imgui.set_next_window_position(x=0, y=0)
    imgui.set_next_window_size(width=1024, height=768)
    main_window_flags = (imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_TITLE_BAR)
    imgui.begin(label="main window", closable=False, flags=main_window_flags)

    imgui.push_font(default_font)

    ## ID & LINK
    with ctx_begin_child(label="window__header", width=0, height=40, border=True):
        imgui.push_item_width(95)
        imgui.input_text(label="", value="28719321", buffer_length=16, flags=imgui.INPUT_TEXT_READ_ONLY)
        imgui.pop_item_width()

        imgui.same_line()

        imgui.push_style_color(imgui.COLOR_BUTTON, r=0/255, g=0/255, b=0/255)
        imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, r=29/255, g=151/255, b=236/255, a=25/255)
        imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, r=29/255, g=151/255, b=236/266, a=75/255)
        imgui.push_style_color(imgui.COLOR_TEXT, r=29/255, g=151/255, b=236/255)
        if imgui.button(label="https://news.ycombinator.com/item?id=28719321", width=600, height=0):
            webbrowser.open("https://news.ycombinator.com/item?id=28719321")
        imgui.pop_style_color(4)


    ## COMMENT TEXT & ARROWS
    with ctx_begin_group():
        with ctx_begin_child(label="window__arrows", width=40, height=460, border=True):
            if imgui.button(label="F", width=22, height=22):
                print("F clicked")
            imgui.dummy(0, 20)
            if imgui.arrow_button(label="button__up", direction=imgui.DIRECTION_UP):
                print("up clicked")
            imgui.dummy(0, 20)
            if imgui.arrow_button(label="button__down", direction=imgui.DIRECTION_DOWN):
                print("down clicked")
            imgui.dummy(0, 20)
            if imgui.button(label="L", width=22, height=22):
                print("L clicked")

        imgui.same_line()

        with ctx_begin_child(label="window__comment", width=0, height=460, border=True):
            imgui.text_wrapped(SAMPLE_COMMENT)


    ## BUTTONS
    with ctx_begin_child(label="window__actions", width=0, height=0, border=True):
        ### buttons
        with ctx_begin_group():
            imgui.dummy(64, 0)
            imgui.same_line()
            imgui.push_style_color(imgui.COLOR_BUTTON, r=167/255, g=34/255, b=0/255)
            imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, r=210/255, g=34/255, b=0/255)
            imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, r=255/255, g=34/255, b=0/255)
            imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 35)
            if imgui.button(label="REJECTED", width=100, height=50):
                print("REJECTED clicked")
            imgui.pop_style_var()
            imgui.pop_style_color(3)
            imgui.same_line()
            imgui.dummy(64, 0)
            imgui.same_line()
            imgui.push_style_color(imgui.COLOR_BUTTON, r=17/255, g=154/255, b=17/255)
            imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, r=17/255, g=194/255, b=17/255)
            imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, r=17/255, g=244/255, b=17/255)
            imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 35)
            if imgui.button(label="...maybe", width=100, height=50):
                print("MAYBE clicked")
            imgui.pop_style_var()
            imgui.pop_style_color(3)

        imgui.dummy(0, 20)

        ### notes & filter mode
        with ctx_begin_group():
            changed, notes_input = imgui.input_text_multiline(label="notes", value="", buffer_length=64*1024, width=400, height=100)
            imgui.same_line()
            imgui.dummy(30, 0)
            imgui.same_line()
            with ctx_begin_child(label="window__info", width=200, height=100, border=True):
                imgui.text("status here")
                imgui.text("modified here")
            imgui.same_line()
            imgui.push_item_width(150)
            changed, filter_selection = imgui.combo(label="filter", current=0, items=["all", "all un-statused", "rejected only", "maybe only"])
            imgui.pop_item_width()

    imgui.pop_font()

    imgui.end() # main window


def main() -> int:
    imgui.create_context()
    window = impl_glwf_init()
    impl = GlfwRenderer(window)

    io = imgui.get_io()
    verdana_16 = io.fonts.add_font_from_file_ttf("verdana.ttf", 16)
    impl.refresh_font_texture()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()
        #######################################


        draw_ui(default_font=verdana_16)


        #######################################
        gl.glClearColor(0.5, 0.5, 0.5, 1) # appears to set the main window background color...
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()

    return 0


if __name__ == "__main__":
    sys.exit(main())
