from PyQt5.QtCore import QObject
import os
import json
import re
from datetime import datetime


class AdBlocker(QObject):
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if AdBlocker._instance is not None:
            raise RuntimeError("Use AdBlocker.instance() to access the singleton")
        super().__init__()
        self.ad_rules = {
            'domains': set(),
            'regex_rules': [],
            'custom_rules': []
        }
        self.blocked_count = 0
        self.last_updated = datetime.now()
        self._load_rules()
        self._load_default_rules()

    def _load_rules(self):
        """Load ad-blocking rules from file"""
        rules_path = "data/adblock_rules.json"
        try:
            if os.path.exists(rules_path):
                with open(rules_path, 'r') as f:
                    data = json.load(f)
                    self.ad_rules['domains'] = set(data.get('domains', []))
                    self.ad_rules['regex_rules'] = [re.compile(rule) for rule in data.get('regex_rules', [])]
                    self.ad_rules['custom_rules'] = data.get('custom_rules', [])
                    self.last_updated = datetime.fromisoformat(data.get('last_updated', datetime.now().isoformat()))
        except Exception as e:
            print(f"Error loading adblock rules: {e}")

    def _load_default_rules(self):
        """Load default ad-blocking rules if none exist"""
        if not self.ad_rules['domains']:
            default_domains = [
                "doubleclick.net",
                "ads.google.com",
                "adserver.com",
                "banner-ad.com",
            ]
            self.ad_rules['domains'].update(default_domains)

        if not self.ad_rules['regex_rules']:
            default_regex = [
                r".*\.ads\..*",
                r".*adserver\..*",
                r".*banners?\..*",
            ]
            self.ad_rules['regex_rules'] = [re.compile(rule) for rule in default_regex]

    def should_block(self, url):
        """Check if a URL should be blocked"""
        if not url:
            return False

        try:
            url_lower = url.lower()
            domain = url_lower.split('/')[2] if len(url_lower.split('/')) > 2 else url_lower

            if domain in self.ad_rules['domains']:
                self.blocked_count += 1
                return True

            for regex in self.ad_rules['regex_rules']:
                if regex.match(url_lower):
                    self.blocked_count += 1
                    return True

            for rule in self.ad_rules['custom_rules']:
                if rule in url_lower:
                    self.blocked_count += 1
                    return True

            return False
        except Exception as e:
            print(f"Error checking URL {url}: {e}")
            return False

    def add_custom_rule(self, rule):
        """Add a custom ad-blocking rule"""
        self.ad_rules['custom_rules'].append(rule)
        self._save_rules()

    def remove_custom_rule(self, rule):
        """Remove a custom ad-blocking rule"""
        if rule in self.ad_rules['custom_rules']:
            self.ad_rules['custom_rules'].remove(rule)
            self._save_rules()

    def get_blocked_count(self):
        """Return the number of blocked requests"""
        return self.blocked_count

    def _save_rules(self):
        """Save ad-blocking rules to file"""
        rules_path = "data/adblock_rules.json"
        try:
            data = {
                'domains': list(self.ad_rules['domains']),
                'regex_rules': [rule.pattern for rule in self.ad_rules['regex_rules']],
                'custom_rules': self.ad_rules['custom_rules'],
                'last_updated': self.last_updated.isoformat()
            }
            with open(rules_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving adblock rules: {e}")

    def update_rules(self):
        """Update ad-blocking rules"""
        self.last_updated = datetime.now()
        self._save_rules()
