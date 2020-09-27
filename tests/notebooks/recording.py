"""Record and playback HTTP responses."""
import vcr


class Record:
    """Wrapper for vcr cassettes recording.."""

    def start(self, title):
        """Start the recording/playback."""
        self.cassete = vcr.use_cassette(
            f"../cassetes/{title}.yaml",
            filter_headers=[('origin', '127.0.0.1')]
        )
        self.cassete.__enter__()
        return self

    def stop(self):
        """Stop the current recording/playback."""
        self.cassete.__exit__()
