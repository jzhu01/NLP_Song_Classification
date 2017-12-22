import csv
from functools import partial 

# Jen Zhu & Dani Mednikoff
# CS 585, Fall 2017
# Final Project Code

# Python File Version of Jupiter Code

PATH_TO_VALENCE_AROUSAL_DATA = "data/Valence, Arousal, Dominance - Ratings_Warriner_et_al.csv"
PATH_TO_EMOTION_VALUES = "data/Emotion Values.csv"
PATH_TO_LYRIC_DATA = "data/lyrics.csv"
OUTPUT_PATH = "generatedCSVFromData/output.csv"
EMOTION_OUTPUT_PATH = "generatedCSVFromData/emotion_vals.csv"
ALL_OUTPUT_PATH = "generatedCSVFromData/alldata.csv"
EMOTION_SONG_OUTPUT_PATH = "generatedCSVFromData/emotion_counts.csv"


def readValenceArousalCSV(PATH_TO_DATA):
    word_info = {}
    with open(PATH_TO_DATA, 'rb') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            word = row.pop(0)
            word_info[word] = row
    return word_info

def readEmotionValuesCSV(PATH_TO_DATA, maxVal, minVal, maxAro, minAro):
    emotionVals = {}
    # calculate valence
    with open(PATH_TO_DATA) as f:
        reader = csv.reader(f)
        reader.next()
        emoVal = [float(x[1]) for x in reader]
        f_emoVals = rescale(emoVal, minVal, maxVal)
    
    # calculate arousal        
    with open(PATH_TO_DATA) as f: 
        reader = csv.reader(f)
        reader.next()
        emoAro = [float(x[2]) for x in reader]
        f_emoAro = rescale(emoAro, minAro, maxAro)
    
    # word    
    with open(PATH_TO_DATA) as f: 
        reader = csv.reader(f)
        reader.next()
        emotions = [x[0] for x in reader]
    
    for i in range(len(emotions)):
        emotionVals[emotions[i]] = [f_emoVals[i], f_emoAro[i]]
    return emotionVals

def readSongDataCSV(PATH_TO_DATA):
    reader = csv.reader(open(PATH_TO_DATA))
    songDict = {}
    reader.next()
    for row in reader:
        key = row[0]
        lyric = row[1].split()
        songDict[key] = lyric
    return songDict

# helper method to create a Bag of Words 
# representaiton of a song's lyrics 
# returns a dictionary of word and their counts 
# only applies to each individual song
def generateBOW(songLyrics):
    bow = {} 
    for word in songLyrics:
        if word not in bow.keys():
            bow[word] = 1
        else:
            bow[word] += 1
    return bow

# method to help rescale the values passed for the
# scale of valence and arousal values in emotions 
def rescale(values, new_min, new_max):
    output = []
    old_min, old_max = min(values), max(values)

    for v in values:
        new_v = (new_max - new_min) / (old_max - old_min) * (v - old_min) + new_min
        output.append(new_v)
    return output

# method for calculating the average valence 
# and arousal scores for each song based on the 
# lyrics returned from generateBOW
def calcValAroForSong(songDict, word_info):
    song_avg_emotion_val = {} 
    for name, lyrics in songDict.items():
        
        # generate a hashmap
        numWords = len(lyrics)
        lyricsBOW = generateBOW(lyrics)
        
        avg_val = 0
        avg_aro = 0
        #avg_dom = 0
        # currently ignoring dominance values since we don't have a comparator 
        
        # get corresponding VAD in word_info
        for word, count in lyricsBOW.items():
            # do nothing if it's not in word_info
            if word not in word_info:
                # if the word is not in the dictionary, 
                # need to remove counts from total length
                # of lyrics for song
                numWords -= count 
                continue
            # if it is inside
            # add to running avg of song - 2 total values  
            # perhaps include perceptron? 
            word_values = word_info[word]
        
            #print "avg_val is:", avg_val
            avg_val += float(word_values[0])*count
            avg_aro += float(word_values[2])*count
            #avg_dom += float(word_values[4])*count
            
        f_avg_val = avg_val/numWords
        f_avg_aro = avg_aro/numWords
        #f_avg_dom = avg_dom/numWords
        #song_avg_emotion_val[name] = [f_avg_val, f_avg_aro, f_avg_dom]
        song_avg_emotion_val[name] = [f_avg_val, f_avg_aro]
    return song_avg_emotion_val

# use euclidean geometry to calculate the closest value
def distance_squared(x, emotionVals):
    y = emotionVals[1]
    return (x[0] - y[0])**2 + (x[1]-y[1])**2

# method that generates a hashmap of songs and
# their corresponding emotions 
def matchSongToEmotion(song_avg_emotion_val, sorted_emoVal):
    song_emotion_mapping = {}
    for song, values in song_avg_emotion_val.items():
        closestEmotion = min(sorted_emoVal, key=partial(distance_squared, values))
        song_emotion_mapping[song] = closestEmotion[0]
    return song_emotion_mapping

# methods for generating various charts
'''
def writeToCSV(path, values, counts, headerVals):
    with open(path, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headerVals)
        for item, value in values.items():
            writer.writerow((item, value))
'''
def writeToCSV(path, emotionVals, counts, headerVals):
    with open(path, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headerVals)
        for emotion, values in emotionVals.items():
            writer.writerow((emotion, values[0], values[1], counts[emotion]))
            
def writeAllToCSV(path, songValues, emotionVals):
    with open(path, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Song", "Emotion", "Valence", "Arousal"])
        for item, value in songValues.items():
            writer.writerow((item, value, emotionVals[value][0], emotionVals[value][1]))

def calculateEmotionData(songEmotionVals, emotions):
    emotionCounts = dict((emotion,0) for emotion in emotions)
    for song,emotion in songEmotionVals.items():
        emotionCounts[emotion] += 1
    return emotionCounts
            
def main():
    val_aro_words = readValenceArousalCSV(PATH_TO_VALENCE_AROUSAL_DATA)
    songData = readSongDataCSV(PATH_TO_LYRIC_DATA)
    total_song_avg_val_aro_scores = calcValAroForSong(songData, val_aro_words)

    # original case - using the maximum and minimum values
    maxVal = max(total_song_avg_val_aro_scores.iteritems(), key=lambda x: x[1][0])[1][0]
    minVal = min(total_song_avg_val_aro_scores.iteritems(), key=lambda x: x[1][0])[1][0]
    maxAro = max(total_song_avg_val_aro_scores.iteritems(), key=lambda x: x[1][1])[1][1]
    minAro = min(total_song_avg_val_aro_scores.iteritems(), key=lambda x: x[1][1])[1][1]

    # experiment, using the upper and lower fences of the dataset's boxplots instead
    #maxVal = 6.872222
    #minVal = 5.120208
    #maxAro = 4.740899
    #minAro = 3.514954

    emotion_values = readEmotionValuesCSV(PATH_TO_EMOTION_VALUES, maxVal, minVal, maxAro, minAro)
    # sorted emotions by valence - lowest to greatest
    sorted_emoVal = sorted(emotion_values.items(), key=lambda pair: pair[1])
    song_emotion_vals = matchSongToEmotion(total_song_avg_val_aro_scores, sorted_emoVal)
    #writeToCSV(EMOTION_OUTPUT_PATH, emotion_values, ["Emotion", "Valence", "Arousal"])
    #writeToCSV(OUTPUT_PATH, song_emotion_vals, ["Song", "Emotion"])
    #writeAllToCSV(ALL_OUTPUT_PATH, song_emotion_vals, emotion_values)
    emotionSongCounts = calculateEmotionData(song_emotion_vals, emotion_values.keys())
    writeToCSV(EMOTION_SONG_OUTPUT_PATH, emotion_values, emotionSongCounts, ["Emotion", "Valence", "Arousal","Counts"])