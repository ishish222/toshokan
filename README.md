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

### Prerequisites

As prerequisites, you'll need to set up some env variables. 

Basic configuration includes setting the host and port variables:

```sh
export APP_HOST=0.0.0.0
export APP_PORT=8080
```

Or you can simply use the provided sample file:

```sh
cp env.sample.cfg .env
```

#### Model keys

Depending on the model broker that you use, you'll need to set API keys, like:
```sh
OPENROUTER_API_KEY=<key>  # If you use openrouter/* models
OPENAI_API_KEY=<key>  # If you use openai/* models
```
etc.

#### Local certificate path 

Optionally, you can use certificates. If you do, put your `server.key` and `server.crt` into a dir and pass the `LOCAL_CERT_PATH` env

#### AWS Cognito integration

Optionally, you can integrate the app with AWS cognito for multitenancy. You need to set the following env vars:

```sh
COGNITO_INTEGRATE=true
COGNITO_DOMAIN=<domain>
COGNITO_DOMAIN_CLIENT_ID=<client id>
COGNITO_DOMAIN_REDIRECT_URI_LOGIN=<redirect client login>
COGNITO_DOMAIN_REDIRECT_URI_LOGOUT=<redirect client logout>
COGNITO_DOMAIN_USER_POOL_ID=<user pool id>
COGNITO_DOMAIN_REGION=<cognito region>
```

#### Optional LangSmith tracing

You can enable Langsmith tracing for registering runs. To do se set LS-related env variables:

```sh
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=<your LS API key>
```

### Building and running directly from code

Clone the repo:

```sh
$ git clone https://github.com/ishish222/toshokan
$ cd toshokan
```

Set the env variables

```sh
$ export OPENROUTER_API_KEY=...
```

Install dependencies and run

```sh
$ poetry install
$ poetry run python -m toshokan.frontend.app
```

Navigate to: http://<APP_HOST>:<APP_PORT>

### Building and running from the dockerfile

Build the image with:

```sh
$ docker build -f dockerfiles/Dockerfile.dashboard.single -t toshokan-dashboard .
```

Run:

```sh
$ docker run -p 80:8080 --env-file .env toshokan-dashboard 
```

## Usage

### Configuration save / load

[...]


### Exercises

[...]

### Conversations

[...]