import argparse
from pathlib import Path
from src import NIBRSDownload

def main(args: argparse.Namespace):
    '''
    Downloads NIBRS master files (.zip) from the FBI Crime Data Explorer (CDE).
    '''
    master_files = NIBRSDownload(output_dir = Path(args.output_dir))
    master_files.get(years = args.year)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = main.__doc__,
        formatter_class = argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--year", "-y", nargs="+", type = int, default = [2025])
    parser.add_argument("--output_dir", "-o", default = "output")
    args = parser.parse_args()
    
    main(args)
