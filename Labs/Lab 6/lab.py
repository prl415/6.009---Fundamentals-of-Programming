# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 15:18:54 2020

@author: Mustafa
"""

"""6.009 Lab 6 -- Autocomplete"""

# NO ADDITIONAL IMPORTS!
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self):
        """
        Initialize an empty trie.
        """
        self.value = None
        self.children = {}
        self.type = None

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        #Check whether the type of the given key is consistent with the type
        #expected by trie. 
        if type(key) != self.type:
            raise TypeError
        
        #Type are consistent, now check whether the given key is in trie
        node = self  #Root
        for i in range(len(key)):
            char = key[i:i+1]
            if char in node.children:
                node = node.children[char]
            else:
                raise KeyError
        
        #No key error raised in the loop. So. key is in the trie. If key's value
        #is None, raise KeyError otherwise return the value of the key value
        if node.value == None:
            raise KeyError
        
        return node.value
                         
    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        #There are two cases. In first case, trie is empty. Add the first node
        #to the trie
        node = self   #Root
        if len(node.children) == 0:
            for i in range(len(key)):
                char = key[i:i+1]
                node.type = type(char)
                node.children[char] = Trie()
                node = node.children[char]
            node.value = value
            return
        
        #Second case, node is not empty
        #Check the type of the key
        if type(key) != node.type:
            raise TypeError
        
        #Type of the key are consistent with the Trie. Add the key to the trie
        for i in range(len(key)):
            char = key[i:i+1]
            if char in node.children:
                node = node.children[char]
            else:
                node.children[char] = Trie()
                node.type = type(char)
                node = node.children[char]
        node.value = value
        return

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists.
        """
        #Check whether key is in the trie
        try:
            val = self.__getitem__(key)
        except:
            return
        
        #Key is in trie
        node = self
        for i in range(len(key)):
            char = key[i:i+1]
            node = node.children[char]
        
        node.value = None
        return

    def __contains__(self, key):
        """
        Return True if key is in the trie and has a value, return False otherwise.
        """
        #Check whether key is in the trie
        try:
            val = self.__getitem__(key)
            return True
        except:
            return False

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator or iterator!
        """
        def helper(node, current_word):
            #End of the branch
            if len(node.children) == 0 and node.value != None:
                yield (current_word, node.value)
            
            else:
                #Value of the current node is not None, yield it
                if len(node.children) != 0 and node.value != None:
                    yield (current_word, node.value)
                
                #Go along the current branch
                for char, child in node.children.items():
                    yield from helper(child, current_word + char)
        
        #Type of trie is tuple so it starts with ()
        if self.type == tuple:
            return helper(self, ())
        
        #Type of trie is tuple so it starts with ''
        return helper(self, '')

    def get_child(self, edge):
        '''
        Returns the child of the current node pointed by edge. If such a child
        isn't exist, raises KeyError.
        '''
        if edge in self.children:
            return self.children[edge]
        else:
            raise KeyError
            
    def get_type(self):
        '''
        Returns the type of the current node
        '''
        return self.type

def make_word_trie(text):
    """
    Given a piece of text as a single string, return a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    #Create a list of the words in the text
    word_list = []
    for sentence in tokenize_sentences(text):
        word_list.extend(sentence.split(sep = ' '))
        
    #Now, by using word_list, create frequency map
    trie = Trie()
    for word in word_list:
        if word not in trie:
            trie[word] = 1
        else:
            trie[word] += 1
            
    return trie
    
def make_phrase_trie(text):
    """
    Given a piece of text as a single string, return a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    #Convert each sentence to a tuple and then by using these tuples create
    #frequncy map
    trie = Trie()
    for sentence in tokenize_sentences(text):
        sent_tup = tuple(sentence.split(sep = ' '))
        if sent_tup not in trie:
            trie[sent_tup] = 1
        else:
            trie[sent_tup] += 1
            
    return trie

def sortSecond(val):
    '''
    Helper function for sorting of the frequncy list. Returns the second
    element of the given tuple val
    '''
    return val[1]

def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    """
    
    #If the prefix's type isn't consistent with the trie's, raise TypeError
    if trie.get_type() != type(prefix):
        raise TypeError
    
    #Type of the prefix are consistent with trie's. Create list of words which
    #starts with the prefix. 
    node = trie
    for i in range(len(prefix)):
        c = prefix[i:i+1]
        try:
            node = node.get_child(c)
        except:
            return []
    
    #Sort the words according to their frequencies from most frequent word
    #to least frequent
    l = list(node)
    
    #Max_count is not specified. Return whole list
    if max_count == None:
        return [prefix + e[0] for e in l]
    
    #Max_count is specified. Return max_count element
    l.sort(key = sortSecond, reverse = True)    
    word_list = [prefix + e[0] for e in l[:max_count]]
    
    return word_list

def get_all_valid_edits(trie, prefix):
    '''
    Helper function for autocorrect
    Returns the list of all valid edits 
    '''
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    
    suggested_words = set()
    
    #A single character addition
    for c in alphabet:
        for i in range(len(prefix),-1, -1):
            new_edit = prefix[:i] + c + prefix[i:]
            if new_edit in trie:
                suggested_words.add((new_edit, trie[new_edit]))
            
    #A single character deletion
    for i in range(len(prefix)-1,-1,-1):
        new_edit = prefix[:i] + prefix[i+1:]
        if new_edit in trie:
            suggested_words.add((new_edit, trie[new_edit]))
        
    #A single character replacement
    for i in range(len(prefix)-1,-1,-1):
        for c in alphabet:
            new_edit = prefix[:i] + c + prefix[i+1:]
            if new_edit in trie:
                suggested_words.add((new_edit, trie[new_edit]))
            
    #Two-character transpose
    for i in range(len(prefix)-1):
        new_edit = prefix[:i] + prefix[i+1] + prefix[i] + prefix[i+2:]
        if new_edit in trie:
            suggested_words.add((new_edit, trie[new_edit]))
            
    return suggested_words

def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.

    Do not use a brute-force method that involves generating/looping over
    all the words in the trie.
    """
    #Type check
    if trie.get_type() != type(prefix):
        raise TypeError
     
    #Get the words which start with the prefix
    word_list = autocomplete(trie, prefix, max_count)
    
    #len(word_list) == max_count. Return word_list
    if max_count != None and max_count == len(word_list):
        return word_list
    
    #max_count == None or number of words found is lower than max_count.
    #By using trie and prefix get the list of all valid edits
    suggested_words = get_all_valid_edits(trie, prefix)
    
    #max_count == None. Return all the autocomplete results and valid edits
    if max_count == None:
        suggested_words = [word for word, _ in suggested_words]
        return list(set(suggested_words).union(set(word_list)))
    
    #Number of words found is lower than max_count. Add the most-occurring 
    #(max_count-len(word_list)) words (edits) to the word_list and 
    #return the word_list
    suggested_words = list(suggested_words)
    suggested_words.sort(key = sortSecond, reverse = True)
    for new_word in suggested_words:
        if new_word[0] not in word_list:
            word_list.append(new_word[0])
        if len(word_list) == max_count:
            return word_list
    
    #len(word_list) + len(suggested_words) < max_count. Return all of them.        
    return word_list

def get_matchings(node, pattern, current_word):
    '''
    Helper function for word_filter
    Returns the list of (word, freq) tuples of words which are matched
    with the pattern
    '''
    #Pattern is matched with the current_word. If current_word exists yield 
    #it and it's value in trie
    if len(pattern) == 0:
        if node.value != None:
            yield (current_word, node.value)
        else:
            return
    
    #Zero or more than character matching
    elif pattern[0] == '*':
        
        #Zero matching
        yield from get_matchings(node, pattern[1:], current_word)
        
        #More than zero matching
        if len(node.children) != 0:
            for char, child in node.children.items():
                yield from get_matchings(child, pattern, current_word + char)
    
    #Any one character matching
    elif pattern[0] == '?':
        for char, child in node.children.items():
            yield from get_matchings(child, pattern[1:], current_word + char)
            
    #Specific one character matching
    elif pattern[0] in node.children:
        child = node.children[pattern[0]]
        yield from get_matchings(child, pattern[1:], current_word + pattern[0])
    
    #No Match    
    else:
        return

def edit_pattern(pattern):
    '''
    Helper function for word_filter
    Returns a converted version of the pattern,which is created by replacing 
    adjacent *s with one *
    '''
    new_pattern = ''
    if set(pattern) == {'*'}:
        new_pattern = '*'
    
    else:
        new_pattern = ''
        for i in range(len(pattern)-1):
            if pattern[i] == '*':
                if pattern[i] == pattern[i+1]:
                    continue
                else:
                    new_pattern = new_pattern + pattern[i]
            else:
                new_pattern = new_pattern + pattern[i]
        new_pattern = new_pattern + pattern[-1]
    
    return new_pattern
 
def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.

    Do not use a brute-force method that involves generating/looping over
    all the words in the trie.
    """
    new_pattern = edit_pattern(pattern)
    
    return list(set(get_matchings(trie, new_pattern, '')))

# you can include test cases of your own in the block below.
if __name__ == '__main__':
    pass