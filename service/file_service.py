import json
import codecs


class FileService(object):

    def load_json_file(self, file_name):
        with codecs.open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_json_file(self, file_name, data):
        with codecs.open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, sort_keys=True, indent=2, ensure_ascii=False)
