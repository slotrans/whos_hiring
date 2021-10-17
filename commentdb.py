import time
import json
import enum
from typing import Optional


REJECTED="REJECTED"
MAYBE="MAYBE"


class FilterMode(enum.Enum):
    ALL = "All"
    ALL_UNSTATUSED = "All un-statused"
    MAYBE_ONLY = "MAYBE only"
    REJECTED_ONLY = "REJECTED only"


class CommentDB:
    def __init__(self, data):
        # data is a list of dicts
        self.data = data

        # cursor is the current index into `data`
        self.cursor = 0

        # filter mode determines what data elements will be included/skipped when moving the cursor
        self.filter_mode = FilterMode.ALL

    @property
    def comment_id(self) -> int:
        return self.data[self.cursor]["comment_id"]

    @property
    def url(self) -> str:
        return f"https://news.ycombinator.com/item?id={self.comment_id}"

    @property
    def comment_text(self) -> str:
        return self.data[self.cursor]["body"]

    @property
    def status(self) -> Optional[str]:
        return self.data[self.cursor].get("status", None)

    @property
    def modified_unixtime(self) -> Optional[int]:
        return self.data[self.cursor].get("modified_unixtime", None)

    @property
    def notes(self) -> Optional[str]:
        return self.data[self.cursor].get("notes", None)

    @property
    def as_json_record(self) -> str:
        return json.dumps(self.data[self.cursor])


    # this is pretty dumb
    def _passes_filter(self, element: dict) -> bool:
        if self.filter_mode == FilterMode.ALL:
            return True
        elif self.filter_mode == FilterMode.ALL_UNSTATUSED:
            return "status" not in element
        elif self.filter_mode == FilterMode.MAYBE_ONLY:
            return element.get("status", "") == MAYBE
        elif self.filter_mode == FilterMode.REJECTED_ONLY:
            return element.get("status", "") == REJECTED


    #def next(self) -> bool:
    #    if self.cursor+1 > len(self.data):
    #        return False
    #        
    #    self.cursor += 1
    #    return True
    def next(self) -> bool:
        temp_cursor = self.cursor

        while True:
            temp_cursor += 1

            if temp_cursor >= len(self.data):
                # we scrolled past the end of the data without finding an element that passes the filter
                return False

            if self._passes_filter(self.data[temp_cursor]):
                self.cursor = temp_cursor
                return True


    #def prev(self) -> bool:
    #    if self.cursor-1 < 0:
    #        return False
    #
    #    self.cursor -= 1
    #    return True
    def prev(self) -> bool:
        temp_cursor = self.cursor

        while True:
            temp_cursor -= 1

            if temp_cursor < 0:
                # we scrolled past the start of the data without finding an element that passes the filter
                return False

            if self._passes_filter(self.data[temp_cursor]):
                self.cursor = temp_cursor
                return True


    def first(self) -> bool:
        self.cursor = 0
        return True


    def last(self) -> bool:
        self.cursor = len(self.data)-1
        return True


    def reject(self, notes: str) -> None:
        self.data[self.cursor]["status"] = REJECTED
        if notes:
            self.data[self.cursor]["notes"] = notes
        self.data[self.cursor]["modified_unixtime"] = int(time.time())


    def maybe(self, notes: str) -> None:
        self.data[self.cursor]["status"] = MAYBE
        if notes:
            self.data[self.cursor]["notes"] = notes
        self.data[self.cursor]["modified_unixtime"] = int(time.time())
