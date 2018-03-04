import typing

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.common.exceptions import StaleElementReferenceException

from hearthstone import api
from hearthstone import deck
from hearthstone import card
from hs_deckgen import model

class ReplayTrainer:

    _BROWSER = None

    @classmethod
    def _setup_browser(cls) -> None:
        opts = FirefoxOptions()
        opts.add_argument("--headless")
        cls._BROWSER = webdriver.Firefox(firefox_options=opts)
        cls._BROWSER.implicitly_wait(10) # seconds

    def lazy_browser(func):
        def decorated(*args, **kwargs):
            if ReplayTrainer._BROWSER is None:
                ReplayTrainer._setup_browser()
            return func(*args, **kwargs)
        return decorated

    @classmethod
    @lazy_browser
    def pull_decks(cls, start: str, max_page: typing.Optional[int] = None) -> typing.Iterator[deck.Deck]:
        browser = cls._BROWSER

        browser.get(start)

        deck_list_wrapper = browser.find_element_by_xpath("html/body/div[@id = 'decks-container']/div[@class = 'decks']/div[@class = 'deck-list-wrapper']")
        pages = int(deck_list_wrapper.find_elements_by_xpath("div/div/nav/ul/li[@class = 'visible-lg-inline']/a")[-1].text)
        forward_button = deck_list_wrapper.find_element_by_xpath('div/div/nav/ul/li[not(@*)]/a')

        if max_page:
            pages = min(max_page, pages)

        for _ in range(pages):
            deck_links = deck_list_wrapper.find_elements_by_xpath("div[@class = 'deck-list']/ul/li/a")
            yield from (api.ReplayAPI.deck_from_url(node.get_attribute('href')) for node in deck_links)
            try:
                forward_button.click()
            except StaleElementReferenceException:
                forward_button = deck_list_wrapper.find_element_by_xpath('div/div/nav/ul/li[not(@*)]/a')
                forward_button.click()

    @classmethod
    def model_from_cards(cls, required: typing.Iterable[card.Card]) -> model.HSModel:
        my_model = model.HSModel()

        for card in required:
            url = f'https://hsreplay.net/decks/#includedCards={card.db_id}'
            decks = cls.pull_decks(url, 1)
            for deck in decks:
                my_model.train(deck.cards)

        return my_model

    @classmethod
    def new_model(cls, max_page: typing.Optional[int] = None) -> model.HSModel:
        return model.HSModel.from_decks(cls.top_30_days('https://hsreplay.net/decks/#timeRange=LAST_30_DAYS', max_page))

