from audio_dakwah_mq.domain.port import AudioDakwahMqCachePort, AudioDakwahMqScraperPort


class GetAudioDakwahMqUseCase:
    def __init__(self, cache: AudioDakwahMqCachePort, scraper: AudioDakwahMqScraperPort):
        self._cache = cache
        self._scraper = scraper

    def execute(self) -> dict:
        cached = self._cache.get()
        if cached:
            return cached

        programs = self._scraper.scrape()

        result = {
            "programs": [
                {
                    "title": p.title,
                    "image_url": p.image_url,
                    "page_url": p.page_url,
                    "tracks": [
                        {"title": t.title, "mp3_url": t.mp3_url, "duration": t.duration}
                        for t in p.tracks
                    ],
                }
                for p in programs
            ]
        }

        self._cache.set(result)
        return result
