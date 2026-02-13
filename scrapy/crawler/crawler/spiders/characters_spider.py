import scrapy
from crawler.items import CharacterItem
from datetime import datetime


class CharactersSpider(scrapy.Spider):
    name = "characters"
    allowed_domains = ["fandom.com"]

    start_urls = [
 	"https://obluda.fandom.com/wiki/Category:Characters",
        "https://nana.fandom.com/wiki/Category:Characters",
        "https://dr-stone.fandom.com/wiki/Category:Characters",
        "https://madeinabyss.fandom.com/wiki/Category:Characters",
        "https://dandadan.fandom.com/wiki/Category:Characters",
        "https://kaichouwamaidsama.fandom.com/wiki/Category:Characters",
        "https://ao-haru-ride.fandom.com/wiki/Category:Characters",
        "https://sayiloveyou.fandom.com/wiki/Category:Characters",
        "https://kiminitodoke.fandom.com/wiki/Category:Characters",
        "https://watashi-ga-motete-dousunda.fandom.com/wiki/Category:Characters",
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
        "https://tokyorevengers.fandom.com/wiki/Category:Characters", ]

    def parse(self, response):
        # Parse Category:Characters pages
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
        # Parse individuel pour chaque page personnage
        item = CharacterItem()

        item["name"] = response.css(
            "span.mw-page-title-main::text"
        ).get()

        item["anime"] = response.meta.get("anime")
        item["character_url"] = response.url

        # --- Gender ---
        # Rendre insensible à la casse
        gender_parts = response.xpath(
            '//div[contains(@class,"pi-item") and '
            "translate(@data-source, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='gender']"
            '//div[contains(@class,"pi-data-value")]//text()'
        ).getall()
        gender = " ".join(g.strip() for g in gender_parts if g.strip())

        if not gender:
            gender_td = response.xpath(
                '//td[b[contains(normalize-space(.),"Gender")]]/following-sibling::td//text()'
            ).getall()
            gender = " ".join(g.strip() for g in gender_td if g.strip())

        item["gender"] = gender or "Unknown"

        # --- Status ---
        # Rendre insensible à la casse
        status = response.xpath(
            "normalize-space(string(//div[translate(@data-source, "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='status']"
            "//div[contains(@class,'pi-data-value')]))"
        ).get()

        if not status:
            status_parts = response.xpath(
                '//div[contains(@class,"pi-item") and '
                "translate(@data-source, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='status']"
                '//div[contains(@class,"pi-data-value")]//div[contains(@class,"mw-collapsible-content")]//text()'
            ).getall()
            status = " ".join(p.strip() for p in status_parts if p.strip())

        if not status:
            status_td = response.xpath(
                '//td[b[contains(normalize-space(.),"Status")]]/following-sibling::td//text()'
            ).getall()
            status = " ".join(p.strip() for p in status_td if p.strip())

        item["status"] = status.strip() if status else "Unknown"

        # --- Image principale ---
        item["image_url"] = response.css(
            "figure.pi-item img::attr(src)"
        ).get()

        item["scraped_at"] = datetime.utcnow().isoformat()

        # --- Verification ---
        fields_to_check = ["name", "gender", "status"]
        missing_count = sum(1 for f in fields_to_check if not item.get(f))


        self.logger.debug("Character parsed: name=%r gender=%r status=%r url=%s",
                          item.get("name"), item.get("gender"), item.get("status"), item.get("character_url"))

        if item["name"] and missing_count < 3:
            yield item
