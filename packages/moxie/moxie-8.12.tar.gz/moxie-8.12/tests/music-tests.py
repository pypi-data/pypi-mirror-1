from __future__ import with_statement

import glob
import os.path
import tempfile
import unittest

from nose.tools import raises

from tests import DATA

from moxie.music import TrackList, TrackInfo

class TrackListTests(unittest.TestCase):
    """TrackListTest tests."""

    @raises(IOError)
    def test_not_found(self):
        """A directory that doesn't exist."""

        fn = tempfile.mktemp()
        TrackList(fn)

    def test_simple(self):
        """Load a simple directory."""

        tracks = TrackList(DATA)

        assert tracks.title == "A Moxie Mixtape!"
        assert tracks.subtitle == "Make a README"

        for fn in glob.glob(os.path.join(DATA, '*.mp3')):
            assert os.path.basename(fn) in tracks

    def test_filename_purity(self):
        """TrackList uses filenames as keys."""

        tracks = TrackList(DATA)

        for fn in tracks:
            assert fn == os.path.basename(fn)

class TrackListHeaderTest(unittest.TestCase):
    def setUp(self):
        self.dirname = tempfile.mkdtemp()
        self.headername = os.path.join(self.dirname, TrackList.HEADER)

        self.header = "Hello!"

        with file(self.headername, 'w') as f:
            f.write(self.header)

    def tearDown(self):
        os.unlink(self.headername)
        os.rmdir(self.dirname)

    def test_only_header(self):
        """Only with a header."""

        tracks = TrackList(self.dirname)

        assert tracks.title == self.header
        assert tracks.subtitle == ''
        assert len(tracks) == 0

class TrackInfoNegativeTests(unittest.TestCase):
    """TrackInfo tests on non-existent data."""

    @raises(IOError)
    def test_not_found(self):
        """Non-existent MP3."""

        fn = tempfile.mktemp()
        TrackInfo(fn)

    @raises(IOError)
    def test_invalid_directory(self):
        """A 'mp3' that is a directory."""

        TrackInfo(DATA)

class TrackInfoDataTests(unittest.TestCase):
    """TrackInfo tests on prepared data."""

    NULL_MP3 = os.path.join(DATA, 'null-noid3.mp3')
    V1_MP3   = os.path.join(DATA, 'null-v1.mp3')
    V2_MP3   = os.path.join(DATA, 'null-v2.mp3')

    def setUp(self):
        print "No such file or directory? Run 'scons'."

    def test_v1(self):
        """An ID3v1 tagged file."""

        info = TrackInfo(self.V1_MP3)
        self.check_info(info)

    def test_v2(self):
        """An ID3v2 tagged file."""

        info = TrackInfo(self.V2_MP3)
        self.check_info(info)

    def test_none(self):
        """An untagged file."""

        info = TrackInfo(self.NULL_MP3)

        assert info.album == 'No Album'
        assert info.artist == 'No Artist'
        assert info.duration == '?:??'
        assert info.length == 0
        assert info.title == 'No Title'

    def check_info(self, info):
        assert info.album == 'Null Album'
        assert info.artist == 'Null Artist'
        assert info.duration == '0:00'
        assert info.title == 'Null Title'
