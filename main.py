import scrapy
from scrapy.http.request.form import FormRequest


class BlogSpider(scrapy.Spider):
    name = "blogspider"
    start_urls = [
        ""
    ]

    def parse(self, response):
        return [
            FormRequest.from_response(
                response,
                formname='login_form',
                formdata={
                    "email": "",
                    "password": "",
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
