import requests
from pathlib import Path

class NIBRSDownloader:
    '''
    Downloads NIBRS master file (.zip) from the FBI Crime Data Explorer (CDE). There exists
    one master file in ASCII format (.txt) per year.
    '''
    SIGNED_URL = "https://cde.ucr.cjis.gov/LATEST/s3/signedurl"

    def __init__(self, output_dir: Path, chunk_size: int = 50):
        self.output_dir = output_dir
        self.chunk_size = chunk_size * 1024 * 1024
        self.session = requests.Session()
        
        self.output_dir.mkdir(parents = True, exist_ok = True)

    def _get_signed_url(self, key: str) -> str:
        response = self.session.get(NIBRSDownloader.SIGNED_URL, params = {"key": key}, timeout = 30)
        response.raise_for_status()
        return response.json()[key]

    def download(self, year: int) -> Path:
        key = f"master_files/nibrs/nibrs-{year}.zip"
        target = self.output_dir.joinpath(f"nibrs-{year}.zip")

        print(f"Downloading {year} master file to {target.resolve()}...")
        with self.session.get(self._get_signed_url(key), stream = True, timeout = 60) as r:
            r.raise_for_status()
            with open(target, "wb") as f:
                for chunk in r.iter_content(chunk_size = self.chunk_size):
                    f.write(chunk)
                    
        print("Done.")
        
        return target

    def get(self, years: int | list[int]) -> list[Path]:
        if isinstance(years, int):
            years = [years]
            
        return [self.download(year) for year in years]
