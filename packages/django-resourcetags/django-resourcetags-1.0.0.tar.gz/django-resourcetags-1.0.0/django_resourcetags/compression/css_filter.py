import re

CSS_DELIMS = '\({};:,'
CSS_COMMENT_RE = re.compile ('\/\*.*?\*\/', re.DOTALL | re.MULTILINE)
CSS_WHITESPACE_RE = re.compile ('\s+', re.MULTILINE)
CSS_ADJ_WHITESPACE_RE = re.compile ('\s?([%s])\s?' % CSS_DELIMS)
def compress_css (text):
	"""Minify CSS by removing comments and whitespace."""
	text = CSS_COMMENT_RE.sub ('', text)
	text = CSS_WHITESPACE_RE.sub (' ', text)
	text = CSS_ADJ_WHITESPACE_RE.sub ('\\1', text)
	
	return text
	
