"""
Template subclass that supports {{double-curly-braces}} as delimiters.
"""
from string import Template

class CurlyBraceTemplate(Template):
    """
    Substitutes anything inside double curly braces.
    """
    pattern = r"""
    {{(?P<named>.*?)}}
    (?P<escaped>)(?P<braced>)(?P<invalid>)"""
    
