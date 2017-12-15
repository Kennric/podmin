"""
Cron job that will publish the Joe Beaver Show podcast

"""
from podmin.models import Podcast

p = Podcast.objects.get(shortname='JoeBeaverShow')

status = p.auto_publish()

f = open('/home/kennric/beavertest', 'w')
f.write(p.title)
f.write(status)
f.close
