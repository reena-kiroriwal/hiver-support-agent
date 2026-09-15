# SpotifyCares Intent Codebook

## Purpose

This codebook defines the intent taxonomy used to manually label the
golden evaluation set.

Each customer message receives:
1. One intent
2. One should_escalate label

---

## 1. playback_issue

### Definition
The customer reports that music, podcasts, or other audio content is
not playing correctly.

### Examples
- Songs won't play
- Music keeps stopping
- Playback is buffering
- A song skips unexpectedly
- Audio stops after a few seconds

### Edge cases
- If the problem is specifically that the app crashes, use
  `app_technical_issue`.
- If the customer cannot access their account, use `account_login`.
- If the customer asks for a new playback feature, use
  `feature_request`.

---

## 2. app_technical_issue

### Definition
A technical problem with the Spotify application or website that is
not primarily about playback.

### Examples
- App crashes
- App freezes
- App won't open
- Spotify website is broken
- App causes unexpected technical problems

### Edge cases
- Music simply not playing → `playback_issue`
- Login problem → `account_login`

---

## 3. account_login

### Definition
Problems accessing, logging into, or recovering a Spotify account.

### Examples
- Cannot log in
- Forgot password
- Facebook login doesn't work
- Cannot access my account
- Login credentials aren't working

### Edge cases
- A payment problem after successful login → `payment_billing`
- A Premium subscription problem → `premium_subscription`

---

## 4. premium_subscription

### Definition
Questions or problems specifically related to Spotify Premium
membership or subscription status.

### Examples
- Premium is not showing
- How do I get Premium?
- Premium subscription isn't working
- I paid for Premium but have a Free account
- How can I cancel Premium?

### Edge cases
- Specific charge/payment problem → `payment_billing`
- Country eligibility for Premium → `availability_region`

---

## 5. payment_billing

### Definition
Problems involving charges, payments, billing, refunds, or payment
methods.

### Examples
- Charged twice
- Payment failed
- Don't recognize a charge
- Need a refund
- Card was charged but Premium wasn't activated

### Edge cases
- General Premium status without a payment issue →
  `premium_subscription`.
- Potential fraud or unauthorized payment should normally have
  `should_escalate = true`.

---

## 6. music_availability

### Definition
Questions or complaints about specific songs, albums, artists, or
other music content being unavailable or missing.

### Examples
- Why is this album missing?
- A song disappeared
- An artist's music isn't available
- When will this album be added?

### Edge cases
- Country-specific availability → `availability_region`
- Song is available but won't play → `playback_issue`

---

## 7. playlist_library

### Definition
Problems involving playlists, saved songs, library content, or
organization of music.

### Examples
- Playlist disappeared
- Can't save a song
- My library is missing
- Playlist won't update
- Songs disappeared from My Music

### Edge cases
- Specific song unavailable everywhere → `music_availability`
- Song won't play → `playback_issue`

---

## 8. feature_request

### Definition
The customer asks Spotify to add, change, or improve a product
feature.

### Examples
- Please add lyrics
- Spotify should add this feature
- Can you add a sleep timer?
- I want a new playlist feature

### Edge cases
- Reporting that an existing feature is broken →
  use the relevant problem intent instead.

---

## 9. availability_region

### Definition
Questions or problems concerning Spotify availability,
subscriptions, content, or features in a particular country or region.

### Examples
- Is Spotify available in India?
- Why isn't this feature available in my country?
- Can I use Premium in another country?
- Why is this song unavailable in my region?

### Edge cases
- If there is no geographic component, use the normal relevant intent.

---

## 10. general_question

### Definition
A general Spotify question that does not clearly belong to another
specific intent.

### Examples
- How does Spotify work?
- What is Spotify Connect?
- How can I use this service?
- General questions about Spotify policies or features

### Edge cases
- If a specific problem is described, use the more specific intent.

---

## 11. other

### Definition
Messages that cannot reasonably be assigned to one of the defined
intents.

### Examples
- Unclear or incomplete messages
- Messages unrelated to Spotify support
- Spam
- Messages where the customer's actual request cannot be determined

### Important
Do NOT force an unclear message into another intent just to reduce the
`other` percentage.

---

# Escalation Label

## should_escalate = true

Use true when the case should be reviewed by a human rather than being
automatically handled.

Examples include:

- Potential fraud
- Unauthorized charges
- Account compromise
- Sensitive billing problems
- Cases where the classifier is uncertain
- Cases where historical evidence is insufficient
- Requests requiring account-specific investigation

## should_escalate = false

Use false when the issue is sufficiently clear and can reasonably be
handled automatically using available historical evidence and
resolution guidance.

---

# General Labelling Rules

1. Choose the customer's PRIMARY intent.
2. Do not infer information that the customer did not provide.
3. Prefer specific intents over `general_question`.
4. Use `other` when the message genuinely does not fit.
5. Label escalation independently from intent.
6. A message can have a valid intent and still require escalation.
7. Potential fraud, unauthorized charges, or account compromise should
   be escalated.