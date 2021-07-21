import scrapy
import yaml
from scrapy.http.request.form import FormRequest
from discord_webhook import DiscordWebhook, DiscordEmbed

config = yaml.safe_load(open("settings.yaml"))


class BlogSpider(scrapy.Spider):
    name = "blogspider"
    start_urls = [config["WISHLIST"]]

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
                callback=self.parse2,
                dont_filter=True,
            )
        ]

    def parse2(self, response):
        for row in response.xpath('//*[@id="main-content"]/div/div[2]/div[2]/div'):
            title = row.css("a::text").get()
            link = row.css("a::attr(href)").get()
            stock = row.css("span::text").get()
            if stock != "Out of stock":
                webhook = DiscordWebhook(url=config["WEBHOOK_URL"], content=stock)
                # create embed object for webhook
                # you can set the color as a decimal (color=242424) or hex (color='03b2f8') number
                embed = DiscordEmbed(title=f'{title}', description=f'{title} is in stock https://www.archonia.com{link}', color='03b2f8')
                # add embed object to webhook
                webhook.add_embed(embed)
                response = webhook.execute()

            yield {
                "title": title,
                "stock": stock
            }
