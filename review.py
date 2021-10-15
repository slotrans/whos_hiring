import sys
import argparse
#import sqlite3
import pathlib
import json

import dearpygui.dearpygui as dpg

import commentdb


def define_themes():
    with dpg.theme(tag="theme__rejected_button"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (167, 34, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 34, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (210, 34, 0))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 35)

    with dpg.theme(tag="theme__maybe_button"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (17, 154, 17))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (17, 194, 17))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (17, 244, 17))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 35)


def register_fonts():
    with dpg.font_registry():
        dpg.add_font("verdana.ttf", 14, tag="font__Verdana14")
        dpg.add_font("verdana.ttf", 16, tag="font__Verdana16")
        dpg.add_font("verdana.ttf", 18, tag="font__Verdana18")
        dpg.add_font("verdana.ttf", 20, tag="font__Verdana20")

        #dpg.add_font("verdanab.ttf", 14, tag="font__VerdanaBold14")

    dpg.bind_font("font__Verdana16") # sets the default


def rejected_callback(sender, app_data, user_data):
    notes = dpg.get_value("input__notes")
    dpg.set_value("text__comment_text", f"REJECTED! (not yet implemented)\nnotes={notes}")


def maybe_callback(sender, app_data, user_data):
    notes = dpg.get_value("input__notes")
    dpg.set_value("text__comment_text", f"...maybe! (not yet implemented)\nnotes={notes}")


def up_arrow_callback(sender, app_data, user_data):
    cdb = user_data
    cdb.prev()

    dpg.set_value("text__comment_id", cdb.comment_id)
    dpg.set_value("text__url", cdb.url)
    dpg.set_value("text__comment_text", cdb.comment_text)


def down_arrow_callback(sender, app_data, user_data):
    cdb = user_data
    cdb.next()

    dpg.set_value("text__comment_id", cdb.comment_id)
    dpg.set_value("text__url", cdb.url)
    dpg.set_value("text__comment_text", cdb.comment_text)


def main(args) -> int:
    ### load data
    infile_path = pathlib.Path(args.json_file)
    input_data = [
        json.loads(x) 
        for x in 
        infile_path.open(mode="rt", encoding="utf-8").readlines() 
        if len(x) > 0
    ]
    cdb = commentdb.CommentDB(input_data)


    ### dearpygui initialization
    dpg.create_context()
    dpg.create_viewport(width=1024, height=768, resizable=False)
    dpg.setup_dearpygui()


    ### our initialization
    define_themes()
    register_fonts()


    ### actually draw stuff
    with dpg.window(
        label="Example Window", 
        no_title_bar=True, 
        width=1010, 
        height=768,
    ):
        # ID & LINK
        with dpg.child_window(label="window__header", autosize_x=True, height=40):
            with dpg.group(horizontal=True):
                dpg.add_input_text(tag="text__comment_id", default_value=cdb.comment_id, readonly=True, width=95)
                dpg.add_input_text(tag="text__url", default_value=cdb.url, readonly=True, width=600)
        

        # COMMENT TEXT & ARROWS
        with dpg.group(horizontal=True):
            # arrows
            with dpg.child_window(label="window__arrows", width=40, height=460):
                dpg.add_spacer(height=20)
                dpg.add_button(label="up", arrow=True, direction=dpg.mvDir_Up, callback=up_arrow_callback, user_data=cdb)
                dpg.add_spacer(height=20)
                dpg.add_button(label="down", arrow=True, direction=dpg.mvDir_Down, callback=down_arrow_callback, user_data=cdb)

            # comment text
            with dpg.child_window(label="window__comment", autosize_x=True, height=460):
                dpg.add_text(tag="text__comment_text", wrap=750, default_value=cdb.comment_text)
                dpg.bind_item_font(dpg.last_item(), "font__Verdana18")


        # BUTTONS & NOTES
        with dpg.child_window(label="window__actions", autosize_x=True, autosize_y=True):
            # buttons
            with dpg.group(horizontal=True, horizontal_spacing=64):
                dpg.add_spacer()

                dpg.add_button(tag="button__rejected", label="REJECTED", callback=rejected_callback, user_data=cdb, width=100, height=50)
                dpg.bind_item_theme(dpg.last_item(), "theme__rejected_button")

                dpg.add_button(tag="button__maybe", label="...maybe", callback=maybe_callback, user_data=cdb, width=100, height=50)
                dpg.bind_item_theme(dpg.last_item(), "theme__maybe_button")

            dpg.add_spacer(height=20)

            # notes
            dpg.add_input_text(tag="input__notes", multiline=True, label="notes", width=400, height=100)

        
    ### dearpygui startup & shutdown
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hacker News \"Who's Hiring\" review tool")
    #parser.add_argument("--db-file", required=True, help="SQLite database file to work with")
    parser.add_argument("--json-file", required=True, help="line-delimited JSON file of input data")
    args = parser.parse_args()

    sys.exit(main(args))
