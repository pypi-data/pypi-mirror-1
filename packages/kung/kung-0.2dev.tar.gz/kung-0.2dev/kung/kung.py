#!/usr/bin/env python

from pygments import highlight
from pygments.lexers import (get_lexer_for_mimetype, get_lexer_for_filename,
                             guess_lexer, guess_lexer_for_filename,
                             ClassNotFound as LexerClassNotFound)
from pygments.util import ClassNotFound as MimeClassNotFound
from pygments.styles import get_style_by_name
from pygments.formatters import HtmlFormatter
from webbrowser import open as webopen
import argparse
from mimetypes import guess_type
from tempfile import NamedTemporaryFile
from sys import exit

class Kung():
    def __init__(self, path):
        self.path = path
        self.file = open(path, 'r')
        self.temp = NamedTemporaryFile(suffix=".html", delete=False)
        self.pygmentize()
        return None

    def run(self):
        webopen(self.temp.name)
        return None

    def pygmentize(self):
        try:
            lexer = get_lexer_for_mimetype(guess_type(self.path)[0])
        except MimeClassNotFound:
            try:
                lexer = get_lexer_for_filename(self.path)
            except LexerClassNotFound:
                try:
                    lexer = guess_lexer(self.file.read())
                except LexerClassNotFound:
                    try:
                        lexer = guess_lexer_for_filename(self.path,
                                                         self.file.read())
                    except LexerClassNotFound:
                        exit("Unknown file type.")
        formatter = HtmlFormatter(full=True, style="colorful")
        result = highlight(self.file.read(), lexer, formatter)
        self.temp.write(result.encode('utf8'))
        return None

def main():
    parser = argparse.ArgumentParser(description="more for less")
    parser.add_argument('file', help="file to be read")
    args = parser.parse_args()
    kung = Kung(args.file)
    kung.run()
