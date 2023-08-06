Products.rpcauth README
=======================

This product allows external applications to make authentication
queries to Zope via XML/RPC.  The product registers an XML-RPC view,
'check_credentials', which takes a mapping holding 'login' and 'password',
and returns a mapping which holds 'userid' and 'login' on success.  The
returned mapping will be empty on failure.
