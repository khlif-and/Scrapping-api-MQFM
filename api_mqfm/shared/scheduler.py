import logging
from apscheduler.schedulers.background import BackgroundScheduler

from artikel_dakwah_mq.infrastructure.cache_adapter import ArtikelDakwahMqCacheAdapter
from artikel_dakwah_mq.infrastructure.scraper_adapter import ArtikelDakwahMqScraperAdapter
from artikel_dakwah_mq.application.use_case import GetArtikelDakwahMqUseCase

from audio_dakwah_mq.infrastructure.cache_adapter import AudioDakwahMqCacheAdapter
from audio_dakwah_mq.infrastructure.scraper_adapter import AudioDakwahMqScraperAdapter
from audio_dakwah_mq.application.use_case import GetAudioDakwahMqUseCase

from audio_dakwah_streaming.infrastructure.cache_adapter import AudioDakwahStreamingCacheAdapter
from audio_dakwah_streaming.infrastructure.scraper_adapter import AudioDakwahStreamingScraperAdapter
from audio_dakwah_streaming.application.use_case import GetAudioDakwahStreamingUseCase

from youtube_dakwah_streaming.infrastructure.cache_adapter import YoutubeDakwahStreamingCacheAdapter
from youtube_dakwah_streaming.infrastructure.scraper_adapter import YoutubeDakwahStreamingScraperAdapter
from youtube_dakwah_streaming.application.use_case import GetYoutubeDakwahStreamingUseCase

from program_and_adds.infrastructure.cache_adapter import ProgramAndAddsCacheAdapter
from program_and_adds.infrastructure.scraper_adapter import ProgramAndAddsScraperAdapter
from program_and_adds.application.use_case import GetProgramAndAddsUseCase

logger = logging.getLogger(__name__)

SCRAPE_INTERVAL_MINUTES = 30
STREAMING_INTERVAL_MINUTES = 5


def _refresh_artikel_dakwah_mq():
    try:
        cache = ArtikelDakwahMqCacheAdapter()
        scraper = ArtikelDakwahMqScraperAdapter()
        use_case = GetArtikelDakwahMqUseCase(cache=cache, scraper=scraper)
        cache.invalidate()
        use_case.execute()
        logger.info("Background refresh: artikel_dakwah_mq OK")
    except Exception as e:
        logger.error(f"Background refresh artikel_dakwah_mq gagal: {e}")


def _refresh_audio_dakwah_mq():
    try:
        cache = AudioDakwahMqCacheAdapter()
        scraper = AudioDakwahMqScraperAdapter()
        use_case = GetAudioDakwahMqUseCase(cache=cache, scraper=scraper)
        cache.invalidate()
        use_case.execute()
        logger.info("Background refresh: audio_dakwah_mq OK")
    except Exception as e:
        logger.error(f"Background refresh audio_dakwah_mq gagal: {e}")


def _refresh_audio_dakwah_streaming():
    try:
        cache = AudioDakwahStreamingCacheAdapter()
        scraper = AudioDakwahStreamingScraperAdapter()
        use_case = GetAudioDakwahStreamingUseCase(cache=cache, scraper=scraper)
        cache.invalidate()
        use_case.execute()
        logger.info("Background refresh: audio_dakwah_streaming OK")
    except Exception as e:
        logger.error(f"Background refresh audio_dakwah_streaming gagal: {e}")


def _refresh_youtube_dakwah_streaming():
    try:
        cache = YoutubeDakwahStreamingCacheAdapter()
        scraper = YoutubeDakwahStreamingScraperAdapter()
        use_case = GetYoutubeDakwahStreamingUseCase(cache=cache, scraper=scraper)
        cache.invalidate()
        use_case.execute()
        logger.info("Background refresh: youtube_dakwah_streaming OK")
    except Exception as e:
        logger.error(f"Background refresh youtube_dakwah_streaming gagal: {e}")


def _refresh_program_and_adds():
    try:
        cache = ProgramAndAddsCacheAdapter()
        scraper = ProgramAndAddsScraperAdapter()
        use_case = GetProgramAndAddsUseCase(cache=cache, scraper=scraper)
        cache.invalidate()
        use_case.execute()
        logger.info("Background refresh: program_and_adds OK")
    except Exception as e:
        logger.error(f"Background refresh program_and_adds gagal: {e}")


def warm_cache():
    logger.info("Cache warming: memulai pre-fetch semua data...")
    _refresh_artikel_dakwah_mq()
    _refresh_audio_dakwah_mq()
    _refresh_audio_dakwah_streaming()
    _refresh_youtube_dakwah_streaming()
    _refresh_program_and_adds()
    logger.info("Cache warming selesai")


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()

    scheduler.add_job(_refresh_artikel_dakwah_mq, 'interval', minutes=SCRAPE_INTERVAL_MINUTES, id='artikel_dakwah_mq')
    scheduler.add_job(_refresh_audio_dakwah_mq, 'interval', minutes=SCRAPE_INTERVAL_MINUTES, id='audio_dakwah_mq')
    scheduler.add_job(_refresh_program_and_adds, 'interval', minutes=SCRAPE_INTERVAL_MINUTES, id='program_and_adds')

    scheduler.add_job(_refresh_audio_dakwah_streaming, 'interval', minutes=STREAMING_INTERVAL_MINUTES, id='audio_dakwah_streaming')
    scheduler.add_job(_refresh_youtube_dakwah_streaming, 'interval', minutes=STREAMING_INTERVAL_MINUTES, id='youtube_dakwah_streaming')

    scheduler.start()
    logger.info(f"Background scheduler aktif - konten: tiap {SCRAPE_INTERVAL_MINUTES} menit, streaming: tiap {STREAMING_INTERVAL_MINUTES} menit")
    return scheduler
