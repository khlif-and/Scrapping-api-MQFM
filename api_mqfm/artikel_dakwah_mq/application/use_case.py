from artikel_dakwah_mq.domain.port import ArtikelDakwahMqCachePort, ArtikelDakwahMqScraperPort


class GetArtikelDakwahMqUseCase:
    def __init__(self, cache: ArtikelDakwahMqCachePort, scraper: ArtikelDakwahMqScraperPort):
        self._cache = cache
        self._scraper = scraper

    def execute(self) -> dict:
        cached = self._cache.get()
        if cached:
            return cached

        entity = self._scraper.scrape()

        result = {
            "channel_name": entity.channel_name,
            "tagline": entity.tagline,
            "website": entity.website,
            "programs": [{"program": p.program, "schedule": p.schedule} for p in entity.programs],
            "contents": [{"title": c.title, "link": c.link, "image": c.image} for c in entity.contents],
        }

        self._cache.set(result)
        return result
