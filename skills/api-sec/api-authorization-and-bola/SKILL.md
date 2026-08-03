---
name: api-authorization-and-bola
description: >-
  API authorization and BOLA testing playbook. Use when APIs expose object identifiers, nested resources, hidden writable fields, or weak function-level authorization.
---

# SKILL: API Authorization and BOLA — Object Access, Function Access, and Mass Assignment

> **AI LOAD INSTRUCTION**: Use this skill when an API exposes object IDs, nested resources, or role-sensitive functions and you need a focused authorization test path: BOLA, BFLA, method abuse, and hidden field control.

## 1. CORE TEST LOOP

1. Create Account A and Account B.
2. As Account A, capture create, read, update, and delete flows.
3. Replay with Account B's token.
4. Test sibling endpoints, nested endpoints, and alternate HTTP verbs.

## 2. TEST SURFACES

| Surface | Example |
|---|---|
| object read | `/api/v1/orders/123` |
| nested object | `/api/v1/users/1/invoices/9` |
| admin or internal function | `/api/v1/admin/users` |
| update path | `PUT`, `PATCH`, `DELETE` variants |
| hidden JSON fields | `role`, `org`, `verified`, `tier` |

## 3. QUICK PAYLOADS

```json
{"role":"admin"}
{"isAdmin":true}
{"org":"target-company"}
{"verified":true}
```

## 4. ID MUTATION STRATEGIES

### Numeric ID
```
id=100 → id=101  (+1)
id=100 → id=99   (-1)
id=100 → id=0    (zero)
```

### UUID / GUID
```
Original: 550e8400-e29b-41d4-a716-446655440000
Modified: 550e8400-e29b-41d4-a716-44665544ffff  (末尾4位)
Try:      550e8400-e29b-41d4-a716-              (截断)
```

### Null Value
```
GET /api/users?user_id=null
POST {"user_id":null}
```

### RESTful Path Tricks
```
PUT /api/users/current/profile/email
 → PUT /api/users/current/../1/profile/email
 → PUT /api/users/me/../1/profile/email
 → PUT /api/users/1/profile/email
```

### Hidden Parameter Injection
Insert ID params into endpoints that don't normally expect them:
```
GET /api/users/profile              (normal)
GET /api/users/profile?user_id=1    (injected)
GET /api/users/profile?user_id=2    (try other user)
```

### Object Nesting (JSON Type Confusion)
```json
// Original:
{"user_id":"1"}

// Try:
{"user_id":1}                     ← string → int
{"user_id":{"user_id":"2"}}       ← object nesting
{"user_id":["1","2"]}             ← array wrap
```

## 5. WHAT TESTERS MISS

- object IDs in headers, cookies, GraphQL args, and nested objects
- alternate methods sharing the same route but weaker authz
- parent check present, child resource check missing
- admin docs revealing extra writable fields

## 6. NEXT ROUTING

- For JWT or token-layer abuse: [api auth and jwt abuse](../api-auth-and-jwt-abuse/SKILL.md)
- For GraphQL and hidden parameter discovery: [graphql and hidden parameters](../graphql-and-hidden-parameters/SKILL.md)
- For broader IDOR patterns outside APIs: [idor broken object authorization](../../auth-sec/idor-broken-object-authorization/SKILL.md)