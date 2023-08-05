#! /usr/bin/env python

# Copyright (c) 2006 L. C. Rees.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 3.  Neither the name of the Portable Site Information Project nor the names
# of its contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
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

'''Doctests for webstring text'''

def _test():
    '''
    >>> from webstring import Template
    >>> example = Template("""<rss version="2.0">
    ...  <channel>
    ...   <title>Example</title>
    ...   <link>http://www.example.org/</link>
    ...   <description>RSS Example</description>
    ...   <language>en-us</language>
    ...   $$cpubdate<pubDate>$month$ $day$, $year$</pubDate>$$
    ...   $$lastbuilddate<lastBuildDate>$month$ $day$, $year$</lastBuildDate>$$
    ...   $$item<item>
    ...    <title>$title$</title>
    ...    <link>$link$</link>
    ...    <guid isPermaLink="true">$guid$</guid>
    ...    <description>$description$</description>
    ...    <pubDate>$ipubdate$</pubDate>
    ...   </item>
    ...  $$</channel>
    ... </rss>""", format='text')
    >>> example.exclude('cpubdate') 
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <lastBuildDate> , </lastBuildDate>
      <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     </channel>
    </rss>
    >>> example.include('cpubdate') 
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate> , </pubDate>
      <lastBuildDate> , </lastBuildDate>
      <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     </channel>
    </rss>
    >>> example.cpubdate %= {'month':'June', 'day':'06', 'year':'2006'}
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate>June 06, 2006</pubDate>
      <lastBuildDate> , </lastBuildDate>
      <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     </channel>
    </rss>
    >>> example.lastbuilddate %= {'month':'June', 'day':'06', 'year':'2006'}
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate>June 06, 2006</pubDate>
      <lastBuildDate>June 06, 2006</lastBuildDate>
      <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     </channel>
    </rss>
    >>> example.item.description.text = 'Example of assigning text to a field.' 
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate>June 06, 2006</pubDate>
      <lastBuildDate>June 06, 2006</lastBuildDate>
      <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description>Example of assigning text to a field.</description>
       <pubDate></pubDate>
      </item>
     </channel>
    </rss>
    >>> example.item.link.text = 'http://www.example.com/rss/5423093'
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate>June 06, 2006</pubDate>
      <lastBuildDate>June 06, 2006</lastBuildDate>
      <item>
       <title></title>
       <link>http://www.example.com/rss/5423093</link>
       <guid isPermaLink="true"></guid>
       <description>Example of assigning text to a field.</description>
       <pubDate></pubDate>
      </item>
     </channel>
    </rss>
    >>> example.item.title.text = 'Example Title: First Example'
    >>> example.item.ipubdate.text = 'June 6, 2006'
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate>June 06, 2006</pubDate>
      <lastBuildDate>June 06, 2006</lastBuildDate>
      <item>
       <title>Example Title: First Example</title>
       <link>http://www.example.com/rss/5423093</link>
       <guid isPermaLink="true"></guid>
       <description>Example of assigning text to a field.</description>
       <pubDate>June 6, 2006</pubDate>
      </item>
     </channel>
    </rss>
    >>> example.item.guid.text = 'http://www.example.com/rss/5423093'
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate>June 06, 2006</pubDate>
      <lastBuildDate>June 06, 2006</lastBuildDate>
      <item>
       <title>Example Title: First Example</title>
       <link>http://www.example.com/rss/5423093</link>
       <guid isPermaLink="true">http://www.example.com/rss/5423093</guid>
       <description>Example of assigning text to a field.</description>
       <pubDate>June 6, 2006</pubDate>
      </item>
     </channel>
    </rss>
    >>> example.reset()
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate> , </pubDate>
      <lastBuildDate> , </lastBuildDate>
      <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     </channel>
    </rss>
    >>> example %= {
    ... 'cpubdate':{'month':'June', 'day':'06', 'year':'2006'}, 
    ... 'lastbuilddate':{'month':'June', 'day':'06', 'year':'2006'},
    ... 'item':{'title':'Example Title: First Example',
    ...     'link':'http://www.example.com/rss/5423093',
    ...     'guid':'http://www.example.com/rss/5423093',
    ...     'description':'Example of assigning text to a field.',
    ...     'ipubdate':'June 6, 2006'}}
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate>June 06, 2006</pubDate>
      <lastBuildDate>June 06, 2006</lastBuildDate>
      <item>
       <title>Example Title: First Example</title>
       <link>http://www.example.com/rss/5423093</link>
       <guid isPermaLink="true">http://www.example.com/rss/5423093</guid>
       <description>Example of assigning text to a field.</description>
       <pubDate>June 6, 2006</pubDate>
      </item>
     </channel>
    </rss>
    >>> print example.current
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate>June 06, 2006</pubDate>
      <lastBuildDate>June 06, 2006</lastBuildDate>
      <item>
       <title>Example Title: First Example</title>
       <link>http://www.example.com/rss/5423093</link>
       <guid isPermaLink="true">http://www.example.com/rss/5423093</guid>
       <description>Example of assigning text to a field.</description>
       <pubDate>June 6, 2006</pubDate>
      </item>
     </channel>
    </rss>
    >>> print example.default
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate> , </pubDate>
      <lastBuildDate> , </lastBuildDate>
      <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     </channel>
    </rss>
    >>> example.reset()
    >>> print example + example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate> , </pubDate>
      <lastBuildDate> , </lastBuildDate>
      <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     </channel>
    </rss><rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate> , </pubDate>
      <lastBuildDate> , </lastBuildDate>
      <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     </channel>
    </rss>
    >>> print example.item + example.item
    <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
    <BLANKLINE>
    >>> print example.item.title + example.item.title
    <BLANKLINE>
    >>> example.item += example.item
    >>> print example.item
    <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
    <BLANKLINE>
    >>> example.reset()
    >>> example.item.repeat()
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate> , </pubDate>
      <lastBuildDate> , </lastBuildDate>
      <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     </channel>
    </rss>
    >>> example.reset()
    >>> example.item *= 2
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate> , </pubDate>
      <lastBuildDate> , </lastBuildDate>
      <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     <item>
       <title></title>
       <link></link>
       <guid isPermaLink="true"></guid>
       <description></description>
       <pubDate></pubDate>
      </item>
     </channel>
    </rss>
    >>> example.reset()
    >>> example.item %= ('Example Title: First Example', 'http://www.example.com/rss/5423092', 'http://www.example.com/rss/5423092', 'Example of assigning text to a field.', 'June 06, 2006')
    >>> example.item.repeat(('Example Title: Second Example', 'http://www.example.com/rss/5423093', 'http://www.example.com/rss/5423093', 'Example of group repetition.', 'June 06, 2006'))
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate> , </pubDate>
      <lastBuildDate> , </lastBuildDate>
      <item>
       <title>Example Title: First Example</title>
       <link>http://www.example.com/rss/5423092</link>
       <guid isPermaLink="true">http://www.example.com/rss/5423092</guid>
       <description>Example of assigning text to a field.</description>
       <pubDate>June 06, 2006</pubDate>
      </item>
     <item>
       <title>Example Title: Second Example</title>
       <link>http://www.example.com/rss/5423093</link>
       <guid isPermaLink="true">http://www.example.com/rss/5423093</guid>
       <description>Example of group repetition.</description>
       <pubDate>June 06, 2006</pubDate>
      </item>
     </channel>
    </rss>
    >>> example.reset()
    >>> example.item **= (('Example Title: First Example', 'http://www.example.com/rss/5423092', 'http://www.example.com/rss/5423092', 'Example of assigning text to a field.', 'June 06, 2006'),
    ... ('Example Title: Second Example', 'http://www.example.com/rss/5423093', 'http://www.example.com/rss/5423093', 'Example of group repetition.', 'June 06, 2006'))
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate> , </pubDate>
      <lastBuildDate> , </lastBuildDate>
      <item>
       <title>Example Title: First Example</title>
       <link>http://www.example.com/rss/5423092</link>
       <guid isPermaLink="true">http://www.example.com/rss/5423092</guid>
       <description>Example of assigning text to a field.</description>
       <pubDate>June 06, 2006</pubDate>
      </item>
     <item>
       <title>Example Title: Second Example</title>
       <link>http://www.example.com/rss/5423093</link>
       <guid isPermaLink="true">http://www.example.com/rss/5423093</guid>
       <description>Example of group repetition.</description>
       <pubDate>June 06, 2006</pubDate>
      </item>
     </channel>
    </rss>
    >>> example.cpubdate %= {'month':'June', 'day':'06', 'year':'2006'}
    >>> example.lastbuilddate %= {'month':'June', 'day':'06', 'year':'2006'}
    >>> print example
    <rss version="2.0">
     <channel>
      <title>Example</title>
      <link>http://www.example.org/</link>
      <description>RSS Example</description>
      <language>en-us</language>
      <pubDate>June 06, 2006</pubDate>
      <lastBuildDate>June 06, 2006</lastBuildDate>
      <item>
       <title>Example Title: First Example</title>
       <link>http://www.example.com/rss/5423092</link>
       <guid isPermaLink="true">http://www.example.com/rss/5423092</guid>
       <description>Example of assigning text to a field.</description>
       <pubDate>June 06, 2006</pubDate>
      </item>
     <item>
       <title>Example Title: Second Example</title>
       <link>http://www.example.com/rss/5423093</link>
       <guid isPermaLink="true">http://www.example.com/rss/5423093</guid>
       <description>Example of group repetition.</description>
       <pubDate>June 06, 2006</pubDate>
      </item>
     </channel>
    </rss>'''
    import doctest
    doctest.testmod()

if __name__ == "__main__": _test()
