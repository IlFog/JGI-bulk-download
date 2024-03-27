from typing import List
import argparse
import getpass
import pandas as pd
import subprocess
import sys

def user_login(exit_command: str = 'q') -> dict:
    """
    Prompt the user for JGI credentials and return a dictionary with keys 'username' and 'password'.
    """
    while True:
        user = input("Insert JGI username/email or {} to exit: ".format(exit_command))
        if user == exit_command:
            return {'username': None, 'password': None}

        pw = getpass.getpass("Insert JGI password or {} to exit:".format(exit_command))
        if pw == exit_command:
            return {'username': None, 'password': None}

        if validate_credentials(user, pw):
            break

    return {'username': user, 'password': pw}

def load_urls(filepath: str) -> List[str]:
    """
    Load URLs from a CSV file.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        List[str]: A list of URLs extracted from the CSV file.
    """
    try:
        data = pd.read_csv(filepath)
        urls = data["JGI Contigs Link"].str.split("/").str[4].dropna().tolist()
        return urls
    except FileNotFoundError:
        sys.exit(f"File not found: {filepath}")
    except Exception as e:
        sys.exit(f"Error loading file: {e}")

def generate_bulk_download_command(portals, filetypes, filepattern, organised_by_filetype, send_email):
    """
    Generate a bulk download command using curl.
    """
    portals = ",".join(portals)
    download = (
        f"curl 'https://genome-downloads.jgi.doe.gov/portal/ext-api/downloads/bulk/request' "
        f"-b cookies "
        f"--data-urlencode 'portals={portals}' "
        f"--data-urlencode 'fileTypes={filetypes}' "
        f"--data-urlencode 'filePattern={filepattern}' "
        f"--data-urlencode 'organizedByFileType={organised_by_filetype}' "
        f"--data-urlencode 'sendMail={send_email}'"
    )
    subprocess.run(download, shell = True)

def login_jgi(username, password):
    """
    Log in to JGI website and save cookies.
    """
    cmd = (
        f"curl 'https://signon.jgi.doe.gov/signon/create' "
        f"--data-urlencode 'login={username}' "
        f"--data-urlencode 'password={password}' "
        f"-s -c cookies > /dev/null"
    )
    subprocess.run(cmd, shell=True)

def main():
    parser = argparse.ArgumentParser(description="Bulk download files from JGI URLs")
    parser.add_argument("-u", "--url-file", required=True, help="Path to a file containing list of URLs")
    parser.add_argument("-T", "--filetypes", default="Report", help="Comma-separated list of file types to download (available types: Report, Alignment, Annotation, Assembly, Sequence)")
    parser.add_argument("-p", "--filepattern", default=None, help="Regular expression pattern to filter file names (should be a Java regular expression, e.g. .*\.fasta\.gz)")
    parser.add_argument("-x", "--organised-by-filetype", default="false", choices=["true", "false"], help="Organize files by file type")
    parser.add_argument("-e", "--send-email", default="true", choices=["true", "false"], help="Send email when files are ready for download")
    args = parser.parse_args()

    username, password = user_login()
    login_jgi(username, password)

    filetypes = args.filetypes
    filepattern = args.filepattern
    organised_by_filetype = args.organised_by_filetype
    send_email = args.send_email

    portals = load_urls(args.url_file)
    bulk_command = generate_bulk_download_command(portals, filetypes, filepattern, organised_by_filetype, send_email)
    #print("\nBulk download command:", bulk_command)

if __name__ == '__main__':
    main()
