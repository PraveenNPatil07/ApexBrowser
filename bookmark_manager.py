import os
import json
from datetime import datetime

class BookmarkManager:
    def __init__(self):
        self.bookmarks = []
        self.tags = set()
        self._load_bookmarks()

    def _load_bookmarks(self):
        """Load bookmarks from file"""
        try:
            if os.path.exists("data/bookmarks.json"):
                with open("data/bookmarks.json", 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.bookmarks = data.get('bookmarks', [])
                        self.tags = set(data.get('tags', []))
                    elif isinstance(data, list):
                        self.bookmarks = data
                        self.tags = set()
                    else:
                        raise ValueError("Invalid bookmarks.json format")
            else:
                self.bookmarks = []
                self.tags = set()
        except Exception as e:
            print(f"Error loading bookmarks: {e}")
            self.bookmarks = []
            self.tags = set()

    def _save_bookmarks(self):
        """Save bookmarks to file"""
        try:
            data = {
                'bookmarks': self.bookmarks,
                'tags': list(self.tags)
            }
            with open("data/bookmarks.json", 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving bookmarks: {e}")

    def add_bookmark(self, url, title, tags=None):
        """Add a new bookmark"""
        bookmark = {
            'url': url,
            'title': title,
            'date_added': datetime.now().isoformat(),
            'tags': tags if tags else []
        }
        self.bookmarks.append(bookmark)
        if tags:
            self.tags.update(tags)
        self._save_bookmarks()

    def remove_bookmark(self, url):
        """Remove a bookmark by URL"""
        self.bookmarks = [bookmark for bookmark in self.bookmarks if bookmark['url'] != url]
        self._save_bookmarks()

    def get_bookmarks(self):
        """Return all bookmarks"""
        return self.bookmarks

    def get_bookmarks_by_tag(self, tag):
        """Return bookmarks with the specified tag"""
        return [bookmark for bookmark in self.bookmarks if tag in bookmark.get('tags', [])]

    def add_tag(self, url, tag):
        """Add a tag to a bookmark"""
        for bookmark in self.bookmarks:
            if bookmark['url'] == url:
                if 'tags' not in bookmark:
                    bookmark['tags'] = []
                if tag not in bookmark['tags']:
                    bookmark['tags'].append(tag)
                    self.tags.add(tag)
        self._save_bookmarks()

    def remove_tag(self, url, tag):
        """Remove a tag from a bookmark"""
        for bookmark in self.bookmarks:
            if bookmark['url'] == url and 'tags' in bookmark:
                if tag in bookmark['tags']:
                    bookmark['tags'].remove(tag)
                    if not bookmark['tags']:
                        del bookmark['tags']
        self.tags.discard(tag)
        self._save_bookmarks()