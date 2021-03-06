from sys import stdout
import conf
import subprocess
import re


MSG="AUTOMATIC COMMIT"


def git_commit_and_push():
    """Run git commit and push it to the repository
    
    If there are some conflicted .ims2 files,
    then revert and try commit again for each conflicted .ims2 file.
    """

    print("CI ims generator")

    print("Commiting...")
    _run_git_command(f"git commit -am '{MSG}'")
    try:
        print("Pushing to the repository...")
        _run_git_command_check_output(f"git push origin {conf.BRANCH}")
    except OSError as push_err:
        raise Exception(f"Error while pushing (reason: {push_err})")
    except subprocess.CalledProcessError:
        try:
            _run_git_command_check_output("git pull --rebase")
        except subprocess.CalledProcessError as pull_err:
            conflicted_ims_files = re.findall(
                r"CONFLICT \(content\): Merge conflict in (.*ims2)", pull_err.output.decode('utf-8'))
            if conflicted_ims_files is not None:
                print("WARNING: Found conflicting configuration. Fixing the conflicts...")
                _run_git_command(f"git checkout --ours {' '.join(conflicted_ims_files)}")
                _run_git_command(f"git add {' '.join(conflicted_ims_files)}")
                _run_git_command(f"GIT_EDITOR=true git rebase --continue")
                _run_git_command(f"git push origin {conf.BRANCH}")
            else:
                raise Exception(f"Error while pushing (reason: {pull_err.output})")


def _run_git_command(cmd):
    print(f"Running {cmd}")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        executable="/bin/bash",
    )
    output, error = process.communicate()
    return output, error

def _run_git_command_check_output(cmd):
    print(f"Running {cmd}")
    return subprocess.check_output(
        cmd,
        shell=True,
        executable="/bin/bash",
    )

if __name__ == '__main__':
    git_commit_and_push()