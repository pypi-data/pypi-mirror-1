# Release information about TGFKLookup

version = "0.1a0"

description = "A collection of widgets to do Foreign Key related lookups"

long_description = """Still a work in progress.

AutoCompletingFKLookupField, it's a prototype based
rewrite of the autocompleting TG widget. It allows lookup by ID and text search
and shows both fields. Check the widget browser for a demo.

UpdatableSingleSelectField receives a function on the opt_feeder param
and will setup a controller automagically to update it when the .update()
javascript method from the manager is called. I'm currently using it to make options
lists based on other fields. 
Also takes a predicate if you want to protect the Ajax calls. Demo coming soon."""

author = "Claudio Martinez"
email = "claudio.s.martinez@gmail.com"
license = "MIT"
