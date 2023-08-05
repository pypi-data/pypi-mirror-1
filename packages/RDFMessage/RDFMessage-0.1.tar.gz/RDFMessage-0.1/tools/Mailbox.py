#!/usr/bin/env python

"""
Import or export of mailboxes from data stores.

Copyright (C) 2006 Paul Boddie <paul@boddie.org.uk>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import RDFMessage.Store
import RDFMessage.Parsers
import RDFMessage.Writers

# Main program.

if __name__ == "__main__":
    import cmdsyntax
    import sys
    import codecs
    import libxml2dom

    # Find the documents.

    syntax = cmdsyntax.Syntax("""
        --store=STORE_NAME
        --store-type=STORE_TYPE
        [--module=MODULE]
        [(--contexts | --context=NAMESPACE)]
        [--uriref=URIREF]
        [--input-mbox=INPUT_FILE]
        [--input-xml=INPUT_FILE]
        [--output-mbox=OUTPUT_FILE]
        [--output-xml=OUTPUT_FILE]
        [--output-xml-value-attr]
        [--remove]
        [--remove-context]
        """)

    syntax_matches = syntax.get_args(sys.argv[1:])

    try:
        args = syntax_matches[0]
    except IndexError:
        print "Syntax:"
        print syntax.syntax
        print "Terms:"
        print
        print "  STORE_TYPE     sqltriples"
        print "  MODULE         PgSQL|pysqlite2"
        print
        print "Examples:"
        print
        print "  python tools/Mailbox.py --store=testdb --store-type=sqltriples --module=PgSQL \\"
        print "    --uriref=MyMailbox --input-mbox=mbox.txt"
        sys.exit(1)

    # Open a store.

    store = RDFMessage.Store.open(args["store"], args["store-type"], args.get("context"), database_module_name=args.get("module"))

    # Perform the requested operations.

    try:
        # Handle different store contexts, if appropriate.

        if args.has_key("contexts"):
            print "Contexts:"
            for context in store.contexts():
                print context
            sys.exit(0)

        # Parse a mailbox input file.

        if args.has_key("input-mbox") and args.has_key("uriref"):
            f = open(args["input-mbox"], "rb")
            print "Added", RDFMessage.Parsers.parse_mailbox(f, store, uriref=store.URIRef(args["uriref"])), "as", args["uriref"]

        # Parse an XML input file.

        if args.has_key("input-xml") and args.has_key("uriref"):
            doc = libxml2dom.parseFile(args["input-xml"])
            print "Added", RDFMessage.Parsers.parse_document(doc, store, uriref=store.URIRef(args["uriref"])), "as", args["uriref"]

        # Save as a mailbox if requested.

        if args.has_key("output-mbox") and args.has_key("uriref"):
            f = codecs.open(args["output-mbox"], "wb", encoding="utf-8")
            RDFMessage.Writers.write_to_stream(
                f, store, main_node=store.URIRef(args["uriref"])
                )
            f.close()

        # Write an XML output file.

        if args.has_key("output-xml") and args.has_key("uriref"):
            if args.has_key("output-xml-value-attr"):
                doc = RDFMessage.Writers.get_document(store, store.URIRef(args["uriref"]), value_as_attribute=1)
            else:
                doc = RDFMessage.Writers.get_document(store, store.URIRef(args["uriref"]))
            f = open(args["output-xml"], "wb")
            doc.toStream(f, encoding="utf-8")
            f.close()

        # Remove from the information store if requested.

        if args.has_key("remove"):
            store.remove_node(store.URIRef(args["uriref"]), deep=1)

        # Remove entire contexts if requested.

        if args.has_key("remove-context"):
            store.remove_context(args["context"])

        store.commit()

    finally:
        store.close()

# vim: tabstop=4 expandtab shiftwidth=4
