# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 15:18:54 2020

@author: Mustafa
"""

"""6.009 Lab 6 -- Autocomplete"""

# NO ADDITIONAL IMPORTS!
from text_tokenize import tokenize_sentences

#Working version 1 (Works only for strs) '16/07/2020 - 23.00'
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
        for char in key:
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
            node.type = type(key)
            for char in key:
                node.children[char] = Trie()
                node = node.children[char]
            node.value = value
            return
        
        #Second case, node is not empty
        #Check the type of the key
        node = self
        if type(key) != self.type:
            raise TypeError
        
        #Type of the key are consistent with the Trie. Add the key to the trie
        for char in key:
            if char in node.children:
                node = node.children[char]
            else:
                node.children[char] = Trie()
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
        for char in key:
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
            if len(node.children) == 0 and node.value != None:
                yield (current_word, node.value)
            
            else:
                for char, child in node.children.items():
                    if len(node.children) != 0 and node.value != None:
                        yield (current_word, node.value)
                        
                    yield from helper(child, current_word + char)
        
        return helper(self, '')


def make_word_trie(text):
    """
    Given a piece of text as a single string, return a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    raise NotImplementedError


def make_phrase_trie(text):
    """
    Given a piece of text as a single string, return a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    raise NotImplementedError


def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    """
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


# you can include test cases of your own in the block below.
if __name__ == '__main__':
    pass

#----------------------------------------------------------------------
#Working version 2 '19/07/2020 - 16.00'
#"""6.009 Lab 6 -- Autocomplete"""
#
## NO ADDITIONAL IMPORTS!
#from text_tokenize import tokenize_sentences
#
#
#class Trie:
#    def __init__(self):
#        """
#        Initialize an empty trie.
#        """
#        self.value = None
#        self.children = {}
#        self.type = None
#
#    def __getitem__(self, key):
#        """
#        Return the value for the specified prefix.  If the given key is not in
#        the trie, raise a KeyError.  If the given key is of the wrong type,
#        raise a TypeError.
#        """
#        #Check whether the type of the given key is consistent with the type
#        #expected by trie. 
#        if type(key) != self.type:
#            raise TypeError
#        
#        #Type are consistent, now check whether the given key is in trie
#        node = self  #Root
#        if node.type == tuple:
#            for char in key:
#                if (char,) in node.children:
#                    node = node.children[(char,)]
#                else:
#                    raise KeyError
#                    
#        else:
#            for char in key:
#                if char in node.children:
#                    node = node.children[char]
#                else:
#                    raise KeyError
#        
#        #No key error raised in the loop. So. key is in the trie. If key's value
#        #is None, raise KeyError otherwise return the value of the key value
#        if node.value == None:
#            raise KeyError
#        
#        return node.value
#                         
#    def __setitem__(self, key, value):
#        """
#        Add a key with the given value to the trie, or reassign the associated
#        value if it is already present in the trie.  Assume that key is an
#        immutable ordered sequence.  Raise a TypeError if the given key is of
#        the wrong type.
#        """
#        #There are two cases. In first case, trie is empty. Add the first node
#        #to the trie
#        node = self   #Root
#        if len(node.children) == 0:
#            node.type = type(key)
#            
#            if node.type == tuple:
#                for char in key:
#                    node.children[(char,)] = Trie()
#                    node = node.children[(char,)]
#                
#            else:
#                for char in key:
#                    node.children[char] = Trie()
#                    node = node.children[char]
#                    
#            node.value = value
#            return
#        
#        #Second case, node is not empty
#        #Check the type of the key
#        node = self
#        if type(key) != self.type:
#            raise TypeError
#        
#        #Type of the key are consistent with the Trie. Add the key to the trie
#        if node.type == tuple:
#            for char in key:
#                c = (char,)
#                if c in node.children:
#                    node = node.children[c]
#                    
#                else:
#                    node.children[c] = Trie()
#                    node = node.children[c]
#        else:
#            for char in key:
#                if char in node.children:
#                    node = node.children[char]
#                    
#                else:
#                    node.children[char] = Trie()
#                    node = node.children[char]
#                    
#        node.value = value
#        return
#
#    def __delitem__(self, key):
#        """
#        Delete the given key from the trie if it exists.
#        """
#        #Check whether key is in the trie
#        try:
#            val = self.__getitem__(key)
#        except:
#            return
#        
#        #Key is in trie
#        node = self
#        if node.type == tuple:
#            for char in key:
#                node = node.children[(char,)]
#        
#        else:
#            for char in key:
#                node = node.children[char]
#                
#        node.value = None
#        return
#
#    def __contains__(self, key):
#        """
#        Return True if key is in the trie and has a value, return False otherwise.
#        """
#        #Check whether key is in the trie
#        try:
#            val = self.__getitem__(key)
#            return True
#        except:
#            return False
#
#    def __iter__(self):
#        """
#        Generator of (key, value) pairs for all keys/values in this trie and
#        its children.  Must be a generator or iterator!
#        """
#        def helper(node, current_word):
#            if len(node.children) == 0 and node.value != None:
#                yield (current_word, node.value)
#            
#            else:
#                for char, child in node.children.items():
#                    
#                    if len(node.children) != 0 and node.value != None:
#                        yield (current_word, node.value)
#                        
#                    yield from helper(child, current_word + char)
#        
#        if self.type == tuple:
#            return helper(self, ())
#        
#        return helper(self, '')
#
#
#def make_word_trie(text):
#    """
#    Given a piece of text as a single string, return a Trie whose keys are the
#    words in the text, and whose values are the number of times the associated
#    word appears in the text
#    """
#    raise NotImplementedError
#
#
#def make_phrase_trie(text):
#    """
#    Given a piece of text as a single string, return a Trie whose keys are the
#    sentences in the text (as tuples of individual words) and whose values are
#    the number of times the associated sentence appears in the text.
#    """
#    raise NotImplementedError
#
#
#def autocomplete(trie, prefix, max_count=None):
#    """
#    Return the list of the most-frequently occurring elements that start with
#    the given prefix.  Include only the top max_count elements if max_count is
#    specified, otherwise return all.
#
#    Raise a TypeError if the given prefix is of an inappropriate type for the
#    trie.
#    """
#    raise NotImplementedError
#
#
#def autocorrect(trie, prefix, max_count=None):
#    """
#    Return the list of the most-frequent words that start with prefix or that
#    are valid words that differ from prefix by a small edit.  Include up to
#    max_count elements from the autocompletion.  If autocompletion produces
#    fewer than max_count elements, include the most-frequently-occurring valid
#    edits of the given word as well, up to max_count total elements.
#
#    Do not use a brute-force method that involves generating/looping over
#    all the words in the trie.
#    """
#    raise NotImplementedError
#
#
#def word_filter(trie, pattern):
#    """
#    Return list of (word, freq) for all words in trie that match pattern.
#    pattern is a string, interpreted as explained below:
#         * matches any sequence of zero or more characters,
#         ? matches any single character,
#         otherwise char in pattern char must equal char in word.
#
#    Do not use a brute-force method that involves generating/looping over
#    all the words in the trie.
#    """
#    raise NotImplementedError
#
#
## you can include test cases of your own in the block below.
#if __name__ == '__main__':
#    pass
#

#Working version 3 - 20/07/2020
## NO ADDITIONAL IMPORTS!
#from text_tokenize import tokenize_sentences
#
#
#class Trie:
#    def __init__(self):
#        """
#        Initialize an empty trie.
#        """
#        self.value = None
#        self.children = {}
#        self.type = None
#
#    def __getitem__(self, key):
#        """
#        Return the value for the specified prefix.  If the given key is not in
#        the trie, raise a KeyError.  If the given key is of the wrong type,
#        raise a TypeError.
#        """
#        #Check whether the type of the given key is consistent with the type
#        #expected by trie. 
#        if type(key) != self.type:
#            raise TypeError
#        
#        #Type are consistent, now check whether the given key is in trie
#        node = self  #Root
#        for i in range(len(key)):
#            char = key[i:i+1]
#            if char in node.children:
#                node = node.children[char]
#            else:
#                raise KeyError
#        
#        #No key error raised in the loop. So. key is in the trie. If key's value
#        #is None, raise KeyError otherwise return the value of the key value
#        if node.value == None:
#            raise KeyError
#        
#        return node.value
#                         
#    def __setitem__(self, key, value):
#        """
#        Add a key with the given value to the trie, or reassign the associated
#        value if it is already present in the trie.  Assume that key is an
#        immutable ordered sequence.  Raise a TypeError if the given key is of
#        the wrong type.
#        """
#        #There are two cases. In first case, trie is empty. Add the first node
#        #to the trie
#        node = self   #Root
#        if len(node.children) == 0:
#            node.type = type(key)
#            for i in range(len(key)):
#                char = key[i:i+1]
#                node.children[char] = Trie()
#                node = node.children[char]
#            node.value = value
#            return
#        
#        #Second case, node is not empty
#        #Check the type of the key
#        if type(key) != node.type:
#            raise TypeError
#        
#        #Type of the key are consistent with the Trie. Add the key to the trie
#        for i in range(len(key)):
#            char = key[i:i+1]
#            if char in node.children:
#                node = node.children[char]
#            else:
#                node.children[char] = Trie()
#                node = node.children[char]
#        node.value = value
#        return
#
#    def __delitem__(self, key):
#        """
#        Delete the given key from the trie if it exists.
#        """
#        #Check whether key is in the trie
#        try:
#            val = self.__getitem__(key)
#        except:
#            return
#        
#        #Key is in trie
#        node = self
#        for i in range(len(key)):
#            char = key[i:i+1]
#            node = node.children[char]
#        
#        node.value = None
#        return
#
#    def __contains__(self, key):
#        """
#        Return True if key is in the trie and has a value, return False otherwise.
#        """
#        #Check whether key is in the trie
#        try:
#            val = self.__getitem__(key)
#            return True
#        except:
#            return False
#
#    def __iter__(self):
#        """
#        Generator of (key, value) pairs for all keys/values in this trie and
#        its children.  Must be a generator or iterator!
#        """
#        def helper(node, current_word):
#            if len(node.children) == 0 and node.value != None:
#                yield (current_word, node.value)
#            
#            else:
#                for char, child in node.children.items():
#                    if len(node.children) != 0 and node.value != None:
#                        yield (current_word, node.value)
#                    
#                    try:
#                        yield from helper(child, current_word + char)
#                    except TypeError:
#                        print()
#                        print('char: ',  char, type(char))
#                        print('current word: ', current_word, type(current_word))
#                        raise TypeError
#        
#        print('the type is: ', self.type)
#        
#        if self.type == tuple:
#            return helper(self, ())
#        
#        return helper(self, '')
#
#def make_word_trie(text):
#    """
#    Given a piece of text as a single string, return a Trie whose keys are the
#    words in the text, and whose values are the number of times the associated
#    word appears in the text
#    """
#    word_list = []
#    for sentence in tokenize_sentences(text):
#        word_list.extend(sentence.split(sep = ' '))
#    trie = Trie()
#    for word in word_list:
#        if word not in trie:
#            trie[word] = 1
#        else:
#            trie[word] = trie[word] + 1
#            
#    return trie
#    
#def make_phrase_trie(text):
#    """
#    Given a piece of text as a single string, return a Trie whose keys are the
#    sentences in the text (as tuples of individual words) and whose values are
#    the number of times the associated sentence appears in the text.
#    """
#    trie = Trie()
#    for sentence in tokenize_sentences(text):
#        sent_tup = tuple(sentence.split(sep = ' '))
#        if sent_tup not in trie:
#            trie[sent_tup] = 1
#        else:
#            trie[sent_tup] = trie[sent_tup] + 1
#            
#    return trie
#
#def autocomplete(trie, prefix, max_count=None):
#    """
#    Return the list of the most-frequently occurring elements that start with
#    the given prefix.  Include only the top max_count elements if max_count is
#    specified, otherwise return all.
#
#    Raise a TypeError if the given prefix is of an inappropriate type for the
#    trie.
#    """
#    if trie.type != type(prefix):
#        raise TypeError
#    
##    prefix_list = []
##    l = len(prefix)
##    for word in list(trie):
##        if word[0][:l] == prefix:
##            prefix_list.append(word)
##    
##    if max_count == None:
##        word_list = [e[0] for e in prefix_list]
##        return word_list
##    
#    def sortSecond(val):
#        return val[1]
##    
##    prefix_list.sort(key = sortSecond)
##    
##    word_list = [e[0] for e in prefix[:max_count]]
##    return word_list
#
#    node = trie
#    for i in range(len(prefix)):
#        c = prefix[i:i+1]
#        if c in node.children:
#            node = node.children[c]
#        else:
#            return []
#    
#    l = list(set(node))
#    l.sort(key = sortSecond, reverse = True)
##    print(l)
#    
#    if max_count == None:
#        return [prefix + e[0] for e in l]
#    
#    word_list = [prefix + e[0] for e in l[:max_count]]
#    
#    return word_list
#
#def autocorrect(trie, prefix, max_count=None):
#    """
#    Return the list of the most-frequent words that start with prefix or that
#    are valid words that differ from prefix by a small edit.  Include up to
#    max_count elements from the autocompletion.  If autocompletion produces
#    fewer than max_count elements, include the most-frequently-occurring valid
#    edits of the given word as well, up to max_count total elements.
#
#    Do not use a brute-force method that involves generating/looping over
#    all the words in the trie.
#    """
#    raise NotImplementedError
#
#
#def word_filter(trie, pattern):
#    """
#    Return list of (word, freq) for all words in trie that match pattern.
#    pattern is a string, interpreted as explained below:
#         * matches any sequence of zero or more characters,
#         ? matches any single character,
#         otherwise char in pattern char must equal char in word.
#
#    Do not use a brute-force method that involves generating/looping over
#    all the words in the trie.
#    """
#    raise NotImplementedError
#
#
## you can include test cases of your own in the block below.
#if __name__ == '__main__':
#    pass

#Working version 4 - 21/07/2020

#"""6.009 Lab 6 -- Autocomplete"""
#
## NO ADDITIONAL IMPORTS!
#from text_tokenize import tokenize_sentences
#
#
#class Trie:
#    def __init__(self):
#        """
#        Initialize an empty trie.
#        """
#        self.value = None
#        self.children = {}
#        self.type = None
#
#    def __getitem__(self, key):
#        """
#        Return the value for the specified prefix.  If the given key is not in
#        the trie, raise a KeyError.  If the given key is of the wrong type,
#        raise a TypeError.
#        """
#        #Check whether the type of the given key is consistent with the type
#        #expected by trie. 
#        if type(key) != self.type:
#            raise TypeError
#        
#        #Type are consistent, now check whether the given key is in trie
#        node = self  #Root
#        for i in range(len(key)):
#            char = key[i:i+1]
#            if char in node.children:
#                node = node.children[char]
#            else:
#                raise KeyError
#        
#        #No key error raised in the loop. So. key is in the trie. If key's value
#        #is None, raise KeyError otherwise return the value of the key value
#        if node.value == None:
#            raise KeyError
#        
#        return node.value
#                         
#    def __setitem__(self, key, value):
#        """
#        Add a key with the given value to the trie, or reassign the associated
#        value if it is already present in the trie.  Assume that key is an
#        immutable ordered sequence.  Raise a TypeError if the given key is of
#        the wrong type.
#        """
#        #There are two cases. In first case, trie is empty. Add the first node
#        #to the trie
#        node = self   #Root
#        if len(node.children) == 0:
#            for i in range(len(key)):
#                char = key[i:i+1]
#                node.type = type(char)
#                node.children[char] = Trie()
#                node = node.children[char]
#            node.value = value
#            return
#        
#        #Second case, node is not empty
#        #Check the type of the key
#        if type(key) != node.type:
#            raise TypeError
#        
#        #Type of the key are consistent with the Trie. Add the key to the trie
#        for i in range(len(key)):
#            char = key[i:i+1]
#            if char in node.children:
#                node = node.children[char]
#            else:
#                node.children[char] = Trie()
#                node.type = type(char)
#                node = node.children[char]
#        node.value = value
#        return
#
#    def __delitem__(self, key):
#        """
#        Delete the given key from the trie if it exists.
#        """
#        #Check whether key is in the trie
#        try:
#            val = self.__getitem__(key)
#        except:
#            return
#        
#        #Key is in trie
#        node = self
#        for i in range(len(key)):
#            char = key[i:i+1]
#            node = node.children[char]
#        
#        node.value = None
#        return
#
#    def __contains__(self, key):
#        """
#        Return True if key is in the trie and has a value, return False otherwise.
#        """
#        #Check whether key is in the trie
#        try:
#            val = self.__getitem__(key)
#            return True
#        except:
#            return False
#
#    def __iter__(self):
#        """
#        Generator of (key, value) pairs for all keys/values in this trie and
#        its children.  Must be a generator or iterator!
#        """
#        def helper(node, current_word):
#            #End of the branch
#            if len(node.children) == 0 and node.value != None:
#                yield (current_word, node.value)
#            
#            else:
#                #Value of the current node is not Node, yield it
#                if len(node.children) != 0 and node.value != None:
#                    yield (current_word, node.value)
#                
#                #Go along the current branch
#                for char, child in node.children.items():
#                    yield from helper(child, current_word + char)
#             
#        if self.type == tuple:
#            return helper(self, ())
#        
#        return helper(self, '')
#
#def make_word_trie(text):
#    """
#    Given a piece of text as a single string, return a Trie whose keys are the
#    words in the text, and whose values are the number of times the associated
#    word appears in the text
#    """
#    #Create a list of the words in the text
#    word_list = []
#    for sentence in tokenize_sentences(text):
#        word_list.extend(sentence.split(sep = ' '))
#        
#    #Now, by using word_list, create frequency map
#    trie = Trie()
#    for word in word_list:
#        if word not in trie:
#            trie[word] = 1
#        else:
#            trie[word] += 1
#            
#    return trie
#    
#def make_phrase_trie(text):
#    """
#    Given a piece of text as a single string, return a Trie whose keys are the
#    sentences in the text (as tuples of individual words) and whose values are
#    the number of times the associated sentence appears in the text.
#    """
#    #Convert each sentence to a tuple and then by using these tuples create
#    #frequncy map
#    trie = Trie()
#    for sentence in tokenize_sentences(text):
#        sent_tup = tuple(sentence.split(sep = ' '))
#        if sent_tup not in trie:
#            trie[sent_tup] = 1
#        else:
#            trie[sent_tup] += 1
#            
#    return trie
#
#def autocomplete(trie, prefix, max_count=None):
#    """
#    Return the list of the most-frequently occurring elements that start with
#    the given prefix.  Include only the top max_count elements if max_count is
#    specified, otherwise return all.
#
#    Raise a TypeError if the given prefix is of an inappropriate type for the
#    trie.
#    """
#    def sortSecond(val):
#        '''
#        Helper function for sorting of the frequncy list. Returns the second
#        element of the given tuple val
#        '''
#        return val[1]
#    
#    #If the prefix's type isn't consistent with the trie's, raise TypeError
#    if trie.type != type(prefix):
#        raise TypeError
#    
#    #Type of the prefix are consistent with trie's. Create list of words which
#    #starts with the prefix. 
#    node = trie
#    for i in range(len(prefix)):
#        c = prefix[i:i+1]
#        if c in node.children:
#            node = node.children[c]
#        else:
#            return []
#    
#    #Sort the words according to their frequencies from most frequent word
#    #to least frequent
#    l = list(node)
#    l.sort(key = sortSecond, reverse = True)
#    
##    Max_count is not specified. Return whole list
#    if max_count == None:
#        return [prefix + e[0] for e in l]
#
#    #Max_count is specified. Return max_count element    
#    word_list = [prefix + e[0] for e in l[:max_count]]
#    
#    return word_list
#
#def autocorrect(trie, prefix, max_count=None):
#    """
#    Return the list of the most-frequent words that start with prefix or that
#    are valid words that differ from prefix by a small edit.  Include up to
#    max_count elements from the autocompletion.  If autocompletion produces
#    fewer than max_count elements, include the most-frequently-occurring valid
#    edits of the given word as well, up to max_count total elements.
#
#    Do not use a brute-force method that involves generating/looping over
#    all the words in the trie.
#    """
#    raise NotImplementedError
#
#
#def word_filter(trie, pattern):
#    """
#    Return list of (word, freq) for all words in trie that match pattern.
#    pattern is a string, interpreted as explained below:
#         * matches any sequence of zero or more characters,
#         ? matches any single character,
#         otherwise char in pattern char must equal char in word.
#
#    Do not use a brute-force method that involves generating/looping over
#    all the words in the trie.
#    """
#    raise NotImplementedError
#
#
## you can include test cases of your own in the block below.
#if __name__ == '__main__':
#    pass