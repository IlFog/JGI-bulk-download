import argparse
import getpass
import pandas as pd
import subprocess
import sys

def user_login():
    """
    Prompt the user for JGI credentials.
    """
    user = input("Insert JGI username/email or q to exit: ")
    if user == "q":
        sys.exit("Exiting now.")

    pw = getpass.getpass("Insert JGI password or q to exit:")
    if pw == "q":
        sys.exit("Exiting now.")
    
    return user, pw

def load_urls(filepath):
    """
    Load URLs from a CSV file.
    """
    try:
        data = pd.read_csv(filepath)
        data["portal"] = data["JGI Contigs Link"].str.split("/").str[4]
        urls = data["portal"].dropna().tolist()
        return urls
    except FileNotFoundError:
        sys.exit(f"File not found: {filepath}")

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
