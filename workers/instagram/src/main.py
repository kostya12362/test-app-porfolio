import json
import os
from typing import Optional

import scrapy
from scrapy.http import Response
from urllib.parse import urlencode
from core.spider import AioPikaQueueSpider
from core.crawler import create_crawler_process
from parser import PostItemParser


class InstagramSpider(AioPikaQueueSpider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    RMQ_URI = os.getenv("RMQ_URI")
    INSTAGRAM_ACCOUNT_DOCUMENT_ID = "9310670392322965"
    parser = PostItemParser
    custom_settings = {
        'ITEM_PIPELINES': {
            'pipelines.save_posts.SavePostsPipeline': 100,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy.core.downloader.handlers.http.HTTPDownloadHandler",
            "https": "scrapy.core.downloader.handlers.http.HTTPDownloadHandler",
        }
    }

    async def start(
            self,
            metadata: Optional[dict] = None
    ):

        """
        {"username": "nasa", "metadata": {"account_id": 1}}
        """
        self.logger.info(f"Starting request for username: {metadata['username']}")
        metadata['items'] = []
        yield self.make_request_get_posts(
            username=metadata['username'],
            page_size=metadata.get('page_size', 10),
            page_number=1,
            max_pages=metadata.get('max_pages', 1),
            metadata=metadata,
        )

    async def get_posts(self, response: Response):
        username = response.meta["username"]
        page_number = response.meta["page_number"]
        max_pages = response.meta["max_pages"]
        page_size = response.meta["page_size"]
        metadata = response.meta['metadata']

        data = json.loads(response.text)
        # If the request is not successful, data["data"] will be None
        posts_connection = data["data"]["xdt_api__v1__feed__user_timeline_graphql_connection"]
        for edge in posts_connection.get("edges", []):
            node = edge.get("node")
            if node:
                parser = self.parser(node, metadata)
                item = parser.get_data
                metadata['items'].append(item.model_dump())

        # Pagination page
        page_info = posts_connection.get("page_info", {})
        if page_info.get("has_next_page"):
            end_cursor = page_info.get("end_cursor")
            variables = response.meta["variables"]
            variables["after"] = end_cursor
            next_page = page_number + 1
            if max_pages and next_page > max_pages:
                self.logger.info("Reached max_pages limit, stopping pagination.")
                yield metadata
            else:
                yield self.make_request_get_posts(
                    username=username,
                    page_size=page_size,
                    page_number=next_page,
                    max_pages=max_pages,
                    next_cursor=end_cursor,
                    metadata=response.meta["metadata"]
                )
        else:
            yield metadata
            self.logger.info("No more pages to scrape.")

    def make_request_get_posts(
            self,
            username: str,
            page_size: int,
            page_number: int,
            max_pages: int,
            next_cursor: str = None,
            metadata: Optional[dict] = None
    ):
        base_url = 'https://www.instagram.com/graphql/query/'
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        variables = {
            "after": next_cursor,
            "before": None,
            "data": {
                "count": page_size,
                "include_reel_media_seen_timestamp": True,
                "include_relationship_info": True,
                "latest_besties_reel_media": True,
                "latest_reel_media": True
            },
            "first": page_size,
            "last": None,
            "username": username,
            "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True,
            "__relay_internal__pv__PolarisShareSheetV3relayprovider": True
        }
        params = {
            "doc_id": self.INSTAGRAM_ACCOUNT_DOCUMENT_ID,
            "variables": json.dumps(variables, separators=(",", ":"))
        }
        final_url = f"{base_url}?{urlencode(params)}"
        self.logger.info(f"Making GET request for page {page_number} with URL: {final_url}")
        req = scrapy.Request(
            url=final_url,
            method='GET',
            headers=headers,
            callback=self.get_posts,
            dont_filter=True,
            meta={
                "username": username,
                "page_size": page_size,
                "page_number": page_number,
                "max_pages": max_pages,
                "variables": variables,
                'metadata': metadata
            }
        )
        return req


if __name__ == '__main__':
    create_crawler_process(InstagramSpider)
