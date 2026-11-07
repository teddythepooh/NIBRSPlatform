import requests
from pathlib import Path
from zipfile_deflate64 import ZipFile

class NIBRSDownload:
    '''
    Downloads NIBRS master file (.zip) from the FBI Crime Data Explorer (CDE)'s underlying S3 bucket.
    There exists one master file in ASCII format (.txt) per year.
    '''
    SIGNED_URL = "https://cde.ucr.cjis.gov/LATEST/s3/signedurl" 
    
    def __init__(self, output_dir: Path, chunk_size: int = 50, timeout: int = 60):
        '''
        output_dir: Path to directory where NIBRS master files will be downloaded.
        chunk_size: Size (in MB) to stream from signed URL to output_dir at a time.
        timeout: Timeout (in seconds) for HTTP requests.
        '''
        self.output_dir = output_dir
        self.chunk_size = chunk_size * 1024 * 1024
        self.session = requests.Session()
        self.timeout = timeout
        
        self.output_dir.mkdir(parents = True, exist_ok = True)

    def _get_signed_url(self, key: str) -> str:
        '''
        key: S3 object key.
        
        Initiates request to FBI CDE for retrieval of NIBRS master file from S3. Nothing is downloaded at this stage.
        '''
        response = self.session.get(NIBRSDownload.SIGNED_URL, params = {"key": key}, timeout = self.timeout)
        response.raise_for_status()
        return response.json()[key]

    def _build_s3_object_key(self, year: int) -> str:
        '''
        year: Desired year to download.
        
        Builds S3 object key that is to be appended to the signed URL.
        '''
        return f"master_files/nibrs/nibrs-{year}.zip"

    def _download(self, year: int) -> Path:
        '''
        year: Desired year to download.
        
        Downloads NIBRS master file for a given year.
        '''
        key = self._build_s3_object_key(year)
        target = self.output_dir.joinpath(Path(key).name)

        print(f"Downloading {year} master file to {target.resolve()}...")
        with self.session.get(self._get_signed_url(key), stream = True, timeout = self.timeout) as r:
            r.raise_for_status()
            with open(target, "wb") as f:
                for chunk in r.iter_content(chunk_size = self.chunk_size):
                    f.write(chunk)
                    
        print("Done.")
        
        return target

    def download(self, years: int | list[int]) -> list[Path]:
        '''
        years: Desired year(s) to download.
        
        Downloads NIBRS master file.
        '''
        if isinstance(years, int):
            years = [years]
            
        return [self._download(year) for year in years]

class NIBRSUnzip:
    '''
    Unzips NIBRS master file (.zip) to recover the underlying ASCII files (.txt). The ASCII file name
    is renamed to match the zip file name. Lastly, it is unzipped to the same location as the zip file.
    '''
    def __init__(self, zip_file: Path):
        '''
        zip_file: Path to NIBRS master file (.zip).
        '''
        self.zip_file = zip_file
        
    def _parse_zip_file(self) -> str:
        '''
        Verifies contents of zip_file. The expected content is simply the ASCII file (.txt) and nothing else.
        '''
        with ZipFile(self.zip_file, "r") as z:
            contents = z.namelist()

        if len(contents) != 1:
            raise ValueError(f"Expected one file in {self.zip_file}. Found {len(contents)}: {contents} instead.")

        if Path(contents[0]).suffix.lower() != ".txt":
            raise ValueError(f"Expected a .txt file in {self.zip_file}. Found {contents[0]} instead.")

        return contents[0]
    
    def _standardize_file_name(self, ascii_file: Path) -> Path:
        '''
        ascii_file: Path to extracted ASCII file (.txt).
        
        Renames the ASCII file to match the zip file name.
        '''
        new_name = (self.zip_file).with_suffix(".txt")
        ascii_file.replace(new_name) # overwrites existing file (if one exists) to avoid FileExistsError
        print(f"{ascii_file} has been renamed to {new_name}")
        
        return new_name

    def unzip(self) -> Path:
        '''
        Unzips NIBRS master file.
        '''
        ascii_file = ((self.zip_file).parent).joinpath(self._parse_zip_file())
        
        with ZipFile(self.zip_file, "r") as z:
            z.extractall(path = (self.zip_file).parent)
            print(f"{self.zip_file} has been unzipped.")    
        
        return self._standardize_file_name(ascii_file)
