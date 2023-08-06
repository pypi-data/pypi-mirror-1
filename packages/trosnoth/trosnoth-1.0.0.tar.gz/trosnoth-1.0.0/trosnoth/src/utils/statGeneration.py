# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import sys
import os
import pickle
import operator
import webbrowser

from trosnoth.data import getPath, user, makeDirs
import trosnoth.data.statGeneration as statGeneration

def generateStats(filename = None):

    def add(value, statName = None):
        if statName is None:
            html.append("\t\t\t\t<td>%s</td>" % value)
        else:
            if value == 1:
                suffix = ""
            else:
                suffix = "s"

            html.append("\t\t\t\t<td>%s&nbsp;%s%s</td>" % (value, statName, suffix))

    statPath = getPath(user, 'stats')
    makeDirs(statPath)

    if filename is None:
        files = os.listdir(statPath)
    else:
        files = [filename + ".stat"]

    stats = {}
    statNames = ['kills', 'deaths', 'zoneTags', 'shotsFired', 'shotsHit',
                 'starsEarned', 'starsUsed', 'starsWasted']
    statEnemies = ['playerKills', 'playerDeaths']
    pointValues = {'kills': 10, 'deaths': 1, 'zoneTags': 20, 'accuracy': 50,
                   'starsUsed': 3}
    leaders = []    # For camp only
    tableHeaders = ['#', 'Nick', 'Kills', 'Deaths', 'KDR', 'Zone Tags',
                    'Shots Fired', 'Shots Hit', 'Accuracy', 'Stars Earned',
                    'Stars Used', 'Stars Wasted', 'Killed the most:', 'Died the most to:', 'Points']
    html = []
    fileMatrix = {}

    for filename in files:
        try:
            statFile = open(os.path.join(statPath, filename))
        except IOError:
            raise Exception("'%s' does not exist!" % filename)

        loadedStats = pickle.load(statFile)

        for ip in loadedStats:
            for nick in loadedStats[ip]:
                if nick not in stats:
                    stats[nick] = loadedStats[ip][nick]
                    fileMatrix[nick] = [filename]
                else:
                    for stat in statNames:
                        stats[nick][stat] += loadedStats[ip][nick][stat]
                    for stat in statEnemies:
                        for enemy in loadedStats[ip][nick][stat]:
                            if enemy not in stats[nick][stat]:
                                stats[nick][stat][enemy] = 0
                            stats[nick][stat][enemy] += loadedStats[ip][nick][stat][enemy]
                    fileMatrix[nick].append(filename)

    ranking = {}
    allData = {}

    for nick in stats:
        data = stats[nick]
        try:
            data['accuracy'] = float(data['shotsHit']) / float(data['shotsFired']) * 100.0
        except ZeroDivisionError:
            data['accuracy'] = 0

        for stat in statEnemies:
            highest = 0
            highestName = "----"
            names = data[stat]
            for k, v in names.items():
                if v > highest:
                    highest = v
                    highestName = k
            if highest == 0:
                data[stat] = highestName
            else:
                data[stat] = "%s (%s)" % (highestName, highest)

        data['score'] = 0
        for stat, value in pointValues.items():
            data['score'] += data[stat] * value

        try:
            data['kdr'] = '%2.2f' % (float(data['kills']) / float(data['deaths']))
        except ZeroDivisionError:
            data['kdr'] = "----"

        ranking[nick] = data['score']
        allData[nick] = data

    rankingList = sorted(ranking.iteritems(), key=operator.itemgetter(1), reverse = True)
    ranking = {}
    rankCount = 0

    html.append("\t\t\t<tr>")
    for caption in tableHeaders:
        html.append("\t\t\t\t<th>%s</th>" % caption)
    html.append("\t\t\t</tr>")

    for pair in rankingList:
        nick = pair[0]
        rankCount += 1
        rankStr = str(rankCount)

        if nick in leaders:
            html.append("<tr style='background-color: #FFC6B3;'>")
            rankStr = '--'
            rankCount -= 1
        
        data = allData[nick]

        html.append("\t\t\t<tr>")

        add('<strong>%s</strong>' % rankStr)
        add(nick)
        add(data['kills'], 'kill')
        add(data['deaths'], 'death')
        add(data['kdr'])
        add(data['zoneTags'], 'tag')
        add(data['shotsFired'], 'shot')
        add(data['shotsHit'], 'shot')
        add('%2.2f%%' % data['accuracy'])
        add(data['starsEarned'], 'star')
        add(data['starsUsed'], 'star')
        add(data['starsWasted'], 'star')
        add(data['playerKills'])
        add(data['playerDeaths'])
        add('<strong>%2.2f</strong>' % data['score'])
        
        html.append("\t\t\t</tr>")

    html = "\n" + "\n".join(html) + "\n"
    
    baseHTML = open(getPath(statGeneration, 'statGenerationBase.htm'), 'r').read()

    html = baseHTML.replace("[[TABLE]]", html)

    htmlPath = getPath(user, 'stats.htm')

    htmlFile = open(htmlPath, "w")
    htmlFile.write(html)
    htmlFile.flush()
    htmlFile.close()

    return htmlPath

# Uncomment the next two lines and hit F5 for temporary testing of stat files
#generateStats(input("Enter filename without the .stat (or type None): "))
#webbrowser.open(getPath(user, 'stats.htm'))
