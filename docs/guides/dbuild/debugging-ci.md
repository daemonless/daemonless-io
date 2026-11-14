---
title: "Debugging a Failed CI Build Over VNC with a One-Time Password"
description: "Get a console in the FreeBSD VM of a failed dbuild CI run. The VNC password is made for that run and encrypted to your GitHub SSH keys, so only you can read it."
---

# Debugging a Failed CI Build

When a build fails in CI, the log is not always enough: a process killed by the
kernel, a hung test, or a VM that ran out of memory leaves little behind. For
those cases a CI run can keep its FreeBSD VM open after the failure and give you
a console in it.

## How it works

The reusable workflow (`daemonless-build.yaml`) builds every image inside a
FreeBSD VM on a GitHub runner. When you re-run a job with **debug logging**
turned on, the VM gets a VNC console reachable through a public tunnel, and a
failed step does not tear the VM down: it waits for you.

A run with the console enabled is **never published**. It skips the push, and
the job fails on purpose at the end so nothing downstream (manifests, signing,
the SBOM commit) runs. Whatever you change at the console stays in that VM.
To publish, run the workflow again without debug logging.

A public link needs a password, and a password printed in a public log is no
password at all. So each debug run:

1. Makes a random 8-character password for this run only.
2. Hides it from the log (GitHub masks it as `***`).
3. Encrypts it with [age](https://age-encryption.org) to the SSH public keys on
   the GitHub account that started the run (or re-ran it), published at
   `https://github.com/<you>.keys`.
4. Prints only the encrypted block in the **One-time VNC password** step log
   (and adds it to the run's summary page when the job finishes).

Only the private key that matches one of those public keys can decrypt it. The
password dies with the VM, and there is no shared secret to store or rotate.
This also works on forks and in other organizations, which have no secrets of
their own.

Without debug logging, no run opens a console: not pushes, not pull requests,
not routine manual rebuilds. Neither does a debug run from an account with no
usable key.

## What you need

- **Write access to the image's repository.** Only accounts that can re-run a
  workflow can get a console, and each one gets its own password.
- **An SSH key on your GitHub account**, type `ssh-ed25519` or `ssh-rsa`.
  Hardware-backed `sk-` keys do not work with age. Check with
  `curl https://github.com/<you>.keys`.
- **The matching private key** on the machine you will decrypt on. A key with
  or without a passphrase both work.
- **age**, installed on that machine:

=== "FreeBSD"

    ```sh
    doas pkg install -y age
    ```

=== "Debian / Ubuntu"

    ```sh
    sudo apt install age
    ```

=== "Fedora"

    ```sh
    sudo dnf install age
    ```

=== "macOS"

    ```sh
    brew install age
    ```

## Step by step

**1. Re-run with debug logging.** Open the failed run in the repository's
**Actions** tab, choose **Re-run jobs** -> **Re-run failed jobs**, tick
**Enable debug logging**, and confirm. Or with the GitHub CLI:

```sh
gh run rerun <run-id> -R <owner>/<image> --failed --debug
```

**2. Wait for it to fail again.** The failed step stops with a line like:

```
Please open the remote vnc link for debugging: https://<random>.trycloudflare.com .
To finish debugging, you can run `touch ~/continue` in the VM.
```

**3. Get the password.** In the running job's log, expand the
**One-time VNC password** step (the run's **Summary** page only updates after
the job ends) and copy the block:

```
-----BEGIN AGE ENCRYPTED FILE-----
...
-----END AGE ENCRYPTED FILE-----
```

Save it to a file and decrypt it with your key:

```sh
age -d -i ~/.ssh/id_ed25519 vnc.age
```

**4. Open the link** from step 2 and enter the password. You are logged in to
the VM as root.

**5. Finish.** When you are done, let the workflow continue:

```sh
touch ~/continue
```

or cancel the run from the Actions tab. Do not leave it open: the run holds a
runner, and the link stays reachable, until it ends. Either way the job ends
failed with "Remote VNC was enabled for this run", which is expected: a debug
run is never published.

## Inside the VM

The build ran in the repository checkout under `~/work`. Useful places to start:

| question | command |
|---|---|
| Did the kernel kill something? | `grep 'was killed' /var/log/messages` |
| Memory and swap | `sysctl hw.physmem` and `swapinfo -h` |
| Disk | `df -h /` and `zpool list` |
| What is still running | `ps auxww` and `top -o res` |
| Re-run the test interactively | `PYTHONPATH=/tmp/dbuild python3 -m dbuild -v test` |
| Live containers or jails | `podman ps -a`, `podman logs <name>`, and `appjail status` |

From inside the VM, `ssh host` reaches the GitHub runner that hosts it.

## Security notes

- **The link is public.** Anyone who has both the link and the password gets a
  root console in the VM. Treat the decrypted password like any other
  credential, and end the run when you are done.
- **The VM holds no credentials.** A debug run publishes nothing, so its VM
  gets no `GITHUB_TOKEN` and no registry token: a leaked password cannot push
  an image or change the repository. The cost is that version lookups against
  the GitHub API run unauthenticated and can hit GitHub's rate limit on shared
  runners; if one fails that way, re-run it.
- **Nothing from a debug run is published.** The push is skipped and the job
  fails on purpose, so an image someone may have changed at the console never
  reaches the registry.
- **Only 8 characters count.** Classic VNC authentication ignores anything past
  eight, which is why the password is exactly eight.
- **Your private key decrypts it.** Anyone who can read your private key can
  read these passwords too, the same as everything else that key unlocks.
- **No key, no console.** A debug run from an account without a usable key
  logs a warning and runs without keeping the VM open, rather than opening a
  console with a password everyone can see.
