import scrapy
import yaml
import json
import os.path
from scrapy.http.request.form import FormRequest
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime

if os.path.isfile("settings.local.yaml"):
    settings = "settings.local.yaml"
else:
    settings = "settings.yaml"

config = yaml.safe_load(open(settings))


class WishListItem:
    def __init__(self, title, image, url, stock, button, last_checked):
        self.title = title
        self.image = image
        self.url = url
        self.stock = stock
        self.button = button
        self.last_checked = last_checked


class ArchoniaWishListSpider(scrapy.Spider):
    name = "archonia-wishlist-spider"
    start_urls = [config["WISHLIST"]]

    def __init__(self):
        self.load_tracked_items()

    def load_tracked_items(self):
        if os.path.isfile("data.json"):
            with open("data.json") as json_file:
                self.tracked_items = json.load(json_file)
        else:
            self.tracked_items = json.loads("""{}""")

    def update_tracked_items(self):
        # TODO: remove empty titles
        with open("data.json", "w") as outfile:
            json.dump(self.tracked_items, outfile)

    def parse(self, response):
        return [
            FormRequest.from_response(
                response,
                formname="login_form",
                formdata={
                    "email": config["EMAIL"],
                    "password": config["PASSWORD"],
                    "cookietime": "on",
                },
                callback=self.parse_wishlist,
                dont_filter=True,
            )
        ]

    def parse_wishlist(self, response):
        for row in response.xpath('//*[@id="main-content"]/div/div[2]/div[2]/div'):
            wishlist_item = self.parse_wishlist_item(row)
            print(wishlist_item.button)

            # Check if the item already exists
            if wishlist_item.title in self.tracked_items:
                # Check if the stock is the same as the stored one
                if wishlist_item.stock != self.tracked_items[wishlist_item.title]:
                    # Remove the wishlist item
                    self.tracked_items.pop(wishlist_item.title)

            if (
                wishlist_item.stock != "Out of stock"
                and wishlist_item.title not in self.tracked_items
                and wishlist_item.button != "\nNot for sale  "
            ):
                self.publish_discord_notification(wishlist_item)
                self.tracked_items[wishlist_item.title] = wishlist_item.stock

            yield wishlist_item.__dict__

        self.update_tracked_items()

    def parse_wishlist_item(self, row):
        title = row.css("a::text").get()
        url = row.css("a::attr(href)").get()
        button = row.css("button::text").get()
        image = row.css("img::attr(src)").get()
        stock = row.css("span::text").get()
        return WishListItem(title, image, url, stock, button, datetime.now())

    def publish_discord_notification(self, wishlist_item: WishListItem):
        webhook = DiscordWebhook(
            url=config["WEBHOOK_URL"],
            content=f'{wishlist_item.stock} {wishlist_item.title} {config["DISCORD_MENTION"]}',
        )
        embed = DiscordEmbed(
            title=f"{wishlist_item.title}",
            description="is in stock!",
            color="03b2f8",
        )
        embed.set_image(url=wishlist_item.image)
        embed.set_url(url=f"https://www.archonia.com{wishlist_item.url}")
        webhook.add_embed(embed)
        webhook.execute()
