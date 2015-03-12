## Ideas

* auto-generate slides from *pure* text

  * like latex beamer, pandoc, or
    [showoff](https://github.com/puppetlabs/showoff)

* make it blend nicely with existing slides
  and templates (Impress, PowerPoint etc)

  * have people **reuse** their corporations'
    materials 1:1

## Previous Slide

~~~
## Ideas

* auto-generate slides from *pure* text

  * like latex beamer, pandoc, or
    [showoff](https://github.com/puppetlabs/showoff)

* make it blend nicely with existing slides
  and templates (Impress, PowerPoint etc)

  * have people **reuse** their corporations'
    materials 1:1
~~~

## You can also embed images

![This is alt text](https://wiki.documentfoundation.org/images/8/87/LibreOffice_external_logo_600px.png "This is optional title for a direct img")

## Previous Slide

~~~
## You can also embed images

![This is alt text](https://wiki.documentfoundation.org/images/8/87/LibreOffice_external_logo_600px.png "This is optional title for a direct img")
~~~

## Or actual code

~~~ c++
::basegfx::B2DPolyPolygon VeeWipe::operator () ( double t )
{
    ::basegfx::B2DPolygon poly;
    poly.append( ::basegfx::B2DPoint( 0.0, -1.0 ) );
    const double d = ::basegfx::pruneScaleValue( 2.0 * t );
    poly.append( ::basegfx::B2DPoint(
           0.0, d - 1.0 ) );
    poly.append( ::basegfx::B2DPoint(
           0.5, d ) );
    poly.append( ::basegfx::B2DPoint(
           1.0, d - 1.0 ) );
    poly.append( ::basegfx::B2DPoint(
           1.0, -1.0 ) );
    poly.setClosed(true);
    return ::basegfx::B2DPolyPolygon( poly );
}
~~~

## Previous Slide

~~~
## Or actual code

~~~ c++
::basegfx::B2DPolyPolygon VeeWipe::operator () ( double t )
{
    ::basegfx::B2DPolygon poly;
    poly.append( ::basegfx::B2DPoint( 0.0, -1.0 ) );
    const double d = ::basegfx::pruneScaleValue( 2.0 * t );
    poly.append( ::basegfx::B2DPoint(
           0.0, d - 1.0 ) );
    poly.append( ::basegfx::B2DPoint(
           0.5, d ) );
    poly.append( ::basegfx::B2DPoint(
           1.0, d - 1.0 ) );
    poly.append( ::basegfx::B2DPoint(
           1.0, -1.0 ) );
    poly.setClosed(true);
    return ::basegfx::B2DPolyPolygon( poly );
}
~~~
~~~

## Want to know more?

[`https://github.com/thorstenb/odpgen/`](https://github.com/thorstenb/odpgen/)

`git clone https://github.com/thorstenb/odpgen/`
