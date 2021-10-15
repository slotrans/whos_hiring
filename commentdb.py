import time
import json


REJECTED="REJECTED"
MAYBE="MAYBE"

class CommentDB:
    def __init__(self, data):
        # data is a list of dicts
        self.data = data

        # cursor is the current index into `data`
        self.cursor = 0

    @property
    def comment_id(self):
        return self.data[self.cursor]["comment_id"]

    @property
    def url(self):
        return f"https://news.ycombinator.com/item?id={self.comment_id}"

    @property
    def comment_text(self):
        return self.data[self.cursor]["body"]

    @property
    def as_json_record(self):
        return json.dumps(self.data[self.cursor])

    def next(self):
        if self.cursor+1 > len(self.data):
            return False
            
        self.cursor += 1
        return True

    def prev(self):
        if self.cursor-1 < 0:
            return False

        self.cursor -= 1
        return True

    def reject(self, notes):
        self.data[self.cursor]["status"] = REJECTED
        if notes:
            self.data[self.cursor]["notes"] = notes
        self.data[self.cursor]["modified_unixtime"] = int(time.time())

    def maybe(self, notes):
        self.data[self.cursor]["status"] = MAYBE
        if notes:
            self.data[self.cursor]["notes"] = notes
        self.data[self.cursor]["modified_unixtime"] = int(time.time())
