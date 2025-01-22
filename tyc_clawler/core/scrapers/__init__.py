from crawl4ai import CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from .mp_scraper import mp_scraper

custom_scrapers = {'mp.weixin.qq.com': mp_scraper}
custom_fetching_configs = {}

md_generator = DefaultMarkdownGenerator(
        options={
            "skip_internal_links": True,
            "escape_html": True
        }
    )

crawler_config = CrawlerRunConfig(delay_before_return_html=2.0, markdown_generator=md_generator,
                                wait_until='commit', magic=True, scan_full_page=True)
