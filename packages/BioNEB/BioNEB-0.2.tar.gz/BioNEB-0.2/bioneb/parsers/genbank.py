#  Copyright 2008 New England Biolabs
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Genbank Parser

Support for parsing Genbank Files
"""

import datetime
import re
import sys
import time

from bioneb.utils.undo import UndoHandle

__all__ = ["GenbankError", "LocationError", "GenbankParser"]

class GenbankError(Exception):
    def __init__(self,filename=None, lineno=None, mesg='Parsing failed.'):
        self._fname = filename
        self._lineno = lineno
        self._mesg = mesg
    
    def __str__(self):
        ret = ["Genbank Error: "]
        if self._fname:
            ret.append(self._fname)
        if self._lineno:
            ret.append('(%s)' % self._lineno)
        if self._fname or self._lineno:
            ret.append(': ')
        ret.append(self._mesg)
        return ''.join(ret)

class LocationError(GenbankError):
    pass

class GenbankParser(object):
    # Parser states
    INITIALIZED = "Initialized" # Initial state.
    INFO = "Info" # Read everything before the features table.
    FEATURES = "Features" # Read the features table
    SEQUENCE = "Sequence" # Read the sequence
    RESET = "Reset" # Between records
    FINISHED = "Finished" # Data source exhausted
    
    def __init__(self, filename=None, stream=None):
        """Genbank Parser
        
            parser = GenbankParser("data.gbk")
            while parser.has_next():
                info = parser.info()
                for feature in parser.features():
                    # Process feature
                    pass
                for data in parser.sequence():
                    # Process sequence
                    pass
        """
        self._source = UndoHandle(filename=filename, stream=stream)
        self._state = self.INITIALIZED
        self._info = None
        self._counts = {}

    #
    # Public properties
    #
    def _get_counts(self):
        self._assert(self._counts != {}, "No base count data available.")
        return self._counts.copy()
    counts = property(_get_counts, doc="""Return base count information.
    Not valid until after the sequence iterator has been exhausted.
    The sequence iterator must be invoked with the `count=True` flag
    or the record included a BASE COUNTS line.
    """)
    
    #
    # PUBLIC API
    #

    def has_next(self):
        """Test if more records can be found in the data stream.
        
        This method will seek to the next available record. You
        should not call it before you have finished processing
        the current record.
        """
        return self.info(next=True) is not None

    def info(self, next=False):
        """Retrieve the information object for the current record.
        
        The information object encopasses everything from the LOCUS
        line to the FEATURES line.
        
        If `next` evaluates to True, the current parsing position
        will be advanced until a new record is found. Raises a
        `NoMoreRecords` exception when the file is finished.
        """
        # Only parse when we have no info yet, the user requests
        # the next record, or we've completel exhausted the
        # current record.
        if self._info and self._state != self.RESET and not next:
            return self._info
        if self._state not in [self.INITIALIZED, self.RESET]:
            self._counts = {}
            self._next_record()
        self._skip_blank() # Skip blank lines between records
        if self._state == self.FINISHED:
            return None
        self._assert(self._state in [self.INITIALIZED, self.RESET], "Failed to position parser.")
        
        # We need to be at a LOCUS or // line for proper parsing.
        locus = self._source.next()
        self._assert(locus.startswith("LOCUS"), "Invalid Genbank record starts with: '%s'" % locus.strip())
        self._source.undo()
        
        info = {}
        for keyword in self._info_keys():
            getattr(self, "_info_%s" % keyword["name"].lower())(keyword, info)
        self._info = info
        self._state = self.INFO
        return info
    
    def features(self):
        """Get an iterator for the feature table of the current record.
        
        You should not call this method with an outstanding features
        iterator. Outstanding iterators must not be consumed once this
        method is called.
        
        If this method is invoked when the current parse position is not
        at the FEATURES line it will attempt to skip everything until the
        next FEATURES section is found. This may involve parsing a new
        record and replacing the current info object, as well as discarding
        the sequence data from the current record.
        """
        if self._state != self.INFO:
            self.info()
        if self._state == self.FINISHED:
            raise StopIteration()
        self._assert(self._state == self.INFO, "Failed to position parser.")
        header = self._source.next()
        match = __regexp__["main"]["features"].match(header)
        self._assert(match, "Invalid FEATURES line: '%s'" % header.strip())
        for key in self._feature_keys():
            yield key
        self._state = self.FEATURES

    def contig(self):
        """Return the contig information describing this record.
        
        This method should not be called before finishing with the features
        iterator as it fast forwards to the contig information in the file.
        """
        if self._state != self.FEATURES:
            self._skip_features()
        if self._state == self.FINISHED:
            raise StopIteration
        if self._info["locus"]["division"] != "CON":
            self._raise("This does not appear to be a contig record.")
        self._assert(self._state == self.FEATURES, "Failed to position parser.")
        header = self._source.next()
        match = __regexp__["main"]["keyword"].match(header)
        self._assert(match and match.group("name") == "CONTIG", "Failed to parse CONTIG info: '%s'" % header.strip())
        loc = [match.group("value")]
        loc.extend([l.strip() for l in self._info_continuation()])
        marker = self._source.next().strip()
        self._assert(marker == '//', "Failed to find end of record: '%s'" % marker)
        self._state = self.RESET
        return self._location_parse(''.join(loc))

    def sequence(self, count=False, strict=False):
        """Get an iterator for the sequence data of the current record.
        
        This method behvaes similarly to `features()` in that it should not be
        called when trying to parse any other part of the file.
        
        `count`: Count the base composition or use BASE COUNTS if present.
        `strict`: Run a regexp over every line of the sequence.
        """
        if self._state != self.FEATURES:
            self._skip_features()
        if self._state == self.FINISHED:
            raise StopIteration
        if self._info["locus"]["division"] == "CON":
            self._raise("Contig records have no sequence data.")
        self._assert(self._state == self.FEATURES, "Failed to position parser.")
        header = self._source.next()
        match = __regexp__["main"]["keyword"].match(header)
        self._assert(match, "Failed to parse sequence header: '%s'" % header.strip())
        if match.group("name") == "BASE COUNT":
            self._counts = self._sequence_base_counts(match.group("value"))
            count = False # Assume provided base counts are correct.
            header = self._source.next()
            match = __regexp__["main"]["keyword"].match(header)
        self._assert(match.group("name") == "ORIGIN", "No ORIGIN sequence data found: '%s'" % header.strip())
        for line in self._source:
            if line.strip() == '//':
                # No undo, so we're positioned for next record
                self._state = self.RESET
                raise StopIteration
            seq = None
            if strict:
                match = __regexp__["main"]["sequence"].match(line)
                self._assert(match, "Invalidly formatted sequence data: '%s'" % line.strip())
                seq = match.group("value")
            else:
                bits = line.split(None, 1)
                if len(bits) > 1:
                    seq = bits[-1]
                else:
                    seq = ""
            if not seq:
                continue
            seq = ''.join(seq.split()).upper()
            if count:
                for c in seq:
                    self._counts[c] = self._counts.get(c, 0) + 1
            yield seq

    #
    # INFO PARSING
    #

    def _info_keys(self):
        """Parse all keyword (LOCUS, REFERENCE, SOURCE...) sections in the record information."""
        for line in self._source:
            if not line.strip():
                continue
            match = __regexp__["main"]["keyword"].match(line)
            if not match or match.group("name") == "FEATURES":
                self._source.undo()
                raise StopIteration
            ret = {"name": match.group("name"), "value": ["%s\n" % match.group("value")], "subkeys": []}
            ret["value"].extend(self._info_continuation())
            ret["value"] = ''.join(ret["value"]).strip()
            ret["subkeys"].extend(self._info_subkeys())
            yield ret
    
    def _info_subkeys(self):
        for line in self._source:
            match = __regexp__["main"]["subkeyword"].match(line)
            if not match:
                self._source.undo()
                raise StopIteration
            ret = {"name": match.group("name"), "value": ["%s\n" % match.group("value")]}
            ret["value"].extend(self._info_continuation())
            ret["value"] = ''.join(ret["value"]).strip()
            yield ret
    
    def _info_continuation(self):
        for line in self._source:
            match = __regexp__["main"]["continuation"].match(line)
            if not match:
                self._source.undo()
                raise StopIteration
            yield "%s\n" % match.group("value")
    
    def _info_locus(self, kw, info):
        self._assert_no_subkeys(kw, "LOCUS")
        tokens = kw["value"].split()
        info["locus"] = {
            "name": tokens[0],
            "date": datetime.datetime(*time.strptime(tokens[-1], "%d-%b-%Y")[0:6])
        }
        self._assert(info["locus"]["date"] is not None, "Failed to parse locus date: '%s'" % tokens[-1])
        for token in tokens[1:-1]:
            curr_name = None
            curr_match = None
            for name, lre in __regexp__["locus"].iteritems():
                match = lre.match(token)
                if curr_match and match:
                    self._raise("Multiple matches for LOCUS attribute '%s'" % name)
                elif match:
                    curr_name, curr_match = name, match
            self._assert(curr_match, "Failed to parse LOCUS token: '%s'" % token)
            if curr_name == "length":
                info["locus"][curr_name] = int(curr_match.group("value"))
            else:
                info["locus"][curr_name] = curr_match.group("value")
    
    def _info_definition(self, kw, info):
        self._assert_no_subkeys(kw, "DEFINITION")
        info["definition"] = kw["value"].strip().rstrip('.')
    
    def _info_accession(self, kw, info):
        self._assert_no_subkeys(kw, "ACCESSION")
        info["accession"] = kw["value"].strip()
    
    def _info_pid(self, kw, info):
        self._assert_no_subkeys(kw, "PID")
        info["pid"] = kw["value"].strip()
    
    def _info_version(self, kw, info):
        self._assert_no_subkeys(kw, "VERSION")
        info["versions"] = []
        for token in kw["value"].split():
            match = __regexp__["version"]["gi"].match(token)
            if match:
                info["gi"] = match.group("value")
            else:
                info["versions"].append(token)

    def _info_dbsource(self, kw, info):
        self._assert_no_subkeys(kw, "DBSOURCE")
        info["db_source"] = kw["value"].strip()

    def _info_project(self, kw, info):
        self._assert_no_subkeys(kw, "PROJECT")
        info["PROJECT"] = kw["value"].strip()
    
    def _info_keywords(self, kw, info):
        self._assert_no_subkeys(kw, "KEYWORDS")
        kws = [t.strip().replace("\n", " ") for t in kw["value"].strip().rstrip('.').split(';')]
        info["keywords"] = filter(None, kws)

    def _info_segment(self, kw, info):
        self._assert_no_subkeys(kw, "SEGMENT")
        match = __regexp__["segment"]["position"].match(kw["value"].strip())
        self._assert(match, "Invalid SEGMENT format: '%s'" % kw["value"].strip())
        info["segment"] = {"id": int(match.group("value"))-1, "total": int(match.group("total"))}

    def _info_source(self, kw, info):
        self._assert(len(kw["subkeys"]) == 1, "Invalid SOURCE definition has no ORGANISM specified.")
        self._assert(kw["subkeys"][0]["name"] == "ORGANISM", "Invalid SOURCE definition has no ORGANISM specified.")
        lines = kw["subkeys"][0]["value"].split("\n")
        info["source"] = {
            "name": kw["value"].strip().rstrip('.'),
            "organism": lines[0].strip(),
            "lineage": [t.strip() for t in ' '.join(lines[1:]).rstrip('.').split(';')]
        }        

    def _info_reference(self, kw, info):
        ref = {}
        match = __regexp__["reference"]["location"].match(kw["value"])
        if match is not None:
            ref["start"] = int(match.group("start"))-1
            ref["end"] = int(match.group("end"))-1
        for sub in kw["subkeys"]:
            # If authors follows the Last,F.M., pattern, create an array of
            # authors. Otherwise, just keep the authors definition as a string.
            if sub["name"] == "AUTHORS":
                valid = True
                authors = []
                tokens = sub["value"].split()
                for idx, auth in enumerate(tokens):
                    if idx == len(tokens) - 2 and auth.lower() == "and":
                        continue
                    if not __regexp__["reference"]["author"].match(auth):
                        valid = False
                        break
                    authors.append(auth.rstrip(','))
                if valid:
                    ref["authors"] = authors
                else:
                    ref["authors"] = ' '.join(sub["value"].split())
            else:
                ref[sub["name"].lower()] = ' '.join(sub["value"].split())
        info.setdefault("references", [])
        info["references"].append(ref)

    def _info_comment(self, kw, info):
        self._assert_no_subkeys(kw, "COMMENT")
        info["comment"] = ' '.join(kw["value"].split())

    def _info_primary(self, kw, info):
        lines = kw["value"].split("\n")
        match = __regexp__["primary"]["header"].match(lines[0])
        self._assert(match, "Invalid PRIMARY header: '%s'" % lines[0].strip())
        rows = []
        for line in lines[1:]:
            match = __regexp__["primary"]["row"].match(line.strip())
            self._assert(match, "Invalid PRIMARY row: '%s'" % line.strip())
            rows.append({
                "refseq_span": {
                    "from": int(match.group("rsfrom"))-1,
                    "to": int(match.group("rsto"))-1
                },
                "ident": match.group("ident"),
                "primary_span": {
                    "from": int(match.group("prfrom"))-1,
                    "to": int(match.group("prto"))-1
                },
                "complement": (match.groupdict().has_key("comp") and match.group("comp") is not None)
            })
        info["primary"] = rows

    #
    # FEATURE TABLE PARSING
    #

    def _feature_keys(self):
        for line in self._source:
            # Initialize Feature Key Data
            if line[:1] != " ":
                self._source.undo()
                raise StopIteration
            match = __regexp__["main"]["key"].match(line)
            self._assert(match, "Failed to parse KEY from: '%s'" % line.strip())
            key = {"type": match.group("type").lower()}
        
            # Parse Location
            loc = [match.group("location")]
            loc.extend(self._location_continuation())
            key["location"] = self._location_parse(''.join(loc))
    
            # Add Qualifiers
            for q in self._feature_qualifiers():
                assert q["name"] not in ["type", "location"], "Broken assumption on qualifier names: '%s'" % q["name"]
                curr = key.get(q["name"], None)
                if curr is None:
                    key[q["name"]] = q["value"]
                elif isinstance(curr, list):
                    key[q["name"]].append(q["value"])
                else:
                    key[q["name"]] = [curr, q["value"]]

            yield key
    
    def _feature_qualifiers(self):
        for line in self._source:
            match = __regexp__["main"]["qual"].match(line)
            if not match:
                self._source.undo()
                raise StopIteration
            name = match.group("name").lower()
            value = match.group("value")
            if value is None or not value[:1] == '"' or (value[:1] == '"' and value[-1:] == '"'):
                if isinstance(value, basestring):
                    value = value.strip('"')
                elif value is None:
                    value = True
                yield {"name": name, "value": value}
            else:
                ret = {"name": name, "value": [match.group("value") or ""]}
                for cont in self._feature_continuation():
                    ret["value"].append(cont or "")
                    if cont.endswith('"'):
                        break
                ret["value"] = ' '.join(ret["value"]).strip('"')
                yield ret

    def _feature_continuation(self):
        for line in self._source:
            match = __regexp__["main"]["qual_cont"].match(line)
            if not match:
                self._source.undo()
                raise StopIteration
            yield match.group("value")
    
    #
    # SEQUENCE PARSING
    #
    
    def _sequence_base_counts(self, value):
        match = __regexp__["main"]["base_counts"].match(value)
        self._assert(match, "Failed to parse base counts: '%s'" % value.strip())
        return dict([(key, int(val)) for key, val in match.groupdict().iteritems() if val is not None])
    
    #
    # LOCATION PARSING
    #

    def _location_continuation(self):
        for line in self._source:
            match = __regexp__["main"]["loc_cont"].match(line)
            if not match:
                self._source.undo()
                raise StopIteration
            yield match.group("value")

    def _location_parse(self, loc, curr=None):
        if curr is None:
            curr = {"strand": "forward"}
        loc = loc.strip()
        for re in __regexp__["location"]:
            match = re[1].match(loc)
            if match is not None:
                fn = getattr(self, '_location_%s' % re[0])
                return fn(loc, match, curr=curr)
        raise LocationError(filename=self._source.filename,
                        lineno=self._source.lineno, mesg="Unable to parse location: '%s'" % loc )
    
    def _location_complement(self, loc, match, curr):
        curr["strand"] = "reverse"
        args = self._location_split(match.group("args"))
        self._assert(len(args) == 1, "Invalid `complement` argument list: '%s'" % match.group("args"))
        curr["strand"] = "reverse"
        self._location_parse(args[0], curr)
        return curr

    def _location_join(self, loc, match, curr):
        args = self._location_split(match.group("args"))
        self._assert(len(args) > 1, "Invalid `join` argument list: '%s'" % match.group("args"))
        curr["join"] = map(self._location_parse, args)
        return curr

    def _location_order(self, loc, match, curr):
        args = self._location_split(match.group("args"))
        self._assert(len(args) > 1, "Invalid `order` argument list: '%s'" % match.group("args"))
        curr["order"] = map(self._location_parse, args)
        return curr

    def _location_bond(self, loc, match, curr):
        args = self._location_split(match.group("args"))
        self._assert(len(args) == 2, "Invalid `bond` argument list: '%s'" % match.group("args"))
        curr["bond"] = map(lambda a: int(a)-1, args)
        return curr
    
    def _location_gap(self, loc, match, curr):
        args = self._location_split(match.group("args"))
        self._assert(len(args) == 1, "Invalid `gap` argument list: '%s'" % match.group("args"))
        curr["gap"] = int(args[0])
        return curr
        
    def _location_ref(self, loc, match, curr):
        next = {"strand": curr.pop("strand")}
        curr["reference"] = {
            self._location_parse(match.group("acc"), None): self._location_parse(match.group("args"), next)
        }
        return curr
    
    def _location_site(self, loc, match, curr):
        curr["site"] = [
            self._location_parse(match.group("start"), {}),
            self._location_parse(match.group("end"), {})
        ]
        return curr
    
    def _location_choice(self, loc, match, curr):
        curr["choice"] = [int(match.group("start"))-1, int(match.group("end"))-1]
        return curr
    
    def _location_span(self, loc, match, curr):
        curr["start"] = self._location_parse(match.group("start"), {})
        curr["end"] = self._location_parse(match.group("end"), {})
        return curr

    def _location_one_of(self, loc, match, curr):
        args = self._location_split(match.group("args"))
        self._assert(len(args) > 1, "Invalid `one-of` argument list: '%s'" % match.group("args"))
        curr["one-of"] = map(lambda a: self._location_parse(a, {}), args)
        return curr
    
    def _location_accession(self, loc, match, curr):
        return loc

    def _location_single(self, loc, match, curr):
        if loc[:1] == "<":
            curr["fuzzy"] = "before"
            curr["coord"] = int(loc[1:])-1
        elif loc[:1] == ">":
            curr["fuzzy"] = "after"
            curr["coord"] = int(loc[1:])-1
        else:
            curr["fuzzy"] = False
            curr["coord"] = int(loc)-1
        return curr

    def _location_split(self, args):
        count = 0
        last = 0
        ret = []
        for i in range(0, len(args)):
            if args[i] == '(':
                count += 1
            elif args[i] == ')':
                count -= 1
            elif args[i] == ',':
                if count == 0:
                    ret.append(args[last:i])
                    last = i+1
        if count != 0:
            raise LocationError(filename=self._source.filename,
                                lineno=self._source.lineno, mesg="Unbalanced parenthesis: '%s'" % args)
        ret.append(args[last:])
        return ret

    #
    # INTERNAL UTILITIES
    #

    def _next_record(self):
        for line in self._source:
            if line.strip() == '//':
                self._state = self.RESET
                break
        self._state = self.FINISHED
    
    def _skip_blank(self):
        for line in self._source:
            if line.strip():
                self._source.undo()
                return
        self._state = self.FINISHED
    
    def _skip_features(self):
        self.info()
        for line in self._source:
            if not line.startswith("FEATURES") and not line[:1] == " ":
                self._source.undo()
                self._state = self.FEATURES
                return
        self._raise("Unexpected EOF while skipping features section.")

    def _assert(self,cond,msg):
        if not cond:
            self._raise(msg)
    
    def _assert_no_subkeys(self, kw, ktype):
        self._assert(len(kw["subkeys"]) == 0, "%s lines should not have subkeyword sections." % ktype)
    
    def _raise(self,msg):
        raise GenbankError(filename=self._source.filename, lineno=self._source.lineno, mesg=msg)

__regexp__ = {
    "main": {
        "features":         re.compile(r"^FEATURES\s+Location/Qualifiers$"),
        "keyword":          re.compile(r"^(?P<name>((BASE COUNT)|([A-Z]+)))\s+(?P<value>.*)$"),
        "subkeyword":       re.compile(r"^\s{2,3}(?P<name>[A-Z]+)\s+(?P<value>.*)$"),
        "continuation":     re.compile(r"^\s{12}(?P<value>.*)$"),
        "key":              re.compile(r"^\s{5}(?P<type>\S+)\s+(?P<location>\S.*)$"),
        "qual":             re.compile(r"^\s{21}/(?P<name>[^\s=]+)(=(?P<value>.+))?$"),
        "loc_cont":         re.compile(r"^\s{21}(?!/[^\s=]+(=.+)?$)(?P<value>.+)$"),
        "qual_cont":        re.compile(r"^\s{21}(?P<value>.*)$"),
        "sequence":         re.compile(r"^\s*\d+\s(?P<value>.*)"),
        "base_counts":      re.compile(r"""
                                    ^
                                    (?P<A>\d+)\s[aA]\s*
                                    (?P<C>\d+)\s[cC]\s*
                                    (?P<G>\d+)\s[gG]\s*
                                    (?P<T>\d+)\s[tT]
                                    (\s*(?P<others>\d+)\s[oO][tT][hH][eE][rR][sS])?
                                    $
                                """, re.VERBOSE),
    },
    "locus": {
        "length":           re.compile(r"^(?P<value>\d+)$"),
        "type":             re.compile(r"^(?P<value>(aa|bp))$"),
        "molecule_type":    re.compile(r"^(?P<value>(ss-|ds-|ms-)?(NA|DNA|RNA|tRNA|rRNA|mRNA|uRNA|snRNA|snoRNA))$"),
        "strand_type":      re.compile(r"^(?P<value>(linear|circular))$"),
        "division":         re.compile(r"""^(?P<value>(
                                      PRI | ROD | MAM | VRT | INV
                                    | PLN | BCT | VRL | PHG | SYN
                                    | UNA | EST | PAT | STS | GSS
                                    | HTG | HTC | ENV | CON))$""", re.VERBOSE)
    },
    "version": {
        "gi":               re.compile(r"^GI:(?P<value>\d+)$"),
    },
    "segment": {
        "position":         re.compile(r"^(?P<value>\d+)\sof\s(?P<total>\d+)$")
    },
    "reference": {
        "location":         re.compile(r"(?P<id>\d+)\s+\((bases|residues)\s+(?P<start>\d+)\s+to\s+(?P<end>\d+)"),
        "author":           re.compile(r"^[^\s,]+,[^\s,]+,?$"),
    },
    "primary": {
        "header":           re.compile(r"^REFSEQ_SPAN\s+PRIMARY_IDENTIFIER\s+PRIMARY_SPAN\s+COMP$"),
        "row":              re.compile(r"""
                                    ^(?P<rsfrom>\d+)-(?P<rsto>\d+) # RefSeq span
                                    \s+
                                    (?P<ident>[^\s]+) # Identifier
                                    \s+
                                    (?P<prfrom>\d+)-(?P<prto>\d+) # Primary Span
                                    (\s+(?P<comp>[^\s]+))?$ # Optional complement info
                            """, re.VERBOSE),
    },
    "location": [
        ("complement",      re.compile(r"^complement\((?P<args>.*)\)$")),
        ("join",            re.compile(r"^join\((?P<args>.*)\)$")),
        ("order",           re.compile(r"^order\((?P<args>.*)\)$")),
        ("bond",            re.compile(r"^bond\((?P<args>.*)\)$")),
        ("gap",             re.compile(r"^gap\((?P<args>\d+)\)$")),
        ("ref",             re.compile(r"^(?P<acc>[^:]+):(?P<args>.*)$")),
        ("site",            re.compile(r"^(?P<start>[^.]*)\^(?P<end>[^.]*)$")),
        ("choice",          re.compile(r"^(?P<start>\d+)\.(?P<end>\d+)$")),
        ("span",            re.compile(r"^(?P<start>[^.]*)\.\.(?P<end>[^.]*)$")),
        ("one_of",          re.compile(r"^one-of\((?P<args>.*)\)$")),
        ("single",          re.compile(r"^[<>]?\d+$")),
        ("accession",       re.compile(r"^[A-Z0-9_]+(\.\d+)?$")),
    ]
}
