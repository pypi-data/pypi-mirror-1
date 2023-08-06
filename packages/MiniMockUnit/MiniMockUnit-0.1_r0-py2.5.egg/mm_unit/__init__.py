# Copyright (c) 2009, James Brady, WebMynd Corp.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the WebMynd Corp. nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from minimock import Printer
import doctest

__all__ = ['TraceTracker', 'assert_same_trace']

class TraceTracker(Printer):
    """
    Keeps track of the usage of a MiniMock-ed object, and allows for that usage
    to be analysed after the fact.
    """
    def __init__(self, *args, **kw):
        self.out = StringIO()
        super(TraceTracker, self).__init__(self.out, *args, **kw)
        self.checker = doctest.OutputChecker()
        self.options =  doctest.ELLIPSIS
        self.options |= doctest.NORMALIZE_WHITESPACE
        self.options |= doctest.REPORT_UDIFF
        
    def check(self, want):
        """
        Compare expected MiniMock usage with that which we expected.
        
        :param want: the MiniMock output that results from expected usage of
            mocked objects
        :type want: string
        :rtype: a ``True`` value if the check passed, ``False`` otherwise
        
        Example::
        
            >>> from minimock import Mock
            >>> tt = TraceTracker()
            >>> m = Mock('mock_obj', tracker=tt)
            >>> m.some_meth('dummy argument')
            >>> tt.check("Called mock_obj.some_meth('dummy argument')")
            True
            >>> tt.check("Failing expected trace")
            False
        """
        return self.checker.check_output(want, self.dump(),
            optionflags=self.options)
        
    def diff(self, want):
        """
        Compare expected MiniMock usage with that which we expected.
        
        :param want: the MiniMock output that results from expected usage of
            mocked objects
        :type want: string
        :rtype: a ``True`` value if the check passed, ``False`` otherwise
        
        Example::
        
            >>> from minimock import Mock
            >>> tt = TraceTracker()
            >>> m = Mock('mock_obj', tracker=tt)
            >>> m.some_meth('dummy argument')
            >>> tt.diff("Dummy string")
            "Expected:\\n    Dummy string\\nGot:\\n    Called mock_obj.some_meth('dummy argument')\\n"
        """
        return self.checker.output_difference(doctest.Example("", want),
            self.dump(), optionflags=self.options)
        
    def dump(self):
        """
        Return the MiniMock usage so far.
        
        Example::
        
            >>> from minimock import Mock
            >>> tt = TraceTracker()
            >>> m = Mock('mock_obj', tracker=tt)
            >>> m.some_meth('dummy argument')
            >>> tt.dump()
            "Called mock_obj.some_meth('dummy argument')\\n"
        """
        return self.out.getvalue()
        
def assert_same_trace(tracker, want):
    """
    Check the usage of a :class:`mm_unit.TraceTracker` is as expected.
    
    :param tracker: a :class:`mm_unit.TraceTracker` instance
    :param want: the expected MiniMock output
    :type want: string
    :raises: :exc:`AssertionError` if the expected and observed outputs don't
        match
    
    Example::
    
            >>> from minimock import Mock
            >>> tt = TraceTracker()
            >>> m = Mock('mock_obj', tracker=tt)
            >>> m.some_meth('dummy argument')
            >>> assert_same_trace(tt,
            ...     "Called mock_obj.some_meth('dummy argument')\\n")
    """
    assert tracker.check(want), tracker.diff(want)
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()