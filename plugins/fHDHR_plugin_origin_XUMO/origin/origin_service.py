import json
import re

import fHDHR.exceptions


class OriginService():

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

        self.base_url = 'http://www.xumo.tv'

        self.geoID, self.geoLST = None, None

        self.login()

    def login(self):
        self.fhdhr.logger.info("Fetching XUMO token")
        self.geoID, self.geoLST = self.getID()
        if not self.geoID or not self.geoLST:
            raise fHDHR.exceptions.OriginSetupError("XUMO Setup Failed")
        else:
            self.fhdhr.logger.info("XUMO Setup Success")
            self.fhdhr.config.write(self.fhdhr.config.dict["main"]["dictpopname"], 'geoid', self.geoID)
            self.fhdhr.config.write(self.fhdhr.config.dict["main"]["dictpopname"], 'geolst', self.geoLST)
        return True

    def getID(self):

        if self.fhdhr.config.dict["origin"]["geoID"] and self.fhdhr.config.dict["origin"]["geoLST"]:
            geoID = self.fhdhr.config.dict["origin"]["geoid"]
            geoLST = self.fhdhr.config.dict["origin"]["geolst"]
            return geoID, geoLST

        try:
            url_headers = {'User-Agent': 'Mozilla/5.0'}
            pagereq = self.fhdhr.web.session.get(self.base_url, headers=url_headers).text
            results = json.loads(re.findall('__JOBS_REHYDRATE_STATE__=(.+?);</script>', (pagereq), flags=re.DOTALL)[0])
            geoID, geoLST = results["jobs"]["1"]["data"]["geoId"], results["jobs"]["1"]["data"]["channelListId"]
        except Exception as e:
            self.fhdhr.logger.warning("XUMO Setup Failed: %s" % e)
            return None, None

        return geoID, geoLST
