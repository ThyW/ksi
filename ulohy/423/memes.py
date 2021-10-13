from typing import Tuple, List, NamedTuple
import json


class Meme(NamedTuple):
    postLink: str
    subreddit: str
    title: str
    url: str
    nsfw: bool
    spoiler: bool
    author: str
    ups: int
    preview: List[str]


class Memes(NamedTuple):
    count: int
    memes: List[Meme]


def sub_memes(memes, subreddit):
    return [meme for meme in filter(lambda x: x.subreddit == subreddit, memes)]


def get_subreddit_memes_ratings(
         memes: List[Meme],
         subreddit: str) -> List[int]:
    return [meme.ups for meme in
            filter(lambda x: x.subreddit == subreddit, memes)]


def get_all_subreddits(memes: List[Meme]) -> List[str]:
    return [meme.subreddit for meme in memes]


def get_all_ups(memes) -> List[int]:
    return [meme.ups for meme in memes]


def load_memes(fileName: str) -> List[Meme]:
    with open(fileName, "r") as file:
        j = json.load(file)
        ret = []
        for meme in j["memes"]:
            ret.append(Meme(
                     meme["postLink"],
                     meme["subreddit"],
                     meme["title"],
                     meme["url"],
                     meme["nsfw"],
                     meme["spoiler"],
                     meme["author"],
                     meme["ups"],
                     meme["preview"]))
        return ret


def analyze_memes(fileName: str) -> Tuple[str, str, str]:
    # meme with best rating all together
    memes: List[Meme] = load_memes(fileName)

    # best average per sub meme rating sub name
    averages_with_sub = [(sub, round(sum(
        get_subreddit_memes_ratings(memes, sub))
        / len(get_subreddit_memes_ratings(memes, sub))))
        for sub in get_all_subreddits(memes)]
    averages: List[int] = [each[1] for each in averages_with_sub]
    subs: List[str] = [each[0] for each in averages_with_sub]
    mx: int = max(averages)
    sub: List[str] = [subs[i] for i, each in enumerate(averages) if each == mx]

    # best rated meme in this sub
    mx2: int = max(get_subreddit_memes_ratings(memes, sub[0]))
    s_memes: List[Meme] = sub_memes(memes, sub[0])
    meme_link: List[str] = [meme.postLink
                            for meme in s_memes if meme.ups == mx2]

    # meme with best rating all together
    mx3: int = max(get_all_ups(memes))
    best_meme: List[str] = [meme.postLink for meme in memes if meme.ups == mx3]
    return (sub[0], meme_link[0], best_meme[0])
