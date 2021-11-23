import scrapy
import yaml
import json
import os.path
from scrapy import Request
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime

if os.path.isfile("settings.local.yaml"):
    settings = "settings.local.yaml"
else:
    settings = "settings.yaml"

config = yaml.safe_load(open(settings))


class WishListItem:
    def __init__(self, title, number, url, last_checked):
        self.title = title
        self.number = number
        self.url = url
        self.last_checked = last_checked


class ArchoniaWishListSpider(scrapy.Spider):
    name = "archonia-wishlist-spider"
    start_urls = ["https://www.archonia.com/en-us/"]

    def __init__(self):
        self.load_tracked_items()

    def load_tracked_items(self):
        if os.path.isfile("volumes.json"):
            with open("volumes.json") as json_file:
                self.tracked_items = json.load(json_file)
        else:
            self.tracked_items = json.loads("""{}""")

    def update_tracked_items(self):
        # TODO: remove empty titles
        with open("volumes.json", "w") as outfile:
            json.dump(self.tracked_items, outfile)

    def parse(self, response):
        for url in self.tracked_items:
            print(url)
        return (Request(url, callback=self.parse_volume) for url in self.tracked_items)

    def parse_volume(self, response):
        title = response.xpath(
            '//*[@id="main-content"]/div/div[5]/div/table/tbody/tr[4]/td[2]/a').css("a::text").get()
        box = response.xpath(
            '//*[@id="main-content"]/div/div[4]/div[1]/div[1]/a')[-1]
        volume = self.parse_wishlist_item(box, title)
        if int(volume.number) != int(self.tracked_items[response.url]):
            self.tracked_items[response.url] = int(volume.number)
            self.publish_discord_notification(volume)
        self.update_tracked_items()

    def parse_wishlist_item(self, row, title):
        number = row.css("span::text").get()
        url = row.css("a::attr(href)").get()
        return WishListItem(title, number, url, datetime.now())

    def publish_discord_notification(self, wishlist_item: WishListItem):
        webhook = DiscordWebhook(
            url=config["WEBHOOK_URL"],
            content=f'{wishlist_item.title} {wishlist_item.number} {config["DISCORD_MENTION"]}',
        )
        embed = DiscordEmbed(
            title=f"{wishlist_item.title} vol {wishlist_item.number}",
            description="is available!",
            color="03b2f8",
        )
        embed.set_url(url=f"https://www.archonia.com{wishlist_item.url}")
        webhook.add_embed(embed)
        webhook.execute()
