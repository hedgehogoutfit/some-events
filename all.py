import vk_api
import re
from datetime import date as d


groups = {'Книжный клуб Бездействие': -62622395,
          'Уличная эпистемология': -165566939,
          'Книжный клуб в СПб': -55130788,
          'Итальянская 16': -161320870,
          'Дискуссионный клуб': -204499696,
          'Книжный клуб Книгочай': -37124231,
          }


def get_posts(group_id, n):  # n is amount of posts
    """Return list of n dictionaries with posts"""
    '''In token you place your own token from vk_api, it's connected to your vk account so you shouldn't share it.
     I used this tutorial https://www.youtube.com/watch?v=gysqjgfLmBc&ab_channel=%D0%A4%D1%81%D0%BE%D0%BA%D0%B8'''
    session = vk_api.VkApi(token='')
    post_ = session.method('wall.get', {'owner_id': group_id, 'count': n})
    return post_['items']


def create_date(x, months):
    """Return date object"""
    """not finished:)"""
    day = int(x.group(1))
    mon = months[x.group(2)]
    year = d.today().year
    date = d(year, mon, day)


def extract_text(item):

    if item.get('copy_history', -1) != -1:
        repost = item['copy_history'][0]
        return repost['text']
    else:
        return item['text']


def search_pattern(text):
    """This function works in half cases. I think i need to make different patterns for different groups. I tried to
    make function that will work with all publics from 'groups' dictionary cause they write date in the same format:
    '12 ноября'. But i can't extract text after date properly. I want to take 2 sentences after date but in some cases
     pattern returns none or empty strings"""
    months = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7,
              "августа": 8, "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12}

    date_pattern = r'(\d\d?)\s([а-я]{3,8})'  # 13 октября

    """I plan to put this date string in create_date function, make date_time object from it and then store it in 
    database in timestamp"""
    date = re.search(date_pattern, text)
    if date is None or date.group(2) not in months.keys():
        return None

    text = text[date.end():]
    """can be None"""
    next_2_sent = re.compile(r"""([^\.\?!]+     # one sentence: any character exept ?.!
                                 (\.|\?|!))    # end of the sentence: punctuation
                                 {1,2}          # 1 or 2 sentences
                             """, flags=re.VERBOSE)

    """Here i exclude all dates that for some reason don't have text after them. Need to check what are these 
    dates later"""
    try:
        text = next_2_sent.match(text).group()
    except AttributeError:
        return None
    replaced = [r'\(.+\)', r'\[.+\]']  # replace all braces
    for repl in replaced:
        text = re.sub(repl, '', text)
    return text


def write_file():
    """Just for tests"""
    with open('test_results.txt', 'a') as f:
        f.write(f'date: {d.strftime("%d %b")}\n')
        f.write(f'time: {time}\n')
        f.write(f'name: {line}')
        f.write('\n-------------------------------------------------\n\n')


if __name__ == '__main__':
    paa = "---------------------------------------------------------------------"
    posts = get_posts(-55130788, 20)    # here you can put any group id and number of posts
    for post in posts:
        text_ = search_pattern(extract_text(post))
        if text_:
            print('(｡◕‿◕｡) ', text_, f'\n\n{paa}\n\n', sep=' ')