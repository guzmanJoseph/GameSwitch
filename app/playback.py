from abc import ABC, abstractmethod

class PlaybackAdapter(ABC):
    @abstractmethod
    def select(self, game: dict) -> dict:
        """Return what happened when selecting a game."""

class SimulatedPlaybackAdapter(PlaybackAdapter):
    def select(self, game: dict) -> dict:
        return {'mode': 'simulation', 'selected_game_id': game['id'], 'channel': game['channel'], 'actual_stream_changed': False}

class YouTubeTVPlaybackAdapter(PlaybackAdapter):
    def select(self, game: dict) -> dict:
        return {'mode': 'unsupported', 'selected_game_id': game['id'], 'actual_stream_changed': False,
                'message': 'YouTube TV automatic channel selection is not implemented or verified.'}
