from service.file_service import FileService

from bs4 import BeautifulSoup
import requests


class LoLBoardsGetter(object):
    def __init__(self):
        self.file_service = FileService()
        self.link = "https://boards.tr.leagueoflegends.com/tr/?sort_type=recent"
        self.raw_data = "failed"
        self.json_data = self.get_checked_threads()
        self.checked_thread_ids = self.json_data["checkedThreads"]

    def get_data(self):
        try:
            return requests.get(self.link, timeout=5).text
        except requests.RequestException:
            return "failed"

    def get_checked_threads(self):
        return self.file_service.load_json_file("resources/checked_threads.json")

    def set_checked_threads(self):
        self.file_service.save_json_file("resources/checked_threads.json", self.json_data)

    def check_new_posts(self):
        self.raw_data = self.get_data()
        if self.raw_data != "failed":
            thread_list = []

            data = BeautifulSoup(self.raw_data, "html.parser")
            discussions = data.find("tbody", {"id": "discussion-list"})
            threads = discussions.find_all("tr", {"class": "discussion-list-item row"})

            for thread in threads:
                parsed_data = thread.find_all("td")

                if len(parsed_data) == 5:
                    votes, title_html, riot_commented, number_of_comments, views = parsed_data
                else:
                    votes, thumbnail, title_html, riot_commented, number_of_comments, views = parsed_data

                spans = title_html.find_all("span")

                username = "Unknown"
                realm = "(unknown)"
                author_url = "https://boards.tr.leagueoflegends.com/tr/player/TR/{0}"
                author_icon = "https://avatar.leagueoflegends.com/tr/{0}.png"

                if len(spans) == 2:
                    # ANNOUNCEMENT
                    title_span, time_span = spans
                    username = "Riot Games"
                    realm = "(TR)"
                    author_url = "https://tr.leagueoflegends.com/tr/news/"
                    author_icon = "https://www.riotgames.com/darkroom/original/06fc475276478d31c559355fa475888c:af22b5d4c9014d23b550ea646eb9dcaf/riot-logo-fist-only.png"

                elif len(spans) == 4:
                    # NORMAL THREAD
                    title_span, username_span, realm_spam, time_span = spans
                    username = username_span.text
                    realm = realm_spam.text
                    author_icon = author_icon.format(username)
                    author_url =author_url.format(username)

                elif len(spans) == 6:
                    # NORMAL THREAD WITH URL
                    title_span, icon_url, icon_info, username_span, realm_spam, time_span = spans
                    username = username_span.text
                    realm = realm_spam.text
                    author_icon =author_icon.format(username)
                    author_url = author_url.format(username)

                board2 = title_html.find("div", {"class": "discussion-footer byline opaque"})
                board = board2.find_all("a")

                thread_id = votes.div["data-apollo-discussion-id"]
                thread_url = "https://boards.tr.leagueoflegends.com/%s" % title_html.a["href"]
                title = title_span.text
                post = title_span["title"]
                post_time = time_span["title"]

                if len(board) == 1:
                    board = board[0].text
                else:
                    board = board[1].text

                post = post.replace("&uuml;", "ü").replace("&Uuml;", "Ü").replace("&ccedil;", "ç")\
                    .replace("&Ccedil;", "Ç")

                if thread_id in self.checked_thread_ids:
                    continue

                thread_info = {"thread_id": thread_id, "thread_url": thread_url, "thread_title": title, "post": post,
                               "post_time": post_time, "username": username, "realm": realm, "board": board,
                               "author_icon": author_icon, "author_url": author_url}

                thread_list.append(thread_info)
                self.json_data["checkedThreads"].append(thread_id)

            self.set_checked_threads()
            return thread_list

        else:
            return []
