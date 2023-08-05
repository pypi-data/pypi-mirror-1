# -*- coding: utf-8 -*-
"""
    jinja tag parser
"""
from jinja.tokens import *
from jinja.exceptions import TagLexerError


# Lexer constants.
STATE_SEP_WS, STATE_START, STATE_START_SEP, STATE_NONE_BOOL_NAME, \
                STATE_OCT_HEX_ZERO, STATE_OCT, STATE_HEX, STATE_INT, \
                STATE_STRINGSINGLEQUOTE, STATE_STRINGSINGLEQUOTEESCAPE, \
                STATE_STRINGDOUBLEQUOTE, STATE_STRINGDOUBLEQUOTEESCAPE = \
                range(12)
ERROR_KEEP = 20

# Parser constants.
CHAIN_PROVIDER, CHAIN_FILTER, CHAIN_ANY = 1, 2, 3


class Lexer(object):
    """Lexer class for tokenizing a string of input into the tokens defined
    above. This is a feed-lexer, meaning that you feed input using the feed()
    function and have to finish input by calling finish(). This makes it
    suitable to parsing unknown-length input.

    Getting tokens is done by calling the pop() method, which pops a certain
    number of tokens from the list of read tokens."""

    def __init__(self):
        """Initialize the lexer."""
        self._state = STATE_START
        self._tokens = []
        self._tokenpos = 0
        self._databuffer = []
        self._curpos = 0
        self._buffer = []
        self._invalid = False
        self._finished = False

    def feed(self, data):
        """Feed data to the lexer. A lexer can only be fed data if it is
        not invalid or finished. In case you try to feed data to the lexer
        in one of the previously mentioned states, a RuntimeError is raised.
        In case the lexer encounters invalid data, a TagLexerError (which is a
        subclass of ValueError) is raised and the lexer is put into invalid
        mode."""

        if self._invalid:
            raise RuntimeError('Cannot feed to invalidated lexer.')
        if self._finished:
            raise RuntimeError('Cannot feed to finished lexer.')

        self._databuffer.append(data)
        pos = 0
        for pos, c in enumerate(data):
            pos += self._curpos
            if self._state == STATE_SEP_WS:
                if c == ',':
                    self._tokens.append(CommaVal())
                    self._state = STATE_START
                elif c == '|':
                    self._tokens.append(PipeVal())
                    self._state = STATE_START
                elif not c.isspace():
                    self._invalid = True
                    raise TagLexerError('Expected separator or whitespace', pos,
                                     self._databuffer)
                else:
                    self._state = STATE_START_SEP
            elif self._state in (STATE_START, STATE_START_SEP):
                if c.isalpha() or c == '_':
                    self._buffer.append(c)
                    self._state = STATE_NONE_BOOL_NAME
                elif c == '0':
                    self._buffer.append(c)
                    self._state = STATE_OCT_HEX_ZERO
                elif c.isdigit():
                    self._buffer.append(c)
                    self._state = STATE_INT
                elif c == '\'':
                    self._buffer.append(c)
                    self._state = STATE_STRINGSINGLEQUOTE
                elif c == '"':
                    self._buffer.append(c)
                    self._state = STATE_STRINGDOUBLEQUOTE
                elif c == ',' and self._state == STATE_START_SEP:
                    self._tokens.append(CommaVal())
                    self._state = STATE_START
                elif c == '|' and self._state == STATE_START_SEP:
                    self._tokens.append(PipeVal())
                    self._state = STATE_START
                elif not c.isspace():
                    self._invalid = True
                    if self._state == STATE_START_SEP:
                        raise TagLexerError('Expected token or separator', pos,
                                            self._databuffer)
                    else:
                        raise TagLexerError('Expected token', pos,
                                            self._databuffer)
            elif self._state == STATE_NONE_BOOL_NAME:
                if c.isalnum() or c in '._':
                    self._buffer.append(c)
                elif c.isspace() or c in ',|':
                    val = ''.join(self._buffer)
                    if val.lower() == 'none':
                        self._tokens.append(NoneVal(val))
                    elif val.lower() in ('false', 'true'):
                        self._tokens.append(BoolVal(val))
                    else:
                        self._tokens.append(NameVal(val))
                    self._buffer = []
                    if c == ',':
                        self._tokens.append(CommaVal())
                        self._state = STATE_START
                    elif c == '|':
                        self._tokens.append(PipeVal())
                        self._state = STATE_START
                    else:
                        self._state = STATE_START_SEP
                else:
                    self._invalid = True
                    raise TagLexerError('Expected name or separator', pos,
                                        self._databuffer)
            elif self._state == STATE_OCT_HEX_ZERO:
                if c in '01234567':
                    self._buffer.append(c)
                    self._state = STATE_OCT
                elif c in 'xX':
                    self._buffer.append(c)
                    self._state = STATE_HEX
                elif c.isspace() or c in ',|':
                    val = "".join(self._buffer)
                    self._tokens.append(IntVal(val, 10))
                    self._buffer = []
                    if c == ',':
                        self._tokens.append(CommaVal())
                        self._state = STATE_START
                    elif c == '|':
                        self._tokens.append(PipeVal())
                        self._state = STATE_START
                    else:
                        self._state = STATE_START_SEP
                else:
                    self._invalid = True
                    raise TagLexerError('Expected digit or separator', pos,
                                        self._databuffer)
            elif self._state == STATE_OCT:
                if c in '01234567':
                    self._buffer.append(c)
                elif c.isspace() or c in ',|':
                    val = ''.join(self._buffer)
                    self._tokens.append(IntVal(val, 8))
                    self._buffer = []
                    if c == ',':
                        self._tokens.append(CommaVal())
                        self._state = STATE_START
                    elif c == '|':
                        self._tokens.append(PipeVal())
                        self._state = STATE_START
                    else:
                        self._state = STATE_START_SEP
                else:
                    self._invalid = True
                    raise TagLexerError('Expected octal digit or separator',
                                        pos, self._databuffer)
            elif self._state == STATE_HEX:
                if c.isdigit() or c in 'aAbBcCdDeEfF':
                    self._buffer.append(c)
                elif c.isspace() or c in ',|':
                    val = ''.join(self._buffer)
                    self._tokens.append(IntVal(val, 16))
                    self._buffer = []
                    if c == ',':
                        self._tokens.append(CommaVal())
                        self._state = STATE_START
                    elif c == '|':
                        self._tokens.append(PipeVal())
                        self._state = STATE_START
                    else:
                        self._state = STATE_START_SEP
                else:
                    self._invalid = True
                    raise TagLexerError('Expected hex digit or separator', pos,
                                        self._databuffer)
            elif self._state == STATE_INT:
                if c.isdigit():
                    self._buffer.append(c)
                elif c.isspace() or c in ',|':
                    val = ''.join(self._buffer)
                    self._tokens.append(IntVal(val, 10))
                    self._buffer = []
                    if c == ',':
                        self._tokens.append(CommaVal())
                        self._state = STATE_START
                    elif c == '|':
                        self._tokens.append(PipeVal())
                        self._state = STATE_START
                    else:
                        self._state = STATE_START_SEP
                else:
                    self._invalid = True
                    raise TagLexerError('Expected decimal digit or separator',
                                        pos, self._databuffer)
            elif self._state == STATE_STRINGSINGLEQUOTE:
                if c == '\\':
                    self._buffer.append(c)
                    self._state = STATE_STRINGSINGLEQUOTEESCAPE
                elif c == '\'':
                    self._buffer.append(c)
                    val = ''.join(self._buffer)
                    self._tokens.append(StringVal(val))
                    self._buffer = []
                    self._state = STATE_SEP_WS
                else:
                    self._buffer.append(c)
            elif self._state == STATE_STRINGSINGLEQUOTEESCAPE:
                if c == '\n':
                    self._buffer.pop()
                else:
                    self._buffer.append(c)
                self._state = STATE_STRINGSINGLEQUOTE
            elif self._state == STATE_STRINGDOUBLEQUOTE:
                if c == '\\':
                    self._buffer.append(c)
                    self._state = STATE_STRINGDOUBLEQUOTEESCAPE
                elif c == '"':
                    self._buffer.append(c)
                    val = ''.join(self._buffer)
                    self._tokens.append(StringVal(val))
                    self._buffer = []
                    self._state = STATE_SEP_WS
                else:
                    self._buffer.append(c)
            elif self._state == STATE_STRINGDOUBLEQUOTEESCAPE:
                if c == '\n':
                    self._buffer.pop()
                else:
                    self._buffer.append(c)
                self._state = STATE_STRINGDOUBLEQUOTE
        self._curpos = pos+1

    def finish(self):
        """Finish the lexing. A lexer can only be finished in case it is not
        invalid. Finishing a finished lexer will have no effect. Trying to
        finish an invalid Lexer will raise a RuntimeError, a processing
        error in the lexer will result in a TagLexerError, which is a subclass
        of ValueError."""

        if self._invalid:
            raise RuntimeError('Cannot finish invalidated lexer.')
        if self._finished:
            return

        if self._state == STATE_NONE_BOOL_NAME:
            val = ''.join(self._buffer)
            if val.lower() == 'none':
                self._tokens.append(NoneVal(val))
            elif val.lower() in ('false', 'true'):
                self._tokens.append(BoolVal(val))
            else:
                self._tokens.append(NameVal(val))
            self._buffer = []
        elif self._state == STATE_OCT_HEX_ZERO:
            val = ''.join(self._buffer)
            self._tokens.append(IntVal(val, 10))
            self._buffer = []
        elif self._state == STATE_OCT:
            val = ''.join(self._buffer)
            self._tokens.append(IntVal(val, 8))
            self._buffer = []
        elif self._state == STATE_HEX:
            val = ''.join(self._buffer)
            self._tokens.append(IntVal(val, 16))
            self._buffer = []
        elif self._state == STATE_INT:
            val = ''.join(self._buffer)
            self._tokens.append(IntVal(val, 10))
            self._buffer = []
        elif self._state not in (STATE_SEP_WS,STATE_START_SEP):
            self._invalid = True
            if self._state == STATE_START:
                raise TagLexerError('No data or dangling separator',
                                    self._curpos, self._databuffer)
            else:
                raise TagLexerError('String not closed',
                                    self._curpos, self._databuffer)

        self._finished = True

    def pop(self, n=1):
        """Pops n tokens from the current token stack. The tokens are returned
        as a list in case n <> 1, if n == 1 the actual token is returned.
        In case no tokens are available, it raises a ValueError. In case you
        request more than one token, returns as many tokens as are available.
        For the special case n == 0 it returns True or False depending on
        whether there are tokens available."""

        if self._invalid:
            raise RuntimeError('Cannot pop tokens from invalid lexer.')

        if n == 0:
            rv = self._tokenpos < len(self._tokens)
        elif n == 1:
            if self._tokenpos == len(self._tokens):
                raise ValueError('No tokens available.')
            rv = self._tokens[self._tokenpos]
            self._tokenpos += 1
        else:
            if self._tokenpos == len(self._tokens):
                raise ValueError('No tokens available.')
            rv = self._tokens[self._tokenpos:self._tokenpos + n]
            self._tokenpos += len(rv)
        return rv

    def __repr__(self):
        if self._finished:
            return '<%s: %r>' % (self.__class__.__name__, self._tokens)
        else:
            return '<%s: running>' % self.__class__.__name__


class Parser(object):

    def __init__(self, rules=None):
        if rules is None:
            rules = {}
        self._lexer = Lexer()
        self._chains = dict([(name, (state, chain[:])) for name, (state, chain)
                             in rules.iteritems()])
        self._curchains = dict([(name, chain[:]) for name, (state, chain) in
                               self._chains.iteritems() if
                               state & CHAIN_PROVIDER])
        self._output = []
        self._curoutput = {}
        self._scores = {}
        self._invalid = False
        self._finished = False

    def feed(self, data):
        if self._invalid:
            raise RuntimeError, 'Cannot feed to invalidated parser.'
        if self._finished:
            raise RuntimeError, 'Cannot feed to finished parser.'
        try:
            self._lexer.feed(data)
        except RuntimeError:
            self._invalid = True
            raise
        self._process_feed()

    def finish(self):
        if self._invalid:
            raise RuntimeError, 'Cannot finish invalidated parser.'
        if self._finished:
            return
        try:
            self._lexer.finish()
        except RuntimeError:
            self._invalid = True
            raise
        self._process_feed()
        self._finish_chains()
        self._finished = True
        
    def collect(self):
        if self._invalid:
            raise RuntimeError, 'Cannot collect data from invalided parser.'
        return self._output

    def _finish_chains(self):
        # Remove all chains that didn't eat all tokens.
        to_delete = []
        expected = []
        for name, chain in self._curchains.iteritems():
            if chain:
                # Eat any possible left opening bracket in case there are no
                # more tokens available.
                if isinstance(chain[0], tuple):
                    # Continue chain.
                    if chain[0][1] is None:
                        del self._curoutput[name][-1][0]
                        continue
                    chain[0] = chain[0][1]

                # Remove possible remaining star reference.
                if ( self._curoutput[name] and
                     isinstance(self._curoutput[name][-1],list) and
                     self._curoutput[name][-1] and
                     self._curoutput[name][-1][0] is chain[0] ):
                    del self._curoutput[name][-1][0]

                # Eat the chain until it stops.
                while chain:
                    score, match, _ = chain[0].match(None)
                    if match is not None:
                        self._curoutput.setdefault(name, [])
                        if ( self._curoutput[name] and
                             isinstance(self._curoutput[name][-1], list) and
                             self._curoutput[name][-1][0] is chain[0] ):
                            self._curoutput[name][-1].extend(match)
                            del self._curoutput[name][-1][0]
                        else:
                            self._curoutput[name].append(match)
                        self._scores[name] = self._scores.get(name, 0) + score
                        chain.pop(0)
                    else:
                        break

                # If anything left on chain, this chain didn't match.
                if chain:
                    expected.append((name, chain[0]))
                    to_delete.append(name)
        for name in to_delete:
            try:
                del self._curchains[name]
                del self._curoutput[name]
                del self._scores[name]
            except KeyError:
                pass

        # Check whether there are any chains left.
        if not self._curchains:
            self._invalid = True
            raise RuntimeError('Found no token, but expected one of %s.' %
                               expected)

        # Get chain with highest score. Scoring rules are part of the nodes
        # return values.
        bestchain = max(zip(self._scores.values(), self._scores.keys()))[1]
        self._output.append((bestchain, self._curoutput[bestchain]))

        # Reset state, this time use only those chains that are allowed to
        # act as filters.
        self._curchains = dict([(name, chain[:]) for name, (state, chain) in
                                self._chains.iteritems() if
                                state & CHAIN_FILTER])
        self._curoutput = {}
        self._scores = {}

    def _process_feed(self):
        skip = False
        while self._curchains:
            skip = True
            expected = []
            to_delete = []
            if not self._lexer._tokens:
                break
            token = self._lexer._tokens.pop(0)

            # Continue right away if we get a PipeVal which separates commands.
            if isinstance(token, PipeVal):
                self._finish_chains()
                continue

            # Update chains with new state if it's something else.
            for name, chain in self._curchains.iteritems():
                # Loop until we truly have a match and no epsilon production.
                # An epsilon production is always tried in case a match fails.
                while True:
                    # Check whether chain has any items left to match.
                    if not chain:
                        to_delete.append(name)
                        break

                    curmatch = chain.pop(0)

                    # If we have a continuation (left open), try to match
                    # nexttoken and reinsert whatever it tells us to. If no
                    # match, continue with alternate token.
                    if isinstance(curmatch, tuple):
                        _, _, nexttoken = curmatch[0].match(token)
                        if nexttoken is not None:
                            chain.insert(0, curmatch[1])
                            chain.insert(0, nexttoken)
                            break
                        else:
                            del self._curoutput[name][-1][0]
                            curmatch = curmatch[1]
                            if curmatch is None:
                                to_delete.append(name)
                                break

                    # Try to match to current token if we had no continuation
                    # or the actual continuation failed.
                    score, match, nexttoken = curmatch.match(token)
                    if match is not None:
                        self._curoutput.setdefault(name, [])
                        if nexttoken:
                            if chain:
                                chain[0] = (nexttoken, chain[0])
                            else:
                                chain.append((nexttoken, None))
                            if ( self._curoutput[name] and
                                 isinstance(self._curoutput[name][-1],list) and
                                 self._curoutput[name][-1] and
                                 self._curoutput[name][-1][0] is curmatch ):
                                self._curoutput[name][-1].extend(match)
                            else:
                                self._curoutput[name].append(match)
                                self._curoutput[name][-1].insert(0, curmatch)
                        else:
                            self._curoutput[name].append(match)
                        self._scores[name] = self._scores.get(name, 0) + score
                        break
                    else:
                        # Try to match epsilon production.
                        score, match, _ = curmatch.match(None)
                        if match is not None:
                            self._curoutput.setdefault(name, [])
                            if ( self._curoutput[name] and
                                 isinstance(self._curoutput[name][-1], list) and
                                 self._curoutput[name][-1] and
                                 self._curoutput[name][-1][0] is curmatch ):
                                self._curoutput[name][-1].extend(match)
                                del self._curoutput[name][-1][0]
                            else:
                                self._curoutput[name].append(match)
                            self._scores[name] = ( self._scores.get(name, 0) +
                                                   score )
                        else:
                            expected.append((name, curmatch))
                            to_delete.append(name)
                            break

            # Delete all chains that have not matched.
            for name in to_delete:
                try:
                    del self._curchains[name]
                    del self._curoutput[name]
                    del self._scores[name]
                except KeyError:
                    pass

        # If we have no more possible states, parsing has failed.
        if not self._curchains:
            self._invalid = True
            if not skip:
                raise RuntimeError, 'No chains found'
            elif not expected:
                raise RuntimeError('Found dangling %s for %s' %
                                   (token,to_delete))
            else:
                raise RuntimeError('Expected one of %s, found %s' %
                                   (expected,token))

    def __repr__(self):
        return '<%s: output %r>' % (self.__class__.__name__, self._output)
