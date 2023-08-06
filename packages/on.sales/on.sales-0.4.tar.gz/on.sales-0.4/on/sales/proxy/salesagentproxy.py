"""SalesAgentProxy

This class is meant to have their contents mirrored from real SalesAgent
objects. The goal is to be able to add these proxy objects somewhere in
the SalesArea hierarchy, and have them automatically be kept in sync
with their non-proxy counterparts.

The intention is to do this via events and catalog queries.

The purpose of having this type of objects in the first place is to
make the display of SalesAgents more natural, namely, within their
respectice region(s), but to prevent stale data from lying around,
as well as inadvertantly "firing" sales personel by deleting an area
that would contain the real sales agent, instead of only a proxy.
"""



