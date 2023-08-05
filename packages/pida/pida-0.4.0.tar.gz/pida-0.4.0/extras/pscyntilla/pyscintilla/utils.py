""" Utilities that make using Scintilla from Python easier

Copyright (c) 1999-2003, Archaeopteryx Software, Inc.  All rights reserved.

Contact: info@wingide.com
License: LGPL

"""

import sys
import string
import copy
from constants import *

# Key modifier codes
NOTHING_PRESSED = 0
SHIFT_PRESSED = 1
CTRL_PRESSED = 2
ALT_PRESSED = 4

# Misc style constants
STYLE_FIRSTRESERVED=STYLE_LINENUMBER
STYLE_LASTRESERVED=STYLE_LASTPREDEFINED

_kDefaultFontName = '!monospace'
_kDefaultFontSize = 12
_kDefaultBackground = "#FFFFFF"
_kDefaultForeground = "#000000"

def _GtkEventToScintillaKey(event):
  """ Convert Gtk event information into the form used by scintilla for key
  event notification. Returns ( keyval, modifier ). This matches how it's done
  in the C++ code. """

  if event.state & GDK.SHIFT_MASK and event.keyval < 128:
    keyval = ord(string.upper(chr(event.keyval)))
  elif event.keyval == GDK.ISO_Left_Tab:
    keyval = GDK.Tab
  else:
    keyval = event.keyval
  modifier = 0
  if event.state & GDK.SHIFT_MASK:
    modifier = modifier | SHIFT_PRESSED
  if event.state & GDK.CONTROL_MASK:
    modifier = modifier | CTRL_PRESSED
  if event.state & GDK.MOD1_MASK:
    modifier = modifier | ALT_PRESSED

  return keyval, modifier


#########################################################################
# Easier access to default lexers
#########################################################################

# Document types
kCppDocument = 1
kJavaDocument = 2
kPythonDocument = 3
kMakefileDocument = 4
kDosBatchDocument = 5
kVBDocument = 6
kHTMLDocument = 7
kPropsDocument = 8
kErrListDocument = 9
kMSIDLDocument = 10
kSQLDocument = 11
kXMLDocument = 12
kXCodeDocument = 13
kLatexDocument = 14
kLuaDocument = 15
kXPIDLDocument = 16
kJavascriptDocument = 17
kRCDocument = 18
kPLSQLDocument = 19
kPHPDocument = 20
kPerlDocument = 21
kDiffDocument = 22
kConfDocument = 23
kPascalDocument = 24
kAveDocument = 25
kAdaDocument = 26
kEiffelDocument = 27
kLispDocument = 28
kRubyDocument = 29
kBashDocument = 30
kBullantDocument = 31
kTCLDocument = 32
kCSSDocument = 33
kFortranDocument = 34
kMatlabDocument = 35
kScriptolDocument = 36
kPOVDocument = 37
kEScriptDocument = 38
kLOUTDocument = 39
kMMIXALDocument = 40
kNSISDocument = 41
kPSDocument = 42
kYAMLDocument = 43
kVXMLDocument = 44
kASMDocument = 45
kBaanDocument = 46
kNNCrontabDocument = 46
kDocbookDocument = 47

# Doc type for given MIME types
kMimeToDocTypeMap = {
  "text/x-python": kPythonDocument,
  'text/x-python-interface': kPythonDocument,
  "text/html": kHTMLDocument, 
  "text/x-c-source": kCppDocument,
  "text/x-cpp-source": kCppDocument,
  "text/x-java-source": kJavaDocument,
  "text/x-vb-source": kVBDocument,
  "text/x-dos-batch": kDosBatchDocument,
  "text/x-properties": kPropsDocument,
  "text/x-makefile": kMakefileDocument,
  "text/x-ms-makefile": kMakefileDocument,
  "text/x-errorlist": kErrListDocument,
  "text/x-ms-idl": kMSIDLDocument,
  "text/x-sql": kSQLDocument,
  "text/xml": kXMLDocument,
  "application/x-tex": kLatexDocument,
  "text/x-lua-source": kLuaDocument,
  "text/x-idl": kXPIDLDocument,
  "text/x-javascript": kJavascriptDocument,
  "text/x-rc": kRCDocument,
  "text/x-pl-sql": kPLSQLDocument,
  "text/x-php-source": kPHPDocument,
  "text/x-perl": kPerlDocument,
  "text/x-diff": kDiffDocument,
  "text/x-conf": kConfDocument,
  "text/x-pascal": kPascalDocument,
  "text/x-ave": kAveDocument,
  "text/x-xcode": kXCodeDocument,
  "text/x-ada": kAdaDocument,
  "text/x-eiffel": kEiffelDocument,
  "text/x-lisp": kLispDocument,
  "text/x-ruby": kRubyDocument,
  "text/x-bash": kBashDocument,
  "text/x-bullant": kBullantDocument,
  "text/x-tcl": kTCLDocument,
  "text/css": kCSSDocument,
  "text/x-asm": kASMDocument,
  "text/x-baan": kBaanDocument,
  "text/x-fortran": kFortranDocument,
  "text/x-matlab": kMatlabDocument,
  "text/x-scriptol": kScriptolDocument,
  "text/x-pov": kPOVDocument,
  "text/x-escript": kEScriptDocument,
  "text/x-lout": kLOUTDocument,
  "text/x-mmixal": kMMIXALDocument,
  "text/x-nsis": kNSISDocument,
  "text/postscript": kPSDocument,
  "text/x-yaml": kYAMLDocument,
  "text/x-vxml": kVXMLDocument,
  "text/x-nncrontab": kNNCrontabDocument,
  "text/x-docbook": kDocbookDocument,
  "text/x-po": kBashDocument,
}

# MIME type to doc type map
kDocToMimeTypeMap = {}
for mimetype, doctype in kMimeToDocTypeMap.items():
  kDocToMimeTypeMap[doctype] = mimetype

# Name for mime types
def _(x):
  return x
kMimeTypeNames = {
  'text/x-python': _("Python"),
  'text/html': _("HTML"),
  'text/x-c-source': _("C Source"),
  'text/x-cpp-source': _("C++ Source"),
  'text/x-java-source': _("Java"),
  'text/x-vb-source': _("Visual Basic"),
  'text/x-dos-batch': _("Dos Batch"),
  'text/x-properties': _("Properties"),
  'text/x-makefile': _("Makefile"),
  'text/x-ms-makefile': _("MS Makefile"),
  'text/x-errorlist': _("Error List"),
  'text/x-ms-idl': _("MS IDL"),
  'text/x-sql': _("SQL"),
  'text/xml': _("XML"),
  'application/x-tex': _("Latex"),
  'text/x-lua-source': _("Lua"),
  'text/x-idl': _("CORBA IDL"),
  'text/x-javascript': _("Javascript"),
  'text/x-rc': _("RC File"),
  'text/x-pl-sql': _("PL SQL"),
  'text/x-php-source': _("PHP"),
  'text/x-perl': _("Perl"),
  'text/x-diff': _("Diff/Patch"),
  'text/x-conf': _("Apache Conf"),
  'text/x-pascal': _("Pascal"),
  'text/x-ave': _("Avenue GIS Language"),
  'text/x-xcode': _("XCode"),
  'text/x-ada': _("Ada"),
  'text/x-eiffel': _("Eiffel"),
  'text/x-lisp': _("Lisp"),
  'text/x-ruby': _("Ruby"),
  'text/x-bash': _("Bash"),
  "text/x-bullant": _("Bullant"),
  "text/x-tcl": _("TCL"),
  "text/css": _("CSS2"),
  "text/x-asm": _("Masm Assembly"),
  "text/x-baan": _("Baan"),
  "text/x-fortran": _("Fortran"),
  "text/x-matlab": _("Matlab"),
  "text/x-scriptol": _("Scriptol"),
  "text/x-pov": _("POV Ray Tracer"),
  "text/x-escript": _("ESCRIPT"),
  "text/x-lout": _("Lout Typesetting Language"),
  "text/x-mmixal": _("MMIX Assembly Language"),
  "text/x-nsis": _("NSIS"),
  "text/postscript": _("Postscript"),
  "text/x-yaml": _("YAML"),
  "text/x-vxml": _("VXML"),
  "text/x-nncrontab": _("NNCrontab"),
  "text/x-docbook": _("Docbook XML"),
  'text/plain': _("Plain Text"),
}

# Comment start/end characters for source code by mime type
kMimeCommentChars = {
  'text/x-python': ('#', ""),
  'text/html': ('<!---', '--->'),
  'text/x-c-source': ('/*', '*/'),
  'text/x-cpp-source': ('//', ""),
  'text/x-java-source': ('//', ""),
  'text/x-vb-source': ("'", ""),
  'text/x-dos-batch': ('#', ""),
  'text/x-properties': ('#', ""),
  'text/x-makefile': ('#', ""),
  'text/x-ms-makefile': ('#', ""),
  'text/x-rc': ('#', ""),
  'text/x-idl': ('//', ""),
  'text/x-perl': ('#', ""),
  'text/x-lua-source': ('/*', '*/'),
  'text/x-sql': ('#', ""),
  'text/x-pl-sql': ('#', ""),
  'text/x-php-source': ('#', ""),
  'application/x-tex': ('%', ""),
  'text/xml': ('<!---', '--->'),
  'text/x-vxml': ('<!---', '--->'),
  'text/x-docbook': ('<!---', '--->'),
  'text/x-javascript': ('//', ""),
  'text/x-errorlist': ("", ""),
  'text/x-diff': ("", ""),
  'text/x-conf': ("#", ""),
  'text/x-pascal': ("{", "}"),
  'text/x-ave': ("", ""),
  'text/x-ada': ("--", ""),
  'text/x-eiffel': ("--", ""),
  'text/x-lisp': (";", ""),
  'text/x-ruby': ("#", ""),
  'text/x-bash': ("#", ""),
  "text/x-bullant": ("#", ""),
  "text/x-tcl": ("#", ""),
  "text/css": ("/*", "*/"),
  "text/x-fortran": ("!", ""),
  "text/x-matlab": ("%", ""),
  'text/plain': ("  [", "]"),
}

def MimeTypeForExtension(ext):
  """Determine the mime type for given file extension, if we can determine it"""
  if ext[:2] != '*.':
    ext = '*.%s' % ext
  import def_lexer_info
  lexer, doctype = def_lexer_info.kFilePatterns.get(ext, (None, None))
  return doctype

gExtensionToMimeTypeMap = None
def ExtensionToMimeTypeMap():
  """Get map from file extension to mime type for all known scintilla 
  document types"""
  
  import def_lexer_info
  
  global gExtensionToMimeTypeMap
  if gExtensionToMimeTypeMap is None:
    gExtensionToMimeTypeMap = {}
    for ext, (lex, dt) in def_lexer_info.kFilePatterns.items():
      if ext[:2] == '*.':  # Omit non-extension patterns
        gExtensionToMimeTypeMap[ext[2:]] = kDocToMimeTypeMap[dt]

  return gExtensionToMimeTypeMap

def LexerForDocType(doctype):
  """Determine what lexer to use for which document type"""
  
  import def_lexer_info
  return def_lexer_info.kLexerForDocType[doctype]

def set_lexer(scint, lexer, doc_type=None, use_defaults=1, style_overrides=None):
  """ Enable lexing using a built-in lexer.  This is used to control 
  colourizing and folding support in a document.

  An example of use is as follows:
 
    1) Obtain mime type of your text
    2) Convert mime type into sci_names listed document type
       (e.g., kCppDocument)
    3) Determine the lexer to use for the document type with
       lexer_id = LexerForDocType(doctype)
    4) Set the lexer with scint.set_lexer(lexer_id, doctype)
 
  This uses the default configured styles defined in def_lexer_info.py.
  (which is generated from the SciTE properties file by _gen_def_lex_info.py 
  but which can also be hand-modified to arrive at different defaults).
  These can be accessed with get_default_styles() or you can also set 
  other styles with set_styles().

  If you wish to alter the keywords used by lexers, call set_keywords()
  after making this call.  Default keywords are set up unless
  use_defaults is false."""

  import def_lexer_info
  
  # Set the lexer to use
  scint.set_lexer(lexer)

  # Set up default keywords and styles used by lexer
  if use_defaults:

    # Set up default basic set of keywords (all lexers need this)
    keywords = def_lexer_info.kDefaultKeywords.get(doc_type)
    if keywords != None:
      scint.set_keywords(0, keywords)
      
    # Set up extra keywords if needed by some lexers
    extra_kw = def_lexer_info.kExtraKeywords.get(doc_type)
    if extra_kw is not None:
      max_i = 0
      for i in extra_kw.keys():
        max_i = max(max_i, i)
      for i in range(1, max_i+1):
        scint.set_keywords(i, extra_kw.get(i, ""))
      
    # Increase number of style bits needed by some lexers
    if lexer == SCLEX_HTML:
      scint.set_style_bits(7)
      
    # Set up styles
    if not style_overrides:
      set_styles(scint)
    else:
      styles = get_default_styles(scint.get_lexer())
      if styles is None:
        styles = style_overrides
      else:
        merged = copy.deepcopy(styles)
        for state, attribs in style_overrides.items():
          if state in styles:
            merged[state].update(attribs)
          else:
            merged[state] = attribs
        if merged != styles:
          styles = merged
          
      set_styles(scint, styles)

  # Recolourise the whole document
  scint.colourise(0, -1)

#########################################################################
# Easier access to manual styling / font setting
#########################################################################

def set_style_attribs(scint, style, font, size, bold, italic, forecolour,
                      backcolour, eolfilled=0, underline=0, 
                      charset=SC_CHARSET_DEFAULT):
  """Set attributes of particular style"""
  
  if font is not None and len(font) != 0:
    scint.style_set_font(style, font)
  scint.style_set_bold(style, bold)
  scint.style_set_italic(style, italic)
  if size is not None and size > 0:
    scint.style_set_size(style, size)
  scint.style_set_eol_filled(style, eolfilled)
  scint.style_set_underline(style, underline)
  scint.style_set_character_set(style, charset)

  scint.style_set_fore(style, xform_colour(forecolour))
  scint.style_set_back(style, xform_colour(backcolour))

def set_fixed_font_size(scint, font_name, font_size, italic, bold):
  """ Set a fixed font/size/italic/bold for all text, which always overrides
  any lexer-sensitive font/size. Use this to avoid mixed fonts within lexed
  documents.  Pass None to unset a previously set value and go back to the
  defaults set by the style."""

  # Save value in the instance for use in set_styles below
  scint._fixed_font = font_name
  scint._fixed_size = font_size
  scint._fixed_italic = italic
  scint._fixed_bold = bold
  
  # Set up styles
  _propagate_style_change(scint)
  
def get_fixed_font_size(scint, style_id):
  """ Returns font/size/italic/bold used, assuming set_fixed_font_size
  was used. """

  def_styles = get_default_styles(scint.get_lexer())
  if def_styles is not None and style_id in def_styles:
    style_values = def_styles[style_id]
  else:
    style_values = {}
    
  fixed_font = getattr(scint, '_fixed_font', None)
  fixed_size = getattr(scint, '_fixed_size', None)
  fixed_italic = getattr(scint, '_fixed_italic', None)
  fixed_bold = getattr(scint, '_fixed_bold', None)
    
  if fixed_font is None:
    fixed_font = style_values.get('font', _kDefaultFontName)
  if fixed_size is None:
    fixed_size = style_values.get('size', _kDefaultFontSize)
  if fixed_italic is None:
    fixed_italic = style_values.get('italic', False)
  if fixed_bold is None:
    fixed_bold = style_values.get('bold', False)

  return fixed_font, fixed_size, fixed_italic, fixed_bold

def set_fixed_background_colour(scint, colour):
  """Set fixed background colour to use.  When set, the code in set_styles will alter
  foreground colours heuristically to work reasonably with the given background."""
  
  # Save value in the instance for use in set_styles below
  if colour is None:
    scint._fixed_background_colour = None
  else:
    scint._fixed_background_colour = xform_colour(colour)
  
  # Set up styles
  _propagate_style_change(scint)

  # Set caret to white or black based on selected colour
  tcolour = get_colour_tuple(xform_colour(colour))
  if tcolour[0] < 0xff / 2 and tcolour[1] < 0xff / 2 and tcolour[2] < 0xff / 2:
    caret_colour = xform_colour((0xff, 0xff, 0xff))
    dark = 1
  else:
    caret_colour = xform_colour((0x00, 0x00, 0x00))
    dark = 0
  scint.set_caret_fore(caret_colour)

  # Set margin color accordingly
  if dark:
    margin_back = ramp_colour(colour, 0x1F)
    fold_margin_back = ramp_colour(colour, 0x0F)
  else:
    margin_back = ramp_colour(colour, -0x1F)
    fold_margin_back = ramp_colour(colour, -0x0F)
  margin_fore = compute_fore_colour(margin_back, (0x00, 0x00, 0x00))
  scint.style_set_back(STYLE_LINENUMBER, xform_colour(margin_back))
  scint.style_set_fore(STYLE_LINENUMBER, xform_colour(margin_fore))
  scint.set_fold_margin_hi_colour(1, xform_colour(fold_margin_back))
  
def get_default_styles(lexer_id):
  """Get the default styles for use with given lexer"""

  import def_lexer_info
  return def_lexer_info.kDefStylesForLexer.get(lexer_id)

def clear_styles(scint):
  """Clear alls styles on given scintilla editor back to default values.
  This ignores fixed override values:  Call set_styles() to use those."""

  def_styles = get_default_styles(scint.get_lexer())
  if def_styles is None:
    def_styles = {}
    
  fixed_font = getattr(scint, '_fixed_font', None)
  fixed_size = getattr(scint, '_fixed_size', None)
  fixed_italic = getattr(scint, '_fixed_italic', None)
  fixed_bold = getattr(scint, '_fixed_bold', None)
    
  for id in range(0, STYLE_MAX+1):

    font, size, italic, bold = get_fixed_font_size(scint, id)
    scint.style_set_font(id, font)
    scint.style_set_size(id, size)
    scint.style_set_italic(id, italic)
    scint.style_set_bold(id, bold)

    if id < STYLE_FIRSTRESERVED or id > STYLE_LASTRESERVED:
      style_values = def_styles.get(id, {})
      scint.style_set_back(id, xform_colour(style_values.get('fore', _kDefaultBackground)))
      scint.style_set_fore(id, xform_colour(style_values.get('back', _kDefaultForeground)))
      scint.style_set_eol_filled(id, style_values.get('eol_filled', 0))
  
def set_styles(scint, styles=None):
  """Set styles for syntax highlighting according to given styles dictionary
  and previously set fixed font, size, italic, bold, and background colour
  values (if any)"""

  # Set up fixed value fields (None means don't override the style values)
  if not hasattr(scint, '_fixed_font'):
    scint._fixed_font = None
  if not hasattr(scint, '_fixed_size'):
    scint._fixed_size = None
  if not hasattr(scint, '_fixed_italic'):
    scint._fixed_italic = None
  if not hasattr(scint, '_fixed_bold'):
    scint._fixed_bold = None
  if not hasattr(scint, '_fixed_background_colour'):
    scint._fixed_background_colour = None
  if not hasattr(scint, '_styles'):
    scint._styles = None

  # If no styles passed, use previously set values or defaults (this is used
  # internally to propagate changes to fixed style attribs)
  if styles is None:
    styles = scint._styles
    if styles is None:
      styles = get_default_styles(scint.get_lexer())
  else:
    if styles is get_default_styles(scint.get_lexer()):
      scint._styles = None
    else:
      scint._styles = styles
      
  # When no styles found (e.g., in non-lexed document), 
  if styles is None:
    styles = {}
  
  # Set style info for each given style id
  for id in range(0, STYLE_MAX+1):

    # Skip reserved styles used for margins, etc
    if id >= STYLE_FIRSTRESERVED and id <= STYLE_LASTRESERVED:
      continue
    defn = styles.get(id, {})

    # Set the styles for this id into scintilla
    items_set = []
    set_back_colour = None
    for name, value in defn.items():
      if name == 'font':
        scint.style_set_font(id, value)
      elif name == 'size':
        scint.style_set_size(id, value)
      elif name == 'fore':
        scint.style_set_fore(id, xform_colour(value))
      elif name == 'back':
        set_back_colour = xform_colour(value)
        scint.style_set_back(id, set_back_colour)
      elif name == 'bold':
        scint.style_set_bold(id, value)
      elif name == 'italic':
        scint.style_set_italic(id, value)
      elif name == 'eol_filled':
        scint.style_set_eol_filled(id, value)
      items_set.append(name)
     
    # Override values set as fixed across all style ids
    if scint._fixed_font is not  None:
      scint.style_set_font(id, scint._fixed_font)
      items_set.append('font')
    if scint._fixed_size is not None:
      scint.style_set_size(id, scint._fixed_size)
      items_set.append('size')
    if scint._fixed_italic is not None:
      scint.style_set_italic(id, scint._fixed_italic)
      items_set.append('italic')
    if scint._fixed_bold is not None:
      scint.style_set_bold(id, scint._fixed_bold)
      items_set.append('bold')
    if scint._fixed_background_colour is not None and not defn.has_key('back'):
      if set_back_colour is not None:
        base_bg = get_colour_tuple(xform_colour(scint._fixed_background_colour))
        style_bg = get_colour_tuple(set_back_colour)
        use_bg = shift_if_too_similar(base_bg, style_bg)
        scint.style_set_back(id, xform_colour(use_bg))
      else:
        scint.style_set_back(id, scint._fixed_background_colour)
      scint.style_set_fore(id, xform_colour(compute_fore_colour(scint._fixed_background_colour,
                                                                defn.get('fore', _kDefaultForeground))))
      items_set.append('back')
      items_set.append('fore')

    # Set defaults for any attributes not set either by the style
    # or overridden by fixed values
    if not 'font' in items_set:
      scint.style_set_font(id, _kDefaultFontName)
    if not 'size' in items_set:
      scint.style_set_size(id, _kDefaultFontSize)
    if not 'fore' in items_set:
      scint.style_set_fore(id, xform_colour(_kDefaultForeground))
    if not 'back' in items_set:
      scint.style_set_back(id, xform_colour(_kDefaultBackground))
    if not 'bold' in items_set:
      scint.style_set_bold(id, 0)
    if not 'italic' in items_set:
      scint.style_set_italic(id, 0)
    if not 'eol_filled' in items_set:
      scint.style_set_eol_filled(id, 0)

gTextToColourCache = {}

def xform_colour(col):
  """ Transforms value for colour into integer that scintilla expects in
  style_set_fore() and style_set_back(). """

  def __hex_to_int(hex_string):
    val = 0
    for i in range(0, len(hex_string)):
      digit = string.upper(hex_string[i])
      if digit not in string.hexdigits:
        raise ValueError
      if digit == 'A': d_val = 10
      elif digit == 'B': d_val = 11
      elif digit == 'C': d_val = 12
      elif digit == 'D': d_val = 13
      elif digit == 'E': d_val = 14
      elif digit == 'F': d_val = 15
      else: d_val = string.atoi(digit)  
      exp = (len(hex_string) - i) - 1
      val = val + d_val * (16 ** exp)
    return val
  
  if type(col) == type(1):
    return col

  elif type(col) == type(()) and len(col) == 3:
    r, g, b = col
    val = ((b & 0xff) << 16) | ((g & 0xff) << 8) | (r & 0xff);
    return val

  elif type(col) == type('') and len(col) != 0:
    val = gTextToColourCache.get(col)
    if val != None:
      return val
    if col[0] == '#' and len(col) == 7:
      rgb = (__hex_to_int(col[1:3]), __hex_to_int(col[3:5]),
             __hex_to_int(col[5:7]))
      val = xform_colour(rgb)
      gTextToColourCache[col] = val
      return val
    
  raise ValueError, 'Incorrect colour value: ' + repr(col)
      
def get_colour_tuple(colour):
  """Convert packaged colour (e.g. output of xform_colour) to (r, g, b) tuple
  with elements in range from 0x00 to 0xff"""
  
  r = colour & 0xff
  g = (colour >> 8) & 0xff
  b = (colour >> 16) & 0xff

  return (r, g, b)
  
def compute_fore_colour(back_colour, fore_colour):
  """Transform given foreground colour heuristically so it looks OK on the given
  background"""
  
  back_colour = get_colour_tuple(xform_colour(back_colour))
  fore_colour = list(get_colour_tuple(xform_colour(fore_colour)))

  # Foreground colours are designed for use on white background, so if background is dark we
  # ramp up the brightness to peg max r,g,b value to top
  brightness = back_colour[0] + back_colour[1] + back_colour[2]
  if brightness < (0xff * 3) / 2:
    min_diff = 0xff
    for i in range(0, 3):
      min_diff = min(min_diff, 0xff - fore_colour[i])
    for i in range(0, 3):
      fore_colour[i] += min_diff

    # Ramp up blues even further since human eye has trouble seeing them on dark background
    if fore_colour[2] == 0xff and fore_colour[0] < 0xff / 2 and fore_colour[1] < 0xff / 2:
      fore_colour[0] = min(0xff, fore_colour[0] + 0x44)
      fore_colour[1] = min(0xff, fore_colour[1] + 0x44)

  # If colour is too similar to background, change it by moving away from background colour
  fore_colour = shift_if_too_similar(back_colour, fore_colour)
      
  return tuple(fore_colour)

def shift_if_too_similar(back_colour, fore_colour, amt=0x22):
  """Check if colour is too similar to a given background colour and alter it so it
  will stand out on that background"""
  
  similarity = 0
  for i in range(0, 3):
    similarity += abs(back_colour[i] - fore_colour[i])
  if similarity < 3 * amt:
    test_colour = list(fore_colour[:])
    for i in range(0, 3):
      test_colour[i] = min(0xff, fore_colour[0] + amt)
    similarity = 0
    for i in range(0, 3):
      similarity += abs(back_colour[i] - test_colour[i])
    if similarity < 3 * amt:
      for i in range(0, 3):
        test_colour[i] = max(0x00, fore_colour[0] - amt)
    fore_colour = test_colour
      
  return tuple(fore_colour)

def ramp_colour(colour, amt):
  """Ramp colour brightness up or down given amount, keeping within allowed ranges"""
  
  return (max(min(colour[0] + amt, 0xff), 0x00), 
          max(min(colour[1] + amt, 0xff), 0x00),
          max(min(colour[2] + amt, 0xff), 0x00))
  
def _propagate_style_change(scint):
  """Used internally to update display when some style attribute changes"""
  
  clear_styles(scint)
  set_styles(scint)
  
