import sys
import argparse
import sqlite3

import dearpygui.dearpygui as dpg


SAMPLE_COMMENT="""Clio | www.clio.com/about/careers/

Location: Canada or California (we are a remote-first org but we also have offices in Vancouver, Calgary and Toronto for those who like seeing people face-to-face sometimes)

We create low-barrier, affordable software for lawyers to manage and grow their law firms effectively so they can offer their services to those who need it the most. We also make it easier for their clients to collaborate with them to create a more inclusive legal system for all. Our mission is to \"transform the legal experience for all\".

What have we been up to? In May of this year, we closed our Series E, giving us a valuation of $1.6B USD and marked us as the first legal practice management unicorn globally! We also just acquired a court document automation company, our 2nd acquisition this year.And recently we just passed the 700 employee mark.

We are hiring across all roles, including security, SRE, engineering, and more.

Interested? Email me at elise.mance (at) clio.com"""


def define_themes():
    with dpg.theme(tag="theme__rejected_button"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (167, 34, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 34, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (210, 34, 0))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 35)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 20, 20)    

    with dpg.theme(tag="theme__maybe_button"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (17, 154, 17))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (17, 194, 17))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (17, 244, 17))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 35)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 20, 20)  


def register_fonts():
    with dpg.font_registry():
        dpg.add_font("verdana.ttf", 14, tag="font__Verdana14")
        dpg.add_font("verdana.ttf", 16, tag="font__Verdana16")
        dpg.add_font("verdana.ttf", 18, tag="font__Verdana18")
        dpg.add_font("verdana.ttf", 20, tag="font__Verdana20")

        #dpg.add_font("verdanab.ttf", 14, tag="font__VerdanaBold14")

    dpg.bind_font("font__Verdana14") # sets the default


def main(args) -> int:
    dpg.create_context()
    dpg.create_viewport(width=1280, height=720, resizable=False)
    dpg.setup_dearpygui()

    define_themes()
    register_fonts()

    with dpg.window(
        label="Example Window", 
        no_title_bar=True, 
        width=1280, 
        height=720,
    ):
        with dpg.group(horizontal=True, pos=[50, 50]):
            dpg.add_input_text(default_value="comment ID", readonly=True, width=95)
            dpg.add_input_text(default_value="HN link to particular comment here", readonly=True, width=600)
        
        dpg.add_input_text(multiline=True, width=800, height=300, pos=[50, 75], default_value=SAMPLE_COMMENT)

        dpg.add_button(label="up", arrow=True, direction=dpg.mvDir_Up, pos=[860,90])
        dpg.add_button(label="down", arrow=True, direction=dpg.mvDir_Down, pos=[860,120])

        dpg.add_button(label="REJECTED", width=100, height=50, pos=[150,400])
        dpg.bind_item_theme(dpg.last_item(), "theme__rejected_button")
        #dpg.bind_item_font(dpg.last_item(), "font__Tahoma14")

        dpg.add_button(label="...maybe", width=100, height=50, pos=[350, 400])
        dpg.bind_item_theme(dpg.last_item(), "theme__maybe_button")

        dpg.add_input_text(multiline=True, label="notes", width=400, height=100, pos=[100, 475])


        # just some riffing to see where these positions end up...
        #dpg.add_button(label="0", arrow=True, direction=dpg.mvDir_Down, pos=[0,0])
        #dpg.add_button(label="20", arrow=True, direction=dpg.mvDir_Down, pos=[20,20])
        #dpg.add_button(label="40", arrow=True, direction=dpg.mvDir_Down, pos=[40,40])
        #dpg.add_button(label="60", arrow=True, direction=dpg.mvDir_Down, pos=[60,60])
        #dpg.add_button(label="80", arrow=True, direction=dpg.mvDir_Down, pos=[80,80])

        

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hacker News \"Who's Hiring\" review tool")
    parser.add_argument("--db-file", required=True, help="SQLite database file to work with")
    args = parser.parse_args()

    sys.exit(main(args))
