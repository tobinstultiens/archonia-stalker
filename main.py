import scrapy
import yaml
import json
import os.path
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
            if os.path.isfile('data.txt'):
                with open('data.txt') as json_file:
                    data = json.load(json_file)
            else:
                data = json.loads("""{}""")

            if stock != "Out of stock" and title not in data:
                webhook = DiscordWebhook(url=config["WEBHOOK_URL"], content=stock + " " + title[:25] + "... <@&867379202839674890>")
                # create embed object for webhook
                # you can set the color as a decimal (color=242424) or hex (color='03b2f8') number
                embed = DiscordEmbed(title=f'{title}', description=f'{title} is in stock https://www.archonia.com{link}', color='03b2f8')
                # add embed object to webhook
                webhook.add_embed(embed)
                response = webhook.execute()
                data[title] = ''

                with open('data.txt', 'w') as outfile:
                    json.dump(data, outfile)
            yield {
                "title": title,
                "stock": stock
            }
