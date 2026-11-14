"""Headless session editor/playback. Edits never replay or grant authority."""
from .session import parse_session, encode_session, SessionError
from .studio import run_studio_session


class StudioController:
    def __init__(self):
        self._session = None
        self._report = None
        self._index = 0
        self._playing = False

    @property
    def report(self):
        return self._report

    @property
    def playing(self):
        return self._playing

    @property
    def index(self):
        return self._index

    @property
    def row(self):
        rows = self._report.model_ticks if self._report else ()
        return rows[self._index] if rows else None

    def invalidate(self):
        self._report, self._index, self._playing = None, 0, False

    def load(self, raw):
        self.invalidate()
        self._session = None
        self._session = parse_session(raw)

    def session_bytes(self):
        if self._session is None:
            raise SessionError('load or create a session first')
        return encode_session(self._session)

    def append(self, action):
        self.invalidate()
        if self._session is None:
            raise SessionError('load or create a session first')
        candidate = dict(self._session, actions=[*self._session['actions'], action])
        self._session = parse_session(encode_session(candidate))

    def run(self, frozen_wire_v2_schema, policy_raw, claimed_host, intent_raw,
            engine_artifact, scheduler_artifact):
        self.invalidate()
        self._report = run_studio_session(self.session_bytes(), frozen_wire_v2_schema,
            policy_raw, claimed_host, intent_raw, engine_artifact, scheduler_artifact)
        return self._report

    def seek(self, index):
        if type(index) is not int:
            raise TypeError('integer playback index required')
        if not self._report or not 0 <= index < len(self._report.model_ticks):
            raise ValueError('no acknowledged tick at index')
        self._index = index
        return self.row

    def play(self):
        self._playing = bool(self._report and self._report.model_ticks)

    def pause(self):
        self._playing = False

    def step(self):
        if self._playing:
            if self._index + 1 < len(self._report.model_ticks):
                self._index += 1
            else:
                self._playing = False
        return self.row
