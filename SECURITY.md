# Security

klarpost evaluates **local fixture files**. It does not connect to a mailbox
and must not grow credential handling without a dedicated design review.

## Please report

- Ways a policy pack or the engine could mark protected mail
  (orders, invoices, tickets, banking, security, identity, medical,
  government) as `delete_candidate`
- Path traversal or unexpected file reads outside the paths you passed
- Anything that would log or commit personal mailbox data

## Please do not report

- "It does not delete enough mail" — that is product taste, not a vulnerability
- Missing IMAP — intentional

## How to report

Use GitHub's **private vulnerability report** on this repository
(Security → Report a vulnerability) if it is available. Otherwise open an
issue titled `security: …` **without** pasting real email contents.

We will treat engine bypasses as P0 and add a fixture + test before anything
else.
