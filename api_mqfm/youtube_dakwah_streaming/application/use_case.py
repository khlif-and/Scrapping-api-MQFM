from youtube_dakwah_streaming.domain.port import YoutubeDakwahStreamingCachePort, YoutubeDakwahStreamingScraperPort


class GetYoutubeDakwahStreamingUseCase:
    def __init__(self, cache: YoutubeDakwahStreamingCachePort, scraper: YoutubeDakwahStreamingScraperPort):
        self._cache = cache
        self._scraper = scraper

    def execute(self) -> dict:
        cached = self._cache.get()
        if cached:
            return cached

        entity = self._scraper.scrape()

        if not entity.youtube_url:
            return {"youtube_url": None, "title": None, "available": False}

        result = {
            "youtube_url": entity.youtube_url,
            "title": entity.title,
            "available": True,
        }

        self._cache.set(result)
        return result
