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
            print("pull_err.output=", pull_err.output)
            print("pull_err.returncode=", pull_err.returncode)
            print("pull_err.cmd=", pull_err.cmd)
            print("pull_err.stdout=", pull_err.stdout)
            print("pull_err.stderr=", pull_err.stderr)
            conflicted_ims = re.search(
                r"^CONFLICT \(content\): Merge conflict in (.*ims2)$", str(pull_err.output))
            print("conflicted_ims=", conflicted_ims)
            if conflicted_ims is not None:
                print("conflicted_ims.group(1)=",conflicted_ims.group(1))
                print("WARNING: Found conflicting configuration. Reverting it...")
                _run_git_command(f"git checkout --ours {conflicted_ims.group(1)}")
                _run_git_command(f"git add {conflicted_ims.group(1)}")
                _run_git_command("git rebase --continue")
                _run_git_command(f"git push origin {conf.BRANCH}")
            else:
                raise Exception(f"Error while pushing (reason: {pull_err.output})")


def _run_git_command(cmd):
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
    return subprocess.check_output(
        cmd,
        shell=True,
        executable="/bin/bash",
    )

if __name__ == '__main__':
    git_commit_and_push()