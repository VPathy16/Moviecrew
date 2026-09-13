## Problem

The portal does not establish a customer identity before serving private work.

## Scope

Add Google/email sign-in, sign-out, session expiry handling and backend token verification. Use the stable identity subject, not display name or email, as the user key. Keep local development explicit.

## Acceptance criteria

- [ ] Reject missing, expired and wrong-project tokens on protected API routes.
- [ ] User can sign in on another browser and load the same owned workspace.
- [ ] Sign-out and revoked-session handling are tested; credentials are never logged.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/37

## Tracking

Priority: **P0** · Area: **SaaS foundation**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
