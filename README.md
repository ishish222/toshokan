# Toshokan (図書館)

The goal of the Toshokan project is to aid English-speaking students in learning Japanese language. In my experience on the path to learn Japanese I realised that there are many obstacles that I haven't come across learning e.g., English or Portuguese. For example:

- Formality levels - Japanese language has Confucianist sense of hierarchy built-in. The conjugation changes depending on age or position in hierarchy (in other languages I know it's just phrases that change or 2nd vs. 3rd person)
- Exposure to language - when looking for ways to gain exposure to language one of first obvious options to explore are Japanese movies, books, manga & anime. Unfortunately, in many of them the language used is not an equivalent of everyday Japanese in real life. Many of these are heavily stylised and rarely match everyday speech
- Kanji logographic register - it's very demanding, you need a way to gradually expose yourself to ever growing number of kanji characters but, especially in the beginning, consulting a kanji dictionary every other word quickly becomes exhausting

In Toshokan I attempted to harness capabilities of contemporary LLMs to remove these barriers. I'm doing so by:

- Controlling the list of known kanji and kanji that you want to schedule to memorise
- Selecting formality level for practicing different language registers. Using LLMs capability to properly select language register for formal / semi-formal / informal situations
- Breaking down the learning process into individual lesson units with limited scope that you can exercise ad infinitum or until you are satisfied
- Including a fast chat for words and auxiliary chat for general questions in context of Japanese
- Listing and annotating all unknown kanji (kanji outside of the known kanji register) during practice conversation

## Installing & running

Clone the repo:

```sh
$ git clone https://github.com/ishish222/toshokan
$ cd toshokan
```

Set the API keys of your favourite model broker in env

```sh
$ export OPENROUTER_API_KEY=...
```

Install dependencies and run

```sh
$ poetry install
$ poetry run python -m toshokan.frontend.app
```

Go to 127.0.0.1:8080

[dockerfile pending]