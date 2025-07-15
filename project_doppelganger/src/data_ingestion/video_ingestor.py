import asyncio

class VideoIngestor:
    """
    A class for ingesting video data.
    """

    async def ingest_data(self, source: str) -> bytes:
        """
        Ingests video data from a source.

        Args:
            source: The source of the video data.

        Returns:
            The video data.
        """
        print(f"Ingesting video data from {source}...")
        await asyncio.sleep(1)  # Simulate I/O
        return b"This is some sample video data."

    async def process_data(self, data: bytes) -> bytes:
        """
        Processes video data.

        Args:
            data: The video data to process.

        Returns:
            The processed video data.
        """
        print("Processing video data...")
        await asyncio.sleep(1)  # Simulate processing
        return data
