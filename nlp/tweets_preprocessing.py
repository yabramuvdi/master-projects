import re
import preprocessor as tp
import contractions
import emoji


def extract_elements(tweets):
    """ Function that uses the tweet-preprocessor and emojis libraries
        to identify and save:
            - #Hashtags
            - @Mentions
            - Emojis

    Args:
        tweets: list containing all tweets

    Returns:
        hashtags: list of hashtags
        mentions: list of mentions
        emojis: list of emojis

    Sources:
        https://pypi.org/project/tweet-preprocessor/
        https://github.com/carpedm20/emoji/

    """

    # set the global options for the library. These settings define which
    # elements of the tweet to pay attention to
    tp.set_options(tp.OPT.URL, tp.OPT.EMOJI, tp.OPT.MENTION,
                   tp.OPT.NUMBER, tp.OPT.HASHTAG)

    # create empty lists to store the resuts
    hashtags = []
    mentions = []
    emojis = []

    # iterate over all tweets in the list
    for tweet in tweets:

        # parse tweet to extract the relevant elements defined in the options
        parsed_tweet = tp.parse(tweet)

        # 1. save the hashtags
        h_tweet = []
        if parsed_tweet.hashtags is not None:
            for hashtag in parsed_tweet.hashtags:
                h_tweet.append(hashtag.match)

        # save to the global list as a space separated string
        hashtags.append(' '.join(h_tweet))

        # 2. save the emojis (using the library)
        e_tweet = []
        if len(emoji.emoji_lis(tweet)) > 0:
            for e in emoji.emoji_lis(tweet):
                e_tweet.append(e['emoji'])

        # save to the global list as a space separated string
        emojis.append(' '.join(e_tweet))

        # 3. save the mentions
        m_tweet = []
        if parsed_tweet.mentions is not None:
            for mention in parsed_tweet.mentions:
                m_tweet.append(mention.match)

        # save to the global list as a space separated string
        mentions.append(' '.join(m_tweet))

    return(hashtags, mentions, emojis)


def tweet_preprocessor(tweets):
    """ Function that uses the tweet-preprocessor and emojis libraries
        to remove:
            - #Hashtags
            - @Mentions
            - Emojis
            - URLs
            - Standalone numbers

        and transform all letters into lower case

    Args:
        tweets: list containing all tweets

    Returns:
        clean_tweets: lower-cased preprocessed list of tweets

    Sources:
        https://pypi.org/project/tweet-preprocessor/
        https://github.com/carpedm20/emoji/

    """

    # set the global options for the library. These settings define which
    # elements of the tweet to pay attention to
    tp.set_options(tp.OPT.URL, tp.OPT.MENTION, tp.OPT.NUMBER, tp.OPT.HASHTAG)

    # create a list to store the results
    clean_tweets = []

    # iterate over all tweets in the list
    for tweet in tweets:

        # remove emojis
        for e in emoji.emoji_lis(tweet):
            tweet = tweet.replace(e['emoji'], '')

        # append the cleaned lowered-cassed tweet
        clean_tweets.append(tp.clean(tweet).lower())

    return(clean_tweets)


def remove_symbols(tweets, symbols):
    """ Function that uses regular expressions to delete all symbols
        given by the user from the tweets

    Args:
        tweets: list containing all tweets
        symbols: list containing all the symbols to replace

    Returns:
        clean_tweets: list of tweets without symbols

    """

    # generate regular expression
    rx = '[' + re.escape(''.join(symbols)) + ']'

    # create empty list to store results
    clean_tweets = []
    for tweet in tweets:
        clean_tweets.append(re.sub(rx, '', tweet))

    return(clean_tweets)


def expand_contractions(tweets):
    """ Function to transform some of the most common English and
        French contractions into their expanded form

    Args:
        tweets: list containing all tweets

    Returns:
        clean_tweets: list of tweets with the contractions expanded

    References:
        https://github.com/kootenpv/contractions

    """

    # since the library is designed for English contractions,
    # we will only have to add French contractions

    contractions.add("c'est", "cest")
    contractions.add("c’est", "cest")
    contractions.add("qu'il", "que il")
    contractions.add("qu’il", "que il")
    contractions.add("s'il", "si il")
    contractions.add("s’il", "si il")

    # create a list for storing the results
    clean_tweets = []
    for tweet in tweets:
        clean_tweets.append(contractions.fix(tweet).lower())

    # the rest of the French contractions will need to be solved
    # through regular expressions

    # l’intelligence --> le intelligence
    clean_tweets = [re.sub(r"\bl['|’](\S)", r"le \1", tweet)
                    for tweet in clean_tweets]

    # d’bananes --> des bananes
    clean_tweets = [re.sub(r"\bd['|’](\S)", r"de \1", tweet)
                    for tweet in clean_tweets]

    # j’avais --> je avais
    clean_tweets = [re.sub(r"\bj['|’](\S)", r"je \1", tweet)
                    for tweet in clean_tweets]

    # n’aurait --> ne aurait
    clean_tweets = [re.sub(r"\bn['|’](\S)", r"ne \1", tweet)
                    for tweet in clean_tweets]

    return(clean_tweets)


def remove_stopwords(tweets_words, stop_words):
    """ Function to remove a list of words from all the corpus

    Args:
        tweets_words: list containing all tweets represented as lists of words
        stop_words: list of words to be removed

    Returns:
        clean_words: list of tweets without stop_words

    """

    # create a list of empty lists to store the results
    clean_words = [[] for tweet in tweets_words]
    for i, tweet in enumerate(tweets_words):
        for word in tweet:
            if word not in stop_words:
                clean_words[i].append(word)

    return(clean_words)


def replace_multiple(tweets_words):
    """ Function to replace 3 or more consecutive vocals (caaaaaat)
        with only one appearence (cat)

    Args:
        tweets_words: list of tweets represented as lists of words

    Returns:
        clean_tweets

    """

    def replace(string, char):
        pattern = char + '{3,}'
        string = re.sub(pattern, char, string)
        return string

    def replace_vocals(string):
        vocals = ["a", "e", "i", "o", "u"]
        clean = string
        for char in vocals:
            clean = replace(clean, char)
        return clean

    # create an empty list to store the results
    clean_tweets = []
    for tweet in tweets_words:
        clean_words = [replace_vocals(word) for word in tweet]
        clean_tweets.append(clean_words)

    return(clean_tweets)


def preprocessor(tweets, symbols, stopwords):
    """ Function that applies sequentially the following cleaning
        procedures to the list of tweets provided as an input:

        1. identifies and stores
            a. #Hashtagas
            b. @Mentions
            c. Emojis
        2. removes from the text:
            a. #Hashtags
            b. @Mentions
            c. Emojis
            d. URL's
            e. Standalone numbers
        3. converts all letters into lowercase
        4. removes user-specified symbols
        5. expands some basic contractions (French only)
        6. represents every tweet as a list of words
        7. removes user-specified stopwords
        8. replaces muuuuultiple appearances of a letter in a word

    Args:
        tweets: list containing all tweets
        symbols: list containing all symbols to be removed
        stopwords: list containing all stopwords to be removed

    Returns:
        tweets_words: list of tweets represented as lists of words
        hashtags: list of hashtags
        mentions: list of mentions
        emojis: list of emojis

    Sources:
        https://pypi.org/project/tweet-preprocessor/
        https://github.com/kootenpv/contractions
        https://github.com/carpedm20/emoji/

    """

    # 1.
    hashtags, mentions, emojis = extract_elements(tweets)

    # 2 and 3
    clean_tweets = tweet_preprocessor(tweets)

    # 4.
    clean_tweets = remove_symbols(clean_tweets, symbols)

    # 5.
    clean_tweets = expand_contractions(clean_tweets)

    # 6.
    tweets_words = [tweet.split() for tweet in clean_tweets]

    # 7.
    clean_words = remove_stopwords(tweets_words, stopwords)

    # 8.
    clean_words = replace_multiple(clean_words)

    return(clean_words, hashtags, mentions, emojis)
