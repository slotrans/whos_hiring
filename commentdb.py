from __future__ import annotations

import time
import json
import enum
import sqlite3
from typing import Optional, TextIO
import sys


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


    @staticmethod
    def from_json_file(fd: TextIO) -> CommentDB:
        data = [json.loads(x) for x in fd.readlines() if len(x) > 0]
        return CommentDB(data)


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


###############################################################################


class SqliteCommentDB:
    def __init__(self, dbconn):
        dbconn.row_factory = SqliteCommentDB._dict_row
        self.dbconn = dbconn

        self.filter_mode = FilterMode.ALL

        self.first()

    @property
    def comment_id(self) -> int:
        return self.current_record["comment_id"]

    @property
    def url(self) -> str:
        return f"https://news.ycombinator.com/item?id={self.comment_id}"

    @property
    def comment_text(self) -> str:
        return self.current_record["body"]

    @property
    def status(self) -> Optional[str]:
        return self.current_record.get("status", None)

    @property
    def modified_unixtime(self) -> Optional[int]:
        return self.current_record.get("modified_unixtime", None)

    @property
    def notes(self) -> Optional[str]:
        return self.current_record.get("notes", None)

    @property
    def as_json_record(self) -> str:
        return json.dumps(self.current_record)


    @staticmethod
    def _dict_row(cursor, row): # pasted from the docs https://docs.python.org/3/library/sqlite3.html
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d


    @staticmethod
    def _initialize_db(db_file_name: str) -> sqlite3.Connection:
        dbconn = sqlite3.connect(db_file_name, check_same_thread=False)

        dbconn.execute("""
            create table comment
            (
              comment_id         integer primary key  not null
            , body               text                 not null
            , status             text
            , notes              text
            , modified_unixtime  integer
            )
        """.strip())

        dbconn.commit()

        return dbconn


    @staticmethod
    def import_json_file(fd: TextIO, db_file_name: str) -> SqliteCommentDB:
        dbconn = SqliteCommentDB._initialize_db(db_file_name)

        for line in fd.readlines():
            if len(line) == 0:
                continue

            temp_record = json.loads(line)
            dbconn.execute("insert into comment(comment_id, body) values(:comment_id, :body)", temp_record)

        dbconn.commit()

        return SqliteCommentDB(dbconn)


    @staticmethod
    def from_db_file(db_file_name: str) -> SqliteCommentDB:
        dbconn = sqlite3.connect(db_file_name, check_same_thread=False)
        return SqliteCommentDB(dbconn)


    @property
    def _filter_clause(self) -> str:
        if self.filter_mode == FilterMode.ALL:
            return "(1=1)"
        elif self.filter_mode == FilterMode.ALL_UNSTATUSED:
            return "(status is null)"
        elif self.filter_mode == FilterMode.MAYBE_ONLY:
            return f"(status = '{MAYBE}')"
        elif self.filter_mode == FilterMode.REJECTED_ONLY:
            return f"(status = '{REJECTED}')"


    def next(self) -> bool:
        query = f"""
            select *
              from comment
             where comment_id > :current_id
               and {self._filter_clause}
             order by comment_id
             limit 1
        """.strip()
        params = dict(current_id=self.comment_id)
        for rec in self.dbconn.execute(query, params):
            self.current_record = rec
            return True

        return False


    def prev(self) -> bool:
        query = f"""
            select *
              from comment
             where comment_id < :current_id
               and {self._filter_clause}
             order by comment_id desc
             limit 1
        """.strip()
        params = dict(current_id=self.comment_id)
        for rec in self.dbconn.execute(query, params):
            self.current_record = rec
            return True

        return False


    def first(self) -> bool:
        query = """
            select *
              from comment
             order by comment_id
             limit 1
        """.strip()
        for rec in self.dbconn.execute(query):
            self.current_record = rec
            return True


    def last(self) -> bool:
        query = """
            select *
              from comment
             order by comment_id desc
             limit 1
        """.strip()
        for rec in self.dbconn.execute(query):
            self.current_record = rec
            return True


    def reject(self, notes: str) -> None:
        query = """
            update comment
               set status = :status
                 , notes = :notes
                 , modified_unixtime = :modified_unixtime
             where comment_id = :comment_id
        """.strip()
        params = {
            "status": REJECTED,
            "notes": notes,
            "modified_unixtime": int(time.time()),
            "comment_id": self.comment_id,
        }
        self.dbconn.execute(query, params)
        self.dbconn.commit()


    def maybe(self, notes: str) -> None:
        query = """
            update comment
               set status = :status
                 , notes = :notes
                 , modified_unixtime = :modified_unixtime
             where comment_id = :comment_id        """.strip()
        params = {
            "status": MAYBE,
            "notes": notes,
            "modified_unixtime": int(time.time()),
            "comment_id": self.comment_id,
        }
        self.dbconn.execute(query, params)
        self.dbconn.commit()
