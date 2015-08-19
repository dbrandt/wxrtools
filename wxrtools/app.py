import pprint
from collections import deque

from .wxr import wxr_parser, fast_iter


def printer_app(fname):
    with open(fname) as f:
        p = wxr_parser(f)
        for ev, el in fast_iter(p):
            print ev, el


class Extractor(object):
    STATE_CHANNEL = 1
    STATE_ITEM = 2
    STATE_AUTHOR = 3
    STATE_IMAGE = 4
    STATE_COMMENT = 5
    STATE_ATTACHMENT = 6

    def __init__(self):
        self.ns_map = {}
        self.state_stack = deque()
        self.blog = {}
        self.author = None
        self.authors = []
        self.image = {}
        self.itunes = {}

    @property
    def state(self):
        if self.state_stack:
            return self.state_stack[-1]
        return 0

    def add_ns(self, prefix, url):
        self.ns_map[prefix] = url

    def switch_state(self, e):
        if e.tag == "channel":
            self.state_stack.append(self.STATE_CHANNEL)
        elif e.tag == "{%(wp)s}author" % self.ns_map:
            self.state_stack.append(self.STATE_AUTHOR)
            self.author = {}
        elif e.tag == "image":
            self.state_stack.append(self.STATE_IMAGE)
        elif e.tag == "item":
            self._current_item = {}
            self.state_stack.append(self.STATE_ITEM)

    def feed(self, e):
        if self.state == self.STATE_CHANNEL:
            if e.tag in ("title", "link", "description", "language"):
                self.blog[e.tag] = e.text
            elif e.prefix == "itunes":
                if e.tag.endswith("image"):
                    self.itunes[e.tag.replace("{%(itunes)s}" % self.ns_map, "")] = e.get("href")
                else:
                    self.itunes[e.tag.replace("{%(itunes)s}" % self.ns_map, "")] = e.text
            elif e.tag == "channel":
                self.state_stack.pop()


        elif self.state == self.STATE_AUTHOR:
            if e.tag == "{%(wp)s}author_id" % self.ns_map:
                self.author["id"] = e.text
            elif e.tag == "{%(wp)s}author_login" % self.ns_map:
                self.author["login"] = e.text
            elif e.tag == "{%(wp)s}author_email" % self.ns_map:
                self.author["email"] = e.text
            elif e.tag == "{%(wp)s}author_display_name" % self.ns_map:
                self.author["display_name"] = e.text
            elif e.tag == "{%(wp)s}author_first_name" % self.ns_map:
                self.author["first_name"] = e.text
            elif e.tag == "{%(wp)s}author_last_name" % self.ns_map:
                self.author["last_name"] = e.text
            elif e.tag == "{%(wp)s}base_blog_url" % self.ns_map:
                self.blog["base_blog_url"] = e.text
            elif e.tag == "{%(wp)s}base_site_url" % self.ns_map:
                self.blog["base_site_url"] = e.text
            elif e.tag == "{%(wp)s}author" % self.ns_map:
                self.authors.append(self.author)
                self.author = None
                self.state_stack.pop()

        elif self.state == self.STATE_IMAGE:
            if e.tag in ("title", "url", "link"):
                self.image[e.tag] = e.text
            elif e.tag == "image":
                self.state_stack.pop()


        elif self.state == self.STATE_ITEM:
            if e.tag in ("title", "link", "pubDate", "guid", "description"):
                self._current_item[e.tag] = e.text
            elif e.tag == "category":
                if e.get("domain") == "category":
                    if "categories" not in self._current_item:
                        self._current_item["categories"] = []
                    self._current_item["categories"].append(
                        {"name": e.text, "nicename": e.get("nicename")})
                elif e.get("domain") == "tag":
                    if "tags" not in self._current_item:
                        self._current_item["tags"] = []
                    self._current_item["tags"].append(
                        {"name": e.text, "nicename": e.get("nicename")})

            elif e.prefix == "dc" and e.tag == "{%(dc)s}creator" % self.ns_map:
                self._current_item["creator"] = e.text
            elif e.prefix == "content" and e.tag == "{%(content)s}encoded" % self.ns_map:
                self._current_item["content"] = e.text
            elif e.prefix == "excerpt" and e.tag == "{%(excerpt)s}encoded" % self.ns_map:
                self._current_item["excerpt"] = e.text
            elif e.prefix == "wp":
                if e.tag == "{%(wp)s}post_id" % self.ns_map:
                    self._current_item["post_id"] = e.text
                elif e.tag == "{%(wp)s}post_date" % self.ns_map:
                    self._current_item["post_date"] = e.text
                elif e.tag == "{%(wp)s}post_date_gmt" % self.ns_map:
                    self._current_item["post_date_gmt"] = e.text
                elif e.tag == "{%(wp)s}comment_status" % self.ns_map:
                    self._current_item["comment_status"] = e.text
                elif e.tag == "{%(wp)s}ping_status" % self.ns_map:
                    self._current_item["ping_status"] = e.text
                elif e.tag == "{%(wp)s}post_name" % self.ns_map:
                    self._current_item["post_name"] = e.text
                elif e.tag == "{%(wp)s}status" % self.ns_map:
                    self._current_item["status"] = e.text
                elif e.tag == "{%(wp)s}post_parent" % self.ns_map:
                    self._current_item["post_parent"] = e.text
                elif e.tag == "{%(wp)s}menu_order" % self.ns_map:
                    self._current_item["menu_order"] = e.text
                elif e.tag == "{%(wp)s}post_type" % self.ns_map:
                    self._current_item["post_type"] = e.text
                elif e.tag == "{%(wp)s}post_password" % self.ns_map:
                    self._current_item["post_password"] = e.text
                elif e.tag == "{%(wp)s}is_sticky" % self.ns_map:
                    self._current_item["is_sticky"] = e.text

            elif e.tag == "item":
                if self._current_item.get("status") == "publish":
                    pprint.pprint(self._current_item)
                    # print "title: %(title)s" % self._current_item
                    # print "link: %(link)s" % self._current_item
                    # print "pubDate: %(pubDate)s" % self._current_item
                    # print "type: %(post_type)s\n" % self._current_item


                # XXX This is where to hook up the code that actually does something
                # with each item.

                del self._current_item
                self.state_stack.pop()

def exctractor_app(fname):
    with open(fname) as f:
        ex = Extractor()
        p = wxr_parser(f)
        for ev, el in fast_iter(p):
            if ev == "start-ns":
                ex.add_ns(*el)
            elif ev == "start":
                ex.switch_state(el)
            elif ev == "end":
                ex.feed(el)

        print ex.blog
        print ex.authors
        print ex.image
        print ex.itunes
