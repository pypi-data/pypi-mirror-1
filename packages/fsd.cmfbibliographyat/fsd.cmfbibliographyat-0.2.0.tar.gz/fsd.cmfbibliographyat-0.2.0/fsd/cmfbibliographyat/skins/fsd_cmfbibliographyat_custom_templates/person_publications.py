##parameters=mode='primary', include_own=False


# Return all publications of the current 'FSDPerson' context based
# on a simple match of the persons's name against the author list.
# a Person object. The heuristic is pretty lame right now.


def normalize(s):
    s = s.lower()
    s = s.replace('ue', 'u')
    s = s.replace('ae', 'a')
    s = s.replace('oe', 'o')
    s = s.replace('ü', 'u')
    s = s.replace('ä', 'a')
    s = s.replace('ö', 'o')
    s = s.replace('&auml;', 'a')
    s = s.replace('&ouml;', 'o')
    s = s.replace('&uuml;', 'u')
    return s

# search all bib references first
fsd = context.getDirectoryRoot()
fsd_path = '/'.join(fsd.getPhysicalPath())
reference_types =   context.portal_bibliography.getReferenceTypes()


# Filter by author name 
firstname = context.getFirstName().strip()
lastname = context.getLastName().strip()
stext = ' AND '.join([item.strip() for item in (firstname, lastname) if item.strip()])

all_pubs = context.portal_catalog(path=fsd_path,
                                 SearchableText=stext,
                                 meta_type=reference_types)


bib_path = '/'.join(context.getPhysicalPath())
primary_pubs = context.portal_catalog(path=bib_path,
                                      meta_type=reference_types)

primary_pub_paths = [p.getURL() for p in primary_pubs]

secondary_pubs = [r 
                  for r in all_pubs 
                  if not r.getURL() in primary_pub_paths
                  ]

if mode == 'primary':
    results = primary_pubs
elif mode == 'secondary':
    results = secondary_pubs
else:
    results = list(primary_pubs) + list(secondary_pubs)


# sort by year desc
sort_on = [('publication_year', 'cmp', 'desc')]
results = sequence.sort(results, sort_on)
return [r.getObject() for r in results]

