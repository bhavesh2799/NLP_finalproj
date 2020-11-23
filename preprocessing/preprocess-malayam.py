import pandas as pd
import numpy as np
import csv
import re
from conllu import parse
from pathlib import Path
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from alive_progress import alive_bar
import nltk
import emoji_data_python
import emoji
import operator
import functools


# files to process
files = ['malayalam_train', 'malayalam_dev', 'malayalam_test']

# Stopwords for English and Hindi
hin_stop_words = pd.read_csv('hin_stop_words.txt', sep="\t", header=None)
hin_stop_words = list(hin_stop_words[0])[:1000]
stop_words = set(stopwords.words('english'))

# variables
snowBallStemmer = SnowballStemmer("english")

symbol_dict = { '❤': 'love', '♥': 'love', '❤❤': 'love', '♥♥': 'love', 'ù§': 'love', '‚ô•': 'love', '☺': 'smile'}

punctuation1 = ['…', '.', '!', '#', '__', '?', '!', '&', '@', '$', '%', '^', '*', '+', '=', ':', ';', ',', '/',
                '[', ']', '{', '}', '|', '_', '`', '~', '✖', '╮', '╭', '🔝', 'º', 'δ', '(', ')']

punctuation2 = ['RT', '_', '.', '…', '...', '!', '#', '__', '___', '____', '_____', '..', '....', '.....', '.…', '.....',
               '@___', '@_', '.........', '.......', '((', '(((', '—…', '........', "'", ',', '|', '?', '!', '......',
               '!!', '??', '…', ' ................', '.....................…', '’', '!!!', '!!!!', '!!!!!', '!!!!!!',
               '!!!!!!!', '!!!!!!!!', '!!!!!!!!!', '!!!!!!!!!!', '!!!!!!!!!!!', '!!!!!!!!!!!!', '??', '—', '???'
               '*', '**', '***', '****', '*****', '******', '*******', '********', '*********', '**********', '&', '-',
               '>', '<', '”', '“', '"', '.......................', '►', 'ക', ' ൊ', 'ണ', '്','ത', 'ന', ' ു', 'ഖ', 'ഗ',
                'ഘ', 'ങ', 'ച', 'ഛ', 'ജ', 'ഝ', 'ഞ', 'ഠ', 'ഡ', 'ഢ', 'ണ', 'ഥ', 'ദ', 'ധ', 'പ', 'ഫ', 'ബ', 'ഭ', 'മ',
                'യ', 'ര', 'റ', 'ല', 'ള', 'ഴ', 'വ', 'ശ', 'ഷ', 'സ', 'ഹ', 'ി', 'ും', ' ൊ', 'ണ', '്', 'ട', ' ോ', 'ു',
                'ാ', 'അ', ' ൂ', 'േ', 'െ', 'ൊ', 'ഈ', ' ൈ', 'െ', 'ൊ']

symbol = ['ðŸ™ðŸŒ¹', 'ðŸ™ðŸŒ¹', 'Â´', 'ðŸ˜ðŸ˜ðŸ˜', '?ðŸ˜‚ðŸ˜‚ðŸ˜‚', '##', '#à¤šà¤®à¥à¤ªà¤¾à¤°à¤£', 'ðŸŽ‚ðŸ™â¤ï¸',
     'ðŸ', 'ðŸ’ƒ', 'ðŸ¤®', 'â¤+ðŸ”¨=ðŸ’”', 'ÙˆØ±Ø¯ÛŒ', '#êµ¬ë…¸', 'ðŸ˜­ðŸ’–ðŸ’–', 'â¤â¤â¤', 'ðŸŽ‚', 'ðŸ–ðŸ½',
     'â¤', 'ðŸ˜ðŸ‘ðŸ’', '..ðŸ™‡â€â™€ï¸', 'ðŸ˜€ðŸ˜€ðŸ˜€ðŸ˜€ðŸ˜…ðŸ˜€ðŸ˜…ðŸ˜€ðŸ˜…', 'ðŸ˜ðŸ˜', 'ðŸ‘ŽðŸ–ðŸ‡µðŸ‡°',
     'ðŸ§¡', 'ðŸ˜©â¤ï¸', 'ðŸŽŸ', 'ðŸ¤—ðŸ¤—ðŸ¤—ðŸ’ðŸ’', 'ðŸ™ðŸ™‚', 'ðŸ”¥ðŸ”¥', 'ðŸ†', 'ðŸŒ´', 'ðŸ’¯', 'ðŸ˜ª',
     'à¤¬à¤¹à¥à¤¤', 'ðŸ‘¶', 'ðŸ‘‡ðŸ‘‡', 'ðŸŽ§', 'ã…‹ã…‹ã…‹ã…‹', 'âœ¨', 'ðŸ¤­ðŸ¤­', 'ðŸ˜¡ðŸ¤¬ðŸ¤¬', 'Ø¯Ú¾Ø´ØªÚ¯Ø±Ø¯ÛŒ',
     'ðŸ‘‰', 'ðŸ˜€ðŸ˜€', 'â€¢', '.â€¦', 'â™¥ï¸â™¥ï¸', 'ðŸŒº', 'ðŸŒ¸ðŸ–¤ðŸ’¥', 'â†‘', 'ðŸ˜ðŸ’›', 'ðŸ’œâ¤', '~ðŸ™',
     '..ðŸ˜‚ðŸ˜‚', 'ðŸ’™', 'ðŸ’«ðŸ’«', 'ðŸ™â¤ï¸â€¦', 'ðŸ’ª', 'ë°¤ë°”ëžŒ', '~', 'Ã', 'ðŸ’•ðŸ’«', 'ðŸ‘‡',
     'ðŸ˜‚ðŸ˜‚ðŸ˜¤', 'à¤¬à¤§à¤¾à¤ˆ', 'ðŸ˜‚', '...â˜ï¸â˜ï¸', 'ðŸ¤ðŸ˜Ÿ', 'ðŸ¤”', 'ðŸ˜˜ðŸ˜˜ðŸ˜˜ðŸ˜˜ðŸ˜˜ðŸ˜˜ðŸ˜˜ðŸ˜˜',
     'ðŸ¥°', 'ðŸ¥°ðŸ’›ðŸ’›ðŸ’›ðŸ’›ðŸ’›', '.@', 'ðŸ™ðŸ»ðŸ™ðŸ»ðŸ™ðŸ»ðŸ™ðŸ»ðŸ™ðŸ»', 'Â', 'ðŸ˜…ðŸ˜…ðŸ¤£ðŸ¤£',
     'ðŸ˜Œ', 'à¤­à¤µà¤¿à¤·à¥â€¦', 'ðŸ™†ðŸ˜«ðŸ˜‚ðŸ˜’', 'ðŸ’€', ';;;;;;;', 'ðŸ˜œðŸ˜œ', 'à¨¸à¨¾à¨²à¨¾à¨¹à©€à¨',
     'ðŸ˜­â¤ï¸', 'ðŸ¥ºâ€¦', 'ðŸ˜ŠðŸ‘', 'ðŸ˜­ðŸ˜‚ðŸ˜‚ðŸ˜­ðŸ˜‚ðŸ˜‚ðŸ˜‚ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­',
     'ðŸ˜‚ðŸ˜­', '..!ðŸ˜‚', '!ðŸ˜Œ', 'ðŸ¤¦', '...ðŸ˜¤', 'ì›Œëˆ„', 'ðŸ˜’ðŸ˜’ðŸ˜’', 'ðŸ™', 'â¤ï¸.', 'â™¥ï¸',
     '#Ù„ÛŒÙ„Ûƒ_Ø§Ù„Ù‚Ø¯Ø±', 'ðŸ˜', 'ðŸ˜‰ðŸ˜ƒ', ').â€¦', '.ðŸ¤—ðŸ¤—', '...â€¦', 'ðŸ˜„ðŸ˜„ðŸŽ¤', 'ðŸ˜Œ.', '??ðŸ˜‚',
     'ðŸ’žðŸŽ‚', 'ðŸ™ŒðŸ’•ðŸ’•', 'ðŸ˜­ðŸ˜‚', 'ðŸ¥´', 'à¤®à¥‡à¤¹à¤¨à¤¤', 'ðŸ’žðŸ’“ðŸ’—ðŸ’–ðŸ’˜', 'ðŸ’ªðŸ˜Ž', 'à¤°à¤¹à¤¾',
     'ðŸ˜ž', 'ðŸ˜‚ðŸ‡¨ðŸ‡¦', '!ðŸ˜', 'ðŸ’–ðŸ’•', 'â¤ï¸â¤ï¸â¤ï¸', 'ðŸ˜»ðŸ˜»ðŸ‘ðŸ‘', 'â€', '!ðŸ‘', 'ðŸŒ¹',
     'ðŸ¤£ðŸ¤£ðŸ¤£ðŸ¤£', 'â–¶ï¸', 'â˜ðŸ»', 'ðŸ˜‰ðŸ˜œ', 'ðŸŒ³', 'ðŸ˜…', 'ðŸ¤£', 'â€™.', 'ðŸŒµ', 'ðŸ‘ŽðŸ‘Ž',
     'ðŸ’“ðŸ’“ðŸ˜ðŸ‘­', 'ðŸ˜œðŸ˜œðŸ˜ƒðŸ˜ƒ', '...ðŸ˜¹', 'ðŸ˜¡', 'ðŸŒ¸', 'ðŸ˜', 'Ã©', '..ðŸ˜˜ðŸ¤˜ðŸ‘', 'â›½ï¸',
     'ðŸ’ðŸ’ðŸ’ðŸ™ðŸ™', 'ðŸ˜‚ðŸ˜â¤ðŸ™', 'ðŸ™„', '#à¤¶à¥‡à¤°', 'ðŸ˜’ðŸ˜’ðŸ˜’ðŸ˜’', 'ðŸ˜…ðŸ˜…ðŸ˜…ðŸ˜…',
     '#çŽ‹å›è±ª', 'ðŸ™ŠðŸ˜‚ðŸ˜†ðŸ˜†', 'ðŸ˜ðŸ˜ðŸ˜ðŸ˜ðŸ”¥', 'Ø§Ø³Ú©Û’', '.ðŸ˜¸', ')â€¦', 'à¤²à¥‡à¤ŸðŸ¤‘',
     '..ðŸ˜‹ðŸ¤“ðŸ˜Ž', 'âŸ¶', 'ðŸ•', '8â€¦', 'ðŸ‡®ðŸ‡³', 'ðŸ˜†ðŸ˜†', 'ðŸ¥°ðŸ¥°ðŸ¥°', 'ðŸ˜‚ðŸ’œ', 'ðŸ’ªðŸ™Œâ™¥ï¸',
     'ðŸ˜­ðŸ’—ðŸ’—', 'ðŸ™ðŸ¾', 'ðŸ¥ºðŸ¥º', 'ì¡´ë‚˜ì›ƒê²¨', 'ðŸ™ðŸ¼.', '?ðŸ˜¬', 'à¨¸à©‹', 'ðŸ’ƒðŸ¾ðŸ’ƒðŸ¾',
     'ðŸ˜ŽðŸ‡µðŸ‡°ðŸ˜Ž', 'ðŸ¥°ðŸ¥°â¤â¤ðŸŒ¹ðŸŒ¹', 'â€¦', 'ðŸ˜Š', 'â—â—', 'ðŸ˜ðŸ˜', '!!ðŸ’œ', 'ðŸ‡µðŸ‡°â¤ðŸ‡®ðŸ‡³',
     'à¤°à¤‚à¤—', 'â­â­â­â­â­â­â€¦', 'ðŸ–¤â¤ï¸', 'ðŸªðŸ¥§', 'à¤•à¤¾', 'ðŸŽ‰ðŸŽ‰ðŸ˜ŒðŸ˜Œ', 'ðŸ˜­ðŸ˜­ðŸ˜‚',
     'ðŸ˜œ', 'ðŸ‘ŒðŸ˜ðŸ’•ðŸ’“ðŸŽ¤ðŸ‘ðŸ‘ðŸ‘ðŸ‘ðŸŒ¹ðŸŒ¹ðŸŒ¹ðŸŒ¹ðŸŒ¹ðŸŒ¹', 'ðŸ˜­ðŸ˜ðŸ”¥', 'ðŸ¤ªðŸ¤ªðŸ¤ª', 'ðŸ¤”ðŸ¤”',
     'ðŸ‘ðŸ‘', 'ðŸ˜‚ðŸ˜‚ðŸ˜‚ðŸ™„', 'ðŸ˜‰ðŸ‘£ðŸŽˆ', 'ðŸ˜·', 'ðŸ˜˜ðŸ˜˜', 'Ú†', 'à¤¸à¤µà¤¤à¥€à¤¨', 'ðŸ¬', 'ðŸ’¯%',
     'ðŸ˜', 'Ã—Ã—Ã—', 'ðŸ’ðŸ’', '!!!â€¦', 'ðŸ˜´âœ¨', 'â™¥', '#â€¦', '..ðŸ¤­', 'ðŸ˜‚ðŸ˜‚.', 'ðŸ˜€ðŸ‘ðŸ‘ðŸ‘ðŸ‘',
     '.......ðŸ™', 'â€ðŸ˜‚ðŸ˜‚', 'ðŸ¤­ðŸŽ¶â¤', 'ðŸ˜¤ðŸ˜¤ðŸ˜¤', 'â¤ðŸ’•', 'ðŸ˜¶ðŸ™„', 'à¥¥',
     'ðŸ˜ŒðŸ˜ŒðŸ˜ŒðŸ˜ŒðŸ˜ŒðŸ˜Œ', 'ðŸ’â€â™€ï¸ðŸ’â€â™€ï¸', 'ðŸ¶', 'ðŸ˜‚ðŸ˜‚ðŸ˜‚ðŸ˜‚', '******', 'ðŸ˜‡', 'ðŸ’',
     'ðŸ¥º', 'Ù¾ÛŒÚ†Û’', 'ðŸ‘ðŸ½', 'ðŸ¤™', 'à¨¦à©‡', 'ðŸ‘', 'Ã¬', 'ðŸ˜ŽðŸ”¥', 'ðŸ˜…ðŸ˜…ðŸ˜…', 'ðŸ¤ž',
     'à¨†à¨§à¨¾à¨°à©', 'ðŸ˜‹ðŸ˜‚', 'ðŸ˜­ðŸ‘', '!!!!!!!!!!!!!â€¦', 'ðŸ™ðŸ»', '!ðŸ˜ðŸ˜', '!â€¦', 'â¤ðŸ”¥',
     'ðŸ’¦ðŸ’¦', 'ðŸ’‹', '_à¤¸à¤ˆà¤¯à¤¾', 'ðŸ˜˜ðŸ˜˜ðŸ˜˜ðŸ˜˜', 'à¤¬à¤§à¤¾à¤‡à¤¯à¤¾à¤‚', '-â€¦', 'ðŸŒ¸â¤ï¸', 'ðŸ˜³',
     'ðŸ˜œðŸ˜œðŸ˜œðŸ˜œ', 'à¤¦à¥‡à¤–â€¦', 'à¤¯à¥‡', 'ðŸ•‹â˜ªï¸', 'ðŸ˜Œ..', '2019ðŸ”¥ðŸ”¥ðŸ”¥', 'ðŸ˜”', 'ðŸ˜ðŸ™Œ',
     'ðŸ‡µðŸ‡°', 'ðŸ˜‚ðŸ˜‚ðŸ˜‚ðŸ˜‚ðŸ˜‚', '...ðŸ˜…ðŸ˜…ðŸ¤£ðŸ¤£', 'â¤ï¸', '..â€¦', 'ðŸµï¸', 'ðŸ”¥ðŸ˜‚',
     'â¤ï¸ðŸ‡®ðŸ‡³ðŸŒ¹', 'ðŸŽ‰ðŸŽ‰ðŸŽ‰ðŸŽ‰ðŸŽ‰', '....ðŸ¤¨', '..#', 'ðŸ˜˜ðŸ˜˜ðŸ˜˜', 'ðŸ¤©âœŠâœŠ', 'â€˜', 'ðŸ™ðŸ™',
     'ðŸ‘Ž', 'ðŸ˜ðŸ˜‚', 'ðŸ’œ..', 'ðŸŽ¶', 'ðŸ˜ðŸ˜ðŸ˜', 'ðŸ¤£ðŸ˜‚', 'ðŸ˜ðŸ˜‚ðŸ¤£', 'ðŸ‘†', 'ðŸŒ²', 'ðŸ˜©ðŸ˜©',
     'ðŸ¤—ðŸ¤—ðŸ˜…ðŸ˜…ðŸ™„', 'ðŸ™ðŸ™ðŸ™', 'ðŸ˜Ž', 'ðŸ˜‡ðŸ˜‡', 'à¤®à¤¾â€¦', 'ðŸ˜ðŸ˜™', 'ðŸ‘ðŸ‘', '?ðŸ¤—', 'ðŸ˜‘',
     'Â â€¦', 'ðŸ˜†ðŸ˜‚ðŸ˜‚ðŸ˜‚', 'ØªÙˆØ§Ø¸Ø¹Ø­', 'â¤ï¸ðŸ˜', 'ðŸ˜‘ðŸ˜‚', 'ðŸ‘Š', 'â€“', 'ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­',
     'ðŸ‘ðŸ‘ðŸ‘', 'Ú†ÙˆØ±', 'â€.', '!!!ðŸ˜€ðŸ˜€ðŸ˜‚ðŸ¤£ðŸ˜‚', 'â€”', 'ÛÛ’', 'âœ…', 'âœŒï¸', 'ðŸ–¤',
     '...ðŸ‘ŒðŸ˜‚ðŸ˜‹', 'ðŸ’¯ðŸ’¯', 'ðŸ˜˜', 'ðŸ˜‰', 'â¤ï¸ðŸ‡µðŸ‡°', 'â¤ðŸ’œ', 'ðŸ˜ƒðŸ˜ƒ', 'ðŸ™ðŸ‘ðŸ˜',
     'ðŸ¤£ðŸ¤£ðŸ¤£ðŸ¤£ðŸ˜‚ðŸ˜‚ðŸ˜‚ðŸ˜‚', '?ðŸ˜›ðŸ˜œðŸ˜›ðŸ˜œðŸ˜›ðŸ˜œðŸ˜›ðŸ˜œðŸ˜›', 'ðŸ˜­', 'â£ï¸', '?â”',
     'à¤µà¥à¤¹à¥€à¤•à¤²â€¦', 'ðŸ’ªðŸ‘Š', 'ðŸ˜›', 'ðŸ‡µðŸ‡°ðŸ½ðŸ·', 'ðŸ˜˜ðŸ˜˜ðŸ˜˜.', '....ðŸ˜ ðŸ˜', 'ðŸ˜£', '...ðŸ¤ž',
     'ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜­ðŸ˜‚ðŸ˜‚ðŸ˜‚', 'à¤®à¥‡à¤°à¥‡', 'â˜ºï¸â˜ºï¸', 'ðŸ˜', 'ðŸ™ðŸ¾ðŸ‡¿ðŸ‡¦', '@â€¦',
     'â¤ï¸â˜€ï¸ðŸ’š', 'ðŸ‘»', '.ðŸ’•', 'ðŸŒ¼', '***', '...ðŸ˜¡ðŸ˜¡ðŸ˜¡ðŸ˜¡ðŸ˜¡ðŸ˜¡', 'ðŸ”', 'ðŸ˜€', '~^^', '@__',
     'à¤¯à¤¾à¤°', 'ðŸ™ƒðŸ¤£', 'â¤ï¸ðŸ’—', 'ðŸŽµ', 'ðŸ’¥ðŸ’¥', 'ðŸ˜‚ðŸ˜ðŸ', 'Ø¬Ùˆ', 'Ã¼', 'â¤ï¸â¤ï¸',
     'ðŸ˜â¤ï¸', 'ðŸ˜˜ðŸ˜˜ðŸ˜˜ðŸ˜˜ðŸ˜˜ðŸ˜˜ðŸ˜˜', '...ðŸ˜ ðŸ˜­ðŸ˜¢', '..âœŒ', '+â¤ï¸', 'ðŸ’•',
     'ðŸŽ‚ðŸŽ‚ðŸŽ‚ðŸŽ‚ðŸŽ‚', '.ðŸ™ˆ', 'ðŸŽ‰', 'ðŸ”¥ðŸ”¥ðŸ”¥', 'ðŸ°ðŸŽˆðŸŽðŸŽ‰', 'ðŸ‡¿ðŸ‡¦', '!!ðŸ’ðŸ’',
     'à¤µà¤‚à¤¦à¥‡', 'ðŸ’œðŸ’œðŸ˜­', '?ðŸ˜ž', 'ðŸ˜¬', '@@@', 'ðŸ˜‰...', 'ðŸ˜‚ðŸ˜‚â€¦', 'âœ¨ðŸ’¥ðŸŽŠðŸŽ‰', 'ðŸ‘…ðŸ‘…',
     'ÛÛ’.', 'ðŸ¥³ðŸŽŠðŸŽ‰', 'ðŸ˜“', 'Â @', 'ðŸ˜ƒðŸ’ðŸ’ðŸ’ðŸ’ðŸ’ðŸ’', 'ðŸ‡®ðŸ‡³ðŸ‡®ðŸ‡³', 'ðŸš¨', 'à¤¸à¥€à¤–',
     'Û”Û”', 'ðŸŒŸ', 'ðŸ¥³', 'ðŸ‘ðŸ˜ƒ', 'ðŸ‘ðŸ‡µðŸ‡°ðŸ‡µðŸ‡°ðŸ‡µðŸ‡°ðŸ‡µðŸ‡°ðŸ‡µðŸ‡°', 'ðŸ‘‰ðŸŒ¹ðŸŒ¹', 'à¨¦à¨¾à¨¤à¨¾',
     'ðŸ˜¡ðŸ˜¡', 'ðŸ’•ðŸ’•.', 'â„', '5â€¦', '.......â€¦', 'ðŸ‘ðŸ¼ðŸ˜‰', '370.â€¦', 'ðŸ˜…ðŸ˜…ðŸ˜…ðŸ¤£ðŸ˜ðŸ˜',
     'ðŸ˜ŠðŸ˜Š', 'â˜‘', 'ï¸âƒ£', 'ðŸ¥Š', '..ðŸ˜†', '-@', '.ðŸ˜‚', 'âœŒ', 'ðŸ˜‚ðŸ˜‚ðŸ†ðŸðŸ†ðŸ', 'ðŸ™ŒðŸ˜‚ðŸ˜‚',
     'ðŸ’“', 'à¤œà¤¯', 'ðŸ¤—ðŸ¤—ðŸ¤—ðŸ˜˜ðŸ˜', 'à¤†à¤ªà¤¨à¥‡à¥¤', 'â˜ºï¸â˜ºï¸ðŸ’žðŸ’ž', '.ðŸ˜ŒðŸ˜Š', '-Â ', 'ðŸ‘‡â€¦',
     'ðŸ‘‹', '...ðŸŒºðŸ’•', '...ðŸ˜±ðŸ˜¨', 'ðŸ’¥', 'ðŸ‘ŒðŸ‘ðŸ˜ŠðŸŒ¹ðŸ™', 'â£ï¸â£ï¸', 'à¤¹à¤¿à¤‚à¤¦', 'ðŸ™Œ',
     '.....ðŸ’”ðŸ’”ðŸ’”', 'ðŸ”¥', 'ðŸ‡§ðŸ‡©', 'ðŸ¥ºâ¤ï¸', 'à¤¹à¥‚à¤', '!!â¤ï¸â¤ï¸â¤ï¸', 'ðŸ˜‚.',
     'ðŸ™ðŸ»ðŸ™ðŸ»', 'à¨¸à¨­à¨¸à©ˆ', 'ðŸ˜‚ðŸ˜‚ðŸ˜‚ðŸ˜‚ðŸ˜‚ðŸ˜‚', 'ðŸ˜', 'ðŸ¤—ðŸ¤—', 'ðŸ¤£ðŸ¤£', 'ðŸ¤£ðŸ¤£ðŸ¤£',
     'ðŸ’—', 'â˜¹ï¸â˜¹ï¸', 'ðŸ¥°ðŸ˜', '??ðŸ¤”ðŸ˜‚ðŸ˜‚', 'ðŸ™„ðŸ™„', 'ðŸ˜‚ðŸ˜ˆ', 'ðŸ‘»ðŸ‘»ðŸ‘»', 'à¤¸à¥à¤…à¤°à¤¨à¥€',
     'ðŸ˜ðŸ˜ðŸ˜ðŸ˜', '?â€¦', 'ðŸ¤­', 'ðŸ˜­ðŸ˜­', 'ðŸ˜­ðŸ˜', 'ðŸ˜ðŸ”¥', 'ðŸ˜‚ðŸ˜‚ðŸ˜ðŸ˜ðŸ˜', 'ðŸ˜’', 'ðŸ’ž',
     'ðŸ’–', 'ðŸ˜”.', 'ðŸ˜‚ðŸ˜‚ðŸ˜‚', 'ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ìš°ë¦¬', 'âŒ', 'ðŸ‘Œ', 'à¤¥à¥€',
     '.â¤ðŸ‘¼', 'Â #', 'ðŸ˜‚ðŸ˜‚', 'ðŸ™ŒðŸ¾', 'â¤â¤', 'ðŸ˜„ðŸ˜„', 'ðŸ˜ˆ', 'Â©', '.ðŸ¤§', '.â€', 'ðŸ™ƒ',
     'ðŸ˜ŽðŸ˜ŽðŸ’ª', 'Ã¢Â€Â¢', 'ðŸ’ðŸŒºðŸŒ¹ðŸŒ¸', 'ðŸŒž', 'ðŸ‘¨â€ðŸ‘§ðŸ˜˜', 'ðŸ™ðŸ™ðŸ™ðŸ‘âš˜âš˜ðŸ˜ŠðŸ˜Š', 'ðŸ˜',
     'ðŸ¤—ðŸ˜‡', 'ðŸ”¥ðŸ”¥ðŸ‘Œ', 'â”', 'ðŸ‘ðŸ’¯', 'à¤­à¤¾à¤°à¤¤', 'âœ…âœ…', 'ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹ã…‹',
     'ðŸ‘Œâ™¥ðŸ”¥â€¦', '.ðŸ‘', '.....ðŸ˜‚ðŸ¤£â€¦', 'ðŸ™ŒðŸ»ðŸ™ðŸ»', 'ðŸ˜•', 'â€™', 'ðŸ‘ðŸ»', 'ðŸ˜ðŸ˜˜',
     'âœŒï¸ðŸ’ðŸ˜ŠðŸŒ¹ðŸŒ¹ðŸ‡®ðŸ‡³', 'ðŸ’©ðŸ’©', 'â¤ï¸ðŸ™ðŸ»', 'ðŸ¤˜ðŸ»', 'â™¥â™¥â™¥â™¥â™¥ðŸ’•ðŸ’•',
     'ðŸŽŠðŸŽ‰ðŸŽˆ', '#ì™•êµ°í˜¸', 'ðŸ˜ðŸ˜ðŸ˜ðŸŽ‚ðŸŽðŸŽðŸŽˆðŸŽˆðŸŽ†ðŸŽ†ðŸŽ‰ðŸŽŠðŸ°ðŸ°',
     '.....â¤ðŸ‘ŒðŸ‘ŒðŸ‘ŒðŸ‘ŒðŸ‘ŒðŸ‘Œ', 'â¤ï¸â¤ï¸â¤ï¸â¤ï¸â¤ï¸â¤ï¸', 'ðŸ¦¹â€â™‚ï¸', 'à¤œà¤¾à¤¤à¥€',
     'ðŸ‘', '****', 'ðŸ˜‹', 'ðŸ‡®ðŸ‡³ðŸ‡®ðŸ‡³ðŸ‡®ðŸ‡³ðŸ‡®ðŸ‡³ðŸ‡®ðŸ‡³', 'ðŸ˜”ðŸ˜”', 'ðŸƒ', 'ðŸ˜†', 'ðŸ’”', 'ðŸ˜â€¦',
     '??ðŸ™„', 'ðŸ˜©ðŸ˜‘', 'ðŸ‘ðŸ‘ðŸ˜‰ðŸ˜‰', '1â€¦', 'ðŸ˜„', 'â˜ºâ˜º', 'à¤¹à¥‹..', 'ðŸ˜¬ðŸ˜¬..', 'à¨œà¨¿',
     'ðŸ’“ðŸ’“ðŸ’“ðŸ˜ðŸ˜ðŸ˜', 'ðŸ¤£ðŸ”¥', 'ðŸ˜‰ðŸ˜‰ðŸ˜‰', 'ðŸ˜‘ðŸ˜‘', 'ÛŒÛ']


pd.set_option("display.max_colwidth", 10000)
# Functions
def cleaning_punctuation(sentence):
    cleaned_tokens = []

    tokenlist = re.compile(r'\w+|[^\w\s]+').findall(sentence)

    for token in tokenlist:
        if any(punct in token for punct in punctuation1):
            # print(token)
            continue
        elif any(punct in token for punct in punctuation2):
            continue
        # elif token not in punctuation2:
        else:
            if 'ു' in token:
                print(token)
            if 'ാ' in token:
                print(token)
            cleaned_tokens.append(token)
    return (' '.join(cleaned_tokens))


def cleaning_symbol(sentence):
    cleaned_tokens = []
    # tokenlist = sentence.split(' ')
    previous = next_ = None
    # print(tokenlist)
    import emoji

    em_split_emoji = emoji.get_emoji_regexp().split(sentence)
    em_split_whitespace = [substr.split() for substr in em_split_emoji]
    tokenlist = functools.reduce(operator.concat, em_split_whitespace)

    # print(em_split)

    l = len(tokenlist)
    for index, token in enumerate(tokenlist):
        if index > 0:
            previous = tokenlist[index - 1]
        if index < (l - 1):
            next_ = tokenlist[index + 1]
        if emoji_data_python.get_emoji_regex().findall(token):
            if token == previous:
                continue
            # if token == next_:
            #     print('found dup2:', token, next_)
            #     continue
            else:
                cleaned_tokens.append(token)
        cleaned_tokens.append(token)
    sentence = ' '.join(cleaned_tokens)
    cleaned_tokens = []

    for token in sentence.split(' '):
        # replaces words for any symbols from dictionary
        if token in symbol_dict:
            cleaned_tokens.append(symbol_dict[token])

        # Checks for emojis and replaces with short names
        if emoji_data_python.get_emoji_regex().findall(token):
            unified = emoji_data_python.char_to_unified(token)
            emojis = unified.split('-')
            emojis = list(dict.fromkeys(emojis))
            for emoji in emojis:
                for index, key in enumerate(emoji_data_python.emoji_short_names):
                    if emoji in emoji_data_python.emoji_short_names[key].__dict__.values():
                        description = key.replace('_', '-').split('-')
                        # print(description)
                        for word in description:
                            cleaned_tokens.append(word)
                        continue
        elif token not in symbol:
            cleaned_tokens.append(token)
    return (' '.join(cleaned_tokens))


def english_remove_stop_words(example_sent):
    word_tokens = word_tokenize(example_sent)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    filtered_sentence = []
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    return (' '.join(filtered_sentence))


def hindi_remove_stop_words(example_sent):
    word_tokens = word_tokenize(example_sent)
    filtered_sentence = [w for w in word_tokens if not w in hin_stop_words]
    filtered_sentence = []
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    return (' '.join(filtered_sentence))


def stemming(sentence):
    wordList = nltk.word_tokenize(sentence)
    stem_words = [snowBallStemmer.stem(word) for word in wordList]
    return (' '.join(stem_words))


# Iterate through files, clean and convert to .csv
for file in files:

    filepath = Path(__file__).resolve().parents[1]
    filepath = str(filepath)
    datapath = filepath + '/' + 'data' + '/' + 'malayam-english' + '/' + file
    # outpath = filepath + '/' + 'data' + '/' + 'malayam-english' + '/' + 'processed' + '/' file

    data = pd.read_csv(datapath + '.tsv', sep="\t", engine='python', quoting=csv.QUOTE_NONE)

    data = data[~data.category.str.contains("unknown_state")]
    data = data[~data.category.str.contains("not-malayalam")]
    data = data.reset_index(drop=True)
    print(file, " length: ", len(data.index))

    data2 = data
    data2['label'] = 0
    data3 = data

    with alive_bar(len(data.index)) as bar:
        for i in data.index:
            if 'Negative' in data['category'].iloc[[i]].to_string(header=False, index=False):
                data2['label'].iloc[[i]] = 0
            elif 'Mixed_feelings' in data['category'].iloc[[i]].to_string(header=False, index=False):
                data2['label'].iloc[[i]] = 1
            elif 'Positive' in data['category'].iloc[[i]].to_string(header=False, index=False):
                data2['label'].iloc[[i]] = 2
            # elif 'unknown_state' in data['category'].iloc[[i]].to_string(header=False, index=False):
            #     data2.drop([i])
            # elif 'not-malayalam' in data['category'].iloc[[i]].to_string(header=False, index=False):
            #     data2.drop([i])

            tweet = data['text'].iloc[[i]].to_string(header=False, index=False)
            tweet = ' '.join(re.sub("(@[A-Za-z0–9]+)|(@)|(#[A-Za-z0–9)]+)|(#)", " ", tweet).split())
            # for j in range(len(tweet)):
            #     if re.search("http[.]*", tweet[j]) != None:
            #         tweet[j] = tweet[j][:re.search("http[.]*", tweet[j]).span()[0]]
            #     else:
            #         continue
            # print(tweet)
            tweet = cleaning_symbol(tweet)
            tweet = cleaning_punctuation(tweet)
            data2['text'].iloc[[i]] = tweet
            bar()
    data2.to_csv(datapath + ".csv", ',', encoding="utf-8")
