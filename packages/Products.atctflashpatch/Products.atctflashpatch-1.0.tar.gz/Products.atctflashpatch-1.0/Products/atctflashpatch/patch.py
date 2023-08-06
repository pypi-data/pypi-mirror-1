from Products.ATContentTypes.content.file import ATFile

# This patch adds flash files as inline types.
# See http://dev.plone.org/plone/ticket/8624
ATFile.inlineMimetypes= ('application/msword',
                         'application/x-msexcel', # ?
                         'application/vnd.ms-excel',
                         'application/vnd.ms-powerpoint',
                         'application/pdf',
                         'application/x-shockwave-flash')

print "PATCHED ATCT'S FILE FOR FLASH INLINE BUG"
print "See http://dev.plone.org/plone/ticket/8624"

