from collections import defaultdict

def count_words (words):
    "count words given in a list, return word and its frequency"
    list = defaultdict(int)
    for i in words:
        list[i] += 1
    return list

def get_ngrams (term, size):
    "returns n-grams of size n"

    # define empty list of n-grams
    ngrams = []

    # length of the term
    term_length = len(term)

    if (size>term_length):
        # we cannot form any n-grams - term too small for given size
        return term
    # end if
    
    # define left and right boundaries
    left = 0
    right = left + size

    while (right<=term_length):
        # extract slice and append to the list
        slice = term[left:right]
        ngrams.append(slice)
        
        # move slice to the right
        left = left + 1
        right = right + 1
    # end while

    # calculate term frequency
    dict = count_words(ngrams)

    # return ngrams = keys of the list
    return dict.keys()

def comp_ngrams (term1, term2, size):
    "compares two terms and returns their degree of equality"

    # equality of terms : Dice coefficient
    # 
    # S = 2C/(A+B)
    # 
    # S = degree of equality
    # C = n-grams contained in term 2 as well as in term 2
    # A = number of n-grams contained in term 1
    # B = number of n-grams contained in term 2

    # get n-grams for term1 and term2
    list1 = get_ngrams(term1, size)
    list2 = get_ngrams(term2, size)

    # find n-grams contained in both lists
    A = len(list1)
    B = len(list2)

    # transform both lists into dictionaries
    list1_dict = count_words(list1)
    list2_dict = count_words(list2)

    # extract the keys which appear in both list1 and list2
    list3 = filter(list1_dict.has_key, list2_dict.keys())

    # convert this list in a dictionary and count the number of keys
    s = set(list3)
    C = len(s)

    # calculate similarity of term 1 and 2
    S = float(float(2*C)/float(A+B))

    # return similarity
    return S

def ngram_stemmer (word_list, size, equality):
    "reduces word_list according to the n-gram stemming method"

    # use return_list and stop_list for the terms to be removed, later
    return_list = []
    stop_list = []

    # calculate length and range
    list_length = len(word_list)
    outer_list_range = range(0, list_length)

    for i in outer_list_range:
        term1 = word_list[i]

        inner_list_range = range (0, i)

        for j in inner_list_range:
            term2 = word_list[j]

            # calculate n-gram value
            ngram_value = comp_ngrams(term1, term2, size)

            # compare
            degree = ngram_value - equality
            if (degree>0):
                # these terms are so similar that they can be conflated
                # remove the longer term, keep the shorter one
                if (len(term2)>len(term1)):
                    stop_list.append(term2)
                else:
                    stop_list.append(term1)
                # end if
            # end if
        # end for
    # end if

    # conflate the matrix
    # extract all the items which do not appear in stop_list
    # work with dictionaries instead of lists
    return_dict = set(word_list)
    stop_dict = set(stop_list)
    new_list = return_dict - stop_dict

    return new_list

if __name__ == "__main__":
    words = ["practical", "sections", "sectional", "predetermined", "suffixed", "prefixed", "nondenominational"]
    print ngram_stemmer(words, 3, 0.5)

    print comp_ngrams("sections", "sectional", 2)

