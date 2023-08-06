#!/usr/bin/python
import string

def main():
  # get the list of tags and their frequency from input file
  # taglist = getTagListSortedByFrequency('tags.txt')
  # taglist = getSortedTagList()
  # find max and min frequency
  # ranges = getRanges(taglist)
  # print "Ranges %s" % ranges
  # write out results to output, tags are written out alphabetically
  # with size indicating the relative frequency of their occurence
  # print writeCloud(taglist, ranges)
  # print writeCloud(taglist, ranges)
  print makeCloud()

def makeCloud():
    import math
    import pg
    steps = 6
    dbx = pg.DB('bel')
    input = dbx.query('select concept, frequency from rattag_frequency order by frequency desc limit 100;').getresult()
    temp, newThresholds, results = [], [], []
    maxWeight = input[0][1]
    minWeight = input[-1][1]
    newDelta = (maxWeight - minWeight)/float(steps)
    for i in range(steps + 1):
       newThresholds.append((100 * math.log((minWeight + i * newDelta) + 2), i))
    for tag in input:
        fontSet = False
        for threshold in newThresholds[1:int(steps)+1]:
            if (100 * math.log(tag[1] + 2)) <= threshold[0] and not fontSet:
                results.append((tag[0],str(threshold[1])))
                fontSet = True
    results.sort(lambda x, y: cmp(x[0], y[0]))
    return ' '.join(['<span style="font-size:%sem"><a href="/news/search/%s">%s</a></span>' % \
                    (f, c, c) for c, f in results])

def writeCloud(taglist, ranges):
  outputf = "<style type=\"text/css\">\n" + \
            ".smallestTag {font-size: xx-small;}\n" + \
            ".smallTag {font-size: small;}\n" + \
            ".mediumTag {font-size: medium;}\n" + \
            ".largeTag {font-size: large;}\n" + \
            ".largestTag {font-size: xx-large;}\n" + \
            "</style>\n"
  rangeStyle = ["smallestTag", "smallTag", "mediumTag", "largeTag", "largestTag"]
  # resort the tags alphabetically
  taglist.sort(lambda x, y: cmp(x[0], y[0]))
  for tag in taglist:
    rangeIndex = 0
    for range in ranges:
      url = "http://www.google.com/search?q=" + tag[0].replace(' ', '+') + "+site%3Abel-epa.com"
      if (tag[1] >= range[0] and tag[1] <= range[1]):
        outputf += "<span class=\"" + rangeStyle[rangeIndex] + "\"><a href=\"" + url + "\">" + tag[0] + "</a></span> "
        break
      rangeIndex = rangeIndex + 1
  return outputf

if __name__ == "__main__":
  main()