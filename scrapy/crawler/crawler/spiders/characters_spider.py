import scrapy
from crawler.items import CharacterItem
from datetime import datetime


class CharactersSpider(scrapy.Spider):
    name = "characters"
    allowed_domains = ["fandom.com"]

    start_urls = [
        "https://bokudakegainaimachi.fandom.com/wiki/Category:Characters",
        "https://violet-evergarden.fandom.com/wiki/Category:Characters",
        "https://ansatsukyoshitsu.fandom.com/wiki/Category:Characters",
        "https://fruitsbasket.fandom.com/wiki/Category:Characters",
        "https://detectiveconan.fandom.com/wiki/Category:Characters",
        "https://dragonball.fandom.com/wiki/Category:Characters",
        "https://codegeass.fandom.com/wiki/Category:Characters",
        "https://gintama.fandom.com/wiki/Category:Characters",
        "https://swordartonline.fandom.com/wiki/Category:Characters",
        "https://noragami.fandom.com/wiki/Category:Characters",
        "https://mob-psycho-100.fandom.com/wiki/Category:Characters",
        "https://vinlandsaga.fandom.com/wiki/Category:Characters",
        "https://shigatsu-wa-kimi-no-uso.fandom.com/wiki/Category:Characters",
        "https://tokyorevengers.fandom.com/wiki/Category:Characters",
    ]

    def parse(self, response):
        """
        Parse les pages Category:Characters
        """
        anime_name = response.url.split("//")[1].split(".")[0].replace("-", " ")

        character_links = response.css(
            "div.category-page__members a.category-page__member-link::attr(href)"
        ).getall()

        for link in character_links:
            yield response.follow(
                link,
                callback=self.parse_character,
                meta={"anime": anime_name}
            )

        next_page = response.css(
            "a.category-page__pagination-next::attr(href)"
        ).get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_character(self, response):
        """
        Parse les pages individuelles des personnages
        """
        item = CharacterItem()

        item["name"] = response.css(
            "span.mw-page-title-main::text"
        ).get()

        item["anime"] = response.meta.get("anime")
        item["fandom"] = response.url.split("//")[1].split(".")[0]
        item["character_url"] = response.url

        # Gender (robuste)
        gender = response.css(
            'div.pi-item[data-source="gender"] div.pi-data-value ::text'
        ).getall()
        item["gender"] = " ".join(g.strip() for g in gender if g.strip())

        # Status (robuste)
        status = response.css(
            'div.pi-item[data-source="status"] div.pi-data-value ::text'
        ).getall()
        item["status"] = " ".join(s.strip() for s in status if s.strip())

        # Image principale
        item["image_url"] = response.css(
            "figure.pi-item img::attr(src)"
        ).get()

        item["scraped_at"] = datetime.utcnow().isoformat()

        # --- Vérification avant yield ---
        fields_to_check = ["name", "gender", "status"]
        missing_count = sum(1 for f in fields_to_check if not item.get(f))

        if item["name"] and missing_count < 3:
            yield item
