from service.file_service import FileService

class FilterService(object):
    def __init__(self):
        self.file_service = FileService()

        self.filters = self.file_service.load_json_file("resources/filters.json")



    def add_filter(self, keyword):
        if keyword in self.filters["filters"]:
            return False

        self.filters["filters"].append(keyword)
        self.file_service.save_json_file("resources/filters.json", self.filters)
        return True

    def remove_filter(self, keyword):
        try:
            self.filters["filters"].remove(keyword)
            self.file_service.save_json_file("resources/filters.json", self.filters)
            return True
        except ValueError:
            return False

