from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import pandas as pd


def txt_features(p_resumetxt, p_jdtxt):
    """
    This function returns a dataframe of features 
    extracted from a list of texts
    :param p_resumetxt: preprocessed list of resume texts
    :param p_jdtxt: preprocessed list of job description texts
    :return: dataframe of features 
    """
    #new code
    if not p_resumetxt or not p_jdtxt:
        # Handle the case when either the resume text or job description text is empty
        print("Either resume text or job description text is empty.")
        return None 
    #new code

    txt = p_resumetxt+p_jdtxt
    tv = TfidfVectorizer(max_df=0.85,min_df=1,ngram_range=(1,3))
    
    
    tfidf_wm = tv.fit_transform(txt)

    tfidf_tokens = tv.get_feature_names_out()
    df_tfidfvect = pd.DataFrame(data = tfidf_wm.toarray(),columns = tfidf_tokens)

    return df_tfidfvect

def feats_reduce(feats_df):

    """
    This function returns a reduced dimensionality of a dataframe of features
    :param feats_df: dataframe of features extracted from a list of texts
    :return: reduced dimensionality of a dataframe of features
    """

    #new code
    if feats_df is None:
        # Handle the case when the input dataframe is None
        print("Input dataframe is None.")
        return None  # You can modify this part based on your requirement

    if feats_df.empty:
        # Handle the case when the input dataframe is empty
        print("Input dataframe is empty.")
        return None  
    #new code
    dimrec = TruncatedSVD(n_components=30, n_iter=7, random_state=42)
    feats_red = dimrec.fit_transform(feats_df)
    # Converting transformed vector to list
    feats_red = feats_red.tolist()
    # Converting list to DataFrame
    feat_red = pd.DataFrame(feats_red)

    return feat_red

