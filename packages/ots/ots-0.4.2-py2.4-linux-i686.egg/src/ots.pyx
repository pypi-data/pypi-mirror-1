"""
ots
~~~~~~~~~~~~~~~~~~~~
ots bindings for python

"""

__author__ = 'Benjamin Saller <bcsaller@objectrealms.net>'
__docformat__ = 'restructuredtext'
__copyright__ = 'Copyright Benjamin Saller, 2004.'
__license__  = 'The GNU Public License V2+'


cdef extern from "stddef.h":
     ctypedef int size_t

cdef extern from "stdio.h":
    ctypedef struct FILE

cdef extern from "glib.h":
    ctypedef struct GList
    int g_list_length(GList *list)
    void * g_list_nth_data(GList *list, int offset)


cdef extern from "ots/libots.h":
    ctypedef struct OtsArticle:
        GList *lines
        char *title
        int lineCount

    ctypedef struct OtsSentence

    OtsArticle *ots_new_article()

    void ots_free_article(OtsArticle *art)

    char *ots_get_doc_text(OtsArticle *doc, int *out_len)
    char *ots_get_doc_HTML(OtsArticle *doc, int *out_len)

    void ots_parse_file(FILE *stream, OtsArticle *doc)
    void ots_parse_stream(char *utf8, size_t len, OtsArticle *doc)

    void ots_grade_doc(OtsArticle *doc)
    void ots_highlight_doc(OtsArticle *doc, int sumPer)

    void ots_load_xml_dictionary(OtsArticle *doc, char *dictname)

    char * ots_get_line_text(OtsSentence *line, int iffSelected, int *size)
    int ots_is_line_selected(OtsSentence *line)

    char* ots_text_topics(char *text, char *lang_code, int topic_number)
    GList* ots_text_stem_list(char *text, char *lang_code, int topic_number)

cdef extern from "Python.h":
        object PyString_FromStringAndSize(char *s, int len)
        FILE *PyFile_AsFile(object)

cdef class OTS:
    cdef OtsArticle *_article
    cdef int _scored, _score
    cdef object lang
    
    def __new__(self, lang='en', score=20):
        self._article = ots_new_article()
        self._scored = 0
        self.lang = lang
        self._score = score
        ots_load_xml_dictionary(self._article, lang)

    def __dealloc__(self):
        ots_free_article(self._article)

    def score(self):
         if self._scored == 0:
              ots_grade_doc(self._article)
              ots_highlight_doc(self._article, self._score)
              self._scored = 1

    def parse(self, filename, percent=20):
         """parse the content of filename"""
         cdef FILE *stream
         f = open(filename, 'r')
         stream = PyFile_AsFile(f)
         ots_parse_file(stream, self._article)
         f.close()
         self.score()
         
    def parseUnicode(self, data):
         """data should be a utf-8 encoded string or an unicode object
         """
         if type(data) == unicode:
              data = unicode.encode(data, 'utf-8')
         ots_parse_stream(data, len(data), self._article)
         self.score()
         
    def asText(self):
         cdef char *data
         cdef int out_len

         data = ots_get_doc_text(self._article, &out_len)
         return PyString_FromStringAndSize(data, out_len)


    def asHTML(self):
         cdef char *data
         cdef int out_len

         data = ots_get_doc_HTML(self._article, &out_len)
         return PyString_FromStringAndSize(data, out_len)

    def hilite(self):
         cdef OtsSentence *line
         cdef GList *lines
         cdef int length, i, size

         lines = self._article.lines
         length = g_list_length(lines)
         result = []
         for i from 0 <= i < length:
              line = <OtsSentence *> g_list_nth_data(lines, i)
              data = (ots_get_line_text(line, 0, &size),
                      ots_is_line_selected(line))
              # really we want to yield here...
              result.append(data)
         return result

    property title:
         def __get__(self):
              return self._article.title

    property lineCount:
         def __get__(self):
              return self._article.lineCount

    cdef __GListToList(self, GList *gl):
         cdef int length, i, size
         result = []
         length = g_list_length(gl)
         for i from 0 <= i < length:
              data = str(<char*>g_list_nth_data(gl, i)).decode('utf-8')
              result.append(data)
         return result

    def topics(self, topic_num=5):
         cdef int out
         return ots_text_topics(ots_get_doc_text(self._article, &out),
                                self.lang,
                                max(0, topic_num-1)
                                )
    

    def topics_stemmed(self, topic_num=5):
         cdef int out
         return self.__GListToList(ots_text_stem_list(
              ots_get_doc_text(self._article, &out),
              self.lang,
              max(0, topic_num-1))
                                   )
    
    
    def __str__(self):
         return self.asText()
