from bs4 import BeautifulSoup
import requests
import json


class LoLBoardsGetter(object):
    def __init__(self):
        self.link = "https://boards.tr.leagueoflegends.com/tr/?sort_type=recent"
        self.raw_data = "failed"
        self.json_data = self.get_checked_threads()
        self.checked_thread_ids = self.json_data["threads"]

    def get_data(self):
        try:
            return requests.get(self.link, timeout=5).text
        except requests.RequestException:
            return "failed"

    def get_checked_threads(self):
        with open("discordutils/threads_checked.json", "r") as f:
            return json.load(f)

    def set_checked_threads(self):
        with open("discordutils/threads_checked.json", "w") as f:
            json.dump(self.json_data, f, sort_keys=True, indent=2)

    def check_new_posts(self):
        self.raw_data = self.get_data()
        if self.raw_data != "failed":
            thread_list = []

            data = BeautifulSoup(self.raw_data, "html.parser")
            discussions = data.find("tbody", {"id": "discussion-list"})
            threads = discussions.find_all("tr", {"class": "discussion-list-item row "})

            for thread in threads:
                parsed_data = thread.find_all("td")

                if len(parsed_data) == 5:
                    votes, title_html, riot_commented, number_of_comments, views = parsed_data
                else:
                    votes, thumbnail, title_html, riot_commented, number_of_comments, views = parsed_data

                spans = title_html.find_all("span")

                if len(spans) == 2:
                    # ANNOUNCEMENT
                    title_span, time_span = spans
                    username = "RiotGames"
                    realm = "(TR)"

                elif len(spans) == 4:
                    # NORMAL THREAD
                    title_span, username_span, realm_spam, time_span = spans
                    username = username_span.text
                    realm = realm_spam.text

                elif len(spans) == 6:
                    # NORMAL THREAD WITH URL
                    title_span, icon_url, icon_info, username_span, realm_spam, time_span = spans
                    username = username_span.text
                    realm = realm_spam.text

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
                               "post_time": post_time, "username": username, "realm": realm, "board": board}

                thread_list.append(thread_info)
                self.json_data["threads"].append(thread_id)

            self.set_checked_threads()
            return thread_list

        else:
            return []