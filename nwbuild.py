import os
import shutil
import argparse
import subprocess
import webbrowser
import urllib.request

HOME = '~'
DIRECTORY = '.nwbuild'
ENV_FILE_NAME = '.env'
JAR_FILE_NAME = 'jenkins-cli.jar'
REMOTE_JAR_PATH = '/jnlpJars/jenkins-cli.jar'

DEFAULT_TAG = '__DEFAULT_TESTS__'
DEFAULT_URL = 'https://jenkins-v2.nextworld.net'
DEFAULT_JOB = 'Server/branch-pipe'

from dotenv import dotenv_values

def main(args):

    url = DEFAULT_URL
    home = os.path.expanduser(HOME)
    directory = os.path.join(home, DIRECTORY)
    env_path = os.path.join(directory, ENV_FILE_NAME)
    jar_path = os.path.join(directory, JAR_FILE_NAME)

    if args.reset:
        reset(url, home, directory, env_path, jar_path)
        return

    if not os.path.exists(env_path) or not os.path.exists(jar_path):
        print("\nConfiguring...")
        setup(url, home, directory, env_path, jar_path)

    config = dotenv_values(env_path)

    branch = args.branch
    if branch is None:
        branch = os.popen("git branch --show-current").read().strip()

    print (f"Submitting build for branch: [{branch}]")

    command = f"java -jar {jar_path} -s {url} -auth {config['USER']}:{config['TOKEN']} build {args.job} -p DisplayName={branch} -p ServerApiBranch={branch} -p SlackInterestedUserEmail={config['EMAIL']}"
    if args.test_tags != DEFAULT_TAG:
        command = command + f" -p NwTestTagToExecute={args.test_tags}"

    os.system(command)

    print("Job submitted")

    webbrowser.open(url + '/job/' + job.replace('/', '/job/'), new=0, autoraise=True)

def reset(url, home, directory, env_path, jar_path):
    shutil.rmtree(directory)
    setup(url, home, directory, env_path, jar_path)

def setup(url, home, directory, env_path, jar_path):

    # Check for directory
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Check for jar
    if not os.path.exists(jar_path):
        print("\nDownloading jenkins CLI...")
        jar_url = url + REMOTE_JAR_PATH
        urllib.request.urlretrieve(jar_url, jar_path)

    # Check for env file
    if not os.path.exists(env_path):
        print("\nAn api token is required for this tool to work. If you don't have a jenkins api token visit:")
        print(f"{DEFAULT_URL}/me/configure")
        print("and create a new token.\n")

        username = input("Enter your jenkins username [Usually same as github]: ")
        email = input("Enter your email: ")
        token = input("Enter your jenkins api token: ")

        with open(str(env_path), 'w+') as f:
            f.write(f"USER={username}\nEMAIL={email}\nTOKEN={token}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple CLI to kick off Jenkins jobs from the command line")

    parser.add_argument('reset', nargs='?', const=True, default=False, help="Reset your username, email or api token")
    parser.add_argument('-b', '--branch', type=str, default=None, help="The branch to build")
    parser.add_argument('-t', '--test-tags', type=str, default=DEFAULT_TAG, help="The test tags to run")
    parser.add_argument('-j', '--job', type=str, default=DEFAULT_JOB, help=f"The Jenkins job to run (Example: {DEFAULT_JOB})")
    parser.add_argument('-u', '--url', type=str, default=DEFAULT_URL, help="The Jenkins server URL")

    args = parser.parse_args()
    main(args)
