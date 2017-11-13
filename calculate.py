import csv
PATH_TO_DATA = "Valence, Arousal, Dominance - Ratings_Warriner_et_al.csv"
word_info = {}
def readCSV():
    with open(PATH_TO_DATA, 'rb') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            word = row.pop(0)
            word_info[word] = row
    
    print word_info
readCSV()