import sys
import argparse
#import sqlite3
import pathlib
import json
import webbrowser
from typing import Optional, Union

import dearpygui.dearpygui as dpg
import pendulum

from commentdb import CommentDB, FilterMode


def iso_from_unix(unixtime: Optional[int]) -> str:
    if unixtime is None:
        return ""
    else:
        return pendulum.from_timestamp(unixtime).in_tz("America/Denver").isoformat()


def define_themes() -> None:
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

    with dpg.theme(tag="theme__hyperlink"): # lifted from demo.py
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 0, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [29, 151, 236, 25])
            dpg.add_theme_color(dpg.mvThemeCol_Text, [29, 151, 236])


def register_fonts() -> None:
    with dpg.font_registry():
        dpg.add_font("verdana.ttf", 14, tag="font__Verdana14")
        dpg.add_font("verdana.ttf", 16, tag="font__Verdana16")
        dpg.add_font("verdana.ttf", 18, tag="font__Verdana18")
        dpg.add_font("verdana.ttf", 20, tag="font__Verdana20")

        #dpg.add_font("verdanab.ttf", 14, tag="font__VerdanaBold14")

    dpg.bind_font("font__Verdana16") # sets the default


def refresh_ui_from_data(cdb) -> None:
    dpg.set_value("text__comment_id", cdb.comment_id)
    #dpg.set_value("text__url", cdb.url)
    dpg.set_value("text__comment_text", cdb.comment_text)
    dpg.set_value("input__notes", (cdb.notes or ""))
    dpg.set_value("text__status", (cdb.status or ""))
    dpg.set_value("text__modified", iso_from_unix(cdb.modified_unixtime))

    # buttons don't support updating their text so it has to be replaced
    url_button_parent = dpg.get_item_parent("button__url")
    dpg.delete_item("button__url")
    draw_url_button(url_button_parent, cdb.url)


def rejected_callback(sender, app_data, user_data) -> None:
    cdb = user_data
    notes = dpg.get_value("input__notes")
    cdb.reject(notes)
    #print(cdb.as_json_record, file=sys.stderr)
    cdb.next()
    refresh_ui_from_data(cdb)


def maybe_callback(sender, app_data, user_data) -> None:
    cdb = user_data
    notes = dpg.get_value("input__notes")
    cdb.maybe(notes)
    #print(cdb.as_json_record, file=sys.stderr)
    cdb.next()
    refresh_ui_from_data(cdb)


def up_arrow_callback(sender, app_data, user_data) -> None:
    cdb = user_data
    cdb.prev()
    refresh_ui_from_data(cdb)


def down_arrow_callback(sender, app_data, user_data) -> None:
    cdb = user_data
    cdb.next()
    refresh_ui_from_data(cdb)


def first_arrow_callback(sender, app_data, user_data) -> None:
    cdb = user_data
    cdb.first()
    refresh_ui_from_data(cdb)


def last_arrow_callback(sender, app_data, user_data) -> None:
    cdb = user_data
    cdb.last()
    refresh_ui_from_data(cdb)


def filter_mode_callback(sender, app_data, user_data) -> None:
    #print(f"filter_mode_callback({sender}, {app_data}, {user_data})", file=sys.stderr)
    cdb = user_data
    cdb.filter_mode = FilterMode(app_data)


def draw_url_button(parent_item: Union[int, str], url: str) -> None:
    dpg.add_button(tag="button__url", parent=parent_item, label=url, width=600, callback=lambda:webbrowser.open(url))
    dpg.bind_item_theme(dpg.last_item(), "theme__hyperlink")


def draw_ui(cdb) -> None:
    with dpg.window(tag="window__main", no_title_bar=True):
        # ID & LINK
        with dpg.child_window(label="window__header", autosize_x=True, height=40):
            with dpg.group(horizontal=True) as g:
                dpg.add_input_text(tag="text__comment_id", default_value=cdb.comment_id, readonly=True, width=95)
                #dpg.add_button(tag="button__url", label=cdb.url, width=600, callback=lambda:webbrowser.open(cdb.url))
                #dpg.bind_item_theme(dpg.last_item(), "theme__hyperlink")
                draw_url_button(g, cdb.url)


        # COMMENT TEXT & ARROWS
        with dpg.group(horizontal=True):
            # arrows
            with dpg.child_window(label="window__arrows", width=40, height=460):
                dpg.add_button(label="F", callback=first_arrow_callback, user_data=cdb, width=22, height=22)
                dpg.add_spacer(height=20)
                dpg.add_button(label="up", arrow=True, direction=dpg.mvDir_Up, callback=up_arrow_callback, user_data=cdb)
                dpg.add_spacer(height=20)
                dpg.add_button(label="down", arrow=True, direction=dpg.mvDir_Down, callback=down_arrow_callback, user_data=cdb)
                dpg.add_spacer(height=20)
                dpg.add_button(label="L", callback=last_arrow_callback, user_data=cdb, width=22, height=22)

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
                dpg.bind_item_font(dpg.last_item(), "font__Verdana20")

                dpg.add_button(tag="button__maybe", label="...maybe", callback=maybe_callback, user_data=cdb, width=100, height=50)
                dpg.bind_item_theme(dpg.last_item(), "theme__maybe_button")
                dpg.bind_item_font(dpg.last_item(), "font__Verdana20")

            dpg.add_spacer(height=20)

            # notes
            with dpg.group(horizontal=True):
                dpg.add_input_text(tag="input__notes", multiline=True, label="notes", width=400, height=100)

                dpg.add_spacer(width=30)

                with dpg.child_window(width=200, height=100):
                    dpg.add_text(tag="text__status", default_value=(cdb.status or ""))
                    dpg.add_text(tag="text__modified", default_value=iso_from_unix(cdb.modified_unixtime))

                filter_items=(FilterMode.ALL.value, FilterMode.ALL_UNSTATUSED.value, FilterMode.MAYBE_ONLY.value, FilterMode.REJECTED_ONLY.value)
                dpg.add_combo(items=filter_items, label="filter", default_value="All", callback=filter_mode_callback, user_data=cdb, width=150)

    dpg.set_primary_window("window__main", True)


def main(args) -> int:
    ### load data
    infile_path = pathlib.Path(args.json_file)
    input_data = [
        json.loads(x)
        for x in
        infile_path.open(mode="rt", encoding="utf-8").readlines()
        if len(x) > 0
    ]
    cdb = CommentDB(input_data)


    ### dearpygui initialization
    dpg.create_context()
    dpg.create_viewport(title="Who's Hiring?", width=1024, height=768, resizable=False)
    dpg.setup_dearpygui()


    ### our initialization
    define_themes()
    register_fonts()


    ### actually draw stuff
    draw_ui(cdb)


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
