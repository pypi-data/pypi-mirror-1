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
from sys import (exit, stdin, argv)

class Kung():
    def __init__(self, file):
        self.file = file
        self.contents = self.file.read()
        self.temp = NamedTemporaryFile(suffix=".html", delete=False)
        self.lexer = None
        self.run()
        return None

    def run(self):
        self.get_lexer()
        self.pygment()
        webopen(self.temp.name)
        return None

    def get_lexer(self):
        try:
            self.lexer = get_lexer_for_mimetype(guess_type(self.file.name)[0])
        except MimeClassNotFound:
            try:
                self.lexer = get_lexer_for_filename(self.file.name)
            except LexerClassNotFound:
                try:
                    self.lexer = guess_lexer_for_filename(self.file.name,
                                                     self.contents)
                except LexerClassNotFound:
                    try:
                        self.lexer = guess_lexer(self.contents)
                    except LexerClassNotFound:
                        exit("Unknown file type.")
        return None

    def pygment(self):
        formatter = HtmlFormatter(full=True, style="colorful")
        result = highlight(self.contents, self.lexer, formatter)
        self.temp.write(result.encode('utf8'))
        return None

def main():
    parser = argparse.ArgumentParser(description="more with less")
    parser.add_argument("file", type=argparse.FileType('r'),
                        default=stdin,
                        help="file to be read. use '-' to read from stdin.")
    if argv[1] == "-":
        args = parser.parse_args(["-"])
    else:
        args = parser.parse_args()
    kung = Kung(args.file)
    kung.run()
