from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from scrapy.exceptions import NotConfigured
from scrapy.utils.conf import build_component_list
from scrapy.utils.misc import build_from_crawler, load_object

if TYPE_CHECKING:
    from scrapy.crawler import Crawler
    from scrapy.settings import BaseSettings, Settings


logger = logging.getLogger(__name__)


class AddonManager:
    """This class facilitates loading and storing :ref:`topics-addons`."""

    def __init__(self, crawler: Crawler) -> None:
        self.crawler: Crawler = crawler
        self.addons: list[Any] = []

    def load_settings(self, settings: Settings) -> None:
        """Load add-ons and configurations from a settings object and apply them.

        This will load the add-on for every add-on path in the
        ``ADDONS`` setting and execute their ``update_settings`` methods.

        :param settings: The :class:`~scrapy.settings.Settings` object from \
            which to read the add-on configuration
        :type settings: :class:`~scrapy.settings.Settings`
        """
        for clspath in build_component_list(settings["ADDONS"]):
            try:
                addoncls = load_object(clspath)
                addon = build_from_crawler(addoncls, self.crawler)
                if hasattr(addon, "update_settings"):
                    addon.update_settings(settings)
                self.addons.append(addon)
            except NotConfigured as e:
                if e.args:
                    logger.warning(
                        "Disabled %(clspath)s: %(eargs)s",
                        {"clspath": clspath, "eargs": e.args[0]},
                        extra={"crawler": self.crawler},
                    )
        logger.info(
            "Enabled addons:\n%(addons)s",
            {
                "addons": self.addons,
            },
            extra={"crawler": self.crawler},
        )

    @classmethod
    def load_pre_crawler_settings(cls, settings: BaseSettings):
        """Update early settings that do not require a crawler instance, such as SPIDER_MODULES.

        Similar to the load_settings method, this loads each add-on configured in the
        ``ADDONS`` setting and calls their 'update_pre_crawler_settings' class method if present.
        This method doesn't have access to the crawler instance or the addons list.

        :param settings: The :class:`~scrapy.settings.BaseSettings` object from \
            which to read the early add-on configuration
        :type settings: :class:`~scrapy.settings.Settings`
        """
        for clspath in build_component_list(settings["ADDONS"]):
            addoncls = load_object(clspath)
            if hasattr(addoncls, "update_pre_crawler_settings"):
                addoncls.update_pre_crawler_settings(settings)
