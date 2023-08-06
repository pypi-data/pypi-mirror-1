#!-*- coding:utf-8 -*-

#The MIT License
#
#Copyright (c) 2008 rubyu (http://d.hatena.ne.jp/ruby-U/)
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import types
import copy
import re
import colors


def escapeSC(s):
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    s = s.replace('"', '&quot;')
    s = s.replace("'", '&#39;')
    return s

output = ''

class Scanner:
    def set(self, obj):
        self.buffer = obj
        self.bufferLen = len(obj)
        self.line = 0
        self.yyl = []
    def get(self):
        PERIOD   = u'。'
        COMMA    = u'、'
        SCREAMER = u'！'
        COLON    = u'：'
        MDOT     = u'・'
        
        if 0 == len(self.yyl):
            if self.bufferLen <= self.line:
                return [0, ['', 0]]
            isLine  = True
            str     = self.buffer[self.line]
            strLen  = len(str)
            hOffset = 0
            self.line += 1
            if   0 == strLen:
                pass
            elif 1 == strLen:
                if   str == PERIOD:
                    return [RIGHT_QUOTE, ['', self.line]]
                elif str == COMMA:
                    return [EB_BOTH,     ['', self.line]] #ERROR
                elif str == COLON:
                    return [PROPERTY,    ['', self.line]] #ERROR
            else:
                if   str.startswith(PERIOD + COMMA):
                    isLine = False
                    hOffset = 2
                    self.yyl.append( [EB_RIGHT, ['', self.line]] )
                elif str.startswith(PERIOD + PERIOD):
                    isLine = False
                    hOffset = 2
                    self.yyl.append( [EB_NONE,  ['', self.line]] )
                elif str.startswith(PERIOD):
                    isLine = False
                    hOffset = 1
                    self.yyl.append( [EB_NONE,  ['', self.line]] )
                
                elif str.startswith(COMMA + PERIOD):
                    isLine = False
                    hOffset = 2
                    self.yyl.append( [EB_LEFT,  ['', self.line]] )
                elif str.startswith(COMMA + COMMA):
                    isLine = False
                    hOffset = 2
                    self.yyl.append( [EB_BOTH,  ['', self.line]] )
                elif str.startswith(COMMA):
                    isLine = False
                    hOffset = 1
                    self.yyl.append( [EB_BOTH,  ['', self.line]] )
                
                elif str.startswith(SCREAMER + MDOT + SCREAMER):
                    return self.get()
                elif str.startswith(SCREAMER + PERIOD):
                    hOffset = 1
                elif str.startswith(SCREAMER + COMMA):
                    hOffset = 1
                elif str.startswith(SCREAMER + COLON):
                    hOffset = 1
                
                elif str.startswith(COLON):
                    isLine = False
                    hOffset = 1
                    self.yyl.append( [PROPERTY, ['', self.line]] )
            
            if isLine:
                if 0 != hOffset:
                    str = str[hOffset:]
                return [LINE, [str, self.line]]
            else:
                if 0 < strLen - hOffset:
                    if   str.endswith(PERIOD):
                        self.yyl.append( [IDENTIFIER, [str[hOffset : strLen - 1], self.line]] )
                        self.yyl.append( [NOVALUE,    ['', self.line]] )
                    elif str.endswith(COMMA):
                        self.yyl.append( [IDENTIFIER, [str[hOffset : strLen - 1], self.line]] )
                        self.yyl.append( [LEFT_QUOTE, ['', self.line]] )
                    else:
                        self.yyl.append( [IDENTIFIER, [str[hOffset :],            self.line]] )
            return self.yyl.pop(0)
        else:
            return self.yyl.pop(0)
    #get end
scanner = Scanner()

def yylex():
    ret = scanner.get()
    global yylval
    yylval = ret[1]
    return ret[0]

error = None

def yyerror(msg):
    global error
    error = {}
    error['line']    = scanner.line
    error['msg']     = msg
    error['linestr'] = scanner.buffer[scanner.line - 1]

class TAG:
    def __init__(self):
        self.property = {}
        self.property['id']  = None
        self.property['cls'] = None
        self.property['style'] = {}
        self.child = []
        self.splitPattern = u'、'

        
    def setChild(self, child):
        if types.ListType is type(child):
            self.child   = child
            self.endline = child[len(child) - 1].endline
        
    def _splitMultiDim(self, pattern):
        x = 0
        y = 0
        md = []
        md.append( [] )
        md[x].append( [] )
        for c in self.child:
            if   3 == c.type:
                ret = c._splitMultiDim(pattern)
                rowCount = len(ret)
                for j in xrange(rowCount):
                    ret_row = ret[j]
                    colCount = len(ret_row)
                    for k in xrange(colCount):
                        if 0 < k:
                            y += 1
                            md[x].append( [] )
                        ret_col = ret_row[k]
                        itemCount = len(ret_col)
                        if 0 < itemCount:
                            t = copy.copy(c)
                            t.child = []
                            for l in xrange(itemCount):
                                t.child.append(ret_col[l])
                            md[x][y].append(t)
                    if j < rowCount - 1:
                        x += 1
                        md.append( [] )
                        y = 0
                        md[x].append( [] )
                         
            elif 1 == c.type:
                ret = c._splitMultiDim(pattern)
                rowCount = len(ret)
                for j in xrange(rowCount):
                    ret_row = ret[j]
                    colCount = len(ret_row)
                    for k in xrange(colCount):
                        if 0 < k:
                            y += 1
                            md[x].append( [] )
                        ret_col = ret_row[k]
                        itemCount = len(ret_col)
                        if 0 < itemCount:
                            t = copy.copy(c)
                            t.child = []
                            t.hasBreak = False
                            for l in xrange(itemCount):
                                t.child.append(ret_col[l])
                            md[x][y].append(t)
                    if j < rowCount - 1:
                        x += 1
                        md.append( [] )
                        y = 0
                        md[x].append( [] )
                    else:
                        if c.hasBreak:
                            x += 1
                            md.append( [] )
                            y = 0
                            md[x].append( [] )
                            
            else:
                md[x][y].append(c)
                if c.hasBreak:
                    x += 1
                    md.append( [] )
                    y = 0
                    md[x].append( [] )
        
        return md
    
    def splitMultiDim(self):
        md = self._splitMultiDim(self.splitPattern)
        x = len(md) - 1
        y = len(md[x]) - 1
        if 0 == len(md[x][y]):
            md[x].pop()
        if 0 == len(md[x]):
            md.pop()
        return md
    
    def html(self):
        self._erasebreakPropagate(False)
        return self._html()
    
    def _html(self):
        arr = []
        arr.append( '<' )
        arr.append( self.name )
        arr.append( self.getProperties() )
        arr.append( '>' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</' )
        arr.append( self.name )
        arr.append( '>' )
        return ''.join(arr)
    
    def addProperty(self, prop):
        for key in prop:
            if   u'背景'  == key:
                color = colors.getColorCode(prop[key])
                self.property['style']['background-color'] = color
            elif u'区切り' == key:
                self.splitPattern = prop[key]
            elif u'場所'  == key:
                self.property['url'] = prop[key]
            elif u'名前'  == key:
                id = prop[key]
                if not re.search('^sr_', id):
                    self.property['id'] = id
            elif u'クラス' == key:
                cls = prop[key]
                if not re.search('^sr_', cls):
                    self.property['cls'] = cls
    
    def getProperties(self):
        arr = []
        id    = self.property['id']
        cls   = self.property['cls']
        style = self.property['style']
        if cls:
            arr.append( ' class="' )
            arr.append( escapeSC(cls) )
            arr.append( '"' )
        if id:
            arr.append( ' id="' )
            arr.append( escapeSC(id) )
            arr.append( '"' )
        sArr = []
        for name in sorted( style.keys() ):
            sArr.append( name )
            sArr.append( ':' )
            sArr.append( style[name] )
            sArr.append( ';' )
        if 0 < len(sArr):
            arr.append( ' style="' )
            arr.append( ''.join(sArr) )
            arr.append( '"' )
        return ''.join(arr)

class TAG_INLINE(TAG):
    def __init__(self):
        TAG.__init__(self)
        self.type = 3 #INLINE
    
    def _erasebreakPropagate(self, erase):
        signal = erase or  (2 == self.prefix) or (3 == self.prefix) #erase or RIGHT or BOTH
        self.hasBreak = not signal
        for i in xrange(len(self.child) - 1, -1, -1):
            signal = self.child[i]._erasebreakPropagate(signal)
        signal = signal or (1 == self.prefix) or (3 == self.prefix) #signal or LEFT or BOTH
        return signal

class TAG_BLOCK(TAG):
    def __init__(self):
        TAG.__init__(self)
        self.type = 2 #BLOCK
    
    def _erasebreakPropagate(self, erase):
        signal = (2 == self.prefix) or (3 == self.prefix) #RIGHT or BOTH
        self.hasBreak = not(erase or signal)
        for i in xrange(len(self.child) - 1, -1, -1):
            signal = self.child[i]._erasebreakPropagate(signal)
        signal = (1 == self.prefix) or (3 == self.prefix) #LEFT or BOTH
        return signal

class TAG_INLINEBLOCK(TAG):
    def __init__(self):
        TAG.__init__(self)
        self.type = 4 #INLINEBLOCK
    
    def _erasebreakPropagate(self, erase):
        signal = erase or (2 == self.prefix) or (3 == self.prefix) #erase or RIGHT or BOTH
        self.hasBreak = not signal
        for i in xrange(len(self.child) - 1, -1, -1):
            signal = self.child[i]._erasebreakPropagate(signal)
        signal = (1 == self.prefix) or (3 == self.prefix) #LEFT or BOTH
        return signal

class TAG_LINE(TAG):
    def __init__(self):
        TAG.__init__(self)
        self.type = 1 #LINE
        self.prefix = 4 #NONE
        
    def _erasebreakPropagate(self, erase):
        signal = erase or (2 == self.prefix) or (3 == self.prefix) #erase or RIGHT or BOTH
        self.hasBreak = not signal
        signal = (1 == self.prefix) or (3 == self.prefix) #LEFT or BOTH
        return signal

    def _splitMultiDim(self, pattern):
        x = 0
        y = 0
        md = []
        md.append( [] )
        s = self.child[0].split(pattern)
        for i in xrange( len(s) ):
            md[0].append( [] )
            md[0][i].append( s[i] )
        return md
    
    def _html(self):
        str = self.child[0]
        arr = []
        if 0 < len(str):
            arr.append( '<span class="sr_line" id="sr_' )
            arr.append( `self.startline` )
            arr.append( '">' )
            arr.append( escapeSC(str) )
            arr.append( '</span>' )
        if self.hasBreak:
            arr.append( '<br />' )
        return ''.join(arr)

class TAG_BLOCK_CENTER(TAG_BLOCK):
    def __init__(self):
        TAG_BLOCK.__init__(self)
        self.name = 'center'
    
    def _html(self):
        arr = []
        arr.append( '<div' )
        arr.append( self.getProperties() )
        arr.append( ' align="center">' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</div>' )
        return ''.join(arr)

class TAG_BLOCK_LEFT(TAG_BLOCK):
    def __init__(self):
        TAG_BLOCK.__init__(self)
        self.name = 'left'
    
    def _html(self):
        arr = []
        arr.append( '<div' )
        arr.append( self.getProperties() )
        arr.append( ' align="left">' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</div>' )
        return ''.join(arr)

class TAG_BLOCK_RIGHT(TAG_BLOCK):
    def __init__(self):
        TAG_BLOCK.__init__(self)
        self.name = 'right'
    
    def _html(self):
        arr = []
        arr.append( '<div' )
        arr.append( self.getProperties() )
        arr.append( ' align="right">' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</div>' )
        return ''.join(arr)

class TAG_BLOCK_HR(TAG_BLOCK):
    def __init__(self):
        TAG_BLOCK.__init__(self)
        self.name = 'hr'
    
    def _html(self):
        return ''.join( ['<hr', self.getProperties(), ' />'] )

class TAG_INLINE_OVERLINE(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'overline'

    def _html(self):
        self.property['style']['text-decoration'] = 'overline'
        arr = []
        arr.append( '<span' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</span>' )
        return ''.join( arr )

class TAG_INLINE_MIDDLELINE(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'middleline'

    def _html(self):
        self.property['style']['text-decoration'] = 'line-through'
        arr = []
        arr.append( '<span' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</span>' )
        return ''.join( arr )

class TAG_INLINE_UNDERLINE(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'underline'

    def _html(self):
        self.property['style']['text-decoration'] = 'underline'
        arr = []
        arr.append( '<span' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</span>' )
        return ''.join( arr )

class TAG_INLINE_A(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'a'
        self.property['url'] = ''
        
    def _html(self):
        arr = []
        url = escapeSC( self.property['url'] )
        if not( url.startswith('http') or url.startswith('ftp') ):
            url = '#' + url
        arr.append( '<a href="' )
        arr.append( url )
        arr.append( '"' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</a>' )
        return ''.join( arr )

class TAG_BLOCK_TABLE(TAG_BLOCK):
    def __init__(self):
        TAG_BLOCK.__init__(self)
        self.name = 'table'

    def _html(self):
        arr = []
        arr.append( '<table' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        ret = self.splitMultiDim()
        for row in ret:
            arr.append( '<tr>' )
            for col in row:
                arr.append( '<td>' )
                for item in col:
                    arr.append( item._html() )
                arr.append( '</td>' )
            arr.append( '</tr>' )
        arr.append( '</table>' )
        return ''.join( arr )

class TAG_BLOCK_UL(TAG_BLOCK):
    def __init__(self):
        TAG_BLOCK.__init__(self)
        self.name = 'ul'

    def _html(self):
        arr = []
        arr.append( '<ul' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        ret = self.splitMultiDim()
        for row in ret:
            arr.append( '<li>' )
            firstCol = row[0]
            for item in firstCol:
                arr.append( item._html() )
            arr.append( '</li>' )
        arr.append( '</ul>' )
        return ''.join( arr )

class TAG_BLOCK_OL(TAG_BLOCK):
    def __init__(self):
        TAG_BLOCK.__init__(self)
        self.name = 'ol'

    def _html(self):
        arr = []
        arr.append( '<ol' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        ret = self.splitMultiDim()
        for row in ret:
            arr.append( '<li>' )
            firstCol = row[0]
            for item in firstCol:
                arr.append( item._html() )
            arr.append( '</li>' )
        arr.append( '</ol>' )
        return ''.join( arr )

class TAG_BLOCK_DL(TAG_BLOCK):
    def __init__(self):
        TAG_BLOCK.__init__(self)
        self.name = 'dl'

    def _html(self):
        arr = []
        arr.append( '<dl' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        ret = self.splitMultiDim()
        for row in ret:
            length = len(row)
            if 1 == length:
                arr.append( '<dt>' )
                col = row[0]
                for item in col:
                    arr.append( item._html() )
                arr.append( '</dt><dd></dd>' )
            if 2 <= length:
                arr.append( '<dt>' )
                col = row[0]
                for item in col:
                    arr.append( item._html() )
                arr.append( '</dt><dt>' )
                col = row[1]
                for item in col:
                    arr.append( item._html() )
                arr.append( '</dt>' )
        arr.append( '</dl>' )
        return ''.join( arr )

class TAG_INLINEBLOCK_RUBY(TAG_INLINEBLOCK):
    def __init__(self):
        TAG_INLINEBLOCK.__init__(self)
        self.name = 'ruby'

    def _html(self):
        arr = []
        ret = self.splitMultiDim()
        firstRow = ret[0]
        length = len(firstRow)
        if   0 == length:
            rb = []
            rt = []
        elif 1 == length:
            rb = firstRow[0]
            rt = []
        else:
            rb = firstRow[0]
            rt = firstRow[1]
        arr.append( '<ruby' )
        arr.append( self.getProperties() )
        arr.append( '><rb>' )
        for c in rb:
            arr.append( c._html() )
        arr.append( '</rb><rp>(</rp><rt>' )
        for c in rt:
            arr.append( c._html() )
        arr.append( '</rt><rp>)</rp></ruby>' )
        if self.hasBreak:
            arr.append( '<br />' ) #because INLINEBLOCK
        return ''.join( arr )

class TAG_BLOCK_ROOT(TAG_BLOCK):
    def __init__(self):
        TAG_BLOCK.__init__(self)
        self.name = 'root'
        self.prefix = 4 #NONE
        
    def _html(self):
        self.property['id'] = 'sr_root'
        self.property['style']['font-size'] = 'medium'
        arr = []
        arr.append( '<div' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</div>' )
        return ''.join( arr )

class TAG_BLOCK_UNKNOWN(TAG_BLOCK):
    def __init__(self):
        TAG_BLOCK.__init__(self)
        self.name = 'unknown'

    def _html(self):
        self.property['cls'] = 'sr_unknown'
        arr = []
        arr.append( '<span' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</span>' )
        return ''.join( arr )

class TAG_INLINE_SIZE(TAG_INLINE):
    def _html(self):
        self.property['style']['font-size'] = `self.size` + '%'
        arr = []
        arr.append( '<span' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</span>' )
        return ''.join(arr)

class TAG_INLINE_SIZE_MULTI(TAG_INLINE_SIZE):
    def __init__(self):
        TAG_INLINE_SIZE.__init__(self)
        self.name = 'size_multi'

class TAG_INLINE_SIZE_PLUS(TAG_INLINE_SIZE):
    def __init__(self):
        TAG_INLINE_SIZE.__init__(self)
        self.name = 'size_plus'

class TAG_INLINE_SIZE_MINUS(TAG_INLINE_SIZE):
    def __init__(self):
        TAG_INLINE_SIZE.__init__(self)
        self.name = 'size_minus'

class TAG_INLINE_SIZEIS(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'size_is'
        
    def _html(self):
        self.property['style']['font-size'] = `self.size` + '%'
        arr = []
        arr.append( '<span style="font-size:medium;"><span' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</span></span>' )
        return ''.join(arr)

class TAG_INLINE_COLOR(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'color'
    
    def _html(self):
        self.property['style']['color'] = self.color
        arr = []
        arr.append( '<span' )
        arr.append( self.getProperties() )
        arr.append( '>' )
        for c in self.child:
            arr.append( c._html() )
        arr.append( '</span>' )
        return ''.join(arr)

class TAG_INLINE_I(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'i'

class TAG_INLINE_B(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'b'

class TAG_INLINE_BIG(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'big'

class TAG_INLINE_SMALL(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'small'

class TAG_INLINE_SUB(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'sub'

class TAG_INLINE_SUP(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'sup'

class TAG_INLINE_TT(TAG_INLINE):
    def __init__(self):
        TAG_INLINE.__init__(self)
        self.name = 'tt'

class TagFactory:
    def __init__(self):
        self.tags = {
            u'中央':     TAG_BLOCK_CENTER,
            u'左':       TAG_BLOCK_LEFT,
            u'右':       TAG_BLOCK_RIGHT,
            u'斜体':     TAG_INLINE_I,
            u'太字':     TAG_INLINE_B,
            u'大':       TAG_INLINE_BIG,
            u'小':       TAG_INLINE_SMALL,
            u'下':       TAG_INLINE_SUB,
            u'上':       TAG_INLINE_SUP,
            u'等幅':     TAG_INLINE_TT,
            u'水平':     TAG_BLOCK_HR,
            u'上線':     TAG_INLINE_OVERLINE,
            u'中線':     TAG_INLINE_MIDDLELINE,
            u'打ち消し':  TAG_INLINE_MIDDLELINE,
            u'下線':     TAG_INLINE_UNDERLINE,
            u'表':       TAG_BLOCK_TABLE,
            u'りすと':     TAG_BLOCK_UL,
            u'リスト':     TAG_BLOCK_UL,
            u'順序りすと':  TAG_BLOCK_OL,
            u'順序リスト':  TAG_BLOCK_OL,
            u'定義りすと':  TAG_BLOCK_DL,
            u'定義リスト':  TAG_BLOCK_DL,
            u'るび':      TAG_INLINEBLOCK_RUBY,
            u'ルビ':      TAG_INLINEBLOCK_RUBY,
            u'リンク':     TAG_INLINE_A,
            u'りんく':     TAG_INLINE_A}

        self.sizeHash = {
            u'ｘ':  1,
            u'×':  1,
            u'+':  2,
            u'＋': 2,
            u'ー': 3,
            u'―':  3,
            u'-':  3}
        self.sizePattern = re.compile(u'^([ｘ×+＋ー―-]?)([０１２３４５６７８９0123456789]{1,3})$')
        self.hPattern    = re.compile(u'^見出し([１２３４５６123456])$')
        
    def get(self, IDENTIFIER, prefix):
        if self.tags.has_key(IDENTIFIER):
            t = self.tags[IDENTIFIER]()
        else:
            color = colors.getColorCode(IDENTIFIER)
            if   '' != color:
                t = TAG_INLINE_COLOR()
                t.color = color
            else:
                m = self.sizePattern.match(IDENTIFIER)
                if m:
                    #size
                    pre   = m.group(1)
                    value = m.group(2)
                    value = value.replace(u'０', '0')
                    value = value.replace(u'１', '1')
                    value = value.replace(u'２', '2')
                    value = value.replace(u'３', '3')
                    value = value.replace(u'４', '4')
                    value = value.replace(u'５', '5')
                    value = value.replace(u'６', '6')
                    value = value.replace(u'７', '7')
                    value = value.replace(u'８', '8')
                    value = value.replace(u'９', '9')
                    value = int( value )
                    if '' == pre:
                        t = TAG_INLINE_SIZEIS()
                        t.size = value
                    else:
                        stype = self.sizeHash[pre]
                        if   1 == stype:
                            t = TAG_INLINE_SIZE_MULTI()
                            t.size = 100 * value
                        elif 2 == stype:
                            t = TAG_INLINE_SIZE_PLUS()
                            t.size = 100 + value
                        elif 3 == stype:
                            t = TAG_INLINE_SIZE_MINUS()
                            t.size = 100 - value
                else:
                    m = self.hPattern.match(IDENTIFIER)
                    if m:
                        value = m.group(1)
                        value = value.replace(u'１', '1')
                        value = value.replace(u'２', '2')
                        value = value.replace(u'３', '3')
                        value = value.replace(u'４', '4')
                        value = value.replace(u'５', '5')
                        value = value.replace(u'６', '6')
                        t = TAG_BLOCK()
                        t.name = 'h' + value
                    else:
                        t = TAG_BLOCK_UNKNOWN()
        t.prefix = prefix
        return t

tagFactory = TagFactory()

def parse(str):
    arr = str.split('\n')
    global error
    error = None
    global output
    output = ''
    scanner.set(arr)
    yyparse()
    return {'output': output,
            'error': error}

'''
Prototype file of Python parser.
Written by Yu Kobayashi
This file is PUBLIC DOMAIN.
'''

buffer = ""
token = ""
toktype = ""
YYDEFAULTSTACK = 65536

YYERRTOK = 256
EB_LEFT = 257
EB_RIGHT = 258
EB_BOTH = 259
EB_NONE = 260
IDENTIFIER = 261
PROPERTY = 262
NOVALUE = 263
LEFT_QUOTE = 264
RIGHT_QUOTE = 265
LINE = 266

    
'''
    #define yyclearin (yychar = -1)
    #define yyerrok (yyerrflag = 0)
    #define YYRECOVERING (yyerrflag != 0)
    #define YYERROR    goto yyerrlab
'''


''' Debug mode flag '''
yydebug = False

''' lexical element object '''
yylval = None

def yyprintln(msg):
    print msg

def yyflush():
    dummy = 0



yytranslate = [ \
        0,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,   12,   12,   12,   12, \
       12,   12,   12,   12,   12,   12,    1,    2,    3,    4, \
        5,    6,    7,    8,    9,   10,   11 \
    ]

YYBADCH = 12
YYMAXLEX = 267
YYTERMS = 12
YYNONTERMS = 14

yyaction = [ \
       19,   20,   21,   22,    9,   10,   -1,    0,    7,   41, \
        6,   37,   13,   30,    0,    0,    0,   11,    0,    0, \
       40 \
    ]

YYLAST = 21

yycheck = [ \
        2,    3,    4,    5,    8,    9,    0,    0,    6,   11, \
        6,   10,    7,   10,   -1,   -1,   -1,    9,   -1,   -1, \
       11 \
    ]

yybase = [ \
        6,    3,   -2,   -2,   -2,   -2,   -4,    8,    1,    5, \
        5,    9,    5,    2,    7,    4,    5,   -2,    0,    0, \
        0,    0,    5,    9,    9 \
    ]

YY2TBLSTATE = 9

yydefault = [ \
       16,32767,32767,32767,    2,32767,   16,32767,32767,   16, \
       16,32767,   17,32767,32767,32767 \
    ]



yygoto = [ \
       24,    1,    5,   24,   31,   29,    3,   35,    0,   39, \
        0,    0,   38 \
    ]

YYGLAST = 13

yygcheck = [ \
        5,    3,    2,    5,    5,    2,    2,   11,   -1,   12, \
       -1,   -1,   12 \
    ]

yygbase = [ \
        0,    0,   -4,   -2,    0,   -1,    0,    0,    0,    0, \
        0,   -5,    1,    0 \
    ]

yygdefault = [ \
    -32768,   14,    2,    4,   15,   23,   25,   26,   27,   28, \
       12,   34,   36,    8 \
    ]

yylhs = [ \
        0,    1,    1,    4,    4,    4,    4,    3,    3,    5, \
        5,    5,    5,    8,    6,    7,    2,    2,   10,   10, \
       11,   11,   13,   13,   12,    9 \
    ]

yylen = [ \
        1,    0,    2,    1,    1,    1,    1,    1,    2,    1, \
        1,    1,    1,    4,    6,    4,    0,    1,    1,    2, \
        3,    5,    1,    2,    1,    1 \
    ]

YYSTATES = 37
YYNLSTATES = 16
YYINTERRTOK = 1
YYUNEXPECTED = 32767
YYDEFAULT = -32766

'''
Parser entry point
'''

def yyparse():
    yyastk = range(YYDEFAULTSTACK)
    yysstk = range(YYDEFAULTSTACK)

    yystate = 0
    yychar = -1

    yysp = 0
    yysstk[yysp] = 0
    yyerrflag = 0
    while True:
        if yybase[yystate] == 0:
            yyn = yydefault[yystate]
        else:
            if yychar < 0:
                yychar = yylex()
                if yychar <= 0:
                    yychar = 0
                if yychar < YYMAXLEX:
                    yychar = yytranslate[yychar]
                else: 
                    yychar = YYBADCH
            yyn = yybase[yystate] + yychar
            goNext = yyn >= 0 and yyn < YYLAST and yycheck[yyn] == yychar
            if not goNext:
                goNext = yystate < YY2TBLSTATE
                if goNext:
                    yyn = yybase[yystate + YYNLSTATES] + yychar
                    goNext = yyn >= 0 and yyn < YYLAST and yycheck[yyn] == yychar
            if goNext:
                yyn = yyaction[yyn]
                goNext = yyn != YYDEFAULT
            if goNext:
                '''
                 >= YYNLSTATE: shift and reduce
                 > 0: shift
                 = 0: accept
                 < 0: reduce
                 = -YYUNEXPECTED: error
                 '''
                if yyn > 0 :
                    ''' shift '''
                    yysp = yysp + 1

                    yysstk[yysp] = yystate = yyn
                    yyastk[yysp] = yylval
                    yychar = -1
                    
                    if yyerrflag > 0:
                        yyerrflag = yyerrflag - 1
                    if yyn < YYNLSTATES:
                        continue
                        
                    ''' yyn >= YYNLSTATES means shift-and-reduce '''
                    yyn -= YYNLSTATES
                else:
                    yyn = -yyn
            else:
                yyn = yydefault[yystate]
        
        while True:
            ''' reduce/error '''
            if yyn == 0:
                ''' accept '''
                yyflush()
                return 0
            elif yyn != YYUNEXPECTED:
                ''' reduce '''
                yyl = yylen[yyn]
                yyval = yyastk[yysp-yyl+1]
                ''' Following line will be replaced by reduce actions '''
                if yyn == 2:
                    
                    p = yyastk[yysp-(2-1)]
                    c = yyastk[yysp-(2-2)]
                    t = TAG_BLOCK_ROOT()
                    t.startline = 1
                    t.setChild(c)
                    if p:
                        t.addProperty( p['value'] )
                    global output
                    output = t.html()
                    yyval = t
                
                if yyn == 3:
                    
                    yyval = 1
                
                if yyn == 4:
                    
                    yyval = 2
                
                if yyn == 5:
                    
                    yyval = 3
                
                if yyn == 6:
                    
                    yyval = 4
                
                if yyn == 7:
                    
                    yyval = [yyastk[yysp-(1-1)]]
                
                if yyn == 8:
                    
                    arr = yyastk[yysp-(2-1)]
                    arr.append(yyastk[yysp-(2-2)])
                    yyval = arr
                
                if yyn == 9:
                    
                    yyval = yyastk[yysp-(1-1)] 
                
                if yyn == 10:
                    
                    yyval = yyastk[yysp-(1-1)]
                
                if yyn == 11:
                    
                    yyval = yyastk[yysp-(1-1)]
                
                if yyn == 12:
                    
                    yyval = yyastk[yysp-(1-1)]
                
                if yyn == 13:
                    
                    id = yyastk[yysp-(4-2)]
                    p  = yyastk[yysp-(4-4)]
                    t  = tagFactory.get(id[0], yyastk[yysp-(4-1)])
                    t.startline = id[1]
                    if p:
                        t.addProperty( p['value'] )
                        t.endline = p['endline']
                    else:
                        t.endline = yyastk[yysp-(4-3)][1]
                    yyval = t
                
                if yyn == 14:
                    
                    id = yyastk[yysp-(6-2)]
                    p  = yyastk[yysp-(6-4)]
                    t  = tagFactory.get(id[0], yyastk[yysp-(6-1)])
                    t.startline = id[1]
                    t.child     = yyastk[yysp-(6-5)]
                    t.endline   = yyastk[yysp-(6-6)][1]
                    if p:
                        t.addProperty( p['value'] )
                    yyval = t
                
                if yyn == 15:
                    
                    id = yyastk[yysp-(4-2)]
                    p  = yyastk[yysp-(4-3)]
                    c  = yyastk[yysp-(4-4)]
                    t  = tagFactory.get(id[0], yyastk[yysp-(4-1)])
                    t.startline = id[1]
                    t.child     = [c]
                    t.endline   = c.endline
                    if p:
                        t.addProperty( p['value'] )
                    yyval = t
                 
                if yyn == 16:
                    
                    yyval = None
                
                if yyn == 17:
                    
                    yyval = yyastk[yysp-(1-1)]
                
                if yyn == 18:
                    
                    yyval = yyastk[yysp-(1-1)]
                
                if yyn == 19:
                    
                    ps = yyastk[yysp-(2-1)]
                    p  = yyastk[yysp-(2-2)]
                    psv = ps['value']
                    pv  = p['value']
                    ps['endline'] = p['endline']
                    for key in pv:
                        psv[key] = pv[key]
                    yyval = ps
                
                if yyn == 20:
                    
                    arr = {}
                    arr['startline'] = yyastk[yysp-(3-1)][1]
                    arr['endline']   = yyastk[yysp-(3-2)][1] + 1
                    arr["value"]     = {}
                    arr["value"][yyastk[yysp-(3-2)][0]] = yyastk[yysp-(3-3)]
                    yyval = arr
                
                if yyn == 21:
                    
                    arr = {}
                    arr['startline'] = yyastk[yysp-(5-1)][1]
                    arr['endline']   = yyastk[yysp-(5-5)][1]
                    arr['value']     = {}
                    arr['value'][yyastk[yysp-(5-2)][0]] = ' '.join( yyastk[yysp-(5-4)] )
                    yyval = arr
                
                if yyn == 22:
                    
                    yyval = [yyastk[yysp-(1-1)]]
                
                if yyn == 23:
                    
                    vs = yyastk[yysp-(2-1)]
                    vs.append(yyastk[yysp-(2-2)])
                    yyval = vs
                
                if yyn == 24:
                    
                    yyval = yyastk[yysp-(1-1)][0]
                
                if yyn == 25:
                    
                    li = yyastk[yysp-(1-1)]
                    t = TAG_LINE()
                    t.startline = li[1]
                    t.endline   = li[1]
                    t.child = [li[0]]
                    yyval = t
                
                ''' Goto - shift nonterminal '''
                yysp -= yyl
                yyn = yylhs[yyn]
                yyp = yygbase[yyn] + yysstk[yysp]
                if yyp >= 0 and yyp < YYGLAST and yygcheck[yyp] == yyn:
                    yystate = yygoto[yyp]
                else:
                    yystate = yygdefault[yyn]
                    
                yysp = yysp + 1

                yysstk[yysp] = yystate
                yyastk[yysp] = yyval
            else :
                ''' error '''
                if yyerrflag == 0:
                    yyerror("syntax error")
                if yyerrflag == 0 or yyerrflat == 1 or yyerrflag == 2:
                    yyerrflag = 3
                    ''' Pop until error-expecting state uncovered '''

                    while True:
                        yyn = yybase[yystate] + YYINTERRTOK
                        b = yyn >= 0 and yyn < YYLAST and yycheck[yyn] == YYINTERRTOK
                        if not b:
                            b = yystate < YY2TBLSTATE
                            if b:
                                yyn = yybase[yystate + YYNLSTATES] + YYINTERRTOK
                                b = yyn >= 0 and yyn < YYLAST and yycheck[yyn] == YYINTERRTOK
                        if not b:
                            break
                        if yysp <= 0:
                            yyflush()
                            return 1
                        yysp = yysp - 1
                        yystate = yysstk[yysp]
                    yyn = yyaction[yyn]
                    yysp = yysp + 1
                    yystate = yyn
                    yysstk[yysp] = yyn
                elif yyerrflatcase == 3:
                    if yychar == 0 :
                        yyflush()
                        return 1
                    yychar = -1
                
            if yystate < YYNLSTATES:
                break
            ''' >= YYNLSTATES means shift-and-reduce '''
            yyn = yystate - YYNLSTATES

