from podmin.models import Podcast, Episode

p = Podcast.objects.get(id=1)

f = open('/home/kennric/beavertest', 'w')
f.write(p.title)
f.close

#p.autopublish
