cdef extern from "stdlib.h":
    ctypedef unsigned long size_t
    void *malloc(int len)
    void free(void *)
    size_t sizeof(void *)

cdef extern from "gl.h":
    ctypedef float GLfloat
    ctypedef float GLclampf
    ctypedef unsigned int GLenum
    ctypedef unsigned int GLbitfield
    ctypedef int GLint
    ctypedef unsigned int GLuint
    ctypedef int GLsizei
    ctypedef double GLdouble
    ctypedef double GLclampd
    ctypedef void GLvoid
    ctypedef short GLushort

    cdef int GL_COLOR_ARRAY
    cdef int GL_EDGE_FLAG_ARRAY
    cdef int GL_INDEX_ARRAY
    cdef int GL_NORMAL_ARRAY
    cdef int GL_TEXTURE_COORD_ARRAY
    cdef int GL_VERTEX_ARRAY
    cdef int GL_FLOAT
    cdef int GL_TEXTURE_2D
    cdef int GL_QUADS

    
    cdef void glEnable(GLenum cap)
    cdef void glVertexPointer(GLint size, GLenum type, GLsizei stride, GLvoid *pointer)
    cdef void glColorPointer(GLint size, GLenum type, GLsizei stride, GLvoid *pointer)
    cdef void glTexCoordPointer(GLint size, GLenum type, GLsizei stride, GLvoid *pointer)
    cdef void glEnableClientState(GLenum array)
    cdef void glDisableClientState(GLenum array)
    cdef void glDrawArrays(GLenum mode, GLint first, GLsizei count)
    cdef void glBindTexture(GLenum target, GLuint texture)


cdef class Array:
    cdef readonly int height
    cdef readonly int width
    cdef int size
    cdef float *array

    def __new__(self, int width, int height):
        cdef float f
        self.height = height
        self.width = width
        self.size = width * height
        self.array = <float*>malloc(self.size * sizeof(f))
        for i from 0 <= i < self.size:
            self.array[i] = 0.0

    def copy(self):
        cdef Array array
        array = Array(self.width, self.height)
        for i from 0 <= i < self.size:
            array.array[i] = self.array[i]
        return array

    def zero(self):
        for i from 0 <= i < self.size:
            self.array[i] = 0.0

    def init(self, seq):
        seq = tuple(seq)
        if(len(seq) != self.width):
            raise TypeError('len(seq) must be %d'%self.width)
        for i from 0 <= i < self.height:
            i = i * self.width
            for x from i <= x < i + self.width:
                self.array[x] = seq[x-i]

    def __repr__(self):
        s = ""
        for i from 0 <= i < self.height:
            i = i * self.width
            r = ""
            for x from 0 <= x < self.width:
                r = r + "%f "%self.array[i+x]
            s = s +  " (" + r[:-1] + ")\n"
        return "[" + s[1:-1] + "]"
            
    def __getitem__(self, int i):
        i = i * self.width
        r = []
        if i >= self.size or i < 0:
            raise IndexError
        for x from i <= x < i + self.width:
            r.append(self.array[x])
        return r

    def __setitem__(self, int i, seq):
        seq = tuple(seq)
        if(len(seq) != self.width):
            raise TypeError('len(seq) must be %d'%self.width)
        i = i * self.width
        if i >= self.size or i < 0:
            raise IndexError
        for x from i <= x < i + self.width:
            self.array[x] = seq[x-i]

    def __dealloc__(self):
        free(self.array)

    def __iadd__(Array self, Array other):
        if self.size != other.size:
            raise TypeError('Array size mismatch')
        for i from 0 <= i < self.size:
            self.array[i] = self.array[i] + other.array[i]
        return self

    def __isub__(Array self, Array other):
        if self.size != other.size:
            raise TypeError('Array size mismatch')
        for i from 0 <= i < self.size:
            self.array[i] = self.array[i] - other.array[i]
        return self

    def __imul__(Array self, float scalar):
        if self.size != other.size:
            raise TypeError('Array size mismatch')
        for i from 0 <= i < self.size:
            self.array[i] = self.array[i] * scalar
        return self

    def __idiv__(Array self, float scalar):
        if self.size != other.size:
            raise TypeError('Array size mismatch')
        for i from 0 <= i < self.size:
            self.array[i] = self.array[i] / scalar
        return self

    def __len__(self):
        return self.height


def quads(count):
    """
    Returns vertices, colors, texture_coods for count quads.
    """
    return Array(2,count*4), Array(4, count*4), Array(2, count*4)


def draw(Array vertices, Array colors=None, Array texture_coords=None, texture_id=0):
    """
    Draws an array of vertices (as quads) using colors, texture coords and texture.
    """
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, vertices.array)
    cdef int vertexcount
    vertexcount = vertices.size / 2
    if colors is not None:
        if colors.width * vertexcount != colors.size:
            raise TypeError('Color Array size mismatch')
        glEnableClientState(GL_COLOR_ARRAY)
        glColorPointer(colors.width, GL_FLOAT, 0, colors.array)
    if texture_coords is not None:
        if 2 * vertexcount != texture_coords.size:
            raise TypeError('Texture Array size mismatch')
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glTexCoordPointer(2, GL_FLOAT, 0, texture_coords.array)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
    glDrawArrays(GL_QUADS, 0, vertexcount)
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
