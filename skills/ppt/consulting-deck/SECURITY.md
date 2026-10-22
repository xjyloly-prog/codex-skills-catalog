# Security Policy

## Supported versions

Security fixes are provided for the latest tagged release.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting for this repository. Please do not
publish credentials, private source material, or an unpatched exploit in a
public issue.

Include:

- affected version or commit;
- the relevant file and behavior;
- the minimum reproduction;
- expected impact;
- a suggested mitigation, if available.

## Runtime boundaries

Consulting Deck is an instruction and validation Skill. Its included Python
scripts:

- read and write files only inside a user-selected deck workspace;
- inspect local PPTX ZIP/XML packages;
- do not collect prompts, credentials, browser data, or private messages;
- do not install hooks or persistence;
- do not make automatic network requests;
- do not download or execute remote code.

Source research, presentation rendering, external publishing, and package
installation are performed by the Agent host and remain subject to that host's
permission model.

The executable exhibit module receives already available host slide objects; it
does not import/download a third-party renderer, start a local server, or contact
an update endpoint. JSON/CSV chart paths must resolve inside the selected workspace;
parent-directory and symlink escapes are rejected. Explicit output paths remain
user-selected and must be permission-scoped by the host. Treat ZIP/XML packages as
untrusted inputs and do not run validation with access to unrelated secrets.

Optional third-party runtimes, including PPT Master, are not bundled or trusted by
default. Consulting Deck must not download, install, update, bridge, or execute one
until the exact version has passed the user's Skill security gate and the user has
approved its runtime and data boundary. Approval of Consulting Deck does not extend
to an external adapter.

Users should review the repository, pin a version or commit, and run Skills with
the minimum filesystem and network access required for the current task.
