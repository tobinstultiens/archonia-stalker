import scrapy
import yaml
from scrapy.http.request.form import FormRequest

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
        for title in response.xpath(
            '//*[@id="main-content"]/div/div[2]/div[2]/div/div/div/div/h4/a'
        ):
            yield {"title": title.css("::text").get()}
