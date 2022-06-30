def git_commit_and_push():
    """Run git commit and push it to the repository
    
    If there are some conflicted .ims2 files,
    then revert and try commit again for each conflicted .ims2 file.
    """

    print("CI ims generator")

    for _ in range(COMMIT_TRIES):
        print("Commiting...")
        _run_git_command(f"git commit -am {MSG}")
        try:
            print("Pushing to the repository...")
            _run_git_command(f"git push origin {conf.BRANCH}")
        except OSError as e:
            raise Exception(f"Error while pushing (reason: {e})")
        except subprocess.CalledProcessError as e:
            output = _run_git_command_check_output("git pull --rebase")
            conflicted_ims = re.search(
                r"CONFLICT (content): Merge conflict in (.*ims2)", str(e.output))
            if conflicted_ims is not None:
                print("WARNING: Found conflicting configuration. Reverting it...")
                _run_git_command(f"git checkout --ours {conflicted_ims.group(1)}")
                _run_git_command("git rebase --continue")
            else:
                raise Exception(f"Error while pushing (reason: {e.output})")
        else:
            print(output)
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