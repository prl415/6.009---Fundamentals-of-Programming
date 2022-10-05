# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 19:55:38 2020

@author: Mustafa
"""

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
        
    alphabet = "abcdefghijklmnopqrstuvwxyz"
     
    #Get the words which start with prefix
    word_list = autocomplete(trie, prefix, max_count=None)
    
    #number of words found is lower than max_count. By using valid edits
    #find additional (max_count - len(word_list)) words
    while len(word_list) < max_count:
        
        #A single character addition
        for c in alphabet:
            for i in range(len(prefix),-1, -1):
                new_prefix = prefix[:i] + c + prefix[i:]
                word_list.extend(autocomplete(trie, new_prefix, max_count - len(word_list)))
                word_list = list(set(word_list))
                if len(word_list) == max_count:
                    return word_list
                
        #A single character deletion
        for i in range(len(prefix)-1,-1,-1):
            new_prefix = prefix[:i] + prefix[i+1:]
            word_list.extend(autocomplete(trie, new_prefix, max_count - len(word_list)))
            word_list = list(set(word_list))
            if len(word_list) == max_count:
                return word_list
            
        #A single character replacement
        for i in range(len(prefix)-1,-1,-1):
            for c in alphabet:
                new_prefix = prefix[:i] + prefix[i+1:]
                word_list.extend(autocomplete(trie, new_prefix, max_count - len(word_list)))
                word_list = list(set(word_list))
                if len(word_list) == max_count:
                    return word_list