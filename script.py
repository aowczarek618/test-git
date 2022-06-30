import conf
import subprocess
import re


COMMIT_TRIES=10
MSG="AUTOMATIC COMMIT"


def git_commit_and_push():
    """Run git commit and push it to the repository
    
    If there are some conflicted .ims2 files,
    then revert and try commit again for each conflicted .ims2 file.
    """

    print("CI ims generator")

    for _ in range(COMMIT_TRIES):
        print("Commiting...")
        _run_git_command(f"git commit -am '{MSG}'")
        try:
            print("Pushing to the repository...")
            _run_git_command(f"git push origin {conf.BRANCH}")
        except OSError as push_err:
            raise Exception(f"Error while pushing (reason: {push_err})")
        except subprocess.CalledProcessError:
            try:
                output = _run_git_command_check_output("git pull --rebase")
            except subprocess.CalledProcessError as pull_err:
                print("pull_err.output=", pull_err.output)
                print("output=", output)
                conflicted_ims = re.search(
                    r"CONFLICT (content): Merge conflict in (.*ims2)", str(pull_err.output))
                if conflicted_ims is not None:
                    print("WARNING: Found conflicting configuration. Reverting it...")
                    _run_git_command(f"git checkout --ours {conflicted_ims.group(1)}")
                    _run_git_command("git rebase --continue")
                else:
                    raise Exception(f"Error while pushing (reason: {pull_err.output})")
        else:
            break


def _run_git_command(cmd):
    process = subprocess.Popen(
        cmd,
        stderr=subprocess.STDOUT,
        shell=True,
        executable="/bin/bash",
    )
    process.communicate()

def _run_git_command_check_output(cmd):
    return subprocess.check_output(
        f"git pull --rebase",
        stderr=subprocess.STDOUT,
        shell=True,
        executable="/bin/bash",
    )

if __name__ == '__main__':
    git_commit_and_push()