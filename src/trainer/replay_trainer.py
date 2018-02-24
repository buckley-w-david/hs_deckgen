import typing

from selenium import webdriver
from selenium.webdriver import FirefoxOptions

from hearthstone import api
from hearthstone import deck
from hs_deckgen import model

class ReplayTrainer:

    _BROWSER = None

    @classmethod
    def _setup_browser(cls) -> None:
        opts = FirefoxOptions()
        opts.add_argument("--headless")
        cls._BROWSER = webdriver.Firefox(firefox_options=opts)

    def lazy_browser(func):
        def decorated(*args, **kwargs):
            if ReplayTrainer._BROWSER is None:
                ReplayTrainer._setup_browser()
            return func(*args, **kwargs)
        return decorated

    @classmethod
    @lazy_browser
    def top_30_days(cls) -> typing.Iterator[deck.Deck]:
        browser = cls._BROWSER

        browser.get("https://hsreplay.net/decks/#timeRange=LAST_30_DAYS")

        deck_list_wrapper = browser.find_element_by_xpath("html/body/div[@id = 'decks-container']/div[@class = 'decks']/div[@class = 'deck-list-wrapper']")
        pages = int(deck_list_wrapper.find_elements_by_xpath("div/div/nav/ul/li[@class = 'visible-lg-inline']/a")[-1].text)
        forward_button = deck_list_wrapper.find_element_by_xpath('div/div/nav/ul/li[not(@*)]/a')

        for _ in range(pages):
            deck_links = deck_list_wrapper.find_elements_by_xpath("div[@class = 'deck-list']/ul/li/a")
            yield from (api.ReplayAPI.deck_from_url(node.get_attribute('href')) for node in deck_links)
            forward_button.click()

    @classmethod
    def new_model(cls) -> model.HSModel:
        return model.HSModel.from_decks(cls.top_30_days())

