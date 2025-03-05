// This is the speller exercise from week 5 by Gabriel Ambrosini
// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
} node;

// TODO: Choose number of buckets in hash table
const unsigned int N = 26;

// Hash table
node *table[N];

int wordsindic = 0;

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // TODO
    char *buffer = malloc(sizeof(char) * LENGTH + 1);
    char *textbuffer = malloc(sizeof(char) * LENGTH + 1);
    // Iterates over hashed table
    for (int i = 0; i < N; i++)
    {
        // Iterates over linked list
        for (node *ptr = table[i]; ptr != NULL; ptr = ptr->next)
        {
            /* Turn word from the dictionary and word from the text
            to uppercase so that the we check case-insesitively */
            strcpy(buffer, ptr->word);
            strcpy(textbuffer, word);
            for (int j = 0, k = strlen(buffer); j < k; j++)
            {
                buffer[j] = toupper(buffer[j]);
            }
            for (int j = 0, k = strlen(textbuffer); j < k; j++)
            {
                textbuffer[j] = toupper(textbuffer[j]);
            }
            // Checks to see wether word is in the dictionary
            if (strcmp(textbuffer, buffer) == 0)
            {
                free(buffer);
                free(textbuffer);
                return true;
            }
        }
    }
    free(buffer);
    free(textbuffer);
    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    // TODO: Improve this hash function
    return toupper(word[0]) - 'A';
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    // TODO
    // Open the dictionary file
    FILE *source = fopen(dictionary, "r");
    if (source == NULL)
    {
        return false;
    }

    // Read each word in the file
    char *buffer = malloc(sizeof(char) * LENGTH + 1);
    for (int i = 0; i < N; i++)
    {
        // Makes sure table does not have garbage values
        table[i] = NULL;
    }
    while (fscanf(source, "%s", buffer) != EOF)
    {
        if (buffer == NULL)
        {
            return false;
        }
        // Prepend each word to the hash table
        wordsindic++;
        node *n = malloc(sizeof(node));
        strcpy(n->word, buffer);
        int hashed = hash(buffer);
        n->next = table[hashed];
        table[hashed] = n;
    }

    // Close the dictionary file
    fclose(source);
    free(buffer);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    // TODO
    return wordsindic;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    // TODO
    for (int i = 0; i < N; i++)
    {
        node *ptr = table[i];
        while (ptr != NULL)
        {
            node *tmp = ptr;
            ptr = ptr->next;
            free(tmp);
        }
    }
    return true;
}
