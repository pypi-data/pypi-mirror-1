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

    cdef int GL_CW
    cdef int GL_ONE
    cdef int GL_SMOOTH
    cdef int GL_LINE_SMOOTH
    cdef int GL_BACK
    cdef int GL_COLOR_BUFFER_BIT
    cdef int GL_BLEND
    cdef int GL_SRC_ALPHA
    cdef int GL_ONE_MINUS_SRC_ALPHA
    cdef int GL_TEXTURE_2D
    cdef int GL_QUADS
    cdef int GL_MODELVIEW
    cdef int GL_LINE_STRIP
    cdef int GL_RGBA
    cdef int GL_RGB
    cdef int GL_NEAREST
    cdef int GL_LINEAR
    cdef int GL_TEXTURE_MAG_FILTER
    cdef int GL_TEXTURE_MIN_FILTER
    cdef int GL_LINEAR_MIPMAP_NEAREST
    cdef int GL_UNSIGNED_BYTE
    cdef int GL_PROJECTION
    cdef int GL_FLAT
    cdef int GL_MODELVIEW_MATRIX
    cdef int GL_PROJECTION_MATRIX
    cdef int GL_VIEWPORT
    cdef int GL_COMPILE
    cdef int GL_LINE_STIPPLE
    cdef int GL_NO_ERROR

    
    cdef void glTranslatef(GLfloat x, GLfloat y, GLfloat z)
    cdef void glEnable(GLenum cap)
    cdef void glClear(GLbitfield mask)
    cdef void glFrontFace(GLenum mode)
    cdef void glShadeModel(GLenum mode)
    cdef void glCullFace(GLenum mode)
    cdef void glClearColor(GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha)
    cdef void glBlendFunc(GLenum sfactor, GLenum dfactor)
    cdef void glRotatef(GLfloat angle, GLfloat x, GLfloat y, GLfloat z)
    cdef void glScalef(GLfloat x, GLfloat y, GLfloat z)
    cdef void glBindTexture(GLenum target, GLuint texture)
    cdef void glColor4f(GLfloat red, GLfloat green, GLfloat blue, GLfloat alpha)
    cdef void glBegin(GLenum mode)
    cdef void glNormal3f(GLfloat nx, GLfloat ny, GLfloat nz)
    cdef void glTexCoord2f(GLfloat s, GLfloat t)
    cdef void glVertex3f(GLfloat x, GLfloat y, GLfloat z)
    cdef void glVertex2f(GLfloat x, GLfloat y)
    cdef void glEnd()
    cdef void glViewport(GLint x, GLint y, GLsizei width, GLsizei height)
    cdef void glOrtho(GLint bottom, GLint left, GLint top, GLint bottom, GLint front, GLint back)
    cdef void glMatrixMode(GLenum mode)
    cdef void glLoadIdentity()
    cdef void glTexParameteri(GLenum target, GLenum pname, GLint param)
    cdef void glTexImage2D(GLenum target, GLint level, GLint internalformat, GLsizei width, GLsizei height, GLint border, GLenum format, GLenum type, GLvoid *pixels)
    cdef void glGenTextures(GLsizei n, GLuint *textures)
    cdef void glDeleteTextures(GLsizei n, GLuint *textures)
    cdef void glLineWidth(GLfloat width)
    cdef void glPushMatrix()
    cdef void glPopMatrix()
    cdef void glGetDoublev(GLenum pname, GLdouble *params)
    cdef void glGetIntegerv(GLenum pname, GLint *params)
    cdef GLuint glGenLists(GLsizei range)
    cdef void glNewList(GLuint list, GLenum mode)
    cdef void glDeleteLists (GLuint list, GLsizei range)
    cdef void glCallList(GLuint list)
    cdef void glEndList()
    cdef void glLineStipple(GLint factor, GLushort pattern)
    cdef GLenum glGetError()



cdef extern from "glu.h":
    cdef GLint gluBuild2DMipmaps( GLenum target, GLint internalFormat, GLsizei width, GLsizei height, GLenum format, GLenum type, void *data)
    cdef GLint gluUnProject (GLdouble winX, GLdouble winY, GLdouble winZ, GLdouble *model, GLdouble *proj, GLint *view, GLdouble* objX, GLdouble* objY, GLdouble* objZ)

class GLException(Exception): pass

def check_error():
    e = glGetError()
    if e != GL_NO_ERROR:
        raise GLException('GL_ERROR %s' % e)

def compile_list(func, *args, **kw):
    """
    Compile a function into an OpenGL display list.
    """
    cdef GLuint list_id
    list_id = glGenLists(1)
    glNewList(list_id, GL_COMPILE)
    func(*args, **kw)
    glEndList()
    return list_id


def execute_list(list_id):
    """
    Execute a display list.
    """
    glCallList(list_id)
    

def delete_list(list_id):
    """
    Delete a display list.
    """
    glDeleteLists(list_id, 1)


def world_coords(screen_coords):
    """
    Turn screen coordinates into world coordinates, using the current 
    transformation matrix.
    """
    cdef GLdouble modelview_matrix[16]
    cdef GLdouble projection_matrix[16]
    cdef GLint viewport[4]
    cdef GLdouble ox, oy, oz
    cdef x
    cdef y
    x,y = screen_coords
    glGetDoublev(GL_MODELVIEW_MATRIX, modelview_matrix)
    glGetDoublev(GL_PROJECTION_MATRIX, projection_matrix)
    glGetIntegerv(GL_VIEWPORT, viewport)
    y = viewport[3] - y
    gluUnProject(x, y, 0, modelview_matrix, projection_matrix, viewport, &ox, &oy, &oz)
    return float(ox), float(oy)
    

def enable_blend(additive=False):
    """
    Enable transparency using alpha channel of textures.
    If additive=True, use additive blending.
    """
    glEnable(GL_BLEND)
    if additive:
        glBlendFunc(GL_SRC_ALPHA,GL_ONE)
    else:
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

    
def clear(rgba=(0.0,0.0,0.0,1.0)):
    """
    Clear the screen to a background color.
    """
    glClearColor(rgba[0], rgba[1], rgba[2], rgba[3])
    glClear(GL_COLOR_BUFFER_BIT)


def push_transform():
    """
    Push the transformation matrix onto the stack.
    """
    glPushMatrix()


def pop_transform():
    """
    Restore the tranformation matrix from the stack.
    """
    glPopMatrix()


def reset_transform():
    """
    Reset the global transformation matrix.
    """
    glLoadIdentity()

        
def transform(translate=(0.0,0.0), angle=0.0, scale=(1.0,1.0)):
    """
    Change the global transformation matrix.
    """
    glTranslatef(translate[0],translate[1],0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)
    glScalef(scale[0], scale[1], 1.0)


def draw_quad(translate, vertices, texture_id=0, rgba=(1.0,1.0,1.0,1.0), texture_coords=((0.0,1.0),(0.0,0.0),(1.0,0.0),(1.0,1.0)), angle=0.0, scale=(1.0,1.0)):
    """
    Draw a quad from 4 points stored in a clockwise direction.
    Optional texture coords, texture_id and color can be used.
    """
    glPushMatrix()
    glTranslatef(translate[0],translate[1],0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)
    glScalef(scale[0], scale[1], 1.0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor4f(rgba[0], rgba[1], rgba[2], rgba[3])
    v = vertices
    t = texture_coords
    glBegin(GL_QUADS)
    glTexCoord2f(t[0][0],t[0][1])
    glVertex2f(v[0][0],v[0][1])
    glTexCoord2f(t[1][0],t[1][1])
    glVertex2f(v[1][0],v[1][1])
    glTexCoord2f(t[2][0],t[2][1])
    glVertex2f(v[2][0],v[2][1])
    glTexCoord2f(t[3][0],t[3][1])
    glVertex2f(v[3][0],v[3][1])
    glEnd()
    glPopMatrix()


def tween(translate, vertices, texture_ids, percentage, texture_coords=((0.0,1.0),(0.0,0.0),(1.0,0.0),(1.0,1.0)), angle=0.0, scale=(1.0,1.0)):
    """
    Draw a quad, crossfading between two textures.
    """
    alphas = 1.0 - percentage, percentage
    glPushMatrix()
    glTranslatef(translate[0],translate[1],0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)
    glScalef(scale[0], scale[1], 1.0)
    glEnable(GL_TEXTURE_2D)
    v = vertices
    t = texture_coords
    glBindTexture(GL_TEXTURE_2D, texture_ids[0])
    glBegin(GL_QUADS)
    glColor4f(1.0,1.0,1.0,alphas[0])
    glTexCoord2f(t[0][0],t[0][1])
    glVertex2f(v[0][0],v[0][1])
    glTexCoord2f(t[1][0],t[1][1])
    glVertex2f(v[1][0],v[1][1])
    glTexCoord2f(t[2][0],t[2][1])
    glVertex2f(v[2][0],v[2][1])
    glTexCoord2f(t[3][0],t[3][1])
    glVertex2f(v[3][0],v[3][1])
    glEnd()
    glBindTexture(GL_TEXTURE_2D, texture_ids[1])
    glBegin(GL_QUADS)
    glColor4f(1.0,1.0,1.0,alphas[1])
    glTexCoord2f(t[0][0],t[0][1])
    glVertex2f(v[0][0],v[0][1])
    glTexCoord2f(t[1][0],t[1][1])
    glVertex2f(v[1][0],v[1][1])
    glTexCoord2f(t[2][0],t[2][1])
    glVertex2f(v[2][0],v[2][1])
    glTexCoord2f(t[3][0],t[3][1])
    glVertex2f(v[3][0],v[3][1])
    glEnd()
    glPopMatrix()


def draw_line(translate, points, rgba=(1.0,1.0,1.0,1.0), width=1.0, angle=0.0, scale=(1.0,1.0), pattern=0xFFFF, factor=0):
    """
    Draw a line or line strip through points.
    """
    glLineStipple(factor, pattern)
    glPushMatrix()
    glTranslatef(translate[0],translate[1],0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)
    glScalef(scale[0], scale[1], 1.0)
    glBindTexture(GL_TEXTURE_2D, 0)
    glLineWidth(width)
    glColor4f(rgba[0], rgba[1], rgba[2], rgba[3])
    glBegin(GL_LINE_STRIP)
    for p in points:
        glVertex2f(p[0], p[1])
    glEnd()
    glPopMatrix()


def init(screen_size):
    """
    Set an area on the screen for current drawing operations.
    """
    width, height = screen_size
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, 0, height, 0, 1)          
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glFrontFace(GL_CW)
    glShadeModel(GL_FLAT)
    glCullFace(GL_BACK)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_LINE_STIPPLE)
    enable_blend()


def load_texture(byte_string, size, type='RGBA', filter=True, mipmap=True):
    """
    Load a texture and return it. 
    """
    cdef GLuint textures[1]
    cdef GLuint id
    glGenTextures(1, textures)
    id = textures[0] 
    update_texture(id, byte_string, size, type, filter, mipmap)
    return id


def update_texture(texture_id, byte_string, size, type='RGBA', filter=True, mipmap=True):
    """
    Update a texture with a different byte_string.
    """
    cdef char *data
    data = byte_string
    if type == 'RGBA':
        ptype = GL_RGBA
        channels = 4
    elif type == 'RGB':
        ptype = GL_RGB
        channels = 3
    else:
        raise ValueError('type must be "RGBA" or "RGB"')

    if size[0]*size[1]*channels != len(byte_string):
        raise ValueError('byte_string is an unexpected size.')
        
    filter_type = GL_NEAREST
    if filter: filter_type = GL_LINEAR
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter_type)
    if mipmap:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
        gluBuild2DMipmaps(GL_TEXTURE_2D, channels, size[0], size[1], ptype, GL_UNSIGNED_BYTE, data)
    else:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter_type)
        glTexImage2D(GL_TEXTURE_2D, 0, ptype, size[0], size[1], 0, ptype, GL_UNSIGNED_BYTE, data)


def unload_texture(texture_id):
    """
    Unload a texture from memory.
    """
    cdef GLuint textures[1]
    textures[0] = texture_id
    glDeleteTextures(1, textures)

