#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Sometimes you want to write a Python script for a project written in PHP.
# For the most part, this is easy, but for a few key things, PHP breaks with
# the standard and does things in a its own way.  For these cases, you can use
# this module to compensate.
#

def http_build_query(params, convention="%s"):
  """

    This was ripped shamelessly from a PHP forum and ported to Python:

      http://www.codingforums.com/showthread.php?t=72179

    Essentially, it's a (hopefully perfect) replica of PHP's
    http_build_query() that allows you to pass multi-dimensional arrays
    to a URL via POST or GET.

  """

  from urllib import quote

  if len(params) == 0:
    return ""
  else:
    output = ""
    for key in params.keys():

      if type(params[key]) is dict:
        output = output + http_build_query(params[key], convention % (key) + "[%s]")

      elif type(params[key]) is list:

        i = 0
        newparams = {}
        for element in params[key]:
          newparams[str(i)] = element
          i = i + 1

        output = output + http_build_query(newparams, convention % (key) + "[%s]")

      else:
        key = quote(key)
        val = quote(str(params[key]))
        output = output + convention % (key) + "=" + val + "&"

  return output



def parse_ini_file(filename, **kwargs):
  """

    A hacked-together attempt at making an .ini file parser that's compatible
    with the "standards" that PHP follows in its parse_ini_file() function.
    Among the handy features included are:

      * List notation (varname[] = value)
      * Associative array notation (varname[key] = value)
      * Removal of wrapping doublequotes (varname = "stuff" -becomes- varname = stuff)

    You can turn off the doublequote removal with stripquotes=False

    Example:
      from php import parse_ini_file
      config = parse_ini_file("config.ini")
      print config["sectionName"]["keyName"]

  """

  import re

  stripquotes = True
  try:
    stripquotes = kwargs["stripquotes"]
  except KeyError:
    pass

  f = open(filename, "r")

  ini = {}

  headerKey = None
  while True:

    line = f.readline()

    if not line:
      break

    header = re.match(r'^\[([^\]]+)\]$', line)

    keyval = None

    if stripquotes:
      keyval = re.match(r'^([^ =]+)\s*=\s*"?([^"]*)"?$', line)
    else:
      keyval = re.match(r'^([^ =]+)\s*=\s*(.*)$', line)

    if header:

      ini[header.group(1)] = {}
      headerKey = header.group(1)

    elif keyval:

      indexedArray = re.search('^([^\]]+)\[\]$', keyval.group(1))
      assocArray   = re.search('^([^\]]+)\["?([^\]"]+)"?\]$', keyval.group(1))

      value = keyval.group(2).rstrip("\n")
      if indexedArray:
        try:
          ini[headerKey][indexedArray.group(1)].append(value)
        except KeyError:
          ini[headerKey][indexedArray.group(1)] = [value]

      elif assocArray:
        try:
          ini[headerKey][assocArray.group(1)][assocArray.group(2)] = value
        except KeyError:
          ini[headerKey][assocArray.group(1)] = {assocArray.group(2): value}

      else:
        ini[headerKey][keyval.group(1)] = value

  f.close()

  return ini
