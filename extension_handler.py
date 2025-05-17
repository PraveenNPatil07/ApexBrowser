import os
import json

class ExtensionHandler:
    def __init__(self):
        self.extensions = {}
        self._load_extensions()

    def _load_extensions(self):
        """Load extensions from the extensions directory"""
        extensions_dir = "extensions"
        if not os.path.exists(extensions_dir):
            return

        for ext_dir in os.listdir(extensions_dir):
            manifest_path = os.path.join(extensions_dir, ext_dir, "manifest.json")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                        self.extensions[ext_dir] = {
                            'name': manifest.get('name', ext_dir),
                            'version': manifest.get('version', '1.0'),
                            'enabled': manifest.get('enabled', True),
                            'path': os.path.join(extensions_dir, ext_dir)
                        }
                except Exception as e:
                    print(f"Error loading extension {ext_dir}: {e}")

    def enable_extension(self, ext_id):
        """Enable an extension"""
        if ext_id in self.extensions:
            self.extensions[ext_id]['enabled'] = True
            self._save_extension_state(ext_id)

    def disable_extension(self, ext_id):
        """Disable an extension"""
        if ext_id in self.extensions:
            self.extensions[ext_id]['enabled'] = False
            self._save_extension_state(ext_id)

    def _save_extension_state(self, ext_id):
        """Save the extension's state to its manifest"""
        manifest_path = os.path.join(self.extensions[ext_id]['path'], "manifest.json")
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            manifest['enabled'] = self.extensions[ext_id]['enabled']
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=4)
        except Exception as e:
            print(f"Error saving extension state for {ext_id}: {e}")

    def get_extensions(self):
        """Return the list of extensions"""
        return self.extensions

    def execute_extension_script(self, ext_id, script):
        """Execute an extension script (placeholder)"""
        if ext_id in self.extensions and self.extensions[ext_id]['enabled']:
            print(f"Executing script from extension {ext_id}: {script}")
        else:
            print(f"Extension {ext_id} not found or disabled")
