import pprint
from collections import deque

from .wxr import wxr_parser, fast_iter


class BaseHandler(object):
    """Base object to show what a Handler object needs to do.

    The WXR data is extracted in an incremental fashion and the Handler object
    is the reciever of the events triggered as data is encountered. This makes
    you free to ignore certain data, save data for later processing, printing
    it (like the included PrintHandler), push it on a queue, save it to a
    database... you get the idea. Do whatever suits your application.

    Data fed to the handlers are always dicts, and I try to extract all I know
    to be relevant. WordPress exports tend to include all kinds of random things
    though, and not seldom things that break XML.
    """

    def handle_author(self, author_data):
        """Authors may be one or more per export file, you may want to
        collect these as they come into an array or something and not
        just grab the first one you get (or overwrite what you already have)."""
        pass

    def handle_image(self, image_data):
        """This image data is related to the channel, not a particular item. As
        such, you should only get one, but you never know with WordPress exports."""
        pass

    def handle_itunes(self, itunes_data):
        """This is not always present. It's the general data that identify a
        RSS feed (WXR is built ontop RSS) that's valid as a podcast feed. I can't
        see what point there is for it to be in an export file, but hey, extra
        data."""
        pass

    def handle_blog(self, blog_data):
        """Used to collect general blog data. It will come at the very end of
        parsing the file since it's not technically done until then."""
        pass

    def handle_item(self, item_data):
        """Items can be all sorts of things. Pages, media, posts, attachments,
        drafts... It's up to you to handle them as you want (if you want). This
        method will be called a lot. Beware that autosaved drafts might be
        appear here. Attachments might follow a post, these are your chance to
        catch images to download that might be present in the post.

        Beware of saving these in an array for later processing. You will run
        out of memory."""
        pass


class PrintHandler(BaseHandler):
    def handle_item(self, item_data):
        if item_data.get("status") == "publish":
            pprint.pprint(item_data)
            # print "title: %(title)s" % self._current_item
            # print "link: %(link)s" % self._current_item
            # print "pubDate: %(pubDate)s" % self._current_item
            # print "type: %(post_type)s\n" % self._current_item


class Extractor(object):
    STATE_CHANNEL = 1
    STATE_ITEM = 2
    STATE_AUTHOR = 3
    STATE_IMAGE = 4
    STATE_COMMENT = 5
    STATE_ATTACHMENT = 6

    def __init__(self, handler=BaseHandler):
        self.ns_map = {}
        self.state_stack = deque()
        self.blog = {}
        self.author = None
        self.image = {}
        self.handler = handler()

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
                    self.handler.handle_itunes(
                        {e.tag.replace("{%(itunes)s}" % self.ns_map, ""): e.get("href")})
                else:
                    self.handler.handle_itunes(
                        {e.tag.replace("{%(itunes)s}" % self.ns_map, ""): e.text})
            elif e.tag == "channel":
                self.handler.handle_blog(self.blog)
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
                self.handler.handle_author(self.author)
                self.state_stack.pop()

        elif self.state == self.STATE_IMAGE:
            if e.tag in ("title", "url", "link"):
                self.image[e.tag] = e.text
            elif e.tag == "image":
                self.handler.handle_image(self.image)
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
                self.handler.handle_item(self._current_item)
                self.state_stack.pop()



def app(fname, handler=PrintHandler):
    with open(fname) as f:
        ex = Extractor(handler=handler)
        p = wxr_parser(f)
        for ev, el in fast_iter(p):
            if ev == "start-ns":
                ex.add_ns(*el)
            elif ev == "start":
                ex.switch_state(el)
            elif ev == "end":
                ex.feed(el)
