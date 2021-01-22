

class OriginChannels():

    def __init__(self, fhdhr, origin):
        self.fhdhr = fhdhr
        self.origin = origin

        self.base_api = 'https://valencia-app-mds.xumo.com/v2/'

    def get_channels(self):

        channel_list = []

        channel_json_path = 'channels/list/%s.json?geoId=%s' % (self.origin.geoLST, self.origin.geoID)
        channel_json_url = self.base_api + channel_json_path
        api_json = self.fhdhr.web.session.get(channel_json_url).json()

        for channel_dict in api_json['channel']['item']:

            if not self.xumo_bad(channel_dict["title"]):

                clean_station_item = {
                                     "name": channel_dict["title"],
                                     "callsign": channel_dict["callsign"],
                                     "number": str(channel_dict["number"]),
                                     "id": str(channel_dict["guid"]["value"]),
                                     "thumbnail": "https://image.xumo.com/v1/channels/channel/%s/512x512.png?type=color_onBlack" % str(channel_dict["guid"]["value"])
                                     }
                channel_list.append(clean_station_item)

        return channel_list

    def get_channel_stream(self, chandict, stream_args):

        try:

            stream_json_path = 'channels/channel/%s/onnow.json' % str(chandict["origin_id"])
            stream_id_url = self.base_api + stream_json_path
            stream_id = self.fhdhr.web.session.get(stream_id_url).json()["id"]

            stream_id_info_path = 'assets/asset/%s.json?f=title&f=providers&f=descriptions&f=runtime&f=availableSince' % str(stream_id)
            stream_id_info_url = self.base_api + stream_id_info_path
            stream_id_info_json = self.fhdhr.web.session.get(stream_id_info_url).json()
            streamurls = []
            for provider in stream_id_info_json["providers"]:
                for source in provider["sources"]:
                    streamurls.append(source["uri"])
            streamurl = streamurls[0]
        except KeyError:
            return None

        stream_info = {"url": streamurl}

        return stream_info

    def xumo_bad(self, name):
        missing = ["ACC Digital Network", "Above Average", "Adventure Sports Network", "Ameba",
                   "America's Funniest Home Videos", "Architectural Digest", "Billboard", "Bloomberg Television",
                   "CBC NEWS", "CHIVE TV", "CNET", "CollegeHumor", "Condé Nast Traveler", "Cooking Light",
                   "CoolSchool", "Copa90", "Cycle World", "FBE", "FOX Sports", "Family Feud", "Field & Stream",
                   "Food52", "Football Daily", "Fox Deportes", "Funny or Die", "Futurism", "GQ", "GameSpot",
                   "Glamour", "Got Talent Global", "Great Big Story", "HISTORY", "Hard Knocks Fighting Championship",
                   "Just For Laughs", "Just For Laughs Gags", "Kid Genius", "MMAjunkie", "MOTORVISION.TV",
                   "Mashable", "Motorcyclist", "NEW K.ID", "Newsy", "Nitro Circus", "Nosey", "NowThis",
                   "Outside TV+", "PBS Digital", "People Are Awesome", "People Magazine", "PeopleTV",
                   "Popular Science", "Real Nosey", "Refinery29", "Rowan and Martin's Laugh-In",
                   "SYFY WIRE", "Saveur", "Southern Living", "Sports Illustrated", "TIME Magazine",
                   "TMZ", "TODAY", "The Hollywood Reporter", "The Inertia", "The New Yorker", "The Pet Collective",
                   "The Preview Channel", "This Is Happening", "Titanic Channel", "Toon Goggles", "USA TODAY News",
                   "USA Today SportsWire", "Uzoo", "Vanity Fair", "Vogue", "Wochit", "World Surf League",
                   "Young Hollywood", "ZooMoo", "batteryPOP", "comicbook", "eScapes"]
        if name in missing:
            return True
        else:
            return False
