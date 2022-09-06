from time import time
import requests
import hmac
import hashlib
import urllib3
from urllib.parse import urlencode
try:
    import ujson as json
except:
    import json

nonce = "b1ab87b4800d4d4590a11701b8551afa"
api_key = "C69BAF41DA5ABD1FFEDC6D2FEA56B"
secret_key = r"~d}$Q7$eIni=V)9\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"
base = "https://picaapi.picacomic.com/"
categories = ["重口地帶","Cosplay","歐美","禁書目錄","WEBTOON","東方","Fate","SAO 刀劍神域","Love Live","艦隊收藏","非人類","強暴","NTR","人妻","足の恋","性轉換","SM","妹妹系","姐姐系","扶他樂園","後宮閃光","偽娘哲學","耽美花園","百合花園","純愛","生肉","英語 ENG","CG雜圖","碧藍幻想","圓神領域","短篇","長篇","全彩","嗶咔漢化"]
orders = {"ua":"默认","dd":"新到旧","da":"旧到新","ld":"最多爱心","vd":"最多指名"}
#token_me = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI1OTE1YzEwZTQ0N2JmYjA4OWUzYTY3MzQiLCJlbWFpbCI6InNhZ2lyaTIzMy5yZW1haW4uMSIsInJvbGUiOiJtZW1iZXIiLCJuYW1lIjoi5LiA6Iis6YCa6L-H5LiL5YyX5rO9bWFuIiwidmVyc2lvbiI6IjIuMi4xLjIuMy4zIiwiYnVpbGRWZXJzaW9uIjoiNDQiLCJwbGF0Zm9ybSI6ImFuZHJvaWQiLCJpYXQiOjE2NjE4NjM2OTUsImV4cCI6MTY2MjQ2ODQ5NX0.lSvBJhKw97_9lekHC2YjMhH1KkwOoHnK0Iab0dI3_U8"

urllib3.disable_warnings()

class Pica:
    Order_Default = "ua"  # 默认
    Order_Latest = "dd"  # 新到旧
    Order_Oldest = "da"  # 旧到新
    Order_Loved = "ld"  # 最多爱心
    Order_Point = "vd"  # 最多指名

    def __init__(self) -> None:
        self.__s = requests.session()
        self.__s.proxies = {"https": "http://127.0.0.1:8888",
                            "http": "http://127.0.0.1:8888"}
        self.__s.verify = False
        self.headers = {
            "api-key":           api_key,
            "accept":            "application/vnd.picacomic.com.v1+json",
            "app-channel":       "2",
            "nonce":             nonce,
            "app-version":       "2.2.1.2.3.3",
            "app-uuid":          "defaultUuid",
            "app-platform":      "android",
            "app-build-version": "44",
            "Content-Type":      "application/json; charset=UTF-8",
            "User-Agent":        "okhttp/3.8.1",
            "image-quality":     "original",
            # "authorization":     "",
            # "signature":         "",
            # "time":              int(time()),
        }

    def http_do(self, method, url, **kwargs):
        kwargs.setdefault("allow_redirects", True)
        header = self.headers.copy()
        ts = str(int(time()))
        raw = url.replace("https://picaapi.picacomic.com/",
                          "") + str(ts) + nonce + method + api_key
        raw = raw.lower()
        hc = hmac.new(secret_key.encode(), digestmod=hashlib.sha256)
        hc.update(raw.encode())
        header["signature"] = hc.hexdigest()
        header["time"] = ts
        kwargs.setdefault("headers", header)
        return self.__s.request(method=method, url=url, **kwargs)

    def login(self, email, password):
        api = "auth/sign-in"
        url = base + api
        send = {"email": email, "password": password}
        __a = self.http_do("POST", url=url, json=send).text
        self.headers["authorization"] = json.loads(__a)["data"]["token"]
        return self.headers["authorization"]

    def comics(self, block="", tag="", order="", page=1):
        args = []
        if len(block) > 0:
            args.append(("c", block))
        if len(tag) > 0:
            args.append(("t", tag))
        if len(order) > 0:
            args.append(("s", order))
        if page > 0:
            args.append(("page", str(page)))
        params = urlencode(args)
        url = f"{base}comics?{params}"
        res = self.http_do("GET", url).json()
        return res

    def comic_info(self, book_id):
        url = f"{base}comics/{book_id}"
        return self.http_do("GET", url=url)

    def episodes(self, book_id, page=1):
        url = f"{base}comics/{book_id}/eps?page={page}"
        return self.http_do("GET", url=url)

    def picture(self, book_id, ep_id=1, page=1):
        url = f"{base}comics/{book_id}/order/{ep_id}/pages?page={page}"
        return self.http_do("GET", url=url)

    def recomm(self, book_id):
        url = f"{base}comics/{book_id}/recommendation"
        return self.http_do("GET", url=url)

    def keyword(self):
        url = f"{base}keywords"
        return self.http_do("GET", url=url)

    def search(self, keyword, categories=[], sort=Order_Default, page=1):
        url = f"{base}comics/advanced-search?page={page}"
        return self.http_do("POST", url=url, json={
            "categories": categories,
            "keyword": keyword,
            "sort": sort,
        })

    def like(self, book_id):
        url = f"{base}comics/{book_id}/like"
        return self.http_do("POST", url=url)

    def get_comment(self, book_id, page=1):
        url = f"{base}comics/{book_id}/comments?page={page}"
        return self.http_do("GET", url=url)

    def favourite(self, book_id):
        url = f"{base}comics/{book_id}/favourite"
        return self.http_do("POST", url=url)

    def my_favourite(self, page=1, order=Order_Default):
        url = f"{base}users/favourite?s={order}&page={page:1}"
        return self.http_do("GET", url=url)

    def categories(self):
        url = "https://picaapi.picacomic.com/categories"
        return self.http_do("GET", url=url)

'''
if __name__ == "__main__":
    p = Pica()
    p.login("sagiri233.remain.1", "Aa123456")
    p.comics(order=Pica.Order_Latest)
    p.comic_info("62b6932c9b7955744875c8b7")
    p.episodes("62b6932c9b7955744875c8b7", 1)
    p.picture("62b6932c9b7955744875c8b7", 1, 1)
    p.recomm("62b6932c9b7955744875c8b7")
    p.keyword()
    p.search("loli")
    p.like("62b6932c9b7955744875c8b7") # 喜欢
    p.like("62b6932c9b7955744875c8b7") # 取消喜欢
    p.get_comment("62b6932c9b7955744875c8b7")
    p.favourite("62b6932c9b7955744875c8b7") # 收藏
    p.favourite("62b6932c9b7955744875c8b7") # 取消收藏
    p.favourite("62b6932c9b7955744875c8b7")
    p.my_favourite()
'''
