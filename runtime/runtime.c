#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>


void
print_string(char *str) 
{
    printf("%s\n", str);
}

void
print_int(int64_t i)
{
    printf("%" PRId64 "\n", i);
}

static int
runtime_getline(char s[], int lim)
{
    int c, i;

    i = 0;

    while (--lim > 0 && (c = getchar()) != EOF && c != '\n')
    {
        s[i++] = c;
    }

    s[i] = '\0';

    return i;
}

char* 
input_string()
{
    int max = 256;

    char *buffer = (char*) malloc(max);

    if (buffer == NULL) 
    {
        return NULL;
    }

    if (runtime_getline(buffer, max) > 0) 
    {
        return buffer;
    }

    return NULL;
}

int64_t
IO_in_int()
{
    int64_t i;
    scanf("%" SCNd64, &i);
    return i;
}

int64_t
string_length(const char *s)
{
    const char *t;
    int64_t count = 0;

    for (t = s; *s != '\0'; s++)
    {
        count++;
    }

    return count;
}

char*
string_concat(const char *s1, const char *s2)
{
    int64_t len1 = string_length(s1);
    int64_t len2 = string_length(s2);

    char *ret = (char*)malloc(sizeof(char) * (len1 + len2));

    int64_t i;
    for (i = 0; i < len1; i++)
    {
        ret[i] = s1[i];
    }

    for (i = 0; i < len2; i++) 
    {
        ret[len1 + i] = s2[i];
    }
    
    return ret;
}


char*
string_substr(const char *s, int64_t start, int64_t length)
{
    char *ret = (char*)malloc(sizeof(char) * (length + 1));

    if (ret == NULL)
    {
        abort();
    }

    strncpy(ret, &s[start], length);

    ret[length] = '\0';

    return ret;
}

// int main(void) {

//     printf("%s", string_substr("abba", 3, 1));
    
// }
