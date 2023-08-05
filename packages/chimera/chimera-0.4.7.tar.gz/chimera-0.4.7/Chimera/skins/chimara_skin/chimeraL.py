##parameters=text,font

c = context.chimera
i = c(text, font)

return "%s,%s,%s" %(i.absolute_url(), i.getProperty('width'), i.getProperty('height'))
