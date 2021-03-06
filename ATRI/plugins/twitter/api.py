import re

from ATRI.utils import request
from ATRI.exceptions import RequestError


_GUEST_TOKEN: str = str()
_COOKIE: str = str()


class API:
    _bearer_token = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    _user_agent = "Mozilla/5.0 (Linux; Android 2.3.6) AppleWebKit/532.2 (KHTML, like Gecko) Chrome/53.0.866.0 Safari/532.2"

    def _gen_headers(self) -> dict:
        return {
            "origin": "https://twitter.com",
            "authorization": self._bearer_token,
            "cookie": _COOKIE,
            "x-guest-token": _GUEST_TOKEN,
            "x-twitter-active-user": "yes",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-site": "same-site",
            "upgrade-insecure-requests": "1",
            "user-agent": self._user_agent,
            "accept": "application/json, text/plain, */*",
            "dnt": "1",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
            "x-twitter-client-language": "zh-cn",
        }

    async def get_token(self):
        global _GUEST_TOKEN

        headers = self._gen_headers()
        del headers["cookie"]
        del headers["x-guest-token"]
        headers["Host"] = "api.twitter.com"

        url = "https://api.twitter.com/1.1/guest/activate.json"
        try:
            resp = await request.post(url, headers=headers)
        except Exception:
            raise RequestError("Request failed!")

        data: dict = resp.json()
        _GUEST_TOKEN = data.get("guest_token", str())

    async def get_cookie(self):
        global _COOKIE

        headers = self._gen_headers()
        del headers["cookie"]
        del headers["authorization"]

        url = "https://twitter.com/explore"
        try:
            resp = await request.get(url, headers=headers)
        except Exception:
            raise RequestError("Request failed!")

        data = str(resp.headers)

        guest_id = str()
        personalization_id = str()
        ct0 = str()
        twitter_sess = str()

        patt_g_id = r"guest_id=.+?; "
        patt_ct0 = r"ct0=.+?; "
        patt_per = r"personalization_id=.+?; "
        patt_t_p = r"(_twitter_sess=.+?);"

        for _ in data:
            if re.findall(patt_g_id, data):
                guest_id = re.findall(patt_g_id, data)[0]
            if re.findall(patt_ct0, data):
                ct0 = re.findall(patt_ct0, data)[0]
            if re.findall(patt_per, data):
                personalization_id = re.findall(patt_per, data)[0]
            if re.findall(patt_t_p, data):
                twitter_sess = re.findall(patt_t_p, data)[0]

        _COOKIE = f"dnt=1; fm=0; csrf_same_site_set=1; csrf_same_site=1; gt={_GUEST_TOKEN}; {ct0}{guest_id}{personalization_id}{twitter_sess}"

    async def _request(self, url: str, params: dict = dict()) -> dict:
        headers = self._gen_headers()
        try:
            resp = await request.get(url, params=params, headers=headers)
        except Exception:
            raise RequestError("Request failed!")
        return resp.json()

    async def search_user(self, name: str) -> dict:
        """????????????????????????????????? Twitter ??????

        Args:
            name (str): ????????????.

        Returns:
            dict: ?????????????????????. ?????????????????????.
        """
        url = "https://api.twitter.com/1.1/users/search.json"
        params = {"q": name, "count": 1}
        data = await self._request(url, params)
        if not data:
            return dict()
        return data[0]

    async def get_user_info(self, tid: int) -> dict:
        """?????????????????????????????????????????????

        Args:
            tid (int): ??????ID

        Returns:
            dict: ????????????.
        """
        url = f"https://api.twitter.com/2/users/{tid}"
        data = await self._request(url)
        if not data:
            return dict()
        return data

    async def get_conversation(self, tweet_id: int) -> dict:
        """????????????????????????????????????

        Args:
            tweet_id (int): ??????id

        Returns:
            dict: ??????json?????????????????????
        """
        url = f"https://twitter.com/i/api/2/timeline/conversation/{tweet_id}.json"
        params = {
            "simple_quoted_tweet": True,
            "tweet_mode": "extended",
            "trim_user": True,
        }
        data = await self._request(url, params)
        return data
