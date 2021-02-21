from datetime import datetime

import dateutil.parser as dp
import sanic
import sanic.response


async def handler(req):

    seasonstart="2020-12-02T08:00:00Z"
    seasonend="2021-03-16T08:00:00Z"

    response = {
        'status': 200,
        'message': 'Everything should work fine',
        'data': {
            'DaysLeft': int((dp.parse(seasonend).timestamp()-datetime.utcnow().timestamp())/86400),
            'DaysGone': int((datetime.utcnow().timestamp()-dp.parse(seasonstart).timestamp())/86400),
            'SeasonLength': int((dp.parse(seasonend).timestamp()-dp.parse(seasonstart).timestamp())/86400)
        }
    }

    return sanic.response.json(response)
