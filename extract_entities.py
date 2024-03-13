import re
from nltk import sent_tokenize, pos_tag, word_tokenize, everygrams
from nltk.corpus import wordnet, stopwords
from fuzzywuzzy import fuzz

def get_number(text,cgpa=False):
    """
    This function returns a list of a phone number from a list of text
    :param text: list of text
    :return: list of a phone number
    """

    #new code : Add CGPA pattern extraction
    if cgpa:
        # Extract CGPA logic (modify as needed)
        cgpa_pattern = r'\b(?:10|\d(?:\.\d{1,2})?)\b' # Example CGPA pattern, modify as needed
        cgpa_match = re.search(cgpa_pattern, text)
        if cgpa_match:
            return cgpa_match.group()
        else:
            return None  # Return None if CGPA not found

    
    # compile helps us to define a pattern for matching it in the text
    # pattern = re.compile(r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*\d*[ \t\r\f\v]*)')
    # # findall finds the pattern defined in compile
    # pt = pattern.findall(text)

    # # sub replaces a pattern matching in the text
    # pt = [re.sub(r'[,.]', '', ah) for ah in pt if len(re.sub(r'[()\-.,\s+]', '', ah))>9]
    # pt = [re.sub(r'\D$', '', ah).strip() for ah in pt]
    # pt = [ah for ah in pt if len(re.sub(r'\D','',ah)) <= 15]

    # for ah in list(pt):
    #     # split splits a text
    #     if len(ah.split('-')) > 3: continue
    #     for x in ah.split("-"):
    #         try:
    #             # isdigit checks whether the text is number or not
    #             if x.strip()[-4:].isdigit():
    #                 if int(x.strip()[-4:]) in range(1900, 2100):
    #                     pt.remove(ah)
                    
    #         except: pass

    #     number = None
    #     number = list(set(pt))
    #     return number
    number_pattern = re.compile(r'(?:(?:\+|0{0,2})91[-\s]?|[0]?)?[6789]\d{9}')

    # Find all phone number matches in the text
    numbers = number_pattern.findall(text)

    return numbers if numbers else None




def get_email(text):
    """
    This function returns a list of an email from a list of text
    :param text: list of text
    :return: list of an email
    """
    # compile helps us to define a pattern for matching it in the text
    r = re.compile(r'[A-Za-z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    return r.findall(str(text))



def rm_number(text):
    """
    This function removes phone number from a list of text
    :param text: list of text
    :return: list of text without phone number
    """
    try:
        # compile helps us to define a pattern for matching it in the text
        pattern = re.compile(r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*\d*[ \t\r\f\v]*)')
        # findall finds the pattern defined in compile
        pt = pattern.findall(text)
        # sub replaces a pattern matching in the text
        pt = [re.sub(r'[,.]', '', ah) for ah in pt if len(re.sub(r'[()\-.,\s+]', '', ah))>9]
        pt = [re.sub(r'\D$', '', ah).strip() for ah in pt]
        pt = [ah for ah in pt if len(re.sub(r'\D','',ah)) <= 15]
        for ah in list(pt):
            if len(ah.split('-')) > 3: continue
            for x in ah.split("-"):
                try:
                    # isdigit checks whether the text is number or not
                    if x.strip()[-4:].isdigit():
                        if int(x.strip()[-4:]) in range(1900, 2100):
                    # removes a the mentioned text
                            pt.remove(ah)
                except: pass

        number = None
        number = pt
        number = set(number)
        number = list(number)
        for i in number:
            text = text.replace(i," ")
        return text
        
    except: pass


def rm_email(text):
    """
    This function removes email from a list of text
    :param text: list of text
    :return: list of text without email
    """
    try:
        email = None
        # compile helps us to define a pattern for matching it in the text
        pattern = re.compile('[\w\.-]+@[\w\.-]+')
        # findall finds the pattern defined in compile
        pt = pattern.findall(text)
        email = pt
        email = set(email)
        email = list(email)
        for i in email:
            # replace will replace a given string with another
            text = text.replace(i," ")

        return text

    except: pass



# def get_name(text):
#     """
#     This function returns a candidate name from a list of text
#     :param text: list of text
#     :return: string of a candidate name
#     """
#     # Tokenizes whole text to sentences
#     Sentences = sent_tokenize(text)
#     t = []

#     for s in Sentences:
#         # Tokenizes sentences to words
#         t.append(word_tokenize(s))
#     # Tags a word with its part of speech
#     words = [pos_tag(token) for token in t]
#     n = []
#     for x in words:
#         for l in x:
#         # match matches the pos tag of a word to a given tag here
#             if re.match('[NN.*]', l[1]):
#                 n.append(l[0])

#     cands = []
#     for nouns in n:
#         if not wordnet.synsets(nouns):
#             cands.append(nouns)

#     cand = ' '.join(cands[:1])
#     return cand
    
def get_name(text):
    """
    This function returns a candidate name from a list of text
    :param text: list of text
    :return: string of a candidate name
    """
    # Tokenizes whole text to sentences
    Sentences = sent_tokenize(text)
    t = []

    for s in Sentences:
        # Tokenizes sentences to words
        t.append(word_tokenize(s))
    # Tags a word with its part of speech
    words = [pos_tag(token) for token in t]
    n = []
    for x in words:
        for l in x:
            # match matches the pos tag of a word to a given tag here
            if re.match('[NN.*]', l[1]):
                n.append(l[0])

    cands = []
    i = 0
    while i < len(n) and len(cands) < 2:
        # Check if the next word is also a noun, indicating a potential part of the name
        if i + 1 < len(n) and i + 1 < len(words) and re.match('[NN.*]', words[i + 1][0][1]):
            cands.append(f"{n[i]} {n[i + 1]}")
            i += 2  # Skip the next word (surname)
        else:
            cands.append(n[i])
            i += 1

    # Join the first two candidates (first name and surname)
    cand = ' '.join(cands[:2]) if len(cands) >= 2 else None

    # Check if there are additional characters or symbols after the extracted name
    if cand:
        match = re.match(r'^([A-Za-z]+ [A-Za-z]+)', cand)
        if match:
            return match.group(1)
        else:
            return None
    else:
        return None

def normalize_skill(skill):
    # Normalize skill name by converting to lowercase and removing special characters
    return re.sub(r'\W+', '', skill.lower())


def get_skills(text,skills):
    """
    This function returns a list of skills from a list of text
    :param text: list of text
    :param skills: dataframe of predefined skills
    :return: list of skills
    """
    
    # sw = set(stopwords.words('english'))
    # tokens = word_tokenize(text)
    # # remove the punctuation
    # ft = [w for w in tokens if w.isalpha()]
    # # remove the stop words
    # ft = [w for w in tokens if w not in sw]
    # # generate bigrams and trigrams
    # n_grams = list(map(' '.join, everygrams(ft, 2, 3)))
    # fs = set()
    # # we text for each token in our skills database
    # for token in ft:
    #     if token.lower() in skills:
    #         fs.add(token)
    
    # for ngram in n_grams:
    #     if ngram.lower() in skills:
    #         fs.add(ngram)
    # return fs


    # sw = set(stopwords.words('english'))
    # tokens = word_tokenize(text.lower())  # Convert text to lowercase before tokenization
    # # Remove stopwords and non-alphabetic tokens
    # tokens = [token for token in tokens if token.isalpha() and token not in sw]
    # # Generate bigrams and trigrams
    # n_grams = list(map(' '.join, everygrams(tokens, 2, 3)))
    # extracted_skills = set()
    # # Check if individual tokens or n-grams are in the predefined skills
    # for token in tokens + n_grams:
    #     normalized_token = normalize_skill(token)
    #     if normalized_token in skills:
    #         extracted_skills.add(normalized_token)
    # return extracted_skills

    sw = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    # remove the punctuation
    ft = [w for w in tokens if w.isalpha()]
    # remove the stop words
    ft = [w for w in tokens if w not in sw]
    # generate bigrams and trigrams
    n_grams = list(map(' '.join, everygrams(ft, 2, 3)))
    fs = set()
    # for each token in our skills database
    for token in ft:
        # Check if the token is in the skills database
        if token.lower() in skills:
            fs.add(token)
        else:
            # If not directly matched, perform fuzzy matching with each skill
            for skill in skills:
                if fuzz.ratio(token.lower(), skill.lower()) >= 90:
                    fs.add(skill)  # Add the skill if the fuzzy ratio is above a threshold
    
    for ngram in n_grams:
        # Perform fuzzy matching for n-grams as well
        for skill in skills:
            if fuzz.ratio(ngram.lower(), skill.lower()) >= 90:
                fs.add(skill)  # Add the skill if the fuzzy ratio is above a threshold
                
    return fs
