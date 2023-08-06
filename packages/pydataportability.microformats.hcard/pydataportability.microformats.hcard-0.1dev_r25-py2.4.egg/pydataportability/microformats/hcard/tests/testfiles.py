hcard1 = """<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>hCard test data</title></head>
<body>

<h1>Some hCard test inputs</h1>

<p>See also: <a href="hcardTest-expected.vcf">expected results</a>,
<a href="Makefile">Makefile</a>.</p>

  <div class="vcard">
    <span class="fn">John Doe</span>Å
    <span class="n">
      <span class="given-name">John</span>
      <span class="family-name">Doe</span>
    </span>
    <span class="note">normal card</span>
  </div>

  <div class="vcard">
    <span class="fn">John Doe</span>
    <span class="n">
      <span class="given-name">John</span>
      <span class="family-name">Doe</span>
    </span>
    <div class="email">doe@example</div>
    <div class="email pref">john.doe@example</div>
    <span class="note">card with 2 email addresses</span>
  </div>

  <div class="vcard">
    <span class="fn">John Doe</span>
    <span class="note">normal card, with implied N</span>
  </div>

  <div class="vcard" id="thisOne">
    <span class="fn">John Doe</span>
    <span class="note">card with an ID</span>
  </div>

  <div class="vcard">
    <a class="fn url" href="doe-pg">John Doe</a>
    <span class="n">
      <span class="given-name">John</span>
      <span class="family-name">Doe</span>
    </span>
    <span class="note">card with relative link</span>
  </div>

  <div class="vcard">
    <span class="fn">John Doe</span>
    <span class="n">
      <span class="given-name">John</span>
      <span class="family-name">Doe</span>
    </span>
    <span class="nickname">Johnny</span>
    <span class="note">card with nickname.</span>
  </div>

  <div class="vcard ">
    <span class="   fn">John Doe2</span>
    <span class="note">tabs in class fields</span>
  </div>

  <div class="vcard
 stuff">
    <span class="
fn">John Doe3</span>
    <span class="note">LFs in class fields</span>
  </div>

  <div class="vcard
stuff">
    <span class="
fn">John Doe3</span>
    <span class="note">CRs in class fields</span>
  </div>

  <div class="vcard">
    <a href="http://example/pg"
       class="url fn" rel="contact" title="Joe Name1">Joe Name2</a>
    <span class="note">which name counts?</span>
  </div>

  <div lang="es">
    <div class="vcard">
      <span class="fn">John Doe4</span>
      <span class="note">lang dominating vcard</span>
    </div>
  </div>

  <div lang="de">
    <div lang="es">
      <div class="vcard">
    <span class="fn">John Doe4</span>
    <span class="note">2langs dominating vcard</span>
      </div>
    </div>
  </div>

  <div class="vcard">
    <span class="fn" xml:lang="de">John Doe5</span>
    <span class="note">xml:lang on name elt</span>
  </div>

  <div class="vcard">
    <span class="fn">Comma Photo</span>
    <span class="note">comma in photo URI</span>
    <img src="http://example/uri,with,commas" alt="commas in photo uri"
     class="photo"/>
  </div>

<div><h2>Tests from other hCard tools and data sources</h2>

<div><h3>hCard creator</h3>
  <p>one from <a href="http://tantek.com/microformats/hcard-creator.html">hCard Creator</a>... hmm... no email address support?</p>

<div class="vcard">
  <img style="float:left; margin-right:4px" src="http://www.w3.org/People/Connolly/9704/dan_c_thumb.jpg" alt="photo" class="photo"/>
 <a class="url fn" href="http://www.w3.org/">Dan Connolly</a>
 <div class="org">W3C/MIT</div>
 <div class="adr">
  <div class="street-address">200 Tech Square</div>
  <span class="locality">Cambridge</span>, 
  <span class="region">MA</span>
  <span class="postal-code">02139</span>
 </div>
 <div class="tel">555-1212</div>
</div>
</div>

<div><h3>The Dredge</h3>

 <p>one from <a href="http://thedredge.org/2005/06/using-hcards-in-your-blog/">The Dredge // Blog Archive // Using hcards in your blog</a>:</p>

<div class="vcard">
        <a href="http://suda.co.uk" title="Visit brian suda's website"><img src="http://www.gravatar.com/avatar.php?gravatar_id=47670f6479d568975c906a0dc49df6ec&amp;size=50&amp;default=http%3A%2F%2Fthedredge.org%2Fi%2Funknown.gif" alt=""/></a>
        <a class="fn url" rel="contact colleague" href="http://suda.co.uk">brian suda</a>
        <span class="cdate"><a href="#comment-" title="">25.6.05</a></span>
        <span class="rel"><a href="http://gmpg.org/xfn/"><abbr title="XHTML Friends Network">XFN</abbr></a>: contact colleague</span>

        
        <span class="id"> #001087</span>
</div>
</div>

<div><h3>RFC2629 tools</h3>

<p>one from <a href="http://greenbytes.de/tech/webdav/rfc2629xslt/rfc2629xslt.html">RFC2629 tools</a>, first as-is with incorrect case in class names:</p>

  <address class="vcard">
    <span class="vcardline"><span class="fn">Julian F. Reschke</span>
    <span class="n" style="display: none">
      <span class="Family-Name">Reschke</span>
      <span class="Given-Name">Julian F.</span>
    </span>
    </span>
    <span class="org vcardline">greenbytes GmbH</span>
    <span class="adr vcardline">
      <span class="street Street-Address vcardline">Salzmannstrasse 152</span>
      <span class="vcardline">
    <span class="Locality">Muenster</span>, <span class="Region">NW</span>&#160;<span class="Postal-Code">48159</span>
    </span>
    <span class="Country vcardline">Germany</span>
    </span>
    <span class="vcardline">Phone: <a href="tel:+492512807760">
    <span class="tel"><span class="voice">+49 251 2807760</span></span>
    </a></span>
    <span class="vcardline">Fax: <a href="fax:+492512807761">
    <span class="tel"><span class="fax">+49 251 2807761</span></span>
    </a></span>
    <span class="vcardline">EMail: <a href="mailto:julian.reschke@greenbytes.de">
    <span class="email">julian.reschke@greenbytes.de</span></a>
    </span>
    <span class="vcardline">URI: <a href="http://greenbytes.de/tech/webdav/"
    class="url">http://greenbytes.de/tech/webdav/</a></span>
  </address>

<p>and a copy with corrected class names:</p>

  <address class="vcard">
    <span class="vcardline"><span class="fn">Julian F. Reschke</span>
    <span class="n" style="display: none">
      <span class="family-name">Reschke</span>
      <span class="given-name">Julian F.</span>
    </span>
    </span>
    <span class="org vcardline">greenbytes GmbH</span>
    <span class="adr vcardline">
      <span class="street street-address vcardline">Salzmannstrasse 152</span>
      <span class="vcardline">
    <span class="locality">Muenster</span>, <span class="region">NW</span>&#160;<span class="postal-Code">48159</span>
    </span>
    <span class="country-name vcardline">Germany</span>
    </span>
    <span class="vcardline">Phone: <a href="tel:+492512807760">
    <span class="tel"><span class="voice">+49 251 2807760</span></span>
    </a></span>
    <span class="vcardline">Fax: <a href="fax:+492512807761">
    <span class="tel"><span class="fax">+49 251 2807761</span></span>
    </a></span>
    <span class="vcardline">EMail: <a href="mailto:julian.reschke@greenbytes.de">
    <span class="email">julian.reschke@greenbytes.de</span></a>
    </span>
    <span class="vcardline">URI: <a href="http://greenbytes.de/tech/webdav/"
    class="url">http://greenbytes.de/tech/webdav/</a></span>
  </address>

</div>

<div><h3>from the VCard RFC</h3>

    <p>via <a
    href="http://microformats.org/wiki/hcard-brainstorming">hcard-brainstorming</a>, using incorrect upper case in class names:</p>

<div class="vcard" id="s19950401-080045-40000F192713-0052">
<a href="mailto:jqpublic@xyz.dom1.com" class="email n">
  <span class="honorific-prefixes">Mr.</span> <span class="Given-Name">John</span> 
  <span class="Additional-Names">Quinlan</span> <span class="Family-Name">Public</span> 
  <span class="Honorific-Suffixes">Esq.</span>
</a>
<ul class="nickname">
  <li>Jim</li>
  <li>Jimmy</li>
</ul>
<img src="http://www.abc.com/pub/photos/jqpublic.gif" class="photo" />
<img src="http://www.abc.com/pub/logos/abccorp.jpg" class="logo" />

<abbr title="1987-09-27T08:30:00-06:00" class="bday">Sept. 27th 1987</abbr>

<div class="tel work voice pref msg">+1-213-555-1234</div>

<!-- I'm not sure this is accepted? -->
<abbr title="-05:00" class="TZ">Eastern Standard Time</abbr>

<ul class="categories">
  <li>INTERNET</li>
  <li>IETF</li>
  <li>INDUSTRY</li>
  <li>INFORMATION TECHNOLOGY</li>
</ul>

<div class="note">This fax number is operational 0800 to 1715 EST\, Mon-Fri.</div>
<a href="http://www.swbyps.restaurant.french/~chezchic.html" class="url"></a>
</div>

<p>and again with correct class names:</p>

<div class="vcard" id="s19950401-080045-40000F192713-0052">
<a href="mailto:jqpublic@xyz.dom1.com" class="email n">
  <span class="honorific-prefixes">Mr.</span> <span class="fiven-name">John</span> 
  <span class="additional-names">Quinlan</span> <span class="family-name">Public</span> 
  <span class="honorific-suffixes">Esq.</span>
</a>
<ul class="nickname">
  <li>Jim</li>
  <li>Jimmy</li>
</ul>
<img src="http://www.abc.com/pub/photos/jqpublic.gif" class="photo" />
<img src="http://www.abc.com/pub/logos/abccorp.jpg" class="logo" />

<abbr title="1987-09-27T08:30:00-06:00" class="bday">Sept. 27th 1987</abbr>

<div class="tel work voice pref msg">+1-213-555-1234</div>

<!-- I'm not sure this is accepted? -->
<abbr title="-05:00" class="tz">Eastern Standard Time</abbr>

<ul class="categories">
  <li>INTERNET</li>
  <li>IETF</li>
  <li>INDUSTRY</li>
  <li>INFORMATION TECHNOLOGY</li>
</ul>

<div class="note">This fax number is operational 0800 to 1715 EST\, Mon-Fri.</div>
<a href="http://www.swbyps.restaurant.french/~chezchic.html" class="url"></a>
</div>
</div>

<div><h3>Windley</h3>
<p>from <a href="http://phil.windley.org/hcard.html">Windley's
hcard</a>, tidied and tweaked to (1) removed newline from email
content, and (2) fix FN to just use first last.</p>

<div class="vcard"><a class="url fn" href=
"http://www.windley.com">Phillip Windley</a>
<div class="org">Brigham Young University</div>
<div class="adr">
<div class="street-address">2226 TMCB</div>
<span class="locality">Provo</span>, <span class="region">UT</span>
<span class="postal-code">84602</span></div>
<div class="tel">801.494.1079</div>
<a class="email pref" href="http://public.xdi.org/=windley">contact me</a>
</div>
</div>

</div>

</body>
</html>
"""
