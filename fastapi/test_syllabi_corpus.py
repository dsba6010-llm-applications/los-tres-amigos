import syllabi_corpus as sc
import json

c = sc.SyllabiCorpus()
print(json.dumps(c.get_documents(),indent=2))
