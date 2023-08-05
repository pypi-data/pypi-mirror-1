Description of ks.pager :

  Author -- Anatoly Bubenkov

  Version -- $Id: README.txt 23735 2007-11-08 18:22:32Z anatoly $

  URL -- $URL: https://code.keysolutions.ru/svn/ks.pager/trunk/src/ks/pager/README.txt $

  Annotation:

    Product ks.pager allows view creation with paged listing of elements(objects).

  Realization idea:

    Product consists of such parts:

        - Base view adapter pager, it's a adapter factory for iterable object.
          Adapter factory provides IPagerFactory interface:

            - init(iterable) -- get adapter to IPager;

        - Base adapter of iterable object and request zope.publisher.interfaces.http.IHTTPRequest
          to IPagerParams pager parameters interface:

          - start -- start element of chunk;

          - chunkSize -- size of chunk;

          - chunkCount -- chunk link count on one page;

          This adapter called by adapter factory IPagerFactory.

        - Base adapter of iterable object to paged source interface IPagedSource:

          - getCount() -- count of all elements in object;

          - getChunk(start, chunkSize) -- get chunk with size chunkSize and start with start;

          This adapter called by adapter factory IPagerFactory. Abstraction is needed
          for cases, when element source supports paged output (sql, for example).

        - Base adapter of paged source IPagedSource,
          pager params IPagerParams
          and request zope.publisher.interfaces.http.IHTTPRequest to IPager:

          - nextChunkUrl() -- link to next chunk;

          - prevChunkUrl() -- link to previous chunk;

          - haveNextChunk() -- flag "have next chunk";

          - havePrevChunk() -- flag "have previous chunk";

          - chunkUrlList() -- chunk url list (tuple (page number, link));

          - сhunk() -- element chunk;

          - сount() -- full element count;

          - lastChunkUrl() -- link to last chunk;

          - firstChunkUrl() -- link to first chunk;

          - onFirstChunk() -- flag "on first chunk";

          - onLastChunk() -- flag "on last chunk";

          This adapter called by adapter factory IPagerFactory.

        - Base macros listing for comfort using of pager.

     Example of using in page template::

        <tal:block tal:define="pager context/@@pager;
                               chunk python:pager.init([1,2,3,4,5,6,7,8,9])">

         <ul tal:repeat="item python:chunk.chunk">
            <li tal:content="item"/>
         </ul>

         <div tal:content="string:Element Count: ${chunk/count}, Page Count: ${chunk/chunkCount}" />

         <tal:block condition="python:chunk.chunkCount > 1">
           <br/>

           <a href="" tal:attributes="href chunk/firstChunkUrl" tal:condition="not:chunk/onFirstChunk"> first </a>

           <a href="" tal:attributes="href chunk/prevChunkUrl" tal:condition="chunk/havePrevChunk"> prev </a>

           <tal:block repeat="item python:chunk.chunkUrlList">
            <a href=""
               tal:define="itemstyle python:item.selected and 'red' or 'black'"
               tal:attributes="href item/url;
                                       style string:color:${itemstyle};" tal:content="item/title"> 1 </a>
           </tal:block>

           <a href="" tal:attributes="href chunk/nextChunkUrl" tal:condition="chunk/haveNextChunk"> next </a>

           <a href="" tal:attributes="href chunk/lastChunkUrl" tal:condition="not:chunk/onLastChunk"> last </a>
          </tal:block>
        </tal:block>

