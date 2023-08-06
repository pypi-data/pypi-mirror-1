"""
IMDbName

A script that renames movie files using data from the IMDb database

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from datetime import date
from optparse import OptionParser
from os import path, rename
from re import findall
from sys import exit
from tempfile import mkstemp

from imdb.parser.http import IMDbHTTPAccessSystem

VERSION = '0.1'

BASIC_COPYRIGHT = 'Copyright (C) 2010 Jimmy Theis'

BASIC_LICENSE = """
================================================================
IMDbName  Copyright (C) 2010  Jimmy Theis
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions; for details, use the `--license' flag.
================================================================
"""

FULL_LICENSE = """
IMDbName: A script for renaming movie files
Copyright (C) 2010  Jimmy Theis

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


def print_basic_license():
    """Prints the basic license statement

       This should happen whenever the program is run.
    """
    print BASIC_LICENSE


def print_full_license():
    """Prints the full license statement

       This should only happen on request, as the statement is pretty long.
    """
    print FULL_LICENSE


def parse_args():
    """Retrieves, validates, and returns command line arguments

       Returns a tuple of the following values:

       opts: object containing command line options
       args: a tuple of arguments (strings)
       parser: OptionParser object
    """

    class CustomParser(OptionParser):
        """Class for overriding some printing functionality of OptionParser
        """

        def format_description(self, formatter):
            """Don't strip newlines when printing the description
            """
            return self.get_description()

    usage = 'usage: %prog [options] FILE1 [FILE2 FILE3 ...]'
    version = '\n%prog ' + VERSION + '\n' + BASIC_COPYRIGHT + '\n'
    description = """Renames movie files using data from the IMDb database

Format Specifiers:
  %t    Title (with 'A' or 'The' moved to the end)
  %T    Title (without 'A' or 'The' moved to the end)
  %y    Year
  %i    IMDb id number
"""

    parser = CustomParser(usage=usage,
                          version=version,
                          description=description)

    parser.add_option('--license',
                      action='store_true',
                      dest='license',
                      help='show license information and exit')

    parser.add_option('-v', '--verbose',
                      action='store_true',
                      dest='verbose',
                      help='print extra helpful information')

    parser.add_option('-f', '--format',
                      dest='format',
                      metavar='FORMATSTRING',
                      default='%t (%y)',
                      help=('specify format for filenames (format '
                            'specifiers above) [default: %default]'))

    parser.add_option('-a', '--assume-correct',
                      action='store_true',
                      dest='assume',
                      help=("don't prompt for files with only one "
                            "possible title"))

    opts, args = parser.parse_args()

    if opts.license:
        print_full_license()
        exit()

    if len(args) < 1:
        print 'Error: You must provide at least one target file\n'
        parser.print_help()
        exit(1)

    return opts, args, parser


def normalize(title):
    """Formats and returns a movie title for easy searching and matching

       Removes any symbols, repeated spaces, and changes all letters to
       lowercase, returning the result.

       Keyword Arguments:
           title - movie title to be formatted
    """
    result = ''
    prevc = ''
    for c in title:
        if c.isalnum():
            result += c.lower()
            prevc = c.lower()
        elif c.isspace() and not prevc.isspace():
            result += c
            prevc = c
    return result


def format_safe_name(title):
    """Formats and returns a finished filename into a Windows-safe filename

       Removes any disallowed characters, replacing some with substitutes a
       necessary.

       Keyword Arguments:
           title - filename to be formatted
    """
    replacements = {'\\': '-',
                    '/': '-',
                    ':': ' - ',
                    '*': '',
                    '?': '',
                    '<': '',
                    '>': '',
                    '|': ''}
    for c in replacements.keys():
        title = title.replace(c, replacements[c])
    return title


def format_filename(format_string, movie):
    """Returns a properly formatted filename from the the movie object

       Does not include the file extension

       Keyword Arguments:
           format_string - formatting template string for new filename
           movie - IMDbPY Movie object that provides movie data
    """
    title = movie['title']
    can_title = movie['canonical title']
    year = str(movie['year'])
    imdb_id = movie.getID()

    format_string_re = r'(.*?)(%[tTyi])(?:([^%])*(?!%))'

    replacements = {'%t': can_title,
                    '%T': title,
                    '%y': year,
                    '%i': imdb_id}

    sr = findall(format_string_re, format_string)

    result = ''

    for terms in sr:
        for item in terms:
            if item in replacements.keys():
                result += replacements[item]
            else:
                result += item

    return format_safe_name(result)


def search_movie(imdb, filename):
    """Searches the IMDb database for matching movies

       Returns a list of tuples, where the first value of each is whether
       or not the titles are an exact match, and the second value is
       the actual (simple) movie object.

       Keyword Arguments:
           imdb - IMDb parser to use
           filename - String to search (in this case the filename without
                      the file extension
    """
    sr = imdb.search_movie(filename)
    title = normalize(filename)
    result = []
    current_year = date.today().year
    for item in sr:
        search_title = normalize(item['title'])
        if 'year' not in item.keys():
            continue
        elif item['year'] > current_year:
            continue
        elif item['kind'] != u'movie':
            continue
        elif search_title == title:
            result.append((True, item))
        else:
            result.append((False, item))
    return result


def get_user_action(imdb_results=[], **kw):
    """Prompts the user for action selection, then calls functions accordingly

       Gives control to whichever function user selection falls under

       Keyword Arguments:
           imdb_results - A list of tuples, with the first value being whether
                          or not the movie title is an exact match, and the
                          second value being a simple movie object
    """
    actions = {'s': skip_file,
               'skip': skip_file,
               'skip file': skip_file,
               'i': alt_id,
               'id': alt_id,
               'imdb id': alt_id,
               'specify imdb id': alt_id,
               'c': custom_name,
               'custom': custom_name,
               'custom filename': custom_name,
               'enter custom filename': custom_name}

    print '================================================================'
    print 'Enter a search result number to apply it or select an action:'
    print '  (s)kip file'
    print '  specify (i)mdb id'
    print '  enter (c)ustom filename'
    print '================================================================'
    user_action = raw_input('>> ')

    kw['imdb_results'] = imdb_results
    kw['user_action'] = user_action

    if user_action.isdigit() and int(user_action) <= len(imdb_results):
        apply_name(**kw)
    else:
        actions.get(user_action, bad_response)(**kw)


def apply_name(exact_match=False, assume=False, verbose=False, fullpath='',
               parentpath='', file_ext='', format_string='',
               imdb_results=[], user_action='', **kw):
    """Applies new filename based on user selection and command line options

       Handles both the exact match and `--assume-correct` option, and the
       entry of a valid selection number by the user.

       Keyword Arguments:
           exact_match - boolean value representing whether or not there is
                         only one exact title match
           assume - command line option `--assume-correct`
           verbose - command line option `--verbose`
           fullpath - full path, including filename, of old file
           parentpath - full path, not including filename, of old file
           file_ext - file extension (including the dot) of old file
           format_string - formatting template string to use
           imdb_results - a list of tuples, with the first value being whether
                          or not the movie is an exact title match, and the
                          second value being a simple movie object
           user_action - action selection string the user entered
    """
    if assume and exact_match:
        for item, movie in imdb_results:
            if item == True:
                new_filename = format_filename(format_string, movie) + file_ext
                break
    else:
        movie = imdb_results[int(user_action) - 1][1]
        new_filename = format_filename(format_string, movie) + file_ext

    print 'Applying filename %s...' % new_filename
    rename(fullpath, path.join(parentpath, new_filename))


def skip_file(filename='', file_ext='', **kw):
    """Handles users skipping files

       Prints an error message and returns.

       Keyword Arguments
           filename - filename of old movie file
           file_ext - file extension (including the dot) of old file
    """
    print 'Skipping file %s...' % (filename + file_ext)


def alt_id(imdb=None, user_action='', format_string='', file_ext='',
           fullpath='', parentpath='', **kw):
    """Handles users entering a custom IMDb id

       Prompts user for new id, verifies it, confirms selection, and applies.

       Keyword Arguments:
           imdb - IMDb parser to use
           user_action - string user entered for action selection
           format_string - formatting template string to use
           file_ext - string of file extention (including the dot)
           fullpath - full path, including filename, of old file
           parentpath - full path, not including filename, of old file
    """
    kw['imdb'] = imdb
    kw['format_string'] = format_string
    kw['file_ext'] = file_ext
    kw['fullpath'] = fullpath
    kw['parentpath'] = parentpath
    user_response = 'n'
    movie = None
    while user_response.lower() not in ('y', 'yes'):
        print 'Enter IMDb id:'
        new_id = raw_input('>> ')
        if not new_id.isdigit():
            print 'Error: Bad IMDb id'
            get_user_action(**kw)
            return
        movie = imdb.get_movie(new_id)
        if len(movie.keys()) == 0:
            print 'Error: Bad IMDb id'
            get_user_action(**kw)
            return
        else:
            print 'Is this the correct movie: '
            print '  %s (%04d)' % (movie['title'], movie['year'])
            user_response = ''
            while user_response.lower() not in ('y', 'yes', 'n', 'no'):
                user_response = raw_input('>> ')
    new_filename = format_filename(format_string, movie) + file_ext
    print 'Applying filename %s...' % new_filename
    rename(fullpath, path.join(parentpath, new_filename))


def custom_name(fullpath='', file_ext='', parentpath='', **kw):
    """Handles users defining their own filenames

       Prompts user for new filename, makes it safe, and applies it

       Keyword Arguments:
           fullpath - full path, including filename, of old file
           parentpath - full path, not including filename, of old file
    """
    print "Enter new filename (I'll add the file extension):"
    new_filename = raw_input('>> ') + file_ext
    print 'Applying filename %s...' % new_filename
    rename(fullpath, path.join(parentpath, new_filename))


def bad_response(user_action='', **kw):
    """Handles invalid user responses

       Prints a simple error message and returns control to get_user_action

       Keyword Arguments:
           user_action - invalid string user entered
    """
    kw['user_action'] = user_action
    print 'Error: Bad response: %s' % user_action
    get_user_action(**kw)


def main():
    """Runs the IMDbName script

       Called when the script is used. Returns 0 or 1 for success and failure,
       so as to work well with other shell commands
    """
    opts, args, parser = parse_args()

    print_basic_license()

    imdb_kwds = {'useModule': 'beautifulsoup'}
    imdb = IMDbHTTPAccessSystem(**imdb_kwds)

    for arg in args:
        fullpath = path.abspath(arg)

        if not path.exists(fullpath):
            print 'Error: No such file: %s. Skipping...' % fullpath
            continue

        parentpath, filename = path.split(arg)

        dot_index = filename.rfind('.')
        if dot_index == -1:
            dot_index = len(filename)

        file_ext = filename[dot_index:]
        file_title = filename[:dot_index]

        print '=' * 64
        print '  %s' % filename
        print '=' * 64

        if opts.verbose:
            print '\nSearching IMDb...\n'

        imdb_results = search_movie(imdb, file_title)

        matches = 0
        exact_match = False

        for ind_match, item in imdb_results:
            matches += ind_match and 1 or 0
            match_text = ind_match and '**EXACT MATCH**' or ''
            outtext = '%2d) %s (%4d) %s'
            outtext = outtext % (imdb_results.index((ind_match, item)) + 1,
                                  item['title'],
                                  item['year'],
                                  match_text)
            print outtext

        exact_match = matches == 1

        keywords = {'filename': file_title,
                    'fullpath': fullpath,
                    'parentpath': parentpath,
                    'file_ext': file_ext,
                    'exact_match': exact_match,
                    'imdb': imdb,
                    'imdb_results': imdb_results,
                    'format_string': opts.format,
                    'verbose': opts.verbose,
                    'assume': opts.assume}

        if exact_match and opts.assume:
            print 'Exact match found.'
            apply_name(**keywords)
        else:
            get_user_action(**keywords)

    return 0


if __name__ == '__main__':
    exit(main())
