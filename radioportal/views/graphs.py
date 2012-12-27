from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Min

from tempfile import TemporaryFile
from threading import Lock
from datetime import timedelta

from radioportal.models import Show, EpisodePart

has_matplotlib=False
try:
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rc('xtick', labelsize='8')
    from matplotlib import pyplot
    graph_lock=Lock()
    has_matplotlib = True
except Exception, e: #no matplotlib available, allow testing of other stuff anyway
    has_matplotlib = False

WOCHENTAGE = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

def graph(request, type, show_name):
    if not has_matplotlib:
        return HttpResponse("matplotlib missing")
    graph = None #TODO: get cached graph
    if not graph:
        graph_lock.acquire()
        tmpfile=TemporaryFile()
        figure = pyplot.figure(1, figsize=(4,3))

        if type == "weekday":
            _weekday_graph(show_name)
        elif type == "hours":
            _hours_graph(show_name)
        elif type == "weekday_hours":
            _weekday_hours_graph(show_name)
        elif type == "time_per_episode":
            _time_per_episode_graph(show_name, figure)

        pyplot.savefig(tmpfile, format="png")
        pyplot.close(figure)
        pyplot.clf()
        tmpfile.seek(0)
        graph = tmpfile.read()
        tmpfile.close()
        graph_lock.release()
        return HttpResponse(graph, mimetype="image/png")

def weekday_graph(request, show_name):
    return graph(request, "weekday", show_name)

def hours_graph(request, show_name):
    return graph(request, "hours", show_name)

def weekday_hours_graph(request, show_name):
    return graph(request, "weekday_hours", show_name)

def time_per_episode_graph(request, show_name):
    return graph(request, "time_per_episode", show_name)

def _weekday_graph(show_name):
    show = get_object_or_404(Show, slug=show_name)
    weekdays_count = [0]*7
    labels = WOCHENTAGE 
    for episode in show.episode_set.all():
        weekdays_count[episode.begin().weekday()] += 1
    # no labels for days with 0 episodes (prevents rendering errors)
    labels = filter(lambda item: weekdays_count[labels.index(item)] >0, labels)
    weekdays_count = filter(lambda item: item >0, weekdays_count)

    pyplot.pie(
        weekdays_count,
        labels=labels,
        shadow=True,
        autopct='%1.1f%%'
    )
    pyplot.title("\"{show_name}\" Episoden nach Wochentagen".format(
        show_name=show.name))

def _hours_graph(show_name):
    show = get_object_or_404(Show, slug=show_name)
    hours_count = [0]*7
    labels = range(24)
    episode_parts = EpisodePart.objects.filter(episode__show=show)
    hours = []
    for episode_part in episode_parts:
        hour = episode_part.begin.hour
        hours.append(hour)
        for i in xrange( (episode_part.end - episode_part.begin).seconds/60/60 ):
            hour = (hour+1)%24
            hours.append(hour)
        pyplot.xticks(range(24))
        pyplot.hist(hours, range(24))
        pyplot.title("\"{show_name}\" -  Stunden in denen gesendet wurde".format(
            show_name=show.name))

def _weekday_hours_graph(show_name):
    show = get_object_or_404(Show, slug=show_name)
    hours_count = [0]*7
    labels = range(24)
    episode_parts = EpisodePart.objects.filter(episode__show=show)
    weekday_hours = map(lambda i: map(lambda j: 0, range(24)), xrange(7))
    for episode_part in episode_parts:
        date = episode_part.begin
        weekday_hours[date.weekday()][date.hour] += 1
        for i in xrange( (episode_part.end - episode_part.begin).seconds/60/60 ):
            date += timedelta(hours=1)
            print date
            weekday_hours[date.weekday()][date.hour] += 1
        pyplot.xticks(range(24))
        pyplot.yticks(range(7), WOCHENTAGE)
        pyplot.imshow(weekday_hours, interpolation="nearest")
        pyplot.title("\"{show_name}\" - Stunden/Wochentage".format(
            show_name=show.name))

def _time_per_episode_graph(show_name, figure):
    show = get_object_or_404(Show, slug=show_name)
    times=[]
    dates=[]
    for episode in show.episode_set.all().annotate(begin=Min('parts__begin')).order_by('begin'):
        time=0
        for episodepart in episode.parts.all():
            time += (episodepart.end - episodepart.begin).seconds
        times.append(time/60.0/60.0)
        dates.append(episode.begin)
    NUM_XTICKS=10
    pyplot.title("\"{show_name}\" - Sendezeit".format(show_name=show.name))
    pyplot.xticks(
        range(0, len(times), len(times)/NUM_XTICKS),
        map(
            lambda i: dates[i],
            range(0, len(times), len(times)/NUM_XTICKS)
        )
    )
    figure.autofmt_xdate(rotation=30)
    pyplot.bar(range(len(times)), times)

