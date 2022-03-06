import datetime


class Plugin_OBJ():

    def __init__(self, channels, plugin_utils):
        self.plugin_utils = plugin_utils

        self.channels = channels

        self.origin = plugin_utils.origin

        self.base_api = 'https://valencia-app-mds.xumo.com/v2/'

    def update_epg(self):
        programguide = {}
        return programguide

        todaydate = datetime.datetime.utcnow().date()
        self.remove_stale_cache(todaydate)

        for fhdhr_channel_id in list(self.channels.list[self.plugin_utils.namespace].keys()):
            chan_obj = self.channels.list[self.plugin_utils.namespace][fhdhr_channel_id]

            if str(chan_obj.number) not in list(programguide.keys()):
                programguide[str(chan_obj.number)] = chan_obj.epgdict

            cached_items = self.get_cached(chan_obj.dict["origin_id"])
            for cached_item in cached_items:

                for asset in cached_item["assets"]:

                    content_id = asset["id"]
                    # content_cache = self.get_cached_content(content_id)
                    content_cache = {
                                    'title': "Unavailable",
                                    'description': "Unavailable",
                                    }

                    timestart = int(asset['timestamps']["start"] / 1000)
                    timeend = int(asset['timestamps']["end"] / 1000)

                    if "descriptions" not in list(content_cache.keys()):
                        content_cache["descriptions"] = {}

                    clean_prog_dict = {
                                    "time_start": timestart,
                                    "time_end": timeend,
                                    "duration_minutes": str((asset['timestamps']["end"] - asset['timestamps']["start"]) / 60),
                                    "thumbnail": 'https://image.xumo.com/v1/assets/asset/%s/600x340.jpg' % content_id,
                                    "title": content_cache['title'] or "Unavailable",
                                    "sub-title": "Unavailable",
                                    "description": self.getDescription(content_cache["descriptions"]) or "Unavailable",
                                    "rating": "N/A",
                                    "episodetitle": "Unavailable",
                                    "releaseyear": None,
                                    "genres": None,
                                    "seasonnumber": None,
                                    "episodenumber": None,
                                    "isnew": None,
                                    "id": str(content_id)
                                    }

                    if not any(d['id'] == clean_prog_dict['id'] for d in programguide[str(chan_obj.number)]["listing"]):
                        programguide[str(chan_obj.number)]["listing"].append(clean_prog_dict)

        return programguide

    def getDescription(self, description):
        if 'large' in description:
            return description['large']
        elif 'medium' in description:
            return description['medium']
        elif 'small' in description:
            return description['small']
        elif 'tiny' in description:
            return description['tiny']
        else:
            return None

    def get_cached_content(self, content_id):
        cacheitem = self.plugin_utils.db.get_plugin_value(str(content_id), "content_cache", "xumo")
        if cacheitem:
            self.plugin_utils.logger.info("FROM CACHE:  %s" % content_id)
            return cacheitem
        else:
            content_url = "%sassets/asset/%s.json?f=title&f=providers&f=descriptions&f=runtime&f=availableSince" % (self.base_api, content_id)
            self.plugin_utils.logger.info("Fetching:  %s" % content_url)
            try:
                resp = self.plugin_utils.web.session.get(content_url)
            except self.plugin_utils.web.exceptions.HTTPError:
                self.plugin_utils.logger.info('Got an error!  Ignoring it.')
                return None
            result = resp.json()
            self.plugin_utils.db.set_plugin_value(str(content_id), "epg_cache", result, "xumo")
            return result

    def get_cached(self, channel_id):
        for hour_num in range(0, 24):
            lineup_url = "%schannels/channel/%s/broadcast.json?hour=%s" % (self.base_api, channel_id, hour_num)
            self.get_cached_item(channel_id, hour_num, lineup_url)
        cache_list = self.plugin_utils.db.get_plugin_value("cache_list", "epg_cache", "xumo") or []
        return [self.plugin_utils.db.get_plugin_value(x, "epg_cache", "xumo") for x in cache_list if x.startswith(channel_id)]

    def get_cached_item(self, channel_id, cache_key, url):
        cache_key = datetime.datetime.today().replace(hour=cache_key).timestamp()
        cache_key = "%s_%s" % (channel_id, cache_key)
        cacheitem = self.plugin_utils.db.get_plugin_value(cache_key, "epg_cache", "xumo")
        if cacheitem:
            self.plugin_utils.logger.info("FROM CACHE:  %s" % cache_key)
            return cacheitem
        else:
            self.plugin_utils.logger.info("Fetching:  %s" % url)
            try:
                resp = self.plugin_utils.web.session.get(url)
            except self.plugin_utils.web.exceptions.HTTPError:
                self.plugin_utils.logger.info('Got an error!  Ignoring it.')
                return
            result = resp.json()

            self.plugin_utils.db.set_plugin_value(str(cache_key), "epg_cache", result, "xumo")
            cache_list = self.plugin_utils.db.get_plugin_value("cache_list", "epg_cache", "xumo") or []
            cache_list.append(str(cache_key))
            self.plugin_utils.db.set_plugin_value("cache_list", "epg_cache", cache_list, "xumo")

    def remove_stale_cache(self, todaydate):
        cache_clear_time = todaydate.strftime('%Y-%m-%dT%H:00:00')
        cache_clear_time = datetime.datetime.strptime(cache_clear_time, '%Y-%m-%dT%H:%M:%S').timestamp()
        cache_list = self.plugin_utils.db.get_plugin_value("cache_list", "epg_cache", "xumo") or []
        cache_to_kill = []
        for cacheitem in cache_list:
            cachetime = str(cacheitem).split("_")[-1]
            if float(cachetime) < cache_clear_time:
                cache_to_kill.append(cacheitem)
                self.plugin_utils.db.delete_plugin_value(str(cacheitem), "epg_cache", "xumo")
                self.plugin_utils.logger.info("Removing stale cache:  %s" % cacheitem)
        self.plugin_utils.db.set_plugin_value("cache_list", "epg_cache", [x for x in cache_list if x not in cache_to_kill], "xumo")

    def clear_cache(self):
        cache_list = self.plugin_utils.db.get_plugin_value("cache_list", "epg_cache", "xumo") or []
        for cacheitem in cache_list:
            self.plugin_utils.db.delete_plugin_value(cacheitem, "epg_cache", "xumo")
            self.plugin_utils.logger.info("Removing cache:  %s" % cacheitem)
        self.plugin_utils.db.delete_plugin_value("cache_list", "epg_cache", "xumo")
