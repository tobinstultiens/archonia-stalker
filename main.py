import scrapy
import yaml
from scrapy.http.request.form import FormRequest
from scrapy.mail import MailSender

config = yaml.safe_load(open("settings.yaml"))
mailer = MailSender()


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
            stock = row.css("span::text").get()
            if stock != "Out of stock":
                mailer.send(to=[config["EMAIL"]], subject=f"{title} is now in stock", body=config["WISHLIST"])

            yield {
                "title": title,
                "stock": stock
            }
