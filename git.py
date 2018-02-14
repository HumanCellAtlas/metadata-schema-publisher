import tarfile
import os

def install_git(event, context):
    target_directory = "/tmp/git"
    # extract git
    tar = tarfile.open("git-2.4.3.tar")
    tar.extractall(path=target_directory)
    tar.close()
    # setup dirs
    git_template_dir = target_directory +  '/usr/share/git-core/templates'
    git_exec_path = target_directory + 'usr/libexec/git-core'
    bin_path = target_directory + '/usr/bin'
    os.environ['PATH'] = os.environ['PATH'] + ":" + bin_path
    os.environ['GIT_TEMPLATE_DIR'] = git_template_dir
    os.environ['GIT_EXEC_PATH'] = git_exec_path
    response = {
        "statusCode": 200,
        "body": os.environ['PATH']
    }
    return response
