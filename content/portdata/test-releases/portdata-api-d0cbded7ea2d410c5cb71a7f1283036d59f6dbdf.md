---
title: portdata
date: 2026-11-03T14:18:38Z
environment: kt
---
- ID-7090: Return 409 when creating a client that already exists (#141)
- Return 409 when creating a client that already exists
- Throw a 409 http status code, when client exists
- Remove unused GlobalExceptionHandler
- Removed non existing check from unit-test add obof client

