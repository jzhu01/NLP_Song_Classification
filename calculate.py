import csv
from functools import partial 

PATH_TO_VALENCE_AROUSAL_DATA = "Valence, Arousal, Dominance - Ratings_Warriner_et_al.csv"
PATH_TO_EMOTION_VALUES = "Emotion Values.csv"
PATH_TO_LYRIC_DATA = "lyrics.csv"

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

# method for calculating the average valence 
# and arousal scores for each song based on the 
# lyrics returned from generateBOW
def calcValAroForSong(songDict):
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
def matchSongToEmotion():
    song_emotion_mapping = {}
    for song, values in song_avg_emotion_val.items():
        closestEmotion = min(sorted_emoVal, key=partial(distance_squared, values))
        song_emotion_mapping[song] = closestEmotion[0]
    return song_emotion_mapping

def main():
	val_aro_words = readValenceArousalCSV(PATH_TO_VALENCE_AROUSAL_DATA)
	songData = readSongDataCSV(PATH_TO_LYRIC_DATA)
	total_song_avg_val_aro_scores = calcValAroForSong(songData)

    maxVal = max(total_song_avg_val_aro_scores.iteritems(), key=lambda x: x[1][0])[1][0]
    minVal = min(total_song_avg_val_aro_scores.iteritems(), key=lambda x: x[1][0])[1][0]
    maxAro = max(total_song_avg_val_aro_scores.iteritems(), key=lambda x: x[1][1])[1][1]
    minAro = min(total_song_avg_val_aro_scores.iteritems(), key=lambda x: x[1][1])[1][1]

    emotion_values = readEmotionVals(PATH_TO_EMOTION_VALUES, maxVal, minVal, maxAro, minAro)
	# sorted emotions by valence - lowest to greatest
	sorted_emoVal = sorted(emotionVals.items(), key=lambda pair: pair[1])
